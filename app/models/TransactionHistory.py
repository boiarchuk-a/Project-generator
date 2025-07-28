from dataclasses import dataclass, field
from typing import List
from typing import Optional
from models.Transaction import Transaction

# --- История транзакций ---
@dataclass
class TransactionHistory:
    transactions: List[Transaction] = field(default_factory=list)

    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)

    def get_by_user(self, user_id: int) -> List[Transaction]:
        return [t for t in self.transactions if t.user_id == user_id]

    def count_transactions(self, user_id: int) -> int:
        return len(self.get_by_user(user_id))

    def get_last_transaction(self, user_id: int) -> Optional[Transaction]:
        user_tx = self.get_by_user(user_id)
        return user_tx[-1] if user_tx else None