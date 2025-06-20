from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class BYOConfig(BaseModel):
    session_id: Optional[str]
    selected_attributes: Dict[str, List[Any]]

class ScreeningDesignOut(BaseModel):
    id: int
    concept: Dict[str, Any]
    position: int
    response: Optional[bool] = None

    class Config:
        from_attributes = True

class ScreeningResponseIn(BaseModel):
    session_id: str
    responses: List[bool]

class TournamentDesignOut(BaseModel):
    task_number: int
    concepts: List[Dict[str, Any]]

class ChoiceResponseIn(BaseModel):
    session_id: str
    task_number: int
    selected_concept_id: int