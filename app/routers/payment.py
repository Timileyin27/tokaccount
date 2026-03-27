from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
import app.schema,app.utils
import app.models, app.services.cart_services
from fastapi import Request,Form,Depends,Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.cart_services import get_or_create_cart
from app.services.payment_services import initialize_payment,verify_payment
router = APIRouter(
    prefix="/payment",
    tags=["Payment"]
)
@router.post("/initiate")
def initiate_payment(email: str = Form(...), request: Request=None, db: Session = Depends(get_db)):
    cart, _ = get_or_create_cart(request, db)
    cart_items = db.query(app.models.CartItem).filter(app.models.CartItem.cart_id == cart.id).all()
    total = sum(item.unit_at_addition * item.quantity for item in cart_items)
    response = initialize_payment(email, total)
    print("Paystack Response:",response)
    if not response["status"]:
        return {
        "detail": "Payment initialization failed",
        "paystack_error": response
    }
    payment_url = response["data"]["authorization_url"]
    return RedirectResponse(payment_url, status_code=303)
@router.get("/verify")
def verify(reference:str, request:Request,db:Session=Depends(get_db)):
    cart_reference = request.cookies.get("cart_reference")
    cart = db.query(app.models.Cart).filter(app.models.Cart.cart_reference == cart_reference,app.models.Cart.status==app.models.CartStatus.ACTIVE).first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active cart not found")
    cart_items = db.query(app.models.CartItem).filter(app.models.CartItem.cart_id == cart.id).all()
    total = sum(item.unit_at_addition * item.quantity for item in cart_items)
    response = verify_payment(reference)
    if response["data"]["status"] == "success" and response["data"]["amount"] == int(total * 100):
        new_order = app.models.Order(name="Customer Name",customer_email="email@example.com", total_amount=total,status=app.models.OrderStatus.PENDING)
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        for item in cart_items:
            account = db.query(app.models.Account).filter(app.models.Account.id == item.account_id).first()
            if account.amount_in_stock < item.quantity:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not enough stock for account with id: {account.id}")
            account.amount_in_stock -= item.quantity
            account.amount_sold += item.quantity
            order_item = app.models.OrderItem(order_id=new_order.id, account_id=account.id, quantity=item.quantity, unit_price=item.unit_at_addition)
            db.add(order_item)
            db.delete(item)
        db.commit()   
        request.session["message"] = "Payment successful and order created"
        response = RedirectResponse(url="/cart/view", status_code=303)
        response.delete_cookie("cart_reference")
        return response
@router.get("/callback")
def payment_callback(request: Request):
    templates = Jinja2Templates(directory="app/templates/public")
    reference = request.query_params.get("reference")
    print("Reference:", reference)
    if not reference:
        return templates.TemplateResponse("callback.html", {
            "request": request,
            "error": "No reference provided"
        })
    response = verify_payment(reference)
    print("Verify response:", response)
    if not response.get("status"):
        return templates.TemplateResponse("callback.html", {
            "request": request,
            "error": "Verification failed"
        })
    data = response.get("data")
    if data["status"] != "success":
        return templates.TemplateResponse("callback.html", {
            "request": request,
            "error": "Payment not successful"
        })

    return templates.TemplateResponse("callback.html", {
        "request": request,
        "success": True,
        "reference": reference
    })