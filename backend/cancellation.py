"""Cooperative cancellation scoped to the worker; never interrupts unrelated requests."""
import threading
from contextlib import contextmanager

_local=threading.local()


class Cancelled(BaseException):
    """Like KeyboardInterrupt, bypass ordinary job error handlers for central cleanup."""


def check():
    event=getattr(_local,'event',None)
    if event is not None and event.is_set():raise Cancelled()


def capture():
    event=getattr(_local,'event',None)
    def checkpoint():
        if event is not None and event.is_set():raise Cancelled()
    return checkpoint


@contextmanager
def scope(event):
    previous=getattr(_local,'event',None);_local.event=event
    try:
        check();yield
        check()
    finally:_local.event=previous
