from sqlalchemy.orm import Session
from sqlmodel import SQLModel, create_engine, select

from database.config import get_settings
from models.User import User

def get_database_engine():
    settings = get_settings()

    engine = create_engine(
        url=settings.DATABASE_URL_psycopg,
        echo=settings.DEBUG,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    return engine


engine = get_database_engine()


def get_session():
    with Session(engine) as session:
        yield session


def init_db(drop_all: bool = False) -> None:
    """
    Инициализация схемы базы данных.

    Аргументы:
        drop_all: Если True, удаляет все таблицы перед созданием

    Исключения:
        Exception: Любые исключения, связанные с базой данных
    """
    try:
        engine = get_database_engine()
        if drop_all:
            # Удаление всех таблиц, если указано
            SQLModel.metadata.drop_all(engine)

        # Создание всех таблиц
        SQLModel.metadata.create_all(engine)

        # Создание начальных данных
        with Session(engine) as session:
            # Проверяем, существуют ли уже пользователи
            if session.exec(select(User)).first() is None:
                hash_password = User.hash_password

                # Создание стандартных пользователей
                admin = User(
                    email="admin@example.com",
                    password=hash_password.create_hash("admin123")
                )
                user1 = User(
                    email="user1@example.com",
                    password=hash_password.create_hash("user123")
                )
                user2 = User(
                    email="user2@example.com",
                    password=hash_password.create_hash("user123")
                )

                # Сохранение в базу данных
                session.add(admin)
                session.add(user1)
                session.add(user2)
                session.commit()

    except Exception as e:
        raise
