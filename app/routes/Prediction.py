from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from models.Prediction import Prediction
from pydantic import BaseModel
from app.database.database import get_session  # предполагаем, что у тебя есть функция получения сессии

prediction_router = APIRouter()

class PredictionRequest(BaseModel):
    input_text: str

@prediction_router.post("/")
def generate_prediction(data: PredictionRequest, session: Session = Depends(get_session)):
    generated = f"Generated title for: {data.input_text}"

    prediction = Prediction(
        input_text=data.input_text,
        generated_title=generated,
        timestamp=datetime.utcnow()
    )

    session.add(prediction)
    session.commit()
    session.refresh(prediction)

    return prediction
