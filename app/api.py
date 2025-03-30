import os
import json
import zipfile
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Depends, Form, UploadFile, File, status
from app.models import SearchResponse, StatusResponse, ResultsResponse, MethodsResponse
from app.utils import clone_repository, generate_task_id
from app.detection import (
    run_nil_fork,
    run_ccaligner,
    run_ccstokener,
)
from app.combination import combine_results

router = APIRouter()

def get_app_state(request: Request):
    return request.app.state

@router.post("/search", response_model=SearchResponse, status_code=201)
async def create_search_task( # TODO: add default parameters
    mode: str = Form(...),
    repository: Optional[str] = Form(None),
    branch: Optional[str] = Form(None),
    snippet: str = Form(...),
    methods: str = Form(...),
    # combination: str = Form(...),
    file: Optional[UploadFile] = File(None),
    state=Depends(get_app_state)
):
    if mode not in ["github", "local"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid mode. Supported modes: 'github', 'local'"
        )
    
    try:
        methods_list = json.loads(methods)
        # combination_dict = json.loads(combination)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON format: {str(e)}"
        )
    
    # TODO: add language validation here (also it should be passed with parameters)
    # TODO: think it's better to add enum
    # NIL-fork allowed:
    #     - "java"
    #     - "cpp"
    #     - "py", "python"
    # CCSTokener allowed:
    #     - "java"
    #     - "c"
    # CCAligner allowed:
    #     - "java"
    #     - "c"
    #     - "c#"
    
    if mode == "github":
        if not repository or not branch:
            raise HTTPException(
                status_code=400,
                detail="Repository and branch are required for github mode"
            )
        if file:
            raise HTTPException(
                status_code=400,
                detail="File upload not allowed in github mode"
            )
    else:  # local mode
        if not file:
            raise HTTPException(
                status_code=400,
                detail="File is required for local mode"
            )
        if repository or branch:
            raise HTTPException(
                status_code=400,
                detail="Repository and branch not allowed in local mode"
            )
    
    task_id = generate_task_id()

    dataset_folder = os.path.join("datasets", f"dataset_{task_id}")
    os.makedirs(dataset_folder, exist_ok=True)
    
    if mode == "github":
        try:
            clone_repository(repository, branch=branch, dest=dataset_folder)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to clone repository: {str(e)}"
            )
    else:
        if not file.filename.endswith(".zip"):
            raise HTTPException(
                status_code=400,
                detail="Only ZIP archives are supported"
            )

        zip_path = os.path.join(dataset_folder, "upload.zip")
        try:
            contents = await file.read()
            with open(zip_path, "wb") as f:
                f.write(contents)
            
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(dataset_folder)
            
            os.remove(zip_path)
        except zipfile.BadZipFile:
            raise HTTPException(
                status_code=400,
                detail="Invalid ZIP file format"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing ZIP file: {str(e)}"
            )
    
    # Save snippet to file
    # TODO: Add language detection/parameter
    snippet_ext = "java"
    snippet_path = f"snippet.{snippet_ext}"
    snippet_file = os.path.join(os.getcwd(), dataset_folder, snippet_path)
    with open(snippet_file, "w", encoding="utf-8") as f:
        if (len(snippet.split('\n')) == 1):
            for line in snippet.split("\\n"):
                f.write(line)
                f.write('\n')
        else:
            f.write(snippet)
    
    task_data = {
        "status": "pending",
        "search_req": {
            "mode": mode,
            "repository": repository,
            "branch": branch,
            "snippet": snippet,
            "snippet_path": snippet_path,
            "methods": methods_list,
            # "combination": combination_dict
        },
        "result": None,
        "dataset_path": dataset_folder
    }
    state.tasks[task_id] = task_data

    state.task_queue.put(task_id)
    
    return SearchResponse(
        task_id=task_id,
        status_url=f"/api/search/{task_id}/status",
        results_url=f"/api/search/{task_id}/results"
    )

def process_search_task(task_id: str, tasks: dict):
    # TODO: wrap into try catch and set error status
    print(f"DEBUG: inside process_search_task, task_id = {task_id}")
    # TODO: add here (just not here, but where we call process_search_task) tasks[task_id]["started_at"] = timestamp
    search_req = tasks[task_id]["search_req"]
    dataset_folder = tasks[task_id]["dataset_path"]

    results_folder = os.path.join("results", f"results_{task_id}")
    os.makedirs(results_folder, exist_ok=True)
    
    results = {}

    # TODO: should process in parallel
    for method in search_req["methods"]: # TODO: make search req also a structure or something like that
        name = method["name"]
        params = method.get("params", {})
        if name.upper() == "NIL-FORK": # TODO: create enum with names of available methods and also make it flexible like NIL/nil/...
            run_nil_fork(dataset_folder, params, search_req["snippet_path"], results_folder)
            results["NIL-fork"] = os.path.join(results_folder, "NIL-fork")
        elif name.upper() == "CCALIGNER":
            run_ccaligner(dataset_folder, params, results_folder)
            results["CCAligner"] = os.path.join(results_folder, "CCAligner")
        elif name.upper() == "CCSTOKENER": 
            run_ccstokener(dataset_folder, params, results_folder)
            results["CCSTokener"] = os.path.join(results_folder, "CCSTokener")
        else:
            continue

    '''
    results = {
        'CCAligner': 'path/to/CCAligner',
        'CCSTokener': 'path/to/CCSTokener',
        'NIL-fork': 'path/to/NIL-fork',
        'output_root': 'path/to/results'
    }

    combination = {
        'strategy': 'weighted_union',
        'weights': {'CCAligner': 0.5, 'CCSTokener': 0.3, 'NIL-fork': 0.2},
        'threshold': 0.4,
        'snippet_path': '/data/dataset/target_file.java'
    }

    final_path = aggregate_results(results, combination)
    '''
    
    result_path = ""
    if "combination" in search_req:
        result_path = combine_results(results, search_req["combination"], search_req["snippet_path"], results_folder)
    else:
        result_path = combine_results(results, {"strategy":"intersection_union"}, search_req["snippet_path"], results_folder)
    
    metrics = {
        "total_files_processed": 42,  # TODO: should calculate number of files in github repo plus 1 for snippet
        "execution_time": 10.5        # TODO: return difference between tasks[task_id]["started_at"] to this moment
    }
    
    print(f"DEBUG: results for task_id={task_id} is written to {result_path}")
    return (result_path, metrics)

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

    result_path = task["result"]["result_path"]
    metrics = task["result"]["metrics"]

    try:
        with open(result_path, 'r') as f:
            results_content = []
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split(',')
                if len(parts) != 6:
                    continue  # TODO: think about adding warning error like format exception here
                
                results_content.append({
                    "snippet1": {
                        "file_path": parts[0],
                        "start_line": int(parts[1]),
                        "end_line": int(parts[2])
                    },
                    "snippet2": {
                        "file_path": parts[3],
                        "start_line": int(parts[4]),
                        "end_line": int(parts[5])
                    }
                })

        return {
            "results": results_content,
            "metrics": metrics
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Result file not found. The results might have been deleted."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading results: {str(e)}"
        )

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
