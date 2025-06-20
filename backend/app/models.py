from sqlalchemy import Column, String, Integer, JSON, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Session(Base):
    __tablename__ = 'sessions'
    id = Column(String, primary_key=True, index=True)
    byo_config = Column(JSON, nullable=False)
    utilities = Column(JSON, nullable=True)
    screening_tasks = relationship('ScreeningTask', back_populates='session')
    tournament_tasks = relationship('TournamentTask', back_populates='session')

class ScreeningTask(Base):
    __tablename__ = 'screening_tasks'
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey('sessions.id'))
    concept = Column(JSON, nullable=False)
    position = Column(Integer, nullable=False)
    response = Column(Boolean, nullable=True)
    session = relationship('Session', back_populates='screening_tasks')

class TournamentTask(Base):
    __tablename__ = 'tournament_tasks'
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey('sessions.id'))
    task_number = Column(Integer, nullable=False)
    concepts = Column(JSON, nullable=False)
    choice = Column(Integer, nullable=True)
    session = relationship('Session', back_populates='tournament_tasks')