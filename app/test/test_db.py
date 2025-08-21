import pytest
from sqlalchemy.orm import Session
from sqlmodel import select
from app.models.User import User
from app.models.Transaction import Transaction

# ---------- POSITIVE ----------
def test_db_user_persist_positive(session: Session, fixed_user: User):
    """Пользователь из фикстуры сохранён и доступен по id."""
    user = session.get(User, fixed_user.id)
    assert user is not None
    assert user.email == "user@test.ru"


def test_db_transactions_write_and_order_positive(session: Session, fixed_user: User):
    """Две транзакции пишутся и читаются по порядку id."""
    Transaction1 = Transaction(user_id=fixed_user.id, amount=100.0, type="deposit")
    Transaction2 = Transaction(user_id=fixed_user.id, amount=-30.0, type="withdraw")
    session.add(Transaction1); session.add(Transaction2); session.commit()

    rows = session.exec(
        select(Transaction).where(Transaction.user_id == fixed_user.id).order_by(Transaction.id)
    ).all()

    assert len(rows) >= 2
    assert [rows[-2].amount, rows[-1].amount] == [100.0, -30.0]
    assert hasattr(rows[-1], "id")


# ---------- NEGATIVE ----------
def test_db_user_email_unique_negative(session: Session):
    """Попытка создать двух пользователей с одинаковым email приводит к ошибке."""
    user1 = User(email="uniq@test.ru", password="hash", id="U1")
    session.add(user1); session.commit()

    with pytest.raises(Exception):
        user2 = User(email="uniq@test.ru", password="hash", id="U2")
        session.add(user2); session.commit()
