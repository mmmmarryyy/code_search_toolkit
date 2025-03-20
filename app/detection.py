import subprocess
import json
import os

def run_nil_fork(dataset_path: str, params: dict, snippet: str, result_folder: str):
    script_path = os.path.join(os.getcwd(), "tools", "run_nil_fork.sh") # TODO: rename
    cmd = [script_path, dataset_path, json.dumps(params), snippet, result_folder]
    output = subprocess.check_output(cmd, universal_newlines=True) # TODO: how subprocess.check_output works?
    return output

def run_ccaligner(dataset_path: str, params: dict, result_folder: str): # TODO: think about using params
    # TODO: run_ccaligner bash script should change dataset_folder and language in my_runner
    script_path = os.path.join(os.getcwd(), "tools", "run_CCAligner.sh") # TODO: rename
    cmd = [script_path, dataset_path, result_folder]
    output = subprocess.check_output(cmd, universal_newlines=True) # TODO: how subprocess.check_output works
    return output

def run_ccstokener(dataset_path: str, params: dict, result_folder: str):
    script_path = os.path.join(os.getcwd(), "tools", "run_CCSTokener.sh") # TODO: rename
    cmd = [script_path, dataset_path, result_folder]
    output = subprocess.check_output(cmd, universal_newlines=True) # TODO: how subprocess.check_output works
    return output

def aggregate_results(results, combination):
    # TODO: make correct aggregating
    aggregated = []
    for res in results:
        aggregated.extend(res.get("result", {}).get("matches", []))
    return aggregated
