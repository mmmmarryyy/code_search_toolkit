from fastapi import FastAPI
from app.api import router as api_router
import signal
from multiprocessing import Process, Manager

app = FastAPI(
    title="Code Search Toolkit API",
    description="REST service for searching code fragments using code clone detection methods",
    version="1.0"
)

app.include_router(api_router, prefix="/api")

def launch_uvicorn(task_queue, tasks):
    import uvicorn
    app.state.task_queue = task_queue
    app.state.tasks = tasks
    uvicorn.run(app, host="0.0.0.0", port=1234) # TODO: move parameters to sys.args

if __name__ == "__main__":
    with Manager() as manager:
        shared_task_queue = manager.Queue()
        shared_tasks = manager.dict()
        from app.worker import worker
        worker_thread = Process(target=worker, args=(shared_task_queue, shared_tasks))

        my_process = Process(target=launch_uvicorn, args=(shared_task_queue, shared_tasks))

        def signal_handler(sig, frame):
            my_process.terminate()
            worker_thread.terminate()

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        worker_thread.start()

        my_process.start()

        worker_thread.join()
        my_process.join()
    