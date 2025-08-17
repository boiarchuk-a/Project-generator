import pika
from datetime import datetime
import os
import logging

from sqlmodel.orm import Session
from app.database.database import engine
from app.Prediction import Prediction
from app.models.Transaction import Transaction
from app.TitleModel import FancyModel
from app.TitleService import TitleService

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
QUEUE_NAME   = os.getenv("QUEUE_NAME", "predictions")

connection_params = pika.URLParameters(RABBITMQ_URL)

connection = pika.BlockingConnection(connection_params)
channel = connection.channel()
queue_name = 'ml_task_queue'
channel.queue_declare(queue=queue_name)

_model = FancyModel()
_service = TitleService(_model)

# ---------- Валидация / Парсинг без JSON ----------
def parse_payload(payload: str) -> tuple[int, str]:
    """
    Формат: 'user_id|текст'
    user_id -> int, текст -> не пустой (>=3 символов)
    """
    if not payload:
        raise ValueError("Empty payload")

    if "|" not in payload:
        raise ValueError("Invalid format. Expected 'user_id|text'")

    user_part, text_part = payload.split("|", 1)
    user_part = user_part.strip()
    text_part = text_part.strip()

    if not user_part.isdigit():
        raise ValueError("Invalid user_id (must be integer)")

    if len(text_part) < 3:
        raise ValueError("Text is too short (min 3 chars)")

    return int(user_part), text_part

# ---------- Бизнес-логика обработки ----------
def process_task(user_id: int, text: str) -> str:
    """
    Выполняет предикт и пишет результат в БД.
    Возвращает сгенерированный заголовок.
    """
    pred_obj = _service.generate(text)
    generated_title = getattr(pred_obj, "generated_title", str(pred_obj))

    # запись в БД
    with Session(engine) as session:

        prediction = Prediction(
            input_text=text,
            generated_title=generated_title,
            timestamp=datetime.utcnow()
        )
        session.add(prediction)

        # Transaction
        tx = Transaction(
            user_id=user_id,
            amount= 10.0,
            result=f"PREDICT:{generated_title}",
        )
        session.add(tx)

        session.commit()

    return generated_title

# ---------- Callback очереди ----------
def callback(ch, method, properties, body: bytes):
    try:
        payload = body.decode("utf-8")
        logger.info(f"Получено сообщение: {payload}")

        user_id, text = parse_payload(payload)
        title = process_task(user_id, text)             # предикт + запись в БД
        logger.info(f"Готово: user_id={user_id}, title='{title}'")

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.exception(f"Ошибка при обработке: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=False
)

logger.info('Waiting for messages. To exit, press Ctrl+C')
channel.start_consuming()