from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .User import User

# --- Класс баланса ---
class Balance(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    # one-to-one: уникальная ссылка на пользователя
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)

    credits: int = Field(default=0, ge=0)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # обратная связь к пользователю
    user: Optional["User"] = Relationship(back_populates="balance")


    def __init__(self, amount: float = 0.0):
        self.__amount = amount

    def deposit(self, value: float):
        if value < 0:
            raise ValueError("Сумма должна быть положительной")
        self.__amount += value

    def withdraw(self, value: float):
        if value > self.__amount:
            raise ValueError("Недостаточно средств")
        self.__amount -= value

    def get_balance(self) -> float:
        return self.__amount

    def __str__(self):
        return f"{self.__amount:.2f} ₽"
