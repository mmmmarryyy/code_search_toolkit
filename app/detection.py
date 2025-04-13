import subprocess
import os

def run_nil_fork(dataset_path: str, params: dict, snippet: str, result_folder: str, language: str, worker_id: int):
    script_path = os.path.join(os.getcwd(), "tools", "run_NIL_fork.sh")
    cmd = [script_path, dataset_path, result_folder, language, snippet, str(worker_id)] # TODO: check that pass correct language format
    try:
        output = subprocess.check_output(cmd, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Код возврата: {e.returncode}, Вывод: {e.output}")
    print(f"INFO: {output}")

def run_ccaligner(dataset_path: str, params: dict, result_folder: str, language: str, worker_id: int):
    script_path = os.path.join(os.getcwd(), "tools", "run_CCAligner.sh")
    cmd = [script_path, dataset_path, result_folder, language, str(worker_id)]  # TODO: check that pass correct language format
    try:
        output = subprocess.check_output(cmd, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Код возврата: {e.returncode}, Вывод: {e.output}")
    print(f"INFO: {output}")

def run_ccstokener(dataset_path: str, params: dict, result_folder: str, language: str, worker_id: int):
    script_path = os.path.join(os.getcwd(), "tools", "run_CCSTokener.sh")
    cmd = [script_path, dataset_path, result_folder, language, str(worker_id)]  # TODO: check that pass correct language format
    try:
        output = subprocess.check_output(cmd, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Код возврата: {e.returncode}, Вывод: {e.output}")
    print(f"INFO: {output}")
