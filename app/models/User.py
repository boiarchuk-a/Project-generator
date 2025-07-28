from dataclasses import dataclass, field
from typing import List
from models.Balance import Balance
from models.Prediction import Prediction
import re
import bcrypt

# --- Пользователь ---
@dataclass
class User:
    id: int

    predictions: List[Prediction] = field(default_factory=list)
    balance: Balance = field(default_factory=Balance)

    # приватные поля
    _email: str = field(init=False, repr=False)
    _password: str = field(init=False, repr=False)

    def __init__(self, id: int, email: str, password: str):
        self.id = id
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
