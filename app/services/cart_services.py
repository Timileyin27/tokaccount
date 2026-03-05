from fastapi import Request, Response
from sqlalchemy.orm import Session
import app.models
from datetime import datetime, timedelta
import uuid

CART_DURATION_MINUTES = 50
def get_or_create_cart(request: Request,  db: Session):
    cart_reference= request.cookies.get("cart_reference")
    cart = None
    if cart_reference:
        cart = db.query(app.models.Cart).filter(app.models.Cart.cart_reference == cart_reference,app.models.Cart.status ==app.models.CartStatus.ACTIVE).first()
        
    
    if not cart:
        new_reference = str(uuid.uuid4())
        cart = app.models.Cart(cart_reference=new_reference, status=app.models.CartStatus.ACTIVE)
    
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return cart, new_reference
    return cart, None