from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class EntityType(str, Enum):
    TABLE = "table"
    DATASET = "dataset"
    DATABASE = "database"
    COLUMN = "column"
    VIEW = "view"
    PIPELINE = "pipeline"
    NOTEBOOK = "notebook"

class Entity(BaseModel):
    id: str
    name: str
    type: EntityType
    qualified_name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)
    classifications: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        use_enum_values = True

class EntitySearchRequest(BaseModel):
    query: Optional[str] = None
    entity_type: Optional[str] = None
    classification: Optional[str] = None
    page: int = 1
    page_size: int = 25
    sort_by: Optional[str] = "name"
    sort_order: Optional[str] = "asc"

class EntityResponse(BaseModel):
    id: str
    name: str
    type: str
    qualified_name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)
    classifications: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    lineage_count: Optional[int] = 0
    classification_count: Optional[int] = 0
