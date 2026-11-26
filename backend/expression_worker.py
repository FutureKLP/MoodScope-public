"""Worker entry point: hold a lease throughout inference and watch the service."""
import os
import runpy
import sys
import threading
import time
from pathlib import Path
from .worker_workspace import lease


def parent_alive(area):
    try:
        with lease(area / 'parent.lease'):
            return False
    except OSError as error:
        # A missing lease is not evidence of a live parent.
        return (area / 'parent.lease').is_file() and isinstance(error, PermissionError | BlockingIOError)


def run(area, command):
    with lease(area / 'worker.lease'):
        if not parent_alive(area):
            return 1
        def watch():
            while True:
                if not parent_alive(area):
                    os._exit(1)
                time.sleep(.25)
        threading.Thread(target=watch, daemon=True).start()
        sys.argv = command
        runpy.run_module(command[0], run_name='__main__')
        return 0


if __name__ == '__main__':
    sys.exit(run(Path(sys.argv[1]), sys.argv[2:]))
