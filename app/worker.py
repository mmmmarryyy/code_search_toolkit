import os
import datetime
import shutil
from app.api import process_search_task
from app.models import TaskStatus

def worker(
    task_queue,
    tasks,
    retry_k: int,
    retry_multiplier: int,
    max_retries: int,
    max_parallel_methods: int,
    save_logs: bool,
    worker_id: int
):
    print("INFO: worker started, retry_k =", retry_k,
          "retry_multiplier =", retry_multiplier,
          "max_retries =", max_retries,
          "max_parallel_methods =", max_parallel_methods,
          "save_logs =", save_logs,
          "worker_id =", worker_id)

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

        task = tasks.get(task_id)
        if not task:
            continue

        if task["status"] == TaskStatus.ERROR.value and task.get("next_attempt_at"):
            next_time = datetime.datetime.fromisoformat(task["next_attempt_at"])
            if now < next_time:
                task_queue.put(task_id)
                continue
            else:
                task["status"] = TaskStatus.PENDING.value
                task.pop("next_attempt_at", None)
                tasks[task_id] = task

        if task["status"] != TaskStatus.PENDING.value:
            continue

        task["started_at"] = datetime.datetime.now().isoformat()
        task["status"] = TaskStatus.PROCESSING.value
        tasks[task_id] = task

        try:
            result_path, metrics, expiry_time = process_search_task(task_id, tasks, worker_id, max_parallel_methods, save_logs)
            task = tasks[task_id]
            task["status"] = TaskStatus.COMPLETED.value
            task["result"] = {"result_path": result_path, "metrics": metrics}
            task["expiry"] = expiry_time.isoformat()

            task.pop("retry_count", None)
            task.pop("next_attempt_at", None)
            tasks[task_id] = task

        except Exception as e:
            print(f"DEBUG: catch error = {e}")
            task = tasks[task_id]
            last_retry = task.get("retry_count", 0)

            if last_retry < max_retries:
                new_retry = last_retry + 1
                print(f"DEBUG: Error {new_retry} for task = {task_id}")
                task["retry_count"] = new_retry

                delay_minutes = retry_k * (retry_multiplier ** (new_retry - 1))
                next_time = now + datetime.timedelta(minutes=delay_minutes)
                task["next_attempt_at"] = next_time.isoformat()

                task["status"] = TaskStatus.ERROR.value
                task["error_message"] = str(e)
                tasks[task_id] = task

                task_queue.put(task_id)
            else:
                task["status"] = TaskStatus.ERROR.value
                task["error_message"] = str(e)
                task.pop("next_attempt_at", None)
                tasks[task_id] = task

        try:
            task_queue.task_done()
        except Exception:
            pass
