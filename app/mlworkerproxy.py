import json
import pika
from typing import Optional

from app.models.User import User
from rabbitmq.settings import RabbitMQSettings
from app.Balance import Balance, BalanceError
from app.ML import ML
from app.MLstatus import MLstatus
from app.MLhistory import MLhistory
from app.Prediction import Prediction


class MLWorkerProxy:
    """Класс, обеспечивающий отправку взаимодействие с воркером, а также выполняющий
    сопутствующие действия: списание и проверку баланса, внесение данных в журнал
    запросов"""

    def publish_to_mq(self, body):
        QUEUE_NAME = "queries_queue"
        connection = pika.BlockingConnection(
            self.__rabbitmq_settings.connection_parameters
        )
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=body,
            properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
        )
        connection.close()

    def send(self, user: User, query: ML) -> None:
        """Отправляет запрос на исполнение воркеру. Предварительно проверяет есть ли
        у пользователя достаточно денег на счету (если нет - выбрасывается исключение
        BalanceError) и вносит запись в журнал запросов со статусом WAITING"""
        if self.__balance[user] < query.price:
            raise BalanceError("Недостаточно денег на балансе для выполнения запроса!")
        query_log_item = self.__query_log_handler.add_new(user, query)
        body = json.dumps({"query_log_id": query_log_item.id, "query_text": query.text})
        self.publish_to_mq(body)

    def recieve(
        self, query_log_id: int, status: MLstatus, result: Optional[Prediction] = None
    ) -> None:
        """Обрабатывает данные, полученные от воркера"""
        if status == MLstatus.RUNNING:
            self.__query_log_handler.update(query_log_id, status)
        elif status == MLstatus.COMPLETED:
            query_log_item = self.__query_log_handler.get_by_id(query_log_id)
            user = query_log_item.user
            query = ML(query_log_item.query_text)
            # Здесь снова проверяем баланс, так как после отправки запроса пользователем
            # и до получения результата от воркера пользователем могли быть сделаны другие
            # запросы и баланс стал меньше необходимого. В этом случае будем считать
            # запрос отмененным (у него будет установлен статус CANCELED)
            if self.__balance[user] < query.price:
                self.__query_log_handler.cancel(query_log_id)
                return
            transaction = self.__balance.pay(user, query.price)
            self.__query_log_handler.update(query_log_id, status, result, transaction)

    def __init__(
        self,
        session,
    ):
        self.__balance = Balance(session)
        self.__query_log_handler = MLhistory(session)
        self.__rabbitmq_settings = RabbitMQSettings()
