from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
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
from langchain.prompts.chat import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from app.vectordb import retriever

ml_router = APIRouter()




@ml_router.post("/generate-title")
def generate_title(req: MLlogdata):
    # Импорты предполагаются выше:
    # from langchain_core.prompts import ChatPromptTemplate
    # from langchain_community.llms import Ollama as OllamaLLM
    # (или ваша конкретная обёртка для OllamaLLM)

    model = OllamaLLM(model="mistral:7b-instruct")

    # Чёткие placeholder'ы под передаваемые переменные:
    template = """You are an expert in generating good titles for research papers.
Generate a {style}, {title_length} title from the user's abstract.
---
context: {docs}
---
Here is the abstract from the user: {abstract}
---
Output ONLY the generated title and nothing else.
Title: """

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    # Безопасно получаем контекст
    try:
        docs_obj = retriever.invoke(req.abstract)  # если retriever есть
        # Нормализуем в строку
        if isinstance(docs_obj, (list, tuple)):
            docs = "\n\n".join(str(d) for d in docs_obj)
        else:
            docs = str(docs_obj)
    except Exception:
        docs = ""  # работаем и без ретривера

    # <-- ВАЖНО: передаём ВСЕ переменные из шаблона
    output = chain.invoke({
        "docs": docs,
        "abstract": req.abstract,
        "style": getattr(req, "style", "concise"),
        "title_length": getattr(req, "title_length", "short"),
    })

    title = str(output).strip()
    # Если LLM вдруг вернул префикс 'Title:'
    if "Title:" in title:
        title = title.split("Title:", 1)[-1].strip()

    return {"title": title}



@ml_router.get("/price", summary="Возвращает стоимость выполнения запроса")
def get_query_price(
        text: str
) -> Decimal:
    try:
        return ML(text).price
    except IncorrectML as iq:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(iq))


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