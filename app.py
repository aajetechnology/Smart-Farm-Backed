# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, predict, chat, weather, notify, social, users
from database import engine
from models import Base

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",      # react native metro
        "http://10.0.2.2:8081",       # android emulator
        "http://127.0.0.1:8081",
        "http://127.0.0.1:8000",
        "https://smart-farm-backed.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# INCLUDE ROUTERS — CORRECT WAY
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")  # ← BEFORE predict
app.include_router(social.router)
app.include_router(weather.router, prefix="/api")
app.include_router(predict.router, prefix="/api", tags=["Plant Prediction"])
app.include_router(notify.router)

@app.get("/")
def root():
    return {"message": "Backend is running locally!"}













# ─────────────────────── RENDER FIX — ADD THIS AT THE END OF app.py ───────────────────────
import os
import uvicorn

if __name__ == "__main__":
    # Render gives you a random PORT (like 10000), we MUST use it
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "app:app",           # ← app.py + app variable
        host="0.0.0.0",      # ← CRITICAL: listen on all interfaces
        port=port,           # ← Use Render's port
        reload=True if os.environ.get("ENV") != "production" else False
    )
# ─────────────────────────────────────────────────────────────────────────────────────────────