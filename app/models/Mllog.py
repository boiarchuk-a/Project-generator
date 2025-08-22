from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON
from typing import Dict, Optional

from app.MLstatus import MLstatus
from app.models.base import Base
from app.models.User import User
from app.models.Transaction import Transaction


class Mllog(Base):
    """Класс, представляющий таблицу с данным о запросах, их результатах и связанных
    транзакциях (операции с данным журналом необходимо выполнять посредством класса
    QueryLogHandler)"""

    __tablename__ = "mllog"

    # Колонки transaction_id и result_json заполняются только после того как от воркера
    # будет получен результата работы модели

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    transaction_id: Mapped[Optional[int]] = mapped_column(ForeignKey("transaction.id"))
    timestamp: Mapped[datetime]
    query_text: Mapped[str]
    status: Mapped[MLstatus]
    result_dict: Mapped[Optional[Dict[str, float]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql")
    )

    user: Mapped[User] = relationship(lazy="joined")
    transaction: Mapped[Optional[Transaction]] = relationship(lazy="joined")
