from dataclasses import dataclass, field
from typing import List
from datetime import datetime
import re

# --- Класс баланса ---
class Balance:
    def __init__(self, amount: float = 0.0):
        self._amount = amount

    def deposit(self, value: float):
        if value < 0:
            raise ValueError("Сумма должна быть положительной")
        self._amount += value

    def withdraw(self, value: float):
        if value > self._amount:
            raise ValueError("Недостаточно средств")
        self._amount -= value

    def get_balance(self) -> float:
        return self._amount

    def __str__(self):
        return f"{self._amount:.2f} ₽"


# --- Предсказание заголовка ---
@dataclass
class Prediction:
    input_text: str
    generated_title: str
    timestamp: datetime = field(default_factory=datetime.now)

# --- Пользователь ---
@dataclass
class User:
    id: int
    email: str
    password: str
    predictions: List[Prediction] = field(default_factory=list)
    balance: Balance = field(default_factory=Balance)

    def __post_init__(self):
        self._validate_email()
        self._validate_password()

    def _validate_email(self):
        pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
        if not pattern.match(self.email):
            raise ValueError("Неверный формат email")

    def _validate_password(self):
        if len(self.password) < 8:
            raise ValueError("Пароль должен быть не менее 8 символов")

    def add_prediction(self, prediction: Prediction):
        self.predictions.append(prediction)

    def __str__(self):
        return f"Пользователь {self.email} — Баланс: {self.balance}"

# --- Админ ---
class Admin(User):
    def __init__(self, id: int, email: str, password: str):
        super().__init__(id=id, email=email, password=password)

    def view_users(self, users: List[User]):
        print("\n Все пользователи:")
        for u in users:
            print(f" - {u.email}, баланс: {u.balance}, предсказаний: {len(u.predictions)}")

    def top_up_balance(self, user: User, amount: float):
        user.balance.deposit(amount)
        print(f" Баланс {user.email} пополнен на {amount}₽")

# --- Модель заголовка (заглушка) ---
class TitleModel:
    def generate_title(self, text: str) -> str:
        return f"Заголовок: {text[:40].strip()}..."


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
        # Пользователи
        user = User(id=1, email="user1@mail.ru", password="strongpass123")

        admin = Admin(id=0, email="admin@titleforge.ai", password="adminsecure")

        # Пополнение баланса
        admin.top_up_balance(user, 50)


        # Сервис генерации
        model = TitleModel()
        service = TitleService(model)

        # Генерация заголовков
        text1 = "Искусственный интеллект меняет подход к образованию и бизнесу."
        prediction1 = service.generate(user, text1)
        print(f"\n Сгенерированный заголовок: {prediction1.generated_title}")
        print(f" Остаток: {user.balance}")

        # Просмотр всех пользователей админом
        admin.view_users([user])

    except ValueError as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()