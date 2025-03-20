import subprocess
import tempfile
import os
import uuid

def clone_repository(repo_url: str, branch: str = "master", dest: str = "") -> str:
    if dest == "":
        dest = tempfile.mkdtemp(prefix="repo_")
    cmd = ["git", "clone", "-b", branch, repo_url, dest]
    subprocess.check_call(cmd)
    return dest

def generate_task_id() -> str:
    return str(uuid.uuid4())
