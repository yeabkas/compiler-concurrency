from threading import RLock
_global_atomic_lock = RLock()

@contextlib.contextmanager
def atomic():
    _global_atomic_lock.acquire()
    try:
        yield
    finally:
        _global_atomic_lock.release()