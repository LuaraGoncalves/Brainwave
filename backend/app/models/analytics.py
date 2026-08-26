from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text, func

from app.db.base import Base


class DataConnection(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    engine = Column(String, nullable=False, default="postgresql")
    host = Column(String, nullable=False, default="localhost")
    database = Column(String, nullable=False)
    status = Column(String, nullable=False, default="active")
    is_read_only = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class SavedAnalysis(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    title = Column(String, nullable=False)
    question = Column(Text, nullable=False)
    sql = Column(Text, nullable=False)
    chart = Column(JSON, nullable=True)
    insights = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class InsightAlert(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    metric = Column(String, nullable=False)
    operator = Column(String, nullable=False)
    threshold = Column(Integer, nullable=False)
    current_value = Column(Integer, nullable=False, default=0)
    severity = Column(String, nullable=False, default="info")
    status = Column(String, nullable=False, default="open")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Report(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    title = Column(String, nullable=False)
    period = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    payload = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
