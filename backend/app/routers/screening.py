from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import re
from urllib.parse import unquote
from ..schemas import ScreeningDesignOut, ScreeningResponseIn
from ..services import get_session, get_session_with_screening_tasks, init_screening, record_screening_responses
from ..database import get_db
from .. import models

router = APIRouter()

@router.get("/design", response_model=List[ScreeningDesignOut])
async def screening_design(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Get screening design for a session."""
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
        
        sess = await get_session_with_screening_tasks(db, session_id)
        if not sess:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return sess.screening_tasks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/design/{path:path}")
async def screening_design_catch_all(
    path: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Catch-all route for malformed screening design URLs."""
    try:
        # Get the full URL and decode it
        full_url = str(request.url)
        decoded_url = unquote(full_url)
        
        # Extract session_id
        session_id = None
        session_match = re.search(r'session_id=+([^&\s]+)', decoded_url)
        if session_match:
            session_id = session_match.group(1)
        
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id parameter is required")
        
        sess = await get_session_with_screening_tasks(db, session_id)
        if not sess:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return sess.screening_tasks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/responses")
async def screening_responses(resp: ScreeningResponseIn, db: AsyncSession = Depends(get_db)):
    """Submit screening responses for a session."""
    try:
        # Check if session exists
        session = await get_session(db, resp.session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session '{resp.session_id}' not found. Please create a session first using the BYO config endpoint.")
        
        # Get screening tasks to validate response count
        result = await db.execute(select(models.ScreeningTask).where(models.ScreeningTask.session_id == resp.session_id))
        tasks = result.scalars().all()
        
        if len(resp.responses) != len(tasks):
            raise HTTPException(
                status_code=422, 
                detail=f"Expected {len(tasks)} responses but got {len(resp.responses)}. Please check the screening design first."
            )
        
        # Validate that all responses are boolean
        for i, response in enumerate(resp.responses):
            if not isinstance(response, bool):
                raise HTTPException(
                    status_code=422,
                    detail=f"Response at position {i} must be a boolean (true/false), got {type(response).__name__}"
                )
        
        await record_screening_responses(db, resp.session_id, resp.responses)
        return {"status": "ok", "message": f"Successfully recorded {len(resp.responses)} screening responses"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")