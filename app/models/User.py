from dataclasses import dataclass, field
from typing import List
from Balance import Balance
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


    # приватные поля
    _email: Optional[str] = None
    _password: Optional[str] = None
    predictions: List[Prediction] = []
    balance: Optional["Balance"] = Relationship(back_populates="user")

    def __init__(self, id: int, email: str, password: str, username: str, role: str = 'user'):
        self.id = id
        self.username = username
        self.role = role
        self._email = email
        self._password = password
        self.predictions = []
        self.balance = Balance()
        self.__post_init__()

    def __post_init__(self):
        self.__validate_email()
        self.__validate_password()

    def __validate_email(self):
        pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
        if not pattern.match(self._email):
            raise ValueError("Неверный формат email")

    def __validate_password(self):
        if len(self._password) < 8:
            raise ValueError("Пароль должен быть не менее 8 символов")
        self.__password = self.__hash_password(self._password)

    def __hash_password(self, password: str) -> bytes:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt)

    def check_password(self, input_password: str) -> bool:
        return self.__hash_password(input_password) == self._password

    def get_email(self) -> str:
        return self._email

    def add_prediction(self, prediction: Prediction):
        self.predictions.append(prediction)

    def get_predictions(self) -> List[Prediction]:
        return self.predictions

    def __str__(self):
        return f"[User] {self._email} — Баланс: {self.balance}"
