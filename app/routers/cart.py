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
router = APIRouter(
        prefix="/cart",
    tags=["Cart"]
)
@router.post("/add")
def add_to_cart(account_id: int = Form(...),quantity: int = Form(...),request: Request = None, db: Session = Depends(get_db)):
    cart,new_reference = get_or_create_cart(request,db)
    account=db.query(app.models.Account).filter(app.models.Account.id == account_id).first()
    if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Account with id: {account_id} not found")
    if account.amount_in_stock < quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not enough stock for account with id: {account_id}")
    
    cart_item = db.query(app.models.CartItem).filter(app.models.CartItem.cart_id == cart.id, app.models.CartItem.account_id == account_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        new_item=app.models.CartItem(cart_id=cart.id, account_id=account_id, quantity=quantity,unit_at_addition=account.price)
        db.add(new_item)
    db.commit()

    request.session["message"] = "Account added to cart"

    response = RedirectResponse(request.headers.get("referer"), status_code=303)
    if new_reference:
        response.set_cookie(
            key="cart_reference",
            value=new_reference,
            httponly=True,
            max_age=50 * 60
        )

    return response
@router.get("/view")
def view_cart(request: Request, db: Session = Depends(get_db)):
    cart_reference = request.cookies.get("cart_reference")
    cart, _ = get_or_create_cart(request, db)
    cart_items = db.query(app.models.CartItem).filter(app.models.CartItem.cart_id == cart.id).all()
    total = sum(item.quantity * item.unit_at_addition  for item in cart_items)
    templates = Jinja2Templates(directory="app/templates/public")
    return templates.TemplateResponse("cart.html", {"request": request, "cart_items": cart_items, "total": total})
@router.post("/remove/{cart_item_id}")
def remove_from_cart(cart_item_id: int, request: Request, db: Session = Depends(get_db)):
    cart, _ = get_or_create_cart(request, db)
    cart_item = db.query(app.models.CartItem).filter(app.models.CartItem.id == cart_item_id, app.models.CartItem.cart_id == cart.id).first()
    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cart item with id: {cart_item_id} not found in your cart")
    db.delete(cart_item)
    db.commit()
    return RedirectResponse(url="/cart/view", status_code=303)
@router.get("/checkout")
def checkout(request: Request, db:Session=Depends(get_db),):
    cart_reference = request.cookies.get("cart_reference")
    cart, _ = app.services.cart_services.get_or_create_cart(request, db)
    cart_items = db.query(app.models.CartItem).filter(app.models.CartItem.cart_id == cart.id).all()
    total = sum(item.quantity * item.unit_at_addition  for item in cart_items)
    templates = Jinja2Templates(directory="app/templates/public")
    return templates.TemplateResponse("checkout.html", {"request": request, "cart_items": cart_items, "total": total})