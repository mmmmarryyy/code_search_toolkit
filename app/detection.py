import subprocess
import os

def run_nil_fork(dataset_path: str, params: dict, snippet: str, result_folder: str, language: str, worker_id: int):
    script_path = os.path.join(os.getcwd(), "tools", "run_NIL_fork.sh")
    cmd = [script_path, dataset_path, result_folder, language, snippet, str(worker_id)] # TODO: check that pass correct language format
    try:
        output = subprocess.check_output(cmd, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Код возврата: {e.returncode}, Вывод: {e.output}")
    # print(f"INFO: {output}") # TODO: think about deleting all of this info

def run_ccaligner(dataset_path: str, params: dict, result_folder: str, language: str, worker_id: int):
    script_path = os.path.join(os.getcwd(), "tools", "run_CCAligner.sh")
    cmd = [script_path, dataset_path, result_folder, language, str(worker_id)]  # TODO: check that pass correct language format
    try:
        output = subprocess.check_output(cmd, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Код возврата: {e.returncode}, Вывод: {e.output}")
    # print(f"INFO: {output}")

def run_ccstokener(dataset_path: str, params: dict, result_folder: str, language: str, worker_id: int):
    script_path = os.path.join(os.getcwd(), "tools", "run_CCSTokener.sh")
    cmd = [script_path, dataset_path, result_folder, language, str(worker_id)]  # TODO: check that pass correct language format
    try:
        output = subprocess.check_output(cmd, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Код возврата: {e.returncode}, Вывод: {e.output}")
    # print(f"INFO: {output}")

def run_ccaligner_fork(dataset_path: str, params: dict, snippet: str, result_folder: str, language: str, worker_id: int):
    script_path = os.path.join(os.getcwd(), "tools", "run_CCAligner_fork.sh")
    cmd = [script_path, dataset_path, result_folder, language, snippet, str(worker_id)] # TODO: check that pass correct language format
    try:
        output = subprocess.check_output(cmd, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Код возврата: {e.returncode}, Вывод: {e.output}")
    # print(f"INFO: {output}")

def run_ccstokener_fork(dataset_path: str, params: dict, snippet: str, result_folder: str, language: str, worker_id: int):
    script_path = os.path.join(os.getcwd(), "tools", "run_CCStokener_fork.sh")
    cmd = [script_path, dataset_path, result_folder, language, snippet, str(worker_id)] # TODO: check that pass correct language format
    try:
        output = subprocess.check_output(cmd, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Код возврата: {e.returncode}, Вывод: {e.output}")
    # print(f"INFO: {output}") #TODO: спрятать вывод логов под флаг и пусть пользователь сам решает хочет он выдавать логи или нет (и пусть они в файл соответствующей задачи записываются)

def run_nicad(dataset_path: str, params: dict, result_folder: str, language: str, worker_id: int):
    script_path = os.path.join(os.getcwd(), "tools", "run_NiCad.sh")
    cmd = [script_path, dataset_path, result_folder, language, str(worker_id)]  # TODO: check that pass correct language format
    try:
        output = subprocess.check_output(cmd, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Код возврата: {e.returncode}, Вывод: {e.output}")
    # print(f"INFO: {output}")

def run_sourcerercc(dataset_path: str, params: dict, result_folder: str, language: str, worker_id: int):
    script_path = os.path.join(os.getcwd(), "tools", "run_SourcererCC.sh")
    cmd = [script_path, dataset_path, result_folder, language, str(worker_id)]  # TODO: check that pass correct language format
    try:
        output = subprocess.check_output(cmd, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Код возврата: {e.returncode}, Вывод: {e.output}")
    # print(f"INFO: {output}")

