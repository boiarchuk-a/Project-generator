from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from models.Prediction import Prediction
from pydantic import BaseModel
from app.database.database import get_session
from typing import List

prediction_router = APIRouter()

class PredictionRequest(BaseModel):
    input_text: str
@prediction_router.get("/history/{user_id}", response_model=List[Prediction])
def get_prediction_history(user_id: int, session: Session = Depends(get_session)):
    history = session.query(Prediction).filter(Prediction.user_id == user_id).all()
    if not history:
        raise HTTPException(status_code=404, detail="No predictions found for this user")
    return history

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
