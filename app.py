from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from routers import auth, predict, chat, weather, notify
from database import engine
from models import Base

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(chat.router)
app.include_router(weather.router)
app.include_router(notify.router)

@app.get("/")
def root():
    return {"message": "Backend is running locally!"}