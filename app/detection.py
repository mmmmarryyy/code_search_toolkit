import subprocess
import os
from app.models import MethodEnum

def run_nil_fork(dataset_path: str, params: dict, snippet: str, result_folder: str, language: str, worker_id: int, save_logs: bool):
    script_path = os.path.join(os.getcwd(), "tools", "run_NIL_fork.sh")
    cmd = [script_path, dataset_path, result_folder, language, snippet, str(worker_id)] # TODO: check that pass correct language format
    
    for key, value in params.items():
        cmd.extend([key, str(value)])

    try:
        output = subprocess.check_output(cmd, universal_newlines=True)
        if "Error" in output or "ERROR" in output or "error" in output or \
            "Exception" in output or "EXCEPTION" in output or "exception" in output:
            raise RuntimeError("find error or exception in output logs")
        if save_logs:
            with open(os.path.join(result_folder, MethodEnum.NIL_FORK.value, "logs.txt"), "w+") as f:
                f.write(output)
    except (subprocess.CalledProcessError, RuntimeError) as e:
        if save_logs:
            with open(os.path.join(result_folder, MethodEnum.NIL_FORK.value, "logs.txt"), "w+") as f:
                f.write(output)
                f.write(f"\nERROR: {e}")
        raise RuntimeError(f"NIL-fork error: {e}")
    

def run_ccaligner(dataset_path: str, params: dict, result_folder: str, language: str, worker_id: int, save_logs: bool):
    script_path = os.path.join(os.getcwd(), "tools", "run_CCAligner.sh")
    cmd = [script_path, dataset_path, result_folder, language, str(worker_id)]  # TODO: check that pass correct language format
    
    for key, value in params.items():
        cmd.extend([key, str(value)])
    
    try:
        output = subprocess.check_output(cmd, universal_newlines=True)
        if "Error" in output or "ERROR" in output or "error" in output or \
            "Exception" in output or "EXCEPTION" in output or "exception" in output:
            raise RuntimeError("find error or exception in output logs")
        if save_logs:
            with open(os.path.join(result_folder, MethodEnum.CCALIGNER.value, "logs.txt"), "w+") as f:
                f.write(output)
    except (subprocess.CalledProcessError, RuntimeError) as e:
        if save_logs:
            with open(os.path.join(result_folder, MethodEnum.CCALIGNER.value, "logs.txt"), "w+") as f:
                f.write(output)
                f.write(f"\nERROR: {e}")
        raise RuntimeError(f"CCAligner error: {e}")


def run_ccstokener(dataset_path: str, params: dict, result_folder: str, language: str, worker_id: int, save_logs: bool):
    script_path = os.path.join(os.getcwd(), "tools", "run_CCSTokener.sh")
    cmd = [script_path, dataset_path, result_folder, language, str(worker_id)]  # TODO: check that pass correct language format
    
    for key, value in params.items():
        cmd.extend([key, str(value)])
    
    try:
        output = subprocess.check_output(cmd, universal_newlines=True)
        if "Error" in output or "ERROR" in output or \
            "Exception" in output or "EXCEPTION" in output or "exception" in output:
            raise RuntimeError("find error or exception in output logs")
        if "error" in output and output.count("error") > output.count("error parse file num: 0"):
            raise RuntimeError("find error or exception in output logs")
        if save_logs:
            with open(os.path.join(result_folder, MethodEnum.CCSTOKENER.value, "logs.txt"), "w+") as f:
                f.write(output)
    except (subprocess.CalledProcessError, RuntimeError) as e:
        if save_logs:
            with open(os.path.join(result_folder, MethodEnum.CCSTOKENER.value, "logs.txt"), "w+") as f:
                f.write(output)
                f.write(f"\nERROR: {e}")
        raise RuntimeError(f"CCStokener error: {e}")


def run_ccaligner_fork(dataset_path: str, _: dict, snippet: str, result_folder: str, language: str, worker_id: int, save_logs: bool):
    script_path = os.path.join(os.getcwd(), "tools", "run_CCAligner_fork.sh")
    cmd = [script_path, dataset_path, result_folder, language, snippet, str(worker_id)] # TODO: check that pass correct language format
    
    try:
        output = subprocess.check_output(cmd, universal_newlines=True)
        if "Error" in output or "ERROR" in output or "error" in output or \
            "Exception" in output or "EXCEPTION" in output or "exception" in output:
            raise RuntimeError("find error or exception in output logs")
        if save_logs:
            with open(os.path.join(result_folder, MethodEnum.CCALIGNER_FORK.value, "logs.txt"), "w+") as f:
                f.write(output)
    except (subprocess.CalledProcessError, RuntimeError) as e:
        if save_logs:
            with open(os.path.join(result_folder, MethodEnum.CCALIGNER_FORK.value, "logs.txt"), "w+") as f:
                f.write(output)
                f.write(f"\nERROR: {e}")
        raise RuntimeError(f"CCAligner-fork error: {e}")


def run_ccstokener_fork(dataset_path: str, params: dict, snippet: str, result_folder: str, language: str, worker_id: int, save_logs: bool):
    script_path = os.path.join(os.getcwd(), "tools", "run_CCStokener_fork.sh")
    cmd = [script_path, dataset_path, result_folder, language, snippet, str(worker_id)] # TODO: check that pass correct language format
    
    for key, value in params.items():
        cmd.extend([key, str(value)])
    
    try:
        output = subprocess.check_output(cmd, universal_newlines=True)
        if "Error" in output or "ERROR" in output or "error" in output or \
            "Exception" in output or "EXCEPTION" in output or "exception" in output:
            raise RuntimeError("find error or exception in output logs")
        if save_logs:
            with open(os.path.join(result_folder, MethodEnum.CCSTOKENER_FORK.value, "logs.txt"), "w+") as f:
                f.write(output)
    except (subprocess.CalledProcessError, RuntimeError) as e:
        if save_logs:
            with open(os.path.join(result_folder, MethodEnum.CCSTOKENER_FORK.value, "logs.txt"), "w+") as f:
                f.write(output)
                f.write(f"\nERROR: {e}")
        raise RuntimeError(f"CCStokener-fork error: {e}")


def run_nicad(dataset_path: str, params: dict, result_folder: str, language: str, worker_id: int, save_logs: bool):
    script_path = os.path.join(os.getcwd(), "tools", "run_NiCad.sh")
    cmd = [script_path, dataset_path, result_folder, language, str(worker_id)]  # TODO: check that pass correct language format
    
    for key, value in params.items():
        cmd.extend([key, str(value)])
    
    try:
        output = subprocess.check_output(cmd, universal_newlines=True)
        if "Error" in output or "ERROR" in output or "error" in output or \
            "Exception" in output or "EXCEPTION" in output or "exception" in output:
            raise RuntimeError("find error or exception in output logs")
        if save_logs:
            with open(os.path.join(result_folder, MethodEnum.NICAD.value, "logs.txt"), "w+") as f:
                f.write(output)
    except (subprocess.CalledProcessError, RuntimeError) as e:
        if save_logs:
            with open(os.path.join(result_folder, MethodEnum.NICAD.value, "logs.txt"), "w+") as f:
                f.write(output)
                f.write(f"\nERROR: {e}")
        raise RuntimeError(f"NiCad error: {e}")


def run_sourcerercc(dataset_path: str, _: dict, result_folder: str, language: str, worker_id: int, save_logs: bool):
    script_path = os.path.join(os.getcwd(), "tools", "run_SourcererCC.sh")
    cmd = [script_path, dataset_path, result_folder, language, str(worker_id)]  # TODO: check that pass correct language format
    
    try:
        output = subprocess.check_output(cmd, universal_newlines=True)
        if "SUCCESS: Search Completed on all nodes" not in output and (
            "Error" in output or "ERROR" in output or "error" in output or \
            "Exception" in output or "EXCEPTION" in output or "exception" in output
        ):
            raise RuntimeError("find error or exception in output logs")
        if save_logs:
            with open(os.path.join(result_folder, MethodEnum.SOURCERERCC.value, "logs.txt"), "w+") as f:
                f.write(output)
    except (subprocess.CalledProcessError, RuntimeError) as e:
        if save_logs:
            with open(os.path.join(result_folder, MethodEnum.SOURCERERCC.value, "logs.txt"), "w+") as f:
                f.write(output)
                f.write(f"\nERROR: {e}")
        raise RuntimeError(f"SourcererCC error: {e}")

