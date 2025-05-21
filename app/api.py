import os
import json
import zipfile
import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Depends, Form, UploadFile, File

from app.models import (
    SearchResponse,
    StatusResponse,
    ResultsResponse,
    MethodsResponse,
    LanguageEnum,
    MethodEnum,
    TaskStatus,
)
from app.utils import clone_repository, generate_task_id
from app.detection import (
    run_nil_fork,
    run_ccaligner,
    run_ccstokener,
    run_ccaligner_fork,
    run_ccstokener_fork,
)
from app.combination import combine_results
import concurrent.futures

router = APIRouter()

def get_app_state(request: Request):
    return request.app.state

ALLOWED_LANGUAGES_FOR_METHOD = {
    MethodEnum.NIL_FORK: [LanguageEnum.JAVA, LanguageEnum.CPP, LanguageEnum.PYTHON],
    MethodEnum.CCALIGNER: [LanguageEnum.JAVA, LanguageEnum.C, LanguageEnum.CSHARP],
    MethodEnum.CCSTOKENER: [LanguageEnum.JAVA, LanguageEnum.C],
    MethodEnum.CCALIGNER_FORK: [LanguageEnum.JAVA, LanguageEnum.PYTHON],
    MethodEnum.CCSTOKENER_FORK: [LanguageEnum.JAVA],
}

EXT_MAPPING = { # TODO: check language text format for languages that are not java (i mean using them like arguments for methods)
    LanguageEnum.JAVA: "java",
    LanguageEnum.CPP: "cpp",
    LanguageEnum.PYTHON: "py",
    LanguageEnum.C: "c",
    LanguageEnum.CSHARP: "cs",
}

@router.post("/search", response_model=SearchResponse, status_code=201)
async def create_search_task(
    mode: str = Form(...),
    repository: Optional[str] = Form(None),
    branch: Optional[str] = Form(None),
    snippet: str = Form(...),
    methods: Optional[str] = Form(None),
    combination: Optional[str] = Form('{"strategy": "intersection_union"}'),
    language: str = Form(...),
    file: Optional[UploadFile] = File(None),
    state=Depends(get_app_state)
):
    if mode not in ["github", "local"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid mode. Supported modes: 'github', 'local'"
        )

    try:
        lang_enum = LanguageEnum(language.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language. Supported: {[lang.value for lang in LanguageEnum]}"
        )

    if mode == "github" and repository:
        branch = branch or "main"

    try:
        methods_list = json.loads(methods) if methods else [{"name": MethodEnum.NIL_FORK.value}]
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON format for methods: {str(e)}"
        )

    for m in methods_list:
        try:
            method_enum = MethodEnum(m["name"])
        except Exception:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported method: {m.get('name')}. Supported methods: {[m.value for m in MethodEnum]}"
            )
        if lang_enum not in ALLOWED_LANGUAGES_FOR_METHOD[method_enum]:
            raise HTTPException(
                status_code=400,
                detail=f"Method {method_enum.value} does not support language {lang_enum.value}"
            )

    try:
        combination_dict = json.loads(combination)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON format for combination: {str(e)}"
        )

    supported_strategies = [
        "intersection_union",
        "weighted_union",
        "union",
        "threshold_union"
    ]

    strategy = combination_dict.get("strategy")
    if strategy not in supported_strategies:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported combination strategy. Supported: {supported_strategies}"
        )

    if strategy == "weighted_union":
        if "weights" not in combination_dict or "threshold" not in combination_dict:
            raise HTTPException(
                status_code=400,
                detail="For weighted_union, you must provide 'weights' and 'threshold' in the combination JSON."
            )
    if strategy == "threshold_union":
        if "min_methods" not in combination_dict:
            raise HTTPException(
                status_code=400,
                detail="For threshold_union, you must provide 'min_methods' (integer) in the combination JSON."
            )
        if not isinstance(combination_dict["min_methods"], int) or combination_dict["min_methods"] < 1:
            raise HTTPException(
                status_code=400,
                detail="'min_methods' must be a positive integer."
            )

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

    snippet_ext = EXT_MAPPING.get(lang_enum, "txt") # TODO: maybe it's better to throw error here
    snippet_filename = f"snippet.{snippet_ext}"
    snippet_path = os.path.join(os.getcwd(), dataset_folder, snippet_filename)
    with open(snippet_path, "w", encoding="utf-8") as f:
        if len(snippet.split('\n')) == 1:
            for line in snippet.split("\\n"):
                f.write(line)
                f.write('\n')
        else:
            f.write(snippet)
        f.write('\n')

    task_data = {
        "status": TaskStatus.PENDING.value,
        "search_req": {
            "mode": mode,
            "repository": repository,
            "branch": branch,
            "snippet": snippet,
            "snippet_path": snippet_filename,
            "methods": methods_list,
            "combination": combination_dict,
            "language": lang_enum.value,
        },
        "result": None,
        "dataset_path": dataset_folder,
        "started_at": None,
        "expiry": None
    }
    state.tasks[task_id] = task_data
    state.task_queue.put(task_id)
    
    return SearchResponse(
        task_id=task_id,
        status_url=f"/api/search/{task_id}/status",
        results_url=f"/api/search/{task_id}/results"
    )


def process_search_task(
    task_id: str,
    tasks: dict,
    worker_id: int,
    max_parallel_methods: int
):
    import datetime
    print(f"DEBUG: inside process_search_task, task_id = {task_id}, worker_id = {worker_id}")

    start_time = datetime.datetime.fromisoformat(tasks[task_id]["started_at"])

    search_req = tasks[task_id]["search_req"]
    dataset_folder = tasks[task_id]["dataset_path"]

    results_folder = os.path.join("results", f"results_{task_id}")
    os.makedirs(results_folder, exist_ok=True)

    def run_method(method: dict):
        name = method["name"]
        params = method.get("params", {})

        if name.upper() == MethodEnum.NIL_FORK.value.upper():
            run_nil_fork(
                dataset_folder,
                params,
                search_req["snippet_path"],
                results_folder,
                search_req["language"],
                worker_id
            )
            return MethodEnum.NIL_FORK.value, os.path.join(results_folder, MethodEnum.NIL_FORK.value)

        elif name.upper() == MethodEnum.CCALIGNER.value.upper():
            run_ccaligner(
                dataset_folder,
                params,
                results_folder,
                search_req["language"],
                worker_id
            )
            return MethodEnum.CCALIGNER.value, os.path.join(results_folder, MethodEnum.CCALIGNER.value)

        elif name.upper() == MethodEnum.CCSTOKENER.value.upper():
            run_ccstokener(
                dataset_folder,
                params,
                results_folder,
                search_req["language"],
                worker_id
            )
            return MethodEnum.CCSTOKENER.value, os.path.join(results_folder, MethodEnum.CCSTOKENER.value)

        elif name.upper() == MethodEnum.CCALIGNER_FORK.value.upper():
            run_ccaligner_fork(
                dataset_folder,
                params,
                search_req["snippet_path"],
                results_folder,
                search_req["language"],
                worker_id
            )
            return MethodEnum.CCALIGNER_FORK.value, os.path.join(results_folder, MethodEnum.CCALIGNER_FORK.value)

        elif name.upper() == MethodEnum.CCSTOKENER_FORK.value.upper():
            run_ccstokener_fork(
                dataset_folder,
                params,
                search_req["snippet_path"],
                results_folder,
                search_req["language"],
                worker_id
            )
            return MethodEnum.CCSTOKENER_FORK.value, os.path.join(results_folder, MethodEnum.CCSTOKENER_FORK.value)

        else:
            raise ValueError(f"Unsupported method: {name}")

    results = {}
    methods_list = search_req["methods"]

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel_methods) as executor:
        future_to_method = {
            executor.submit(run_method, method): method
            for method in methods_list
        }
        for future in concurrent.futures.as_completed(future_to_method):
            method_dict = future_to_method[future]
            try:
                method_name, method_output_dir = future.result()
                results[method_name] = method_output_dir
                print(f"DEBUG: Method {method_name} finished, output at {method_output_dir}")
            except Exception as exc:
                raise

    result_path = combine_results(
        results,
        search_req.get("combination", {"strategy": "intersection_union"}),
        search_req["snippet_path"],
        results_folder
    )

    total_files = 0
    for _, _, files in os.walk(dataset_folder):
        total_files += len(files)
    total_files += 1

    execution_time = (datetime.datetime.now() - start_time).total_seconds()

    metrics = {
        "total_files_processed": total_files,
        "execution_time": execution_time
    }
    
    print(f"DEBUG: results for task_id={task_id} is written to {result_path}")

    expiry_time = start_time + datetime.timedelta(days=1)
    tasks[task_id]["expiry"] = expiry_time.isoformat()

    return result_path, metrics, expiry_time


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
        "started_at": task["started_at"] if task["started_at"] else "not_started",
        "processed_snippet": task["search_req"]["snippet"]
    }


@router.get("/search/{task_id}/results", response_model=ResultsResponse)
async def get_task_results(
    task_id: str,
    state=Depends(get_app_state)
):
    task = state.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    if task["status"] != TaskStatus.COMPLETED.value:
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
                    continue

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
async def get_available_methods(): # TODO: make it actual
    available_methods = [
        {
            "name": MethodEnum.NIL_FORK.value,
            "description": "Large-variance clone detection",
            "params": {
                "threshold": {
                    "type": "float",
                    "default": 0.7,
                    "min": 0.1,
                    "max": 1.0
                }
            }
        },
        {
            "name": MethodEnum.CCALIGNER.value,
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
            "name": MethodEnum.CCSTOKENER.value,
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
