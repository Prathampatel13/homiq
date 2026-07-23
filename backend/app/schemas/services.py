from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ServiceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    base_price: float = Field(..., ge=0)
    duration_minutes: Optional[int] = Field(
        0,
        ge=0,
        description="Estimated service duration in minutes.",
    )
    category_id: Optional[int] = Field(
        None, description="Category identifier for the service."
    )
    is_active: Optional[bool] = Field(
        True, description="Whether the service is active and visible to customers."
    )


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    base_price: Optional[float] = Field(None, ge=0)
    duration_minutes: Optional[int] = Field(
        None,
        ge=0,
        description="Estimated service duration in minutes.",
    )
    category_id: Optional[int] = Field(
        None, description="Category identifier for the service."
    )
    is_active: Optional[bool] = Field(
        None, description="Whether the service is active and visible to customers."
    )


class ServiceResponse(ServiceBase):
    id: int
    image_url: Optional[str] = None
    category: Optional[CategoryResponse] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ServiceImageResponse(BaseModel):
    image_url: str
    message: str = "Service image uploaded successfully"


class ServiceListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: list[ServiceResponse]
