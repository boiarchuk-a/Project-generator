from sqlmodel import Session, select
from app.models.Balance import Balance

def get_user_balance(session: Session, user_id: int) -> int:
    bal = session.exec(select(Balance).where(Balance.user_id == user_id)).first()
    return bal.credits if bal else 0