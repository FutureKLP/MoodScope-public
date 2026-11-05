"""Supervise only MoodScope's backend worker; restart without orphaning model processes."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

ROOT=Path(__file__).resolve().parents[1]


def stop_children():
    import psutil
    children=psutil.Process().children(recursive=True)
    for child in reversed(children):
        try:child.terminate()
        except psutil.Error:pass
    _,alive=psutil.wait_procs(children,timeout=3)
    for child in alive:
        try:child.kill()
        except psutil.Error:pass


def worker(port):
    sys.path.insert(0,str(ROOT))
    import uvicorn
    import backend.app as module
    server=uvicorn.Server(uvicorn.Config(module.app,host='127.0.0.1',port=port,access_log=False))
    state={'code':0}
    def control(action,force):
        state['code']=75 if action=='restart' else 0
        def finish():
            if force:
                stop_children()
                os._exit(state['code'])
            server.should_exit=True
        threading.Timer(.5,finish).start()
    module.SYSTEM_CONTROL=control
    server.run()
    return state['code']


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8765);parser.add_argument('--worker',action='store_true')
    args=parser.parse_args();os.chdir(ROOT)
    if args.worker:return worker(args.port)
    child=None
    try:
        while True:
            child=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker','--port',str(args.port)],cwd=ROOT,stdout=sys.stdout,stderr=sys.stderr,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            code=child.wait()
            if code!=75:return code
            time.sleep(.4)
    except KeyboardInterrupt:return 0
    finally:
        if child and child.poll() is None:stop_children()


if __name__=='__main__':raise SystemExit(main())
