from fastapi import APIRouter, HTTPException, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy import select, func
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, desc, func
from sqlalchemy.orm import Session

from app.models.Transaction import Transaction
from app.database.database import get_session
from app.services.crud.Transaction import create_transaction, get_user_transactions

templates = Jinja2Templates(directory="view")
transaction_router = APIRouter()

@transaction_router.post("/deposit")
async def deposit(
    user_id: int,
    amount: float,
    session: AsyncSession = Depends(get_session)
):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    transaction = Transaction(user_id=user_id, amount=amount, type="deposit")
    created_transaction = await create_transaction(transaction, session)
    return {"message": "Deposit successful", "transaction": created_transaction}


@transaction_router.post("/withdraw")
async def withdraw(
    user_id: int,
    amount: float,
    session: AsyncSession = Depends(get_session)
):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    transaction = Transaction(user_id=user_id, amount=-amount, type="withdraw")
    created_transaction = await create_transaction(transaction, session)
    return {"message": "Withdrawal successful", "transaction": created_transaction}


@transaction_router.get("/history/{user_id}", response_model=List[Transaction])
async def get_history(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    transactions = await get_user_transactions(user_id=user_id, session=session)
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found for this user")
    return transactions

@transaction_router.get("/history")
def transaction_history_page(
    request: Request,
    user_id: int = Query(..., description="ID пользователя"),
    page: int = 1,
    per_page: int = 20,
    session: Session = Depends(get_session),
):
    offset = (page - 1) * per_page

    rows = (
        session.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.created_at.desc())   # замени поле, если у тебя другое
        .offset(offset)
        .limit(per_page)
        .all()
    )

    total = (
        session.query(func.count(Transaction.id))
        .filter(Transaction.user_id == user_id)
        .scalar()
    )

    return templates.TemplateResponse(
        "transaction_history.html",
        {
            "request": request,
            "items": rows,
            "page": page,
            "per_page": per_page,
            "total": total,
            "user_id": user_id,
        },
    )