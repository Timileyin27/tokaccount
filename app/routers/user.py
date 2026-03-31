from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
import app.schema,app.utils
import app.models
from fastapi import Request,Form,Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
router = APIRouter(
        prefix="/users",
    tags=["Users"]
)
@router.get("/", )
def read_users(request: Request, db:Session=Depends(get_db)):
    templates = Jinja2Templates(directory="app/templates/admin")
    users = db.query(app.models.User).all()
    return templates.TemplateResponse("register.html", {"request": request, "users": users})
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user( request: Request, email: str = Form(...), password: str = Form(...),confirm_password:str=Form(...),db:Session=Depends(get_db)):
      templates = Jinja2Templates(directory="app/templates/admin")

      hashed_password=app.utils.hash_password(password)
      existing_user = db.query(app.models.User).filter(app.models.User.email == email).first()
      if existing_user:
            return templates.TemplateResponse("register.html", {"request": request, "message": "Email already registered"})
      user = app.models.User(
        email=email,
        password=hashed_password,
    )
      db.add(user)
      db.commit()
      db.refresh(user)
      access_token = app.oauth2.create_access_token(data={"user_id": user.id})
      response = RedirectResponse(url="/Dashboard", status_code=303)
      response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True
    )

      return response
@router.get("/{id}", response_model=app.schema.UserOut)
def get_user(id:int, db:Session=Depends(get_db)):
    user = db.query(app.models.User).filter(app.models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} not found")
    return user