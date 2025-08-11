# app/routes/ml.py
from typing import Dict
from fastapi import APIRouter, HTTPException
from services.rm.rm import send_task  # важно: импорт из services.rm, не services.rm.rm

ml_route = APIRouter(prefix="/ml", tags=["ML"])

@ml_route.post(
    "/send_task",
    response_model=Dict[str, str],
    summary="Отправить задачу в RabbitMQ",
    description="Принимает текст сообщения и публикует его в очередь."
)
async def send_ml_task(message: str) -> Dict[str, str]:
    """
    Публикация задачи в очередь RabbitMQ через services.rm.send_task.
    """
    try:
        if not message or not message.strip():
            raise HTTPException(status_code=422, detail="message is empty")

        send_task(message)  # синхронная публикация
        return {"message": "Task sent successfully!"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
