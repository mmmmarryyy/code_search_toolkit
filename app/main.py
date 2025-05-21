from fastapi import FastAPI
from app.api import router as api_router
import signal
from multiprocessing import Process, Manager
import argparse
import subprocess
import sys
import os

app = FastAPI(
    title="Code Search Toolkit API",
    description="REST service for searching code fragments using code clone detection methods",
    version="1.0"
)

app.include_router(api_router, prefix="/api")


def launch_uvicorn(task_queue, tasks, host, port):
    import uvicorn
    app.state.task_queue = task_queue
    app.state.tasks = tasks
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Launch Code Search API")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address")
    parser.add_argument("--port", type=int, default=1234, help="Port number")

    parser.add_argument(
        "--retry_k",
        type=int,
        default=5,
        help="Base delay (в минутах) перед первой попыткой повтора (default: 10)"
    )
    parser.add_argument(
        "--retry_multiplier",
        type=int,
        default=2,
        help="Множитель c для задержки (delay = retry_k * (retry_multiplier)^(retry_count-1)) (default: 2)"
    )
    parser.add_argument(
        "--max_retries",
        type=int,
        default=5,
        help="Максимальное число попыток (default: 5)"
    )
    parser.add_argument(
        "--max_parallel_methods",
        type=int,
        default=1,
        help="Сколько методов (Docker-контейнеров) запускаем одновременно (default: 1)"
    )
    parser.add_argument(
        "--num_workers",
        type=int,
        default=1,
        help="Сколько worker-процессов запустить для обработки задач (default: 1)"
    )

    args = parser.parse_args()

    TOOLS_DIR = os.path.join(os.getcwd(), "tools")

    methods = ["CCAligner", "CCStokener", "NIL_fork", "CCAligner_fork", "CCStokener_fork"]

    for worker_id in range(1, args.num_workers + 1):
        print(f"INFO: Building Docker images для worker_id = {worker_id} ...")
        for method in methods:
            script_path = os.path.join(TOOLS_DIR, f"build_{method}.sh")
            if not os.path.isfile(script_path):
                print(f"ERROR: Скрипт {script_path} не найден.", file=sys.stderr)
                sys.exit(1)

            try:
                subprocess.run(
                    ["bash", script_path, str(worker_id)],
                    check=True,
                    cwd=TOOLS_DIR
                )
                print(f"[OK] Built image для {method}, worker_id={worker_id}")
            except subprocess.CalledProcessError as ex:
                print(f"ERROR: Сборка образа для {method}, worker_id={worker_id} завершилась с ошибкой.", file=sys.stderr)
                sys.exit(1)

    with Manager() as manager:
        shared_task_queue = manager.Queue()
        shared_tasks = manager.dict()
        from app.worker import worker

        worker_processes = []
        for worker_id in range(1, args.num_workers + 1):
            p = Process(
                target=worker,
                args=(
                    shared_task_queue,
                    shared_tasks,
                    args.retry_k,
                    args.retry_multiplier,
                    args.max_retries,
                    args.max_parallel_methods,
                    worker_id
                )
            )
            p.start()
            worker_processes.append(p)

        api_process = Process(
            target=launch_uvicorn,
            args=(shared_task_queue, shared_tasks, args.host, args.port)
        )
        api_process.start()

        def signal_handler(sig, frame):
            for p in worker_processes:
                p.terminate()
            api_process.terminate()

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        for p in worker_processes:
            p.join()
        api_process.join()
