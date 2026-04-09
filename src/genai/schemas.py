from typing import Optional, Dict, Any
from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    payload: Optional[Dict[str, Any]] = None


class AskResponse(BaseModel):
    answer: str