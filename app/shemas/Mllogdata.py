from datetime import datetime
from pydantic import BaseModel
from typing import Dict, Optional

from app.shemas.Transactiondata import TransactionData

class MLlogdata(BaseModel):
    """Данные о запросе, возвращаемые пользователю"""

    # Когда мы возвращаем пользователю данные о запросе, то делаем это
    # для уже определенного пользователя, поэтому включать сюда информацию
    # о пользователе, который сделал запрос, нет необходимости

    id: int
    transaction: Optional[TransactionData]
    timestamp: datetime
    query_text: str
    status: int
    result_dict: Optional[Dict[str, float]]
    abstract: str
    title_length: str
    style: str
    model_config = {"from_attributes": True}
