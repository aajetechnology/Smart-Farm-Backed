# import os
# import logging
# import requests
# from fastapi import APIRouter, HTTPException, status, Depends
# from pydantic import BaseModel
# from dotenv import load_dotenv
# from routers.auth import get_current_user  # ✅ For authentication

# load_dotenv()
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# router = APIRouter()

# HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
# print("Token loaded:", HF_TOKEN)
# if not HF_TOKEN:
#     raise ValueError("HUGGINGFACEHUB_API_TOKEN not found in environment variables")

# # ✅ Switched to Mistral-7B-Instruct (free, chat-friendly)
# API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"


# class ChatRequest(BaseModel):
#     message: str

# class ChatResponse(BaseModel):
#     reply: str

# @router.post("/chat", response_model=ChatResponse)
# def chat(req: ChatRequest, current_user: dict = Depends(get_current_user)):
#     """Chat endpoint using Mistral 7B Instruct model."""
#     logger.info(f"User: {req.message}")

#     headers = {"Authorization": f"Bearer {HF_TOKEN}"}
#     # ✅ Instruction-style format for conversational context
#     payload = {
#         "inputs": f"User: {req.message}\nAssistant (Farmi):",
#         "parameters": {
#             "max_new_tokens": 350,
#             "temperature": 0.7,
#             "top_p": 0.9,
#             "repetition_penalty": 1.2,
#             "return_full_text": False
#         }
#     }

#     try:
#         response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
#         logger.info(f"HuggingFace status: {response.status_code}")

#         if response.status_code == 401:
#             raise HTTPException(status_code=401, detail="Invalid HuggingFace token.")
#         if response.status_code == 403:
#             raise HTTPException(status_code=403, detail="Model access forbidden.")
#         response.raise_for_status()

#         data = response.json()
#         logger.debug(f"Response JSON: {data}")

#         reply = None
#         if isinstance(data, list) and len(data) > 0:
#             reply = data[0].get("generated_text", None)

#         if not reply:
#             reply = "Sorry, I couldn’t generate a response."

#         reply = reply.replace("Assistant:", "").replace("Farmi:", "").strip()
#         return ChatResponse(reply=reply)

#     except requests.exceptions.Timeout:
#         raise HTTPException(status_code=504, detail="HuggingFace API timeout.")
#     except requests.exceptions.RequestException as e:
#         raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
