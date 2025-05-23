from pydantic import BaseModel, Field
from typing import List, Dict, Any
from enum import Enum

class LanguageEnum(str, Enum):
    JAVA = "java"
    CPP = "cpp"
    PYTHON = "python"
    C = "c"
    CSHARP = "c#"

class MethodEnum(str, Enum):
    NIL_FORK = "NIL-fork"
    CCALIGNER = "CCAligner"
    CCSTOKENER = "CCSTokener"
    CCALIGNER_FORK = "CCAligner-fork"
    CCSTOKENER_FORK = "CCSTokener-fork"
    NICAD = "NiCad"
    SOURCERERCC = "SourcererCC"

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    DELETED = "deleted"

class SearchResponse(BaseModel):
    task_id: str
    status_url: str
    results_url: str

class StatusResponse(BaseModel):
    status: str
    started_at: str
    processed_snippet: str

class ResultsResponse(BaseModel):
    results: List[Dict[str, Any]]
    metrics: Dict[str, Any]

class MethodsResponse(BaseModel):
    available_methods: List[Dict[str, Any]]
