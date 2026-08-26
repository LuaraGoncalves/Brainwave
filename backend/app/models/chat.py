from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Chat(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, default="Nova analise")
    user_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    owner = relationship("Usuario", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
