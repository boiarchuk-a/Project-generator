from app.models.MLTask import MLTask
from models.User import User
from app.Admin import Admin
from app.TitleModel import FancyModel
from app.TitleService import TitleService
from models.Transaction import Transaction
from app.TransactionHistory import TransactionHistory
from datetime import datetime

# --- Главная функция ---
if __name__ == "__main__":
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
