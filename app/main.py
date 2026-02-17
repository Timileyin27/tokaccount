from fastapi import FastAPI
from app.database import engine, Base
import app.models as models
from app.routers import  account, user, auth
import psycopg2
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
models.Base.metadata.create_all(bind=engine)
app.router.include_router(account.router)
app.router.include_router(user.router)
app.router.include_router(auth.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
Jinja2Templates(directory="app/templates")
