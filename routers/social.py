from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from routers.schemas import ContactResponse, AddContactRequest, MessageCreate, MessageResponse, UserOut
from crud import get_contacts, add_contact, create_message, get_messages_with_contact, search_users
from models import User
from routers.auth import get_current_user

router = APIRouter(prefix="/api/social", tags=["social"])

@router.get("/contacts", response_model=List[ContactResponse])
def get_user_contacts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    contacts = get_contacts(db, current_user.id)
    return contacts

@router.post("/contacts/add")
def add_user_contact(req: AddContactRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    friend = add_contact(db, current_user.id, req.username)
    if not friend:
        raise HTTPException(status_code=400, detail="User not found or already a contact")
    return {"message": "Contact added"}

@router.get("/messages/{contact_id}", response_model=List[MessageResponse])
def get_message_history(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    messages = get_messages_with_contact(db, current_user.id, contact_id)
    return messages

@router.get("/users/search", response_model=List[UserOut])
def search_users_endpoint(search: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    users = search_users(db, search, current_user.id)
    return users

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...), db: Session = Depends(get_db)):
    try:
        current_user = get_current_user(token=token, db=db)
    except:
        await websocket.close(code=1008)
        return
    await manager.connect(current_user.id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            contact_id = data.get("contact_id")
            content = data.get("content")
            if not contact_id or not content:
                continue
            message = create_message(db, current_user.id, contact_id, content)
            await manager.send_personal_message({
                "id": message.id,
                "sender_id": message.sender_id,
                "content": message.content,
                "timestamp": message.timestamp.isoformat()
            }, current_user.id)
            await manager.send_personal_message({
                "id": message.id,
                "sender_id": message.sender_id,
                "content": message.content,
                "timestamp": message.timestamp.isoformat()
            }, contact_id)
    except WebSocketDisconnect:
        manager.disconnect(current_user.id)