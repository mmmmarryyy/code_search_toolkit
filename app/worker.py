from app.api import process_search_task

def worker(task_queue, tasks):
    print("Debug: worker")
    while True:
        try:
            task_id = task_queue.get(timeout=30)
        except:
            continue
        if task_id is None:
            break

        task = tasks[task_id]
        task["status"] = "processing"
        tasks[task_id] = task

        (result_path, metrics) = process_search_task(task_id, tasks)
        
        task = tasks[task_id]
        task["status"] = "completed"
        task["result"] = {"result_path": result_path, "metrics": metrics}
        tasks[task_id] = task

        task_queue.task_done()
