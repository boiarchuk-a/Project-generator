from datetime import datetime
from decimal import Decimal
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.User import User


class Transaction(Base):
    """Класс, представляющий таблицу с данным о транзакциях (операции с транзакциями
    и их валидацию необходимо выполнять посредством класса Balance)"""

    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    timestamp: Mapped[datetime]
    amount: Mapped[Decimal]  # Сумма транзакции (+ пополнение, - трата на услугу)
    balance: Mapped[Decimal]  # Остаток на счету после выполнения транзакции

    user: Mapped[User] = relationship(lazy="joined")
