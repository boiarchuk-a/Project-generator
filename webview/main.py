from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
# Импортируем все роуты
from app.routes.auth import auth_router
from app.routes.Home import home_router
from app.routes.ML import ml_router
from app.routes.Prediction import prediction_router
from app.routes.Transaction import transaction_router
from app.routes.User import user_router

def main():
    app = FastAPI(title="ML Title Generator")

    # Статика и шаблоны
    app.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="view")

    # Подключаем роуты
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(home_router, prefix="", tags=["home"])
    app.include_router(ml_router, prefix="/ml", tags=["ml"])
    app.include_router(prediction_router, prefix="/prediction", tags=["prediction"])
    app.include_router(transaction_router, prefix="/transaction", tags=["transaction"])
    app.include_router(user_router, prefix="/user", tags=["user"])

    return app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)
