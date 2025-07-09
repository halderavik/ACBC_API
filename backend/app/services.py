import uuid
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from . import models, schemas, utils
from .database import get_db

async def create_session_record(byo: schemas.BYOConfig, db: AsyncSession) -> str:
    sid = byo.session_id or str(uuid.uuid4())
    session = models.Session(id=sid, byo_config=byo.selected_attributes)
    db.add(session)
    await db.commit()
    return sid

async def get_session(db: AsyncSession, sid: str):
    result = await db.execute(select(models.Session).where(models.Session.id == sid))
    return result.scalar_one_or_none()

async def get_session_with_screening_tasks(db: AsyncSession, sid: str):
    """Get session with screening tasks explicitly loaded."""
    result = await db.execute(
        select(models.Session)
        .options(selectinload(models.Session.screening_tasks))
        .where(models.Session.id == sid)
    )
    return result.scalar_one_or_none()

async def init_screening(db: AsyncSession, sid: str, byo: Dict[str, List[Any]]):
    tasks = utils.generate_screening_matrix(byo)
    for idx, concept in enumerate(tasks, start=1):
        db.add(models.ScreeningTask(session_id=sid, concept=concept, position=idx))
    await db.commit()
    return tasks

async def record_screening_responses(db: AsyncSession, sid: str, responses: List[bool]):
    result = await db.execute(select(models.ScreeningTask).where(models.ScreeningTask.session_id == sid))
    tasks = result.scalars().all()
    for task, resp in zip(tasks, responses):
        task.response = resp
    utils.estimate_initial_utilities(responses, [t.concept for t in tasks])
    await db.commit()

async def get_tournament(db: AsyncSession, sid: str, task_number: int, nso: int = 3):
    session = await get_session(db, sid)
    
    # Check if tournament task already exists for this session and task number
    existing_tasks = await db.execute(
        select(models.TournamentTask)
        .where(models.TournamentTask.session_id == sid)
        .where(models.TournamentTask.task_number == task_number)
    )
    existing_tasks = existing_tasks.scalars().all()
    
    if existing_tasks:
        # Return existing concepts if task already exists (use the first one if multiple)
        existing_task = existing_tasks[0]
        return existing_task.concepts
    
    # Generate new concepts if task doesn't exist
    concepts = utils.generate_tournament_set(session.utilities or {}, session.byo_config, task_number, nso)
    
    # Store the concepts array in the database
    db.add(models.TournamentTask(session_id=sid, task_number=task_number, concepts=concepts))
    await db.commit()
    
    return concepts

async def record_choice(db: AsyncSession, sid: str, task_number: int, choice_id: int):
    result = await db.execute(
        select(models.TournamentTask)
        .where(models.TournamentTask.session_id == sid)
        .where(models.TournamentTask.task_number == task_number)
    )
    tasks = result.scalars().all()
    if not tasks:
        raise ValueError(f"Tournament task not found for session {sid}, task {task_number}")
    if len(tasks) > 1:
        # Log a warning or handle cleanup as needed
        # For now, pick the first one
        # Optionally, you could delete duplicates here
        task = tasks[0]
    else:
        task = tasks[0]
    
    # Validate that choice_id is within the range of available concepts
    if choice_id < 0 or choice_id >= len(task.concepts):
        raise ValueError(f"Invalid choice_id {choice_id}. Must be between 0 and {len(task.concepts) - 1}")
    
    # Record the choice (choice_id is the index into the concepts array)
    task.choice = choice_id
    
    # Update utilities based on the chosen concept
    session = await get_session(db, sid)
    chosen_concept = task.concepts[choice_id]["attributes"]  # Extract attributes from concept with ID
    session.utilities = utils.adaptive_update(session.utilities or {}, chosen_concept)
    
    await db.commit()
    return task_number + 1