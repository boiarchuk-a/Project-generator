from models.Transaction import Transaction
from sqlmodel import select
from sqlalchemy.orm import Session
from typing import List, Optional

def get_user_transactions(user_id: int, session: Session) -> List[Transaction]:
    statement = select(Transaction).where(Transaction.user_id == user_id)
    return session.exec(statement).all()

def get_all_transactions(session: Session) -> List[Transaction]:
    try:
        statement = select(Transaction)
        return session.exec(statement).all()
    except Exception as e:
        raise

def get_transactions_by_user(user_id: int, session: Session) -> List[Transaction]:
    try:
        statement = select(Transaction).where(Transaction.user_id == user_id)
        return session.exec(statement).all()
    except Exception as e:
        raise

def create_transaction(transaction: Transaction, session: Session) -> Transaction:
    try:
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        return transaction
    except Exception as e:
        session.rollback()
        raise

def delete_transaction(transaction_id: int, session: Session) -> bool:
    try:
        statement = select(Transaction).where(Transaction.id == transaction_id)
        transaction = session.exec(statement).first()
        if not transaction:
            return False
        session.delete(transaction)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise
