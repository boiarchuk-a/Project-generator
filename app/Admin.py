import bcrypt
import re
from sqlalchemy import select
from typing import Optional

from app.models.User import User

class UserNotFound(Exception):
    """Исключение для случаев, когда пользователя не удалось найти"""
    pass


class IncorectUserData(Exception):
    """Исключение для случаев, когда данные о пользователе не прошли валидацию"""
    pass


class AuthenticationFail(Exception):
    """Исключение для случая неудачной аутенитификации"""
    pass


class Admin:
    """Класс, обеспечивающий работу с учетными записями пользователей"""

    def find_by_id(self, id: int):
        """Ищет пользователя по заданному id. Если пользователя с таким id нет,
        выбрасывает исключение UserNotFound"""
        q = select(User).filter_by(id=id)
        user = self.__session.scalars(q).first()
        if not user:
            raise UserNotFound(f"Пользователь с user_id={id} не найден")
        return user

    def signin(self, username: str, password: str) -> User:
        """Если заданы верные имя пользователя и пароль, возвращает соответсвующий
        экземпляр User. В ином случае выбрасывает исключение ValueError"""
        q = select(User).filter_by(username=username)
        user = self.__session.scalars(q).first()
        if user and bcrypt.checkpw(password.encode("utf-8"), user.hashed_password):
            return user
        else:
            raise AuthenticationFail("Неверные имя пользователя и/или пароль")

    def __validate_username(self, username: str) -> None:
        """Проверяет корректность имени пользователя (не менее 3 символов, включает
        только буквы, числа или символ _), а также его уникальность (в базе данных
        не может быть два пользователя с одним именем). Если имя некорректно или уже
        занято, выбрасывает исключение ValueError"""
        if not re.fullmatch(r"\w{3,}", username):
            raise IncorectUserData(
                "Имя пользователя должно содержать не менее 3 символов: "
                + "буквы, числа или символ _"
            )
        q = select(User).filter_by(username=username)
        user = self.__session.scalars(q).first()
        if user is not None:
            raise IncorectUserData("Пользователь с заданным именем уже существует")

    def __validate_email(self, email: str) -> None:
        """Проверяет корректность адреса электронной почты. Если адрес некорректен,
        выбрасывает исключение ValueError"""
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
            raise IncorectUserData("Некорректный адрес электронной почты")

    def __validate_password(self, password: str) -> None:
        """Проверяет корректность пароля (не менее 8 символов). Если пароль некорректен,
        выбрасывает исключение ValueError"""
        if len(password) < 8:
            raise IncorectUserData("Пароль должен содержать более 8 символов")

    def __hash_password(self, password: str) -> bytes:
        """Хэширует пароль пользователя для его сохранения в базе данных"""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    def signup(
        self, username: str, password: str, email: str, fullname: Optional[str] = None
    ) -> User:
        """Регистрирует нового пользователя, предварительно валидируя данные"""

        self.__validate_username(username)
        self.__validate_email(email)
        self.__validate_password(password)

        hashed_password = self.__hash_password(password)

        new_user = User(
            username=username,
            hashed_password=hashed_password,
            email=email,
            fullname=fullname,
        )
        self.__session.add(new_user)
        self.__session.commit()
        return new_user

    def __init__(self, session):
        self.__session = session
