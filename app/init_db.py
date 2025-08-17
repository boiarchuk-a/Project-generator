from sqlmodel.orm import SQLModel, Session
from datetime import datetime
from database.database import engine
from models.User import User
from models.Transaction import Transaction
from app.MLTask import MLTask
from app.TitleModel import FancyModel
from app.TitleService import TitleService
from services.crud.Transaction import get_user_transactions
from app.TransactionHistory import TransactionHistory
def init_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # --- Пользователи ---
        demo_user = User(username="demo_user", email="demo@mail.com", password="password123")
        admin = User(username="admin", email="admin@mail.com", password="admin123", role="admin")
        session.add_all([demo_user, admin])
        session.commit()
        session.refresh(demo_user)
        session.refresh(admin)

        # --- Транзакции ---
        tx1 = Transaction(user_id=demo_user.id, amount=100.0, result="Пополнение")
        tx2 = Transaction(user_id=demo_user.id, amount=-40.0, result="Списание")
        session.add_all([tx1, tx2])
        session.commit()

        # --- Инициализация модели и задачи ---
        model = FancyModel()
        service = TitleService(model)

        raw_text = "Демонстрация ML-сервиса заголовков"
        prediction = service.generate(demo_user, raw_text)

        task = MLTask(
            input_text=raw_text,
            created_at=datetime.now()
        )

        tx_model = Transaction(
            user_id=demo_user.id,
            task=task,
            amount=10.0,
            result=prediction.generated_title,
            timestamp=datetime.now()
        )

        session.add_all([task, tx_model])
        session.commit()

        print("База данных инициализирована демо-данными и ML-моделью.")


        transactions = get_user_transactions(demo_user.id, session)
        print(f"История транзакций demo_user: {[t.result for t in transactions]}")

        history = TransactionHistory()
        history.add_transaction(tx_model)


        print("\n История транзакций пользователя 1:")
        for t in history.get_by_user(1):
            print("-", t.summary())

if __name__ == "__main__":
    init_db()
