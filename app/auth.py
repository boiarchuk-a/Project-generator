from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, Request, Response, status
from jose import jwt
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.database.database import get_session
from app.models.User import User
from app.Admin import Admin

class AuthSettings(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_TOKEN_COOKIE_KEY: str

    model_config = SettingsConfigDict(
        env_file="app/.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

auth_settings = AuthSettings()  # type: ignore

def add_access_token_to_cookie(access_token: str, response: Response):
    """Добавляет JWT токен к HTTP ответу"""
    response.set_cookie(
        key=auth_settings.JWT_TOKEN_COOKIE_KEY,
        value=f"Bearer {access_token}",
        httponly=True,
    )

def delete_access_token_from_cookie(response: Response):
    """Удаляет JWT токен из HTTP ответа"""
    response.delete_cookie(key=auth_settings.JWT_TOKEN_COOKIE_KEY)

def create_access_token(user: User) -> str:
    """Формирует JWT токен для заданного пользователя"""
    DURATION = timedelta(hours=1)
    payload = {
        "user_id": user.id,
        "exp": (datetime.now(timezone.utc) + DURATION).timestamp(),
    }
    access_token = jwt.encode(payload, auth_settings.JWT_SECRET_KEY, algorithm="HS256")
    return access_token

def access_token_user(request: Request, session=Depends(get_session)) -> User:
    """Берет из куки JWT токен, проверяет его, находит и возвращает пользователя.
    Если что-то пошло не так (отсутствует токен, он просрочен, является некорректным
    по какой-либо еще причине и т.д.) возвращает 403 код (клиентская часть при его
    получении выполняет редирект на страницу логина)"""
    # jwt.decode() автоматически проверяет в числе прочего срок действия токена,
    # если установлен exp, поэтому вручную этого можно не делать
    users_manager = Admin(session)
    try:
        access_token_cookie = request.cookies[auth_settings.JWT_TOKEN_COOKIE_KEY]
        access_token = access_token_cookie[len("Bearer ") :]
        claims = jwt.decode(
            access_token, auth_settings.JWT_SECRET_KEY, algorithms=["HS256"]
        )
        user_id = claims["user_id"]
        return users_manager.find_by_id(user_id)
    except:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
