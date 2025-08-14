from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Импортируем все роуты
from routes import auth, Home, ML, Prediction, Transaction, User


def main():
    app = FastAPI(title="ML Title Generator")

    # Статика и шаблоны
    app.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="view")

    # Подключаем роуты
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(Home.router, prefix="", tags=["home"])
    app.include_router(ML.router, prefix="/ml", tags=["ml"])
    app.include_router(Prediction.router, prefix="/prediction", tags=["prediction"])
    app.include_router(Transaction.router, prefix="/transaction", tags=["transaction"])
    app.include_router(User.router, prefix="/user", tags=["user"])

    return app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:main", host="0.0.0.0", port=80, reload=True)
