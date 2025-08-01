from sqlmodel import SQLModel, Session
from app.database import engine
from app.models.User import User
from app.models.Transaction import Transaction

def init_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Создание пользователей
        demo_user = User(username="demo_user", email="demo@mail.com", password="password123")
        admin = User(username="admin", email="admin@mail.com", password="admin123", role="admin")

        session.add_all([demo_user, admin])
        session.commit()
        session.refresh(demo_user)
        session.refresh(admin)

        # Пример транзакций
        tx1 = Transaction(user_id=demo_user.id, amount=100.0, result="Пополнение")
        tx2 = Transaction(user_id=demo_user.id, amount=-40.0, result="Списание")
        session.add_all([tx1, tx2])
        session.commit()

        print(" База данных инициализирована демо-данными.")


if __name__ == "__main__":
    init_db()
