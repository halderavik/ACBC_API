from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, List, Any
import json
import re
from urllib.parse import unquote
from ..schemas import BYOConfig
from ..services import create_session_record, init_screening
from ..database import get_db

router = APIRouter()

@router.post("")
async def byo_config(config: BYOConfig, db: AsyncSession = Depends(get_db)):
    """Create a new BYO configuration and session."""
    try:
        # Validate selected_attributes
        if not config.selected_attributes:
            raise HTTPException(
                status_code=422, 
                detail="selected_attributes is required and cannot be empty"
            )
        
        # Validate that each attribute has at least one value
        for attr_name, attr_values in config.selected_attributes.items():
            if not attr_values or len(attr_values) == 0:
                raise HTTPException(
                    status_code=422,
                    detail=f"Attribute '{attr_name}' must have at least one value"
                )
        
        sid = await create_session_record(config, db)
        await init_screening(db, sid, config.selected_attributes)
        return {"session_id": sid, "message": "Session created successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("")
async def byo_config_get(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle GET request with query parameters, including malformed ones."""
    try:
        # Get the full URL and decode it
        full_url = str(request.url)
        decoded_url = unquote(full_url)
        
        # Extract session_id
        session_id = None
        session_match = re.search(r'session_id=([^&\s]+)', decoded_url)
        if session_match:
            session_id = session_match.group(1)
            if session_id == "null":
                session_id = None
        
        # Extract selected_attributes
        selected_attributes = None
        attr_match = re.search(r'selected_attributes=([^&\s]+)', decoded_url)
        if attr_match:
            selected_attributes = attr_match.group(1)
        
        if not selected_attributes:
            raise HTTPException(status_code=400, detail="selected_attributes parameter is required")
        
        # Parse the selected_attributes JSON string robustly
        try:
            attributes_dict = json.loads(selected_attributes)
        except json.JSONDecodeError:
            from urllib.parse import unquote_plus
            try:
                decoded_attributes = unquote_plus(selected_attributes)
                attributes_dict = json.loads(decoded_attributes)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in selected_attributes")
        
        # Create BYOConfig object
        config = BYOConfig(
            session_id=session_id,
            selected_attributes=attributes_dict
        )
        
        sid = await create_session_record(config, db)
        await init_screening(db, sid, config.selected_attributes)
        return {"session_id": sid}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{path:path}")
async def byo_config_catch_all(
    path: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Catch-all route for malformed URLs with spaces."""
    try:
        # Get the full URL and decode it
        full_url = str(request.url)
        decoded_url = unquote(full_url)
        
        # Extract session_id
        session_id = None
        session_match = re.search(r'session_id=([^&\s]+)', decoded_url)
        if session_match:
            session_id = session_match.group(1)
            if session_id == "null":
                session_id = None
        
        # Extract selected_attributes
        selected_attributes = None
        attr_match = re.search(r'selected_attributes=([^&\s]+)', decoded_url)
        if attr_match:
            selected_attributes = attr_match.group(1)
        
        if not selected_attributes:
            raise HTTPException(status_code=400, detail="selected_attributes parameter is required")
        
        # Parse the selected_attributes JSON string robustly
        try:
            attributes_dict = json.loads(selected_attributes)
        except json.JSONDecodeError:
            from urllib.parse import unquote_plus
            try:
                decoded_attributes = unquote_plus(selected_attributes)
                attributes_dict = json.loads(decoded_attributes)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in selected_attributes")
        
        # Create BYOConfig object
        config = BYOConfig(
            session_id=session_id,
            selected_attributes=attributes_dict
        )
        
        sid = await create_session_record(config, db)
        await init_screening(db, sid, config.selected_attributes)
        return {"session_id": sid}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))