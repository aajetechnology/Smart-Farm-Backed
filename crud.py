# crud.py
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import User, Friendship, Message



def get_contacts(db: Session, user_id: int):
    contacts = (
        db.query(User)
        .join(Friendship, User.id == Friendship.friend_id)  # ← friend_id NOT contact_id
        .filter(Friendship.user_id == user_id)
        .all()
    )
    return contacts

def add_contact(db: Session, user_id: int, target_username: str):
    clean_username = target_username.strip()
    if not clean_username:
        return None

    # ← CASE-INSENSITIVE SEARCH
    target_user = db.query(User).filter(
        User.username.ilike(clean_username)
    ).first()

    if not target_user or target_user.id == user_id:
        return None

    # Prevent duplicates
    existing = db.query(Friendship).filter(
        ((Friendship.user_id == user_id) & (Friendship.friend_id == target_user.id)) |
        ((Friendship.user_id == target_user.id) & (Friendship.friend_id == user_id))
    ).first()
    if existing:
        return None

    # Add friendship
    friendship1 = Friendship(user_id=user_id, friend_id=target_user.id)
    friendship2 = Friendship(user_id=target_user.id, friend_id=user_id)
    db.add(friendship1)
    db.add(friendship2)
    db.commit()
    return target_user

def create_message(db: Session, sender_id: int, receiver_id: int, content: str):
    message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_messages_with_contact(db: Session, user_id: int, contact_id: int):
    return db.query(Message).filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == contact_id)) |
        ((Message.sender_id == contact_id) & (Message.receiver_id == user_id))
    ).order_by(Message.timestamp.asc()).all()


def search_users(db: Session, query: str, current_user_id: int):
    q = query.strip()
    if not q:
        return []

    return db.query(User).filter(
        User.id != current_user_id,
        or_(
            User.username.ilike(f"%{q}%"),
            User.full_name.ilike(f"%{q}%")
        )
    ).limit(20).all()