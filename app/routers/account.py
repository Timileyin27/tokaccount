from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status,Request
from sqlalchemy.orm import Session
from sqlalchemy import func
import app.schema,app.utils
import app.models
from fastapi import Request,Form,Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.oauth2 import get_current_user
from typing import Optional,List
from sqlalchemy import func

router = APIRouter(
        prefix="/Dashboard",
    tags=["Dashboard"]
)
@router.get("/")
def read_accounts(request: Request, db:Session=Depends(get_db),current_user:app.models.User=Depends(get_current_user)):
    templates = Jinja2Templates(directory="app/templates/admin")
    accounts = db.query(app.models.Account).filter(app.models.Account.owner_id == current_user.id).all()
    total_revenue = db.query(func.sum(app.models.Account.price * app.models.Account.amount_sold)).filter(app.models.Account.owner_id == current_user.id).scalar() or 0
    total_stock_value = db.query(func.sum( app.models.Account.amount_in_stock)).filter( app.models.Account.owner_id == current_user.id
    ).scalar() or 0
    total_sold_value = db.query(func.sum(app.models.Account.amount_sold)).filter(app.models.Account.owner_id == current_user.id
    ).scalar() or 0
    total_accounts = db.query(func.count(app.models.Account.id)).filter(app.models.Account.owner_id == current_user.id
    ).scalar() or 0

    return templates.TemplateResponse("dashboard.html", {"request": request,"current_user":current_user, "accounts": accounts,"total_stock_value": total_stock_value,"total_sold_value": total_sold_value,"total_accounts": total_accounts,"total_revenue": total_revenue})
@router.post("/", status_code=status.HTTP_201_CREATED,)
def create_account( request: Request, name: str = Form(...), price: float = Form(...),amount_in_stock: int =Form(...),amount_sold: int =Form(...),db:Session=Depends(get_db),current_user:app.models.User=Depends(get_current_user)): 
    templates = Jinja2Templates(directory="app/templates/admin")
    account = app.models.Account(owner_id=current_user.id, name=name,price=price,amount_in_stock=amount_in_stock,amount_sold=amount_sold)
    db.add(account)
    db.commit()
    response = RedirectResponse(url="/Dashboard/", status_code=303)

    return response
@router.get("/add")
def add_account(request: Request, db:Session=Depends(get_db),current_user:app.models.User=Depends(get_current_user)):
    templates = Jinja2Templates(directory="app/templates/admin")
    return templates.TemplateResponse("add_account.html", {"request": request,"current_user":current_user})
@router.get("order")
def order_accounts(request: Request, db:Session=Depends(get_db)):
    templates = Jinja2Templates(directory="app/templates/admin")
    orders = db.query(app.models.Order).order_by(app.models.Order.created_at.desc()).all()
    return templates.TemplateResponse("order.html", {"request": request, "orders": orders})