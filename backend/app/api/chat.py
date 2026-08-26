from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.chat import Chat
from app.models.message import Message
from app.models.usuario import Usuario
from app.schemas.chat import ChatSummary, QueryRequest, QueryResponse
from app.schemas.message import MessageRead
from app.services.chatbot_service import analyze_question

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/history", response_model=list[ChatSummary])
def list_chats(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return (
        db.query(Chat)
        .filter(Chat.user_id == current_user.id)
        .order_by(Chat.created_at.desc())
        .all()
    )


@router.get("/{chat_id}/messages", response_model=list[MessageRead])
def list_messages(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat nao encontrado")
    return db.query(Message).filter(Message.chat_id == chat.id).order_by(Message.created_at.asc()).all()


@router.post("/ask", response_model=QueryResponse)
def ask(
    payload: QueryRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    chat = None
    if payload.chat_id:
        chat = db.query(Chat).filter(Chat.id == payload.chat_id, Chat.user_id == current_user.id).first()
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat nao encontrado")
    if chat is None:
        title = payload.question[:60] or "Nova analise"
        chat = Chat(title=title, user_id=current_user.id)
        db.add(chat)
        db.commit()
        db.refresh(chat)

    analysis = analyze_question(db, payload.question)
    db.add(Message(chat_id=chat.id, role="user", content=payload.question))
    db.add(
        Message(
            chat_id=chat.id,
            role="assistant",
            content=analysis["answer"],
            sql=analysis["sql"],
            result=analysis["rows"],
            chart=analysis["chart"],
        )
    )
    db.commit()

    return {"chat_id": chat.id, **analysis}
