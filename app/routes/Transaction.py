from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from models.Transaction import Transaction
from database.database import get_session
from services.crud.Transaction import create_transaction, get_user_transactions

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
