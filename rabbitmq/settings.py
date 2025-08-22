import pika
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import cached_property
from typing import Optional


class RabbitMQSettings(BaseSettings):

    RABBITMQ_HOST: Optional[str] = None
    RABBITMQ_PORT: Optional[int] = None
    RABBITMQ_USER: Optional[str] = None
    RABBITMQ_PASS: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file="rabbitmq/.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @cached_property
    def connection_parameters(self):

        if not all(
            [
                self.RABBITMQ_HOST,
                self.RABBITMQ_PORT,
                self.RABBITMQ_USER,
                self.RABBITMQ_PASS,
            ]
        ):
            raise RuntimeError("Не заданы параметры подключения к RabbitMQ")

        return pika.ConnectionParameters(
            host=self.RABBITMQ_HOST,
            port=self.RABBITMQ_PORT,
            credentials=pika.PlainCredentials(
                username=self.RABBITMQ_USER, password=self.RABBITMQ_PASS
            ),
        )
