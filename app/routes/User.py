from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.auth import (
    create_access_token,
    add_access_token_to_cookie,
    access_token_user,
    delete_access_token_from_cookie,
)
from app.database.database import get_session
from app.models.User import User
from app.Admin import Admin, IncorectUserData, AuthenticationFail
from app.shemas.Userdata import UserDataForSignin, UserDataForSignup, UserDataForBaseView

user_router = APIRouter()


@user_router.post(
    "/signup", status_code=status.HTTP_201_CREATED, summary="Регистрирует пользователя"
)
def signup(
    user_data: UserDataForSignup, response: Response, session=Depends(get_session)
):
    users_manager = Admin(session)
    try:
        new_user = users_manager.signup(**dict(user_data))
        token = create_access_token(new_user)
        add_access_token_to_cookie(token, response)
    except IncorectUserData as iud:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(iud))


@user_router.post("/signin", summary="Осуществляет аутентификацию пользователя")
def signin(
    user_data: UserDataForSignin, response: Response, session=Depends(get_session)
):
    users_manager = Admin(session)
    try:
        user = users_manager.signin(**dict(user_data))
    except AuthenticationFail as af:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(af))
    token = create_access_token(user)
    add_access_token_to_cookie(token, response)


@user_router.post("/exit", summary="Выход пользователя из учетной записи")
def exit(response: Response):
    # Просто удалим куки с токеном. Перенаправление на страницу логина
    # сделает уже js
    delete_access_token_from_cookie(response)

@user_router.get(
    "/me",
    response_model=UserDataForBaseView,
    summary="Возвращает данные пользователя для его личной страницы",
)
def about_me(user: User = Depends(access_token_user)):
    return user
