from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProjectCategory(str, Enum):
    ML = "Machine Learning"
    DL = "Deep Learning"
    FLASK = "Flask"
    FASTAPI = "FastAPI"
    DJANGO = "Django"
    REACT = "React"
    NEXTJS = "Next.js"
    FULLSTACK = "Full Stack SaaS"
    BLOCKCHAIN = "Blockchain"
    CYBERSECURITY = "Cybersecurity"
    AUTOMATION = "Automation"
    AI_AGENT = "AI Agent"
    DATA_SCIENCE = "Data Science"
    IEEE = "IEEE Research-Based"


class ComplexityLevel(str, Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


# ── Create Request ─────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    title: str
    category: ProjectCategory
    technologies: List[str]
    features: List[str]
    complexity: ComplexityLevel = ComplexityLevel.INTERMEDIATE

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Project title cannot be empty")
        return v.strip()

    @field_validator("technologies", "features")
    @classmethod
    def list_not_empty(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("Must provide at least one item")
        return [item.strip() for item in v if item.strip()]


# ── Response ───────────────────────────────────────────────────────────────────

class GenerationLogResponse(BaseModel):
    id: str
    agent_name: str
    status: str
    output: Optional[str]
    duration_ms: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectResponse(BaseModel):
    id: str
    title: str
    category: Optional[str]
    technologies: Optional[List[str]]
    features: Optional[List[str]]
    complexity: str
    status: str
    architecture: Optional[str]
    folder_structure: Optional[Dict[str, Any]]
    files: Optional[Dict[str, str]]
    readme: Optional[str]
    env_example: Optional[str]
    zip_path: Optional[str]
    llm_provider: Optional[str]
    tokens_used: Optional[int]
    error_message: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectListItem(BaseModel):
    id: str
    title: str
    category: Optional[str]
    status: str
    complexity: str
    technologies: Optional[List[str]]
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectStatusResponse(BaseModel):
    project_id: str
    status: str
    logs: List[GenerationLogResponse] = []
    progress_percent: int = 0
