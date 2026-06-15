from fastapi import FastAPI
from app.database import engine, Base
import app.models as models
from app.routers import  account, user, auth, cart,payment
import psycopg2
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import app.schema,app.utils
from app.models import Account
from fastapi import Request,Form,Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.oauth2 import get_current_user
from typing import Optional,List
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db

from starlette.middleware.sessions import SessionMiddleware
app = FastAPI()
models.Base.metadata.create_all(bind=engine)
app.router.include_router(account.router)
app.router.include_router(user.router)
app.router.include_router(auth.router)
app.router.include_router(cart.router)
app.router.include_router(payment.router)
app.add_middleware(SessionMiddleware, secret_key="your_secret_key_here")


app.mount("/static", StaticFiles(directory="app/static"), name="static")
Jinja2Templates(directory="app/templates")

@app.get("/")
def home(request: Request, db:Session=Depends(get_db)):
    message = request.session.pop("message", None)
    accounts = db.query(Account).all()
    templates = Jinja2Templates(directory="app/templates/public")
    return templates.TemplateResponse("home.html", {"request": request, "accounts": accounts ,"message": message})
@app.get("/health")
async def health_check():
    return {"status": "alive"}