from pydantic import BaseModel, Field
from typing import List, Dict, Any

class MethodConfig(BaseModel):
    name: str
    params: Dict[str, Any] #TODO: enable not making this musthave

class CombinationConfig(BaseModel):
    # strategy: str
    weights: Dict[str, float]

class SearchRequest(BaseModel):
    mode: str = Field(..., description="Search mode: 'github' or 'local'")
    repository: str = Field(None, description="GitHub repository URL (required for github mode)")
    branch: str = Field("master", description="Repository branch, defaults to 'master'")
    snippet: str = Field(..., description="Code snippet for search")
    methods: List[MethodConfig]
    # combination: CombinationConfig # TODO: add after creating normal aggregation result

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
