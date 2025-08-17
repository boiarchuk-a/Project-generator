from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi import Request, Depends, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, desc, func
from datetime import datetime
from app.models.User import User
from app.Prediction import Prediction
from pydantic import BaseModel
from app.database.database import get_session
from typing import List

templates = Jinja2Templates(directory="view")
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

@prediction_router.get("/history")
def prediction_history_page(
    request: Request,
    user_id: int = Query(..., description="ID пользователя"),
    page: int = 1,
    per_page: int = 20,
    session: Session = Depends(get_session),
):
    offset = (page - 1) * per_page


    rows = (
        session.query(Prediction)
        .filter(Prediction.user_id == user_id)
        .order_by(Prediction.timestamp.desc())
        .offset(offset)
        .limit(per_page)
        .all()
    )

    total = (
        session.query(func.count(Prediction.id))
        .filter(Prediction.user_id == user_id)
        .scalar()
    )

    return templates.TemplateResponse(
        "prediction_history.html",
        {
            "request": request,
            "items": rows,
            "page": page,
            "per_page": per_page,
            "total": total,
            "user_id": user_id,
        },
    )
