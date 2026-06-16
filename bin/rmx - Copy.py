import subprocess
import threading
import sys
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

MAX_WORKERS = 4


def worker(task_queue: Queue, lock: threading.Lock):
    while True:
        try:
            pattern = task_queue.get_nowait()
        except Exception:
            return

        try:
            subprocess.run(
                ["rm", "-rf", pattern],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            with lock:
                print(f"Deleted: {pattern}")

        finally:
            task_queue.task_done()


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <pattern1> <pattern2> ...")
        sys.exit(1)

    patterns = sys.argv[1:]

    task_queue = Queue()
    lock = threading.Lock()

    for p in patterns:
        task_queue.put(p)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for _ in range(MAX_WORKERS):
            executor.submit(worker, task_queue, lock)

    task_queue.join()
    print("All tasks completed.")


if __name__ == "__main__":
    main()