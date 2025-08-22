from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
import aiohttp
import json
import os

from app.auth import access_token_user
from app.database.database import get_session
from app.ML import ML, IncorrectML
from app.MLstatus import MLstatus
from app.mlworkerproxy import MLWorkerProxy
from app.models.User import User
from app.MLhistory import MLhistory
from app.Prediction import Prediction
from app.shemas.Mllogdata import MLlogdata
from app.shemas.Mllogupdatedata import MLlogupdatedata
from app.Admin import Admin, UserNotFound

ml_router = APIRouter()


class OllamaClient:
    def __init__(self):
        # Используем host.docker.internal для доступа к хосту из контейнера
        # или имя сервиса Ollama в Docker Compose
        self.ollama_url = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
        self.model_name = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")

    async def generate_title(self, text: str) -> dict:
        """Генерирует заголовок для текста используя Ollama"""
        try:
            prompt = f"""
            Создай краткий и информативный заголовок для этого текста на русском языке.
            Заголовок должен отражать основную суть текста и быть не длиннее 10 слов.

            Текст: {text}

            Заголовок:
            """

            data = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 50,
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                        f"{self.ollama_url}/api/generate",
                        json=data,
                        timeout=30
                ) as response:

                    if response.status == 200:
                        result = await response.json()
                        title = result.get('response', '').strip()
                        return {"title": title, "success": True}
                    else:
                        return {"error": f"Ollama API error: {response.status}", "success": False}

        except Exception as e:
            return {"error": str(e), "success": False}


# Создаем клиент Ollama
ollama_client = OllamaClient()


@ml_router.post("/execute", summary="Отправляет запрос на исполнение")
async def send_query_for_execution(
        text: str,
        user: User = Depends(access_token_user),
        session=Depends(get_session)
):
    ml_worker_proxy = MLWorkerProxy(session)
    try:
        query = ML(text)
        # Генерируем заголовок сразу при выполнении запроса
        result = await ollama_client.generate_title(text)
        if result["success"]:
            # Создаем prediction с заголовком
            prediction = Prediction(title=result["title"])
            await ml_worker_proxy.send(user, query, prediction)
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                f"Ошибка генерации заголовка: {result.get('error', 'Unknown error')}")
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@ml_router.get("/price", summary="Возвращает стоимость выполнения запроса")
def get_query_price(
        text: str
) -> Decimal:
    try:
        return ML(text).price
    except IncorrectML as iq:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(iq))


@ml_router.put(
    "/update", summary="Служебный endpoint для получения данных от воркера"
)
async def update_querylog(query_log_update: MLlogupdatedata, session=Depends(get_session)):
    ml_worker_proxy = MLWorkerProxy(session)
    await ml_worker_proxy.recieve(
        query_log_update.id,
        MLstatus(query_log_update.status),
        (
            Prediction(**query_log_update.result_dict)
            if query_log_update.result_dict
            else None
        ),
    )


@ml_router.get(
    "/history",
    response_model=List[MLlogdata],
    summary="Возвращает историю запросов к ML модели",
)
async def get_queries_history(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        user: User = Depends(access_token_user),
        session=Depends(get_session),
):
    query_log_handler = MLhistory(session)
    return await query_log_handler.get_for_user(user, start_date, end_date)