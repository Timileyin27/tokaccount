from fastapi import Request, Response
from sqlalchemy.orm import Session
import app.models
from datetime import datetime, timedelta
import uuid

CART_DURATION_MINUTES = 50
def get_or_create_cart(request: Request, response: Response, db: Session):
    cart_reference= request.cookies.get("cart_reference")

    if cart_reference:
        cart = db.query(app.models.Cart).filter(app.models.Cart.cart_reference == cart_reference,app.models.Cart.status ==app.models.CartStatus.ACTIVE).first()
        if cart:
            return cart
    if cart and cart.expire_at < datetime.utcnow():
        cart.status = app.models.CartStatus.EXPIRED
        db.commit()
        cart = None
    if not cart:
        new_reference = str(uuid.uuid4())
        cart = app.models.Cart(cart_reference=new_reference, status=app.models.CartStatus.ACTIVE)
    
    db.add(cart)
    db.commit()
    db.refresh(cart)
    response.set_cookie(
                key="cart_reference",
                value=new_reference,
                httponly=True,
                max_age=50 * 60  
            )

    return cart