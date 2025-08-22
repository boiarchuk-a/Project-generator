from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from app.models.base import Base

class User(Base):
    """Класс, представляющий таблицу с данным о пользователях (операции с пользователями
    и их валидацию необходимо выполнять посредством класса UsersManager)"""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[bytes]
    email: Mapped[str]
    fullname: Mapped[Optional[str]]
