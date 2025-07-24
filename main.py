from dataclasses import dataclass, field
from typing import List
from datetime import datetime
import re
import hashlib
from typing import Optional

# --- Класс баланса ---
class Balance:
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


# --- Предсказание заголовка ---
@dataclass
class Prediction:
    input_text: str
    generated_title: str
    timestamp: datetime = field(default_factory=datetime.now)

    def preview(self, max_len: int = 30) -> str:
        """Вернуть обрезанную версию текста"""
        return self.input_text[:max_len] + "..."

    def to_dict(self) -> dict:
        """Преобразовать в словарь для логирования/сохранения"""
        return {
            "input": self.input_text,
            "title": self.generated_title,
            "timestamp": self.timestamp.isoformat()
        }

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.generated_title}"

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

    def __hash_password(self, raw_password: str) -> str:
        return hashlib.sha256(raw_password.encode()).hexdigest()

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

# --- Админ ---
class Admin(User):
    def __init__(self, id: int, email: str, password: str):
        super().__init__(id=id, email=email, password=password)

    def view_users(self, users: List[User]):
        print("\n Все пользователи:")
        for u in users:
            print(f" - {u.get_email}, баланс: {u.balance}, предсказаний: {len(u.predictions)}")

    def top_up_balance(self, user: User, amount: float):
        user.balance.deposit(amount)
        print(f" Баланс {user.get_email} пополнен на {amount}₽")

# --- Модель задачи для ML ---
@dataclass
class MLTask:
    id: int
    input_text: str
    created_at: datetime
    status: str = "новая"

    def mark_as_processed(self):
        self.status = "обработана"

    def preview_input(self, length: int = 20) -> str:
        return self.input_text[:length] + "..." if len(self.input_text) > length else self.input_text


# --- История транзакций ---
@dataclass
class Transaction:
    user_id: int
    task: MLTask
    amount: float
    result: str
    timestamp: datetime

    def summary(self) -> str:
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] User {self.user_id} → {self.result}"

@dataclass
class TransactionHistory:
    transactions: List[Transaction] = field(default_factory=list)

    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)

    def get_by_user(self, user_id: int) -> List[Transaction]:
        return [t for t in self.transactions if t.user_id == user_id]

    def count_transactions(self, user_id: int) -> int:
        return len(self.get_by_user(user_id))

    def get_last_transaction(self, user_id: int) -> Optional[Transaction]:
        user_tx = self.get_by_user(user_id)
        return user_tx[-1] if user_tx else None

# --- Модель заголовка (заглушка) ---
class TitleModel:
    def generate_title(self, text: str) -> str:
        """Основной метод генерации заголовка"""
        raise NotImplementedError("Нужно переопределить метод")

    def evaluate_quality(self, title: str) -> str:
        """Простая эвристика для оценки качества заголовка"""
        if len(title) < 10:
            return f"Слишком короткий ({len(title)} символов)"
        elif len(title) > 50:
            return f"Слишком длинный ({len(title)} символов)"
        else:
            return "Хороший"

    def format_title(self, title: str) -> str:
        """Приводит заголовок к формату: первая буква заглавная, без точки"""
        return title.capitalize().strip('.!?')

class SimpleModel(TitleModel):
    def generate_title(self, text: str) -> str:
        return f"[Simple] {text[:30]}..."

class FancyModel(TitleModel):
    def generate_title(self, text: str) -> str:
        return f"[Fancy✨] {text.upper()[:40]}!"

# --- Сервис генерации заголовков ---
class TitleService:
    def __init__(self, model: TitleModel):
        self.model = model

    def generate(self, user: User, text: str) -> Prediction:
        if user.balance.get_balance() < 10:
            raise ValueError("Недостаточно средств на балансе (нужно минимум 10₽)")

        user.balance.withdraw(10)
        title = self.model.generate_title(text)
        prediction = Prediction(input_text=text, generated_title=title)
        user.add_prediction(prediction)
        return prediction

# --- Главная функция ---
def main():
    try:
        # --- Пользователи ---
        user1 = User(id=1, email="user1@example.com", password="password123")
        user2 = User(id=2, email="user2@example.com", password="securepass456")
        admin = Admin(id=0, email="admin@titleforge.ai", password="adminsecure")

        # --- Пополнение баланса ---
        admin.top_up_balance(user1, 100)
        admin.top_up_balance(user2, 80)

        # --- Сервис и модель ---
        model = FancyModel()
        service = TitleService(model)

        # --- Генерация заголовков ---
        raw_text1 = "Это пример исходного текста для генерации заголовка"
        raw_text2 = "Машинное обучение и его применение в образовании"

        prediction1 = service.generate(user1, raw_text1)
        prediction2 = service.generate(user2, raw_text2)

        print("\n Предсказания пользователя 1:")
        for p in user1.get_predictions():
            print("-", p)

        # --- Транзакции ---
        task1 = MLTask(id=1, input_text=raw_text1, created_at=datetime.now())
        task2 = MLTask(id=2, input_text=raw_text2, created_at=datetime.now())

        transaction1 = Transaction(user_id=1, task=task1, amount=10.0, result=prediction1.generated_title, timestamp=datetime.now())
        transaction2 = Transaction(user_id=2, task=task2, amount=10.0, result=prediction2.generated_title, timestamp=datetime.now())

        history = TransactionHistory()
        history.add_transaction(transaction1)
        history.add_transaction(transaction2)

        print("\n История транзакций пользователя 1:")
        for t in history.get_by_user(1):
            print("-", t.summary())

        print("\n Текущий баланс:")
        print(f" - {user1.get_email()}: {user1.balance}")
        print(f" - {user2.get_email()}: {user2.balance}")

        print("\n Информация об админ-панели:")
        admin.view_users([user1, user2])

    except ValueError as e:
        print(f"\n Ошибка: {e}")


if __name__ == "__main__":
    main()