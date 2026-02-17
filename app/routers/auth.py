from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import app.models, app.schema, app.utils, app.oauth2
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Request,Form,Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
router = APIRouter(tags=["Authentication"])

@router.get("/login")
def login_page(request: Request):
    templates = Jinja2Templates(directory="app/templates/admin")
    return templates.TemplateResponse("login.html", {
        "request": request
    })


@router.post("/login")
def login( request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    templates = Jinja2Templates(directory="app/templates/admin")
    user = db.query(app.models.User).filter( app.models.User.email == email).first()

    if not user:
        return templates.TemplateResponse("login.html", { "request": request,"message": "Invalid Credentials" })

    if not app.utils.verify_password(password, user.password):
        return templates.TemplateResponse("login.html", {  "request": request, "message": "Invalid Credentials"  })
    access_token = app.oauth2.create_access_token(data={"user_id": user.id})
    response = RedirectResponse(url="/Dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True
    )

    return response

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response