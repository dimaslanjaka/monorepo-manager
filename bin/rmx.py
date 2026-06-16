import subprocess
import threading
import sys
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

MAX_WORKERS = 4


def run_rm(pattern: str):
    """
    Execute rm in a POSIX shell to ensure compatibility:
    PowerShell, CMD, Git Bash, Cygwin all supported.
    """

    command = f'rm -rf "{pattern}"'

    print(f"Executing: {command}")
    # Try bash first (Git Bash / Cygwin)
    shells = [
        ["bash", "-lc", command],
        ["sh", "-c", command],
    ]

    for shell_cmd in shells:
        try:
            result = subprocess.run(
                shell_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            return result.returncode
        except FileNotFoundError:
            continue

    # fallback: direct execution (rare case)
    return subprocess.run(
        ["rm", "-rf", pattern],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode


def worker(task_queue: Queue, lock: threading.Lock):
    print(f"Worker started (thread: {threading.current_thread().name})")
    while True:
        try:
            pattern = task_queue.get_nowait()
            print(f"Worker got pattern: {pattern}")
        except Exception as e:
            print(f"Worker exiting: {e}")
            return

        try:
            result = run_rm(pattern)
            print(f"run_rm returned: {result}")

            with lock:
                print(f"Deleted: {pattern}")

        except Exception as e:
            print(f"Error processing {pattern}: {e}")
        finally:
            task_queue.task_done()


def main():
    # print(f"Script started with args: {sys.argv[1:]}")
    if len(sys.argv) < 2:
        print("Usage: python script.py <pattern1> <pattern2> ...")
        sys.exit(1)

    task_queue = Queue()
    lock = threading.Lock()

    for p in sys.argv[1:]:
        task_queue.put(p)

    print(f"Task queue size: {task_queue.qsize()}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        print(f"Submitting {MAX_WORKERS} workers...")
        for i in range(MAX_WORKERS):
            executor.submit(worker, task_queue, lock)
            print(f"Worker {i+1} submitted")

    print("Waiting for task queue to complete...")
    task_queue.join()
    print("All tasks completed.")


if __name__ == "__main__":
    main()