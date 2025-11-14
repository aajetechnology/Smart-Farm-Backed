# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, predict, chat, weather, notify, social
from database import engine
from models import Base

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# INCLUDE ROUTERS — CORRECT WAY
app.include_router(auth.router, prefix="/api")
app.include_router(social.router, prefix="/api")  # assuming it has .router
app.include_router(weather.router, prefix="/api")
app.include_router(predict.router, prefix="/api", tags=["Plant Prediction"])  # ← FROM routers/predict.py
# app.include_router(chat.router, prefix="/api", tags=["Chatbot"])
app.include_router(notify.router)

@app.get("/")
def root():
    return {"message": "Backend is running locally!"}