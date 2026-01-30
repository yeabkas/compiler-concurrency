import threading, queue, contextlib, time

class Channel:
    def __init__(self, maxsize=0):
        self.q = queue.Queue(maxsize=maxsize)
    def send(self, v):
        self.q.put(v)
    def recv(self):
        return self.q.get()

class Lock:
    def __init__(self):
        self._lock = threading.RLock()
    def acquire(self, timeout=None):
        return self._lock.acquire(timeout=timeout) if timeout else self._lock.acquire()
    def release(self):
        self._lock.release()
    @contextlib.contextmanager
    def hold(self, timeout=None):
        acquired = self.acquire(timeout=timeout)
        try:
            yield acquired
        finally:
            if acquired:
                self.release()

class ThreadManager:
    def __init__(self):
        self.threads = []
    def spawn(self, target, *args, **kwargs):
        t = threading.Thread(target=target, args=args, kwargs=kwargs)
        t.start()
        self.threads.append(t)
        return t
    def join_all(self):
        for t in self.threads:
            t.join()