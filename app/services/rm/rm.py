import os
import pika

# как в твоём файле: одно URL-подключение и имя очереди из env
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
QUEUE_NAME   = os.getenv("QUEUE_NAME", "predictions")

# глобальные параметры подключения (одна строка, без разнесённых хост/порт)
connection_params = pika.URLParameters(RABBITMQ_URL)

def send_task(message: str) -> None:
    """
    Отправка задачи в очередь RabbitMQ.
    Принимает строку; при желании можно передавать JSON-строки.
    """
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    # гарантируем, что очередь существует и устойчива
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # публикуем как persistent-сообщение
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=message.encode("utf-8"),
        properties=pika.BasicProperties(delivery_mode=2),
    )

    connection.close()
