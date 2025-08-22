from dataclasses import asdict
from datetime import datetime, date, time
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.Mllog import Mllog
from app.models.User import User
from app.models.Transaction import Transaction
from app.ML import ML
from app.MLstatus import MLstatus
from app.Prediction import Prediction


class MLhistory:
    """Класс, обеспечивающий работу с журналом запросов генерации заголовков"""

    async def add_new(
            self,
            user: User,
            query: ML,
    ) -> Mllog:
        """Добавляет запись о новом запросе на генерацию заголовка в журнал"""
        query_log_item = Mllog(
            user_id=user.id,
            timestamp=datetime.now(),
            query_text=query.text,
            status=MLstatus.WAITING,
            query_type="title_generation",  # Тип запроса для фильтрации
            price=float(query.price)  # Сохраняем стоимость запроса
        )
        self.__session.add(query_log_item)
        await self.__session.commit()
        await self.__session.refresh(query_log_item)
        return query_log_item

    async def update(
            self,
            query_log_id: int,
            status: MLstatus,
            prediction: Optional[Prediction] = None,
            transaction: Optional[Transaction] = None,
            generated_title: Optional[str] = None,
            confidence: Optional[float] = None,
            model_version: Optional[str] = None
    ) -> None:
        """Обновляет запись в журнале полученными данными"""
        query_log_item = await self.get_by_id(query_log_id)

        if status == MLstatus.RUNNING:
            query_log_item.status = status
            query_log_item.started_at = datetime.now()

        elif status == MLstatus.COMPLETED:
            query_log_item.status = status
            query_log_item.completed_at = datetime.now()

            if not transaction:
                raise RuntimeError(
                    "Запрос имеет статус исполненного, но не задана транзакция оплаты"
                )

            # Сохраняем результаты генерации заголовка
            if generated_title:
                query_log_item.generated_title = generated_title
            if confidence is not None:
                query_log_item.confidence_score = confidence
            if model_version:
                query_log_item.model_version = model_version

            query_log_item.transaction_id = transaction.id

        elif status == MLstatus.CANCELED:
            query_log_item.status = status
            query_log_item.completed_at = datetime.now()
            query_log_item.error_message = "Ошибка генерации заголовка"

        await self.__session.commit()

    async def cancel(self, query_log_id: int) -> None:
        """Отменяет запрос на генерацию заголовка"""
        query_log_item = await self.get_by_id(query_log_id)
        query_log_item.status = MLstatus.CANCELED
        query_log_item.completed_at = datetime.now()
        await self.__session.commit()

    async def get_for_user(
            self,
            user: User,
            start_date: Optional[date] = None,
            end_date: Optional[date] = None,
            query_type: str = "title_generation"
    ) -> List[Mllog]:
        """Возвращает историю запросов пользователя на генерацию заголовков между заданными датами"""
        if start_date is None:
            start_date = date(2025, 1, 1)
        if end_date is None:
            end_date = datetime.now()

        end_datetime = datetime.combine(
            end_date, time(hour=23, minute=59, second=59, microsecond=999999)
        )

        q = (
            select(Mllog)
            .filter(
                Mllog.user_id == user.id,
                Mllog.query_type == query_type,
                Mllog.timestamp.between(start_date, end_datetime),
            )
            .order_by(Mllog.timestamp.desc())  # Сначала новые
        )

        result = await self.__session.execute(q)
        return result.scalars().all()

    async def get_by_id(self, query_log_id: int) -> Mllog:
        """Возвращает запись из журнала запросов по ее id"""
        q = select(Mllog).filter_by(id=query_log_id)
        result = await self.__session.execute(q)
        query_log_item = result.scalar_one_or_none()

        if not query_log_item:
            raise ValueError(f"В журнале запросов нет записи с id={query_log_id}")
        return query_log_item

    async def get_user_stats(
            self,
            user: User,
            days: int = 30
    ) -> Dict[str, Any]:
        """Возвращает статистику пользователя по генерации заголовков"""
        from_date = datetime.now() - timedelta(days=days)

        q = (
            select(Mllog)
            .filter(
                Mllog.user_id == user.id,
                Mllog.query_type == "title_generation",
                Mllog.timestamp >= from_date,
            )
        )

        result = await self.__session.execute(q)
        queries = result.scalars().all()

        completed = [q for q in queries if q.status == MLstatus.COMPLETED]
        failed = [q for q in queries if q.status == MLstatus.CANCELED   ]
        total_cost = sum(q.price for q in completed if q.price is not None)

        return {
            "total_queries": len(queries),
            "completed": len(completed),
            "failed": len(failed),
            "success_rate": len(completed) / len(queries) * 100 if queries else 0,
            "total_cost": total_cost,
            "avg_confidence": sum(q.confidence_score for q in completed if q.confidence_score) / len(
                completed) if completed else 0
        }

    def __init__(self, session: AsyncSession):
        self.__session = session