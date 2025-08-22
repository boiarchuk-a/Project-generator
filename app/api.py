from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import uvicorn

from app.database.database import init_db
from app.models.base import Base
from app.routes.Balance import balance_router
from app.routes.ML import ml_router
from app.routes.User import user_router


app = FastAPI()

app.include_router(balance_router, prefix="/balance")
app.include_router(user_router, prefix="/user")
app.include_router(ml_router, prefix="/query")

app.mount("/view", StaticFiles(directory="app/view"), name="view")


@app.get("/")
def root():
    return RedirectResponse(url="/view/base.html")


if __name__ == "__main__":
    init_db(Base, drop_all=True)
    #init_db(Base, drop_all=True)
    uvicorn.run("api:app", host="0.0.0.0", port=8080, reload=True)
