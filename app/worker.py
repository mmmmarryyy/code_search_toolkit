import os
import datetime
import shutil
from app.api import process_search_task
from app.models import TaskStatus

def worker(task_queue, tasks):
    print("INFO: worker started")
    while True:
        now = datetime.datetime.now()
        for tid, task in list(tasks.items()):
            expiry = task.get("expiry")
            if expiry:
                expiry_dt = datetime.datetime.fromisoformat(expiry)
                if now > expiry_dt and task["status"] not in [TaskStatus.DELETED.value]:
                    dataset_path = task.get("dataset_path")
                    if dataset_path and os.path.exists(dataset_path):
                        shutil.rmtree(dataset_path)

                    if task.get("result") and task["result"].get("result_path"):
                        result_path = task["result"]["result_path"]
                        res_folder = os.path.dirname(os.path.dirname(result_path))
                        if os.path.exists(res_folder):
                            shutil.rmtree(res_folder)
                    task["status"] = TaskStatus.DELETED.value
                    tasks[tid] = task

        try:
            task_id = task_queue.get(timeout=30)
        except Exception:
            continue
        if task_id is None:
            break

        task = tasks[task_id]
        task["started_at"] = datetime.datetime.now().isoformat()
        task["status"] = TaskStatus.PROCESSING.value
        tasks[task_id] = task

        try:
            result_path, metrics, expiry_time = process_search_task(task_id, tasks)
            task = tasks[task_id]
            task["status"] = TaskStatus.COMPLETED.value
            task["result"] = {"result_path": result_path, "metrics": metrics}
            task["expiry"] = expiry_time.isoformat()
        except Exception as e:
            task = tasks[task_id]
            task["status"] = TaskStatus.ERROR.value
            task["error_message"] = str(e)

            start_time = datetime.datetime.fromisoformat(task["started_at"])
            expiry_time = start_time + datetime.timedelta(days=1)
            task["expiry"] = expiry_time.isoformat()
        tasks[task_id] = task

        try:
            task_queue.task_done()
        except Exception:
            pass
