from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Subject(BaseModel):
    name: str
    credits: int
    last_studied: Optional[str] = None
    confidence_level: Optional[int] = 5  # 1-10 scale
    revision_count: Optional[int] = 0

class Assignment(BaseModel):
    title: str
    subject: str
    deadline: str
    priority: str
    estimated_hours: Optional[float] = 1.0

class DailyContext(BaseModel):
    subjects: List[Subject]
    assignments: List[Assignment]
    sleep_hours: float
    energy_level: str  # low, medium, high
    available_hours: float
    age_group: str  # class3, class8, class12, college
    missed_days: Optional[int] = 0
    confusion_dump: Optional[str] = None
    study_mode: Optional[str] = "study"  # study, revision, exam_sprint, light

class NextAction(BaseModel):
    task: str
    duration: int  # minutes
    reason: str
    difficulty: str  # easy, medium, hard
    type: str  # study, revision, break, recovery

class PlanResponse(BaseModel):
    next_action: NextAction
    plan_message: str
    recovery_message: Optional[str] = None
    confidence_boost: Optional[str] = None
    revision_reminder: Optional[str] = None

class ConfusionDump(BaseModel):
    confusion: str
    age_group: str

class ConfusionResponse(BaseModel):
    calm_response: str
    action_items: List[str]
    plan_adjustment: str
