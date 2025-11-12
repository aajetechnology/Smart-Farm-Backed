from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base
from pydantic import BaseModel


class User(Base):
    __tablename__="users"
    id = Column(Integer, primary_key=True, index=True)
    email= Column(String, unique=True, index=True)
    hashed_password = Column(String)

class UserIn(BaseModel):
    email: str
    password: str   

class Token ( BaseModel):
    access_token: str
    token_type: str