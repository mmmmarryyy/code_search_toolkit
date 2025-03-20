import os
import json
import queue
from fastapi import APIRouter, HTTPException, Request, Depends
from app.models import SearchRequest, SearchResponse, StatusResponse, ResultsResponse, MethodsResponse
from app.utils import clone_repository, generate_task_id
from app.detection import (
    run_nil_fork,
    run_ccaligner,
    run_ccstokener,
    aggregate_results
)

router = APIRouter()

def get_app_state(request: Request):
    return request.app.state

@router.post("/search", response_model=SearchResponse, status_code=201)
async def create_search_task(
    search_req: SearchRequest,
    state=Depends(get_app_state)
):
    if search_req.mode != "github": # TODO: support also local mode 
        raise HTTPException(status_code=400, detail="Only 'github' mode is supported.")

    # TODO: also add validation of language cause not all methods can processed python for example
    
    task_id = generate_task_id()
    
    # Create a folder for data: datasets/dataset_{taskID}
    dataset_folder = os.path.join("datasets", f"dataset_{task_id}")
    os.makedirs(dataset_folder, exist_ok=True)
    
    # Clone the repository into the dataset folder
    try:
        clone_repository(search_req.repository, branch=search_req.branch, dest=dataset_folder)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cloning repository: {e}")
    
    # Save the code fragment to the snippet.txt file (for original methods)
    snippet_file = os.path.join(dataset_folder, "snippet.txt") # TODO: here should save to snippet.{language extension} file
    with open(snippet_file, "w", encoding="utf-8") as f:
        f.write(search_req.snippet) # TODO: move file processing from NIL-fork to this code add add preprocessing here
    
    state.tasks[task_id] = { # TODO: create Task data class/struct
        "status": "pending", # TODO: add enum for task status
        "result": None,
        "search_req": search_req.dict(),
        "dataset_path": dataset_folder
    }


    state.task_queue.put(task_id)
    
    return SearchResponse(
        task_id=task_id,
        status_url=f"/api/search/{task_id}/status",
        results_url=f"/api/search/{task_id}/results"
    )

def process_search_task(task_id: str, tasks: dict):
    tasks[task_id]["status"] = "processing"
    # TODO: add here tasks[task_id]["started_at"] = timestamp
    search_req = tasks[task_id]["search_req"]
    dataset_folder = tasks[task_id]["dataset_path"]
    
    # Create a folder for results: results/results_{taskID}
    results_folder = os.path.join("results", f"results_{task_id}")
    os.makedirs(results_folder, exist_ok=True)
    
    results = []

    # TODO: fix processing and remove return
    return

    # Processing each method
    # TODO: should process in parallel
    for method in search_req["methods"]: # TODO: make search req also a structure or something like that
        name = method["name"]
        params = method.get("params", {})
        if name.upper() == "NIL": # TODO: create enum with names of available methods and also make it flexible like NIL/nil/...
            output = run_nil_fork(dataset_folder, params, search_req["snippet"], results_folder) # TODO: we should use not search_req["snippet"] but path to snippet_file from function above
        elif name.upper() == "CCALIGNER":
            output = run_ccaligner(dataset_folder, params, results_folder)
        elif name.upper() == "CCSTOKENER": 
            output = run_ccstokener(dataset_folder, params, results_folder)
        else:
            continue

        try:
            method_result = json.loads(output) # TODO: output is not in json format
        except Exception:
            method_result = {"raw_output": output}
        results.append({
            "method": name,
            "result": method_result
        })
    
    aggregated_results = aggregate_results(results, search_req["combination"])
    metrics = {
        "total_files_processed": 42,  # TODO: should calculate number of files in github repo plus 1 for snippet
        "execution_time": 10.5        # TODO: return difference between tasks[task_id]["started_at"] to this moment
    }
    tasks[task_id]["result"] = {"results": aggregated_results, "metrics": metrics}
    tasks[task_id]["status"] = "completed"

@router.get("/search/{task_id}/status", response_model=StatusResponse)
async def get_task_status(
    task_id: str,
    state=Depends(get_app_state)
):
    task = state.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return {
        "status": task["status"],
        "started_at": "",  # TODO: return task["started_at"] if it is setted or otherwise not_started
        "processed_snippet": task["search_req"]["snippet"] # TODO: add here after moving preprocessing to this code from NIL-fork
    }

@router.get("/search/{task_id}/results", response_model=ResultsResponse)
async def get_task_results(
    task_id: str,
    state=Depends(get_app_state)
):
    task = state.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="The task is not yet complete.")
    return task["result"]

@router.get("/methods", response_model=MethodsResponse)
async def get_available_methods():
    available_methods = [
        {
            "name": "NIL",
            "description": "Large-variance clone detection",
            "params": {
                "threshold": { # TODO: think about default parameters here and check it according to articles
                    "type": "float",
                    "default": 0.7,
                    "min": 0.1,
                    "max": 1.0
                }
            }
        },
        {
            "name": "CCAligner",
            "description": "Token-based clone detection",
            "params": {
                "min_tokens": {
                    "type": "integer",
                    "default": 50,
                    "min": 10,
                    "max": 1000
                }
            }
        },
        {
            "name": "CCSTokener",
            "description": "Semantic token-based clone detection",
            "params": {
                "some_param": {
                    "type": "string",
                    "default": "value"
                }
            }
        }
    ]
    return MethodsResponse(available_methods=available_methods)
