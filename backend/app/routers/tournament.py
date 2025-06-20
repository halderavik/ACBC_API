from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
import re
from urllib.parse import unquote
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import TournamentDesignOut, ChoiceResponseIn
from ..services import get_tournament, record_choice, get_session
from ..database import get_db

router = APIRouter()

@router.get("/choice", response_model=TournamentDesignOut)
async def tournament_choice(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Get tournament choice for a session and task number."""
    try:
        # Get the full URL and decode it
        full_url = str(request.url)
        decoded_url = unquote(full_url)
        
        # Extract session_id from URL
        session_id = None
        session_match = re.search(r'session_id=+([^&\s]+)', decoded_url)
        if session_match:
            session_id = session_match.group(1)
        
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id parameter is required")
        
        # Extract task_number from URL (default to 1)
        task_number = 1
        task_match = re.search(r'task_number=+([^&\s]+)', decoded_url)
        if task_match:
            try:
                task_number = int(task_match.group(1))
            except ValueError:
                raise HTTPException(status_code=400, detail="task_number must be an integer")
        
        if not await get_session(db, session_id):
            raise HTTPException(status_code=404, detail="Session not found")
        
        concepts = await get_tournament(db, session_id, task_number)
        return {"task_number": task_number, "concepts": concepts}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/choice/{path:path}")
async def tournament_choice_catch_all(
    path: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Catch-all route for malformed tournament choice URLs."""
    try:
        # Get the full URL and decode it
        full_url = str(request.url)
        decoded_url = unquote(full_url)
        
        # Extract session_id from URL
        session_id = None
        session_match = re.search(r'session_id=+([^&\s]+)', decoded_url)
        if session_match:
            session_id = session_match.group(1)
        
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id parameter is required")
        
        # Extract task_number from URL (default to 1)
        task_number = 1
        task_match = re.search(r'task_number=+([^&\s]+)', decoded_url)
        if task_match:
            try:
                task_number = int(task_match.group(1))
            except ValueError:
                raise HTTPException(status_code=400, detail="task_number must be an integer")
        
        if not await get_session(db, session_id):
            raise HTTPException(status_code=404, detail="Session not found")
        
        concepts = await get_tournament(db, session_id, task_number)
        return {"task_number": task_number, "concepts": concepts}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/choice-response")
async def choice_response(resp: ChoiceResponseIn, db: AsyncSession = Depends(get_db)):
    if not await get_session(db, resp.session_id):
        raise HTTPException(404, "Session not found")
    next_task = await record_choice(db, resp.session_id, resp.task_number, resp.selected_concept_id)
    return {"next_task": next_task}