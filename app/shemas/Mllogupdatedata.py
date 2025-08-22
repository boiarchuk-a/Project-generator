from pydantic import BaseModel
from typing import Dict, Optional


class MLlogupdatedata(BaseModel):
    """Обновление статуса запроса, возвращаемое mlworker"""

    id: int
    status: int
    result_dict: Optional[Dict[str, float]]
