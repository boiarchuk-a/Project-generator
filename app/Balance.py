from datetime import datetime, date, time
from decimal import Decimal
from sqlalchemy import select
from typing import List, Optional

from app.models.User import User
from app.models.Transaction import Transaction

class BalanceError(Exception):
    """Специальное исключение для ошибок, связанных с выполнением операций с балансом"""
    pass

class Balance:
    """Класс представлят методы для работы с хранилищем транзакций всех пользователей"""

    def replenish(self, user: User, amount: Decimal) -> Transaction:
        """Пополняет баланс пользователя на заданную сумму и возвращает экземпляр
        Transaction. При невозможности пополнения генерирует исключение
        BalanceError"""
        if amount <= 0:
            raise BalanceError("Баланс может быть пополнен только на сумму > 0")
        transaction = Transaction(
            user_id=user.id,
            timestamp=datetime.now(),
            amount=amount,
            balance=self[user] + amount,
        )
        self.__session.add(transaction)
        self.__session.commit()
        return transaction

    def pay(self, user: User, amount: Decimal) -> Transaction:
        """Списывает деньги с баланса пользователя на выполнение запроса и возвращает
        экземпляр Transaction. При недостаточности денег генерирует исключение
        BalanceError"""
        if amount <= 0:
            raise BalanceError("Сумма платежа должна быть > 0")
        if self[user] < amount:
            raise BalanceError("Недостаточно средств на балансе пользователя")
        transaction = Transaction(
            user_id=user.id,
            timestamp=datetime.now(),
            amount=amount * (-1),
            balance=self[user] - amount,
        )
        self.__session.add(transaction)
        self.__session.commit()
        return transaction

    def __getitem__(self, user: User) -> Decimal:
        """Для получения текущего баланса пользователя реализуем поддержку
        синтаксиса [...]"""
        q = (
            select(Transaction.balance)
            .filter_by(user_id=user.id)
            .order_by(Transaction.id.desc())
        )
        user_balance = self.__session.scalars(q).first()
        if user_balance is None:
            # Если в таблице ничего не нашлось, то пользователь никогда
            # не пополнял баланс, значит он равен 0
            user_balance = Decimal(0)
        return user_balance

    def transactions_history(
        self,
        user: User,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Transaction]:
        """Возвращает историю транзакций пользователя между заданными датами.
        Если start_date не задана, возвращаются транзакции, начиная с самой ранней.
        Если end_date не задана, возвращаются все транзакции до момента вызова метода"""
        if start_date is None:
            # Произвольная дата, ранее которой точно не может быть транзакций в БД
            start_date = date(2025, 1, 1)
        if end_date is None:
            end_date = datetime.now()
        # Если не установить время, то при вызове between будут взяты 00 час 00 мин
        # последней даты, то есть записи последнего дня не будут учтены
        end_date = datetime.combine(
            end_date, time(hour=23, minute=59, second=59, microsecond=999999)
        )
        q = (
            select(Transaction)
            .filter(
                Transaction.user_id == user.id,
                Transaction.timestamp.between(start_date, end_date),
            )
            .order_by(Transaction.id)
        )
        return self.__session.scalars(q).all()

    def __init__(self, session):
        self.__session = session
