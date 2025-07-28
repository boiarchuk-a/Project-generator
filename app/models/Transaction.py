from dataclasses import dataclass
from datetime import datetime
from models.MLTask import MLTask

# --- История транзакций ---
@dataclass
class Transaction:
    user_id: int
    task: MLTask
    amount: float
    result: str
    timestamp: datetime

    def summary(self) -> str:
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] User {self.user_id} → {self.result}"
