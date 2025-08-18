import pytest
from sqlalchemy.orm import Session
from sqlmodel import select
from app.models.User import User
from app.models.Transaction import Transaction

# ---------- POSITIVE ----------
def test_db_user_persist_positive(session: Session, fixed_user: User):
    """Пользователь из фикстуры сохранён и доступен по id."""
    u = session.get(User, fixed_user.id)
    assert u is not None
    assert u.email == "user@test.ru"


def test_db_transactions_write_and_order_positive(session: Session, fixed_user: User):
    """Две транзакции пишутся и читаются по порядку id."""
    t1 = Transaction(user_id=fixed_user.id, amount=100.0, type="deposit")
    t2 = Transaction(user_id=fixed_user.id, amount=-30.0, type="withdraw")
    session.add(t1); session.add(t2); session.commit()

    rows = session.exec(
        select(Transaction).where(Transaction.user_id == fixed_user.id).order_by(Transaction.id)
    ).all()

    assert len(rows) >= 2
    assert [rows[-2].amount, rows[-1].amount] == [100.0, -30.0]
    assert hasattr(rows[-1], "id")


# ---------- NEGATIVE ----------
def test_db_user_email_unique_negative(session: Session):
    """Попытка создать двух пользователей с одинаковым email приводит к ошибке."""
    u1 = User(email="uniq@test.ru", password="hash", id="U1")
    session.add(u1); session.commit()

    with pytest.raises(Exception):
        u2 = User(email="uniq@test.ru", password="hash", id="U2")
        session.add(u2); session.commit()
