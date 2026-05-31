from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from app.database.connection import Base


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(120), unique=True, index=True, nullable=False)
    token_type = Column(String(20), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, default=datetime.utcnow)