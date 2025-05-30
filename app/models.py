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

METHODS_METADATA: Dict[str, Dict[str, Any]] = {
    MethodEnum.NIL_FORK.value: {
        "description": "Large-variance clone detection",
        "params": {
            "min_line": {
                "type": "int",
                "default": 6,
                "min": 1,
                "max": 1000,
                "description": "Minimum line"
            },
            "min_token": {
                "type": "int",
                "default": 50,
                "min": 1,
                "max": 1000,
                "description": "Minimum token"
            },
            "n_gram": {
                "type": "int",
                "default": 5,
                "min": 1,
                "max": 1000,
                "description": "N of N-gram"
            },
            "filtration_threshold": {
                "type": "int",
                "default": 10,
                "min": 0,
                "max": 100,
                "description": "Filtration threshold"
            },
            "verification_threshold": {
                "type": "int",
                "default": 70,
                "min": 0,
                "max": 100,
                "description": "Verification threshold"
            },
        },
    },
    MethodEnum.CCALIGNER.value: {
        "description": "Token-based clone detection",
        "params": {
            "window_size": {
                "type": "int",
                "default": 6,
                "min": 1,
                "max": 1000
            },
            "edit_distance": {
                "type": "int",
                "default": 1,
                "min": 0,
                "max": 1000
            },
            "similarity_threshold": {
                "type": "float",
                "default": 0.6,
                "min": 0,
                "max": 1
            }
        },
    },
    MethodEnum.CCALIGNER_FORK.value: {
        "description": "Custom adaptation of CCAligner",
    },
    MethodEnum.CCSTOKENER.value: {
        "description": "Semantic token-based clone detection",
        "params": {
            "similarity_threshold": {
                "type": "float",
                "default": 0.6,
                "min": 0,
                "max": 1
            }
        },
    },
    MethodEnum.CCSTOKENER_FORK.value: {
        "description": "Custom adaptation of CCStokener",
        "params": {
            "beta": {
                "type": "float",
                "default": 0.6,
                "min": 0,
                "max": 1,
                "description": "Filtration threshold"
            },
            "theta": {
                "type": "float",
                "default": 0.4,
                "min": 0,
                "max": 1,
                "description": "Block size difference threshold"
            },
            "eta": {
                "type": "float",
                "default": 0.55,
                "min": 0,
                "max": 1,
                "description": "Verification threshold"
            }
        },
    },
    MethodEnum.NICAD.value: {
        "description": "Text-based clone detector",
        "params": {
            "min_size": {
                "type": "int",
                "default": 10,
                "min": 1,
                "max": 10000,
                "description": "Min size of clones we are interested in"
            },
            "max_size": {
                "type": "int",
                "default": 10000,
                "min": 1,
                "max": 10000,
                "description": "Max size of clones we are interested in"
            },
            "threshold": {
                "type": "float",
                "default": 0.3,
                "min": 0,
                "max": 1,
                "description": "Maximum near-miss difference threshold we are interested in"
            },
        },
    },
    MethodEnum.SOURCERERCC.value: {
        "description": "Token-based clone detector",
    },
}

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
