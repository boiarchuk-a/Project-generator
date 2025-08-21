from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from auth.authenticate import authenticate_cookie, authenticate
from models.User import User
from auth.jwt_handler import create_access_token
from database.database import get_session
from services.auth.loginform import LoginForm
from services.crud import User as UsersService
from database.config import get_settings
from typing import Dict

settings = get_settings()
auth_router = APIRouter()
hash_password = User.hash_password
templates = Jinja2Templates(directory="view")


@auth_router.post("/token")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
                                 session=Depends(get_session)) -> dict[str, str]:
    user_exist = UsersService.get_user_by_email(form_data.username, session)
    if user_exist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    if hash_password.verify_hash(form_data.password, user_exist.password):
        access_token = create_access_token(user_exist.email)
        response.set_cookie(
            key=settings.COOKIE_NAME,
            value=f"Bearer {access_token}",
            httponly=True
        )

        # return {"access_token": access_token, "token_type": "Bearer"}
        return {settings.COOKIE_NAME: access_token, "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid details passed."
    )


@auth_router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    context = {
        "request": request,
    }
    return templates.TemplateResponse("login.html", context)


@auth_router.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, session=Depends(get_session)):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            response = RedirectResponse("/", status.HTTP_302_FOUND)
            await login_for_access_token(response=response, form_data=form, session=session)
            form.__dict__.update(msg="Login Successful!")
            print("[green]Login successful!!!!")
            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrect Email or Password")
            return templates.TemplateResponse("login.html", form.__dict__)
    return templates.TemplateResponse("login.html", form.__dict__)


@auth_router.get("/logout", response_class=HTMLResponse)
async def login_get():
    """
       Выход: удаляем cookie и отправляем на главную.
    """
    response = RedirectResponse(url="/")
    response.delete_cookie(settings.COOKIE_NAME)
    return response
