"""Frozen entry point. Stdin is a lease held exclusively by the native client."""
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time


def wait_for_eof():
    # A buffered daemon read holds Python's stdin lock during finalization.
    # Raw descriptor reads allow clean worker exit as well as abrupt parent loss.
    while os.read(sys.stdin.fileno(),1024):pass


def stop(process):
    """Use process objects (including creation times), never a persisted PID file."""
    import psutil
    from scripts.service import stop_children
    try:
        parent=psutil.Process(process.pid)
        stop_children(parent)
        parent.terminate()
        try:parent.wait(5)
        except psutil.TimeoutExpired:parent.kill();parent.wait(5)
    except psutil.NoSuchProcess:pass
    process.wait()


def serve(listener):
    import uvicorn
    import backend.app as module
    from scripts.service import stop_children
    def parent_lease():
        wait_for_eof()
        stop_children()
        os._exit(0)
    threading.Thread(target=parent_lease,daemon=True).start()
    server=uvicorn.Server(uvicorn.Config(module.app,host='127.0.0.1',port=8765,
        access_log=False,timeout_graceful_shutdown=3,
        loop='asyncio:SelectorEventLoop' if os.name=='nt' else 'asyncio'))
    state={'code':0}
    def control(action,force):
        state['code']=75 if action=='restart' else 0
        def finish():
            server.should_exit=True
            def deadline():
                stop_children();os._exit(state['code'])
            watchdog=threading.Timer(8,deadline);watchdog.daemon=True;watchdog.start()
        threading.Timer(.5,finish).start()
    module.SYSTEM_CONTROL=control
    try:server.run(sockets=[listener])
    finally:stop_children()
    return state['code']


def bind_listener(port=8765):
    listener=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    if os.name=='nt':listener.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
    else:listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    try:
        listener.bind(('127.0.0.1',port));listener.listen(128)
    except BaseException:
        listener.close();raise
    return listener


def main():
    # The serving worker reserves the address before importing models. An unknown
    # listener is never adopted, signalled, or used as a readiness result.
    if '--serve' in sys.argv:
        if os.name=='nt':
            listener=socket.fromshare(bytes.fromhex(sys.stdin.buffer.readline().decode().strip()))
        else:
            listener=socket.socket(fileno=int(os.environ['MOODSCOPE_LISTENER_FD']))
        with listener:return serve(listener)
    listener=bind_listener()  # Retained across worker restarts: no port takeover gap.
    from backend.paths import data_dir,model_dir
    data=data_dir();data.mkdir(parents=True,exist_ok=True)
    model_dir().mkdir(parents=True,exist_ok=True)
    temporary=data/'tmp';temporary.mkdir(exist_ok=True)
    os.environ['TMPDIR']=os.environ['TEMP']=os.environ['TMP']=str(temporary)
    os.environ['PYTHONNOUSERSITE']='1'
    done=threading.Event()
    def lease():
        wait_for_eof();done.set()
    threading.Thread(target=lease,daemon=True).start()
    args=[sys.executable,'--serve'] if getattr(sys,'frozen',False) else [sys.executable,'-m','scripts.packaged_backend','--serve']
    child=None
    crashes=0
    try:
        with (data/'backend.log').open('ab') as log:
            while not done.is_set():
                options={}
                if os.name!='nt':
                    options={'pass_fds':(listener.fileno(),),'env':{**os.environ,'MOODSCOPE_LISTENER_FD':str(listener.fileno())}}
                child=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=log,stderr=log,
                    creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),**options)
                if os.name=='nt':
                    child.stdin.write(listener.share(child.pid).hex().encode()+b'\n');child.stdin.flush()
                while child.poll() is None and not done.wait(.1):pass
                if done.is_set():break
                code=child.wait()
                if code==0:return 0
                if code!=75:
                    crashes+=1
                    if crashes>2:return code
                if done.wait(.5):break
    finally:
        if child and child.poll() is None:stop(child)
        listener.close()
    return 0


if __name__=='__main__':raise SystemExit(main())
