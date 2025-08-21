from dataclasses import dataclass, field
from typing import List

from models.MLTask import MLTask
from .Balance import Balance
from Prediction import Prediction
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import re
import bcrypt

if TYPE_CHECKING:
    from .Transaction import Transaction

# --- Пользователь ---
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    hashed_password: str
    role: str = "user"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    email: str = Field(index=True, unique=True)

    # приватные поля
    _password: Optional[str] = None
    balance: Optional["Balance"] = Relationship(back_populates="user")
    transactions: List["Transaction"] = Relationship(back_populates="user")
    ml_tasks: List["MLTask"] = Relationship(back_populates="user")


    def __post_init__(self):
        self.__validate_email()
        self.__validate_password()

    def __validate_email(self):
        pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
        if not pattern.match(self.email):
            raise ValueError("Неверный формат email")

    def __validate_password(self):
        if len(self._password) < 8:
            raise ValueError("Пароль должен быть не менее 8 символов")
        self.hashed_password = self.hash_password(self._password)

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt)

    def check_password(self, input_password: str) -> bool:
        return self.hash_password(input_password) == self.hashed_password

    def get_email(self) -> str:
        return self.email

    def add_prediction(self, prediction: Prediction):
        self.predictions.append(prediction)

    def get_predictions(self) -> List[Prediction]:
        return self.predictions

    def __str__(self):
        return f"[User] {self.email} — Баланс: {self.balance}"
