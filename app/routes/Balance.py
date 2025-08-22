from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from app.auth import access_token_user
from app.database.database import get_session
from app.Balance import Balance, BalanceError
from app.models.User import User
from app.shemas.Transactiondata import TransactionData

balance_router = APIRouter()


@balance_router.get("/", summary="Возвращает текущий баланс пользователя")
def get_current_balance(
    user: User = Depends(access_token_user), session=Depends(get_session)
) -> Decimal:
    balance = Balance(session)
    return balance[user].quantize(Decimal("0.01"))


@balance_router.get(
    "/history",
    response_model=List[TransactionData],
    summary="Возвращает историю транзакций пользователя",
)
def get_transactions_history(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    user: User = Depends(access_token_user),
    session=Depends(get_session),
):
    balance = Balance(session)
    return balance.transactions_history(user, start_date, end_date)


@balance_router.post(
    "/replenish", summary="Пополняет баланс пользователя на заданную сумму"
)
def replenish_balance(
    amount: int,
    user: User = Depends(access_token_user),
    session=Depends(get_session),
):
    balance = Balance(session)
    try:
        balance.replenish(user, Decimal(amount))
        return balance[user]
    except BalanceError as be:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(be))
