from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, field_validator


class TransactionData(BaseModel):
    """Данные о транзакции, возвращаемые пользователю"""

    # Когда мы возвращаем пользователю данные о транзакции, то делаем это
    # для уже определенного пользователя, поэтому включать сюда информацию
    # о пользователе, который сделал транзакцию, нет необходимости

    id: int
    timestamp: datetime
    amount: Decimal
    balance: Decimal

    @field_validator("amount")
    def quantize_amount(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"))

    @field_validator("balance")
    def quantize_balance(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"))

    model_config = {"from_attributes": True}
