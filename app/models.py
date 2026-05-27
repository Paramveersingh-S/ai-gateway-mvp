from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.db import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    client_id = Column(String, index=True)
    prompt = Column(String)
    response = Column(String, nullable=True)
    decision = Column(String)
    reason = Column(String)
    agents_results = Column(String) 
    latency_ms = Column(Float)

class Policy(Base):
    __tablename__ = "policies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    content = Column(String)
    is_active = Column(Boolean, default=True)

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    stream: Optional[bool] = False
    temperature: Optional[float] = 1.0

class PolicyCreate(BaseModel):
    name: str
    content: str
    is_active: bool = True

class AgentResult(BaseModel):
    risk_score: float = Field(description="Risk score from 0.0 to 1.0. 0.0 is safe, 1.0 is highest risk.")
    explanation: str = Field(description="Explanation of findings")

class OrchestratorDecision(BaseModel):
    decision: str = Field(description="Must be exactly one of: 'allow', 'block', or 'flag'")
    reason: str = Field(description="User-friendly explanation for the decision")