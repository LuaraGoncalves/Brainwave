from sqlalchemy.orm import Session

from app.models.chat import Chat


def get_user_chat(db: Session, chat_id: int, user_id: int) -> Chat | None:
    return db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()
