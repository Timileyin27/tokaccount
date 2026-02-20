from fastapi import FastAPI
from app.database import engine, Base
import app.models as models
from app.routers import  account, user, auth
import psycopg2
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import app.schema,app.utils
import app.models
from fastapi import Request,Form,Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.oauth2 import get_current_user
from typing import Optional,List
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db

app = FastAPI()
models.Base.metadata.create_all(bind=engine)
app.router.include_router(account.router)
app.router.include_router(user.router)
app.router.include_router(auth.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
Jinja2Templates(directory="app/templates")

@app.get("/")
def home(request: Request, db:Session=Depends(get_db),):
    templates = Jinja2Templates(directory="app/templates/public")
    return templates.TemplateResponse("home.html", {"request": request})