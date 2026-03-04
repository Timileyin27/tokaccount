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
def add_to_cart(account_id: int = Form(...),quantity: int = Form(...),request: Request = None, response: Response = None, db: Session = Depends(get_db)):
    cart_reference = request.cookies.get("cart_reference")
    cart = get_or_create_cart(request,response,db)
    account=db.query(app.models.Account).filter(app.models.Account.id == account_id).first()
    if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Account with id: {account_id} not found")
    if account.amount_in_stock < quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not enough stock for account with id: {account_id}")
    
    cart_item = db.query(app.models.CartItem).filter(app.models.CartItem.cart_id == cart.id, app.models.CartItem.account_id == account_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        new_item=app.models.CartItem(cart_id=cart.id, account_id=account_id, quantity=quantity)
        db.add(new_item)
    db.commit()

    return RedirectResponse(url="/cart/view", status_code=303)
@router.get("/view")
def view_cart(request: Request,response:Response, db: Session = Depends(get_db)):
    cart_reference = request.cookies.get("cart_reference")
    cart = get_or_create_cart(request, response, db)
    cart_items = db.query(app.models.CartItem).filter(app.models.CartItem.cart_id == cart.id).all()
    total = sum(item.quantity * item.account.price for item in cart_items)
    templates = Jinja2Templates(directory="app/templates/public")
    return templates.TemplateResponse("cart.html", {"request": request, "cart_items": cart_items, "total": total})