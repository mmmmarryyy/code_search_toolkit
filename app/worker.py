from app.api import process_search_task

def worker(task_queue, tasks): # TODO: add here argument for stopping thread
    while True:
        try:
            task_id = task_queue.get(timeout=30)
        except:
            continue
        if task_id is None:
            break
        process_search_task(task_id, tasks)
        task_queue.task_done()

