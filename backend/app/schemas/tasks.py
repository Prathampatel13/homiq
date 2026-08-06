from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class TaskStatusEnum(str, Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
    REVOKED = "REVOKED"


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None

    model_config = {"from_attributes": True}


class TaskRetryRequest(BaseModel):
    task_name: Optional[str] = None
    args: list[Any] = []
    kwargs: dict[str, Any] = {}


class TaskRetryResponse(BaseModel):
    task_id: str
    status: str
    message: str

    model_config = {"from_attributes": True}


class ScheduledJobItem(BaseModel):
    name: str
    task_name: str
    schedule: str
    last_run: Optional[str] = None
    next_run: Optional[str] = None

    model_config = {"from_attributes": True}


class SchedulerJobsResponse(BaseModel):
    total_jobs: int
    jobs: list[ScheduledJobItem] = []

    model_config = {"from_attributes": True}
