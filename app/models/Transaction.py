from dataclasses import dataclass
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.User import User

# --- История транзакций ---
class Transaction(SQLModel, table=True):
    user: Optional[User] = Relationship(back_populates="transactions")
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

    amount: float
    result: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    def summary(self) -> str:
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] User {self.user_id} → {self.result}"
