from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

# Auth schemas
class UserIn(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    profile_pic: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    profile_pic: Optional[str]

    @property
    def profile_pic_url(self):
        if self.profile_pic:
            # CHANGE THIS TO YOUR PC IP
            return f"http://192.168.0.102:8000/{self.profile_pic}"
        return None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Social feature schemas
class ContactResponse(BaseModel):
    id: int
    full_name: Optional[str]
    username: str
    profile_pic: Optional[str]

    class Config:
        from_attributes = True

class AddContactRequest(BaseModel):
    username: str

class MessageCreate(BaseModel):
    sender_id: int
    receiver_id: int
    content: str

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut