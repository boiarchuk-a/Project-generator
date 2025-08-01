from models.User import User
from sqlmodel import Session, select
from typing import List, Optional
from models.Transaction import Transaction

def add_balance(user_id: int, amount: float, session: Session) -> Optional[User]:
    user = get_user_by_id(user_id, session)
    if not user:
        return None
    user.balance += amount
    tx = Transaction(user_id=user.id, amount=amount, result="Пополнение")
    session.add(tx)
    session.commit()
    session.refresh(user)
    return user

def deduct_balance(user_id: int, amount: float, session: Session) -> Optional[User]:
    user = get_user_by_id(user_id, session)
    if not user:
        return None
    if user.balance < amount:
        raise ValueError("Недостаточно средств")
    user.balance -= amount
    tx = Transaction(user_id=user.id, amount=-amount, result="Списание")
    session.add(tx)
    session.commit()
    session.refresh(user)
    return user

def get_all_users(session: Session) -> List[User]:
    """ Получить всех пользователей."""
    try:
        statement = select(User)
        return session.exec(statement).all()
    except Exception as e:
        raise


def get_user_by_id(user_id: int, session: Session) -> Optional[User]:
    """ Получить пользователя по ID."""
    try:
        statement = select(User).where(User.id == user_id)
        return session.exec(statement).first()
    except Exception as e:
        raise


def get_user_by_email(email: str, session: Session) -> Optional[User]:
    """ Получить пользователя по email. """
    try:
        statement = select(User).where(User.email == email)
        return session.exec(statement).first()
    except Exception as e:
        raise


def create_user(user: User, session: Session) -> User:
    """ Создать нового пользователя. """
    try:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception as e:
        session.rollback()
        raise


def delete_user(user_id: int, session: Session) -> bool:
    """ Удалить пользователя по ID. """
    try:
        user = get_user_by_id(user_id, session)
        if user:
            session.delete(user)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise
