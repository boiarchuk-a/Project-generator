from pydantic import BaseModel
from typing import Optional


class UserDataForSignin(BaseModel):
    """Данные пользователя, необходимые для авторизации"""

    username: str
    password: str


class UserDataForSignup(UserDataForSignin):
    """Данные пользователя, необходимые для регистрации"""

    email: str
    fullname: Optional[str] = None


class UserDataForBaseView(BaseModel):
    """Данные пользователя, отображаемые на страницу /view/user/base"""

    username: str
    email: str
    fullname: Optional[str] = None

    model_config = {"from_attributes": True}
