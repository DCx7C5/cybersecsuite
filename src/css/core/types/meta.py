import threading


class SingletonMetaClass(type):
    """Singleton Metaclass — ensures only one instance of the target class exists.
    
    Usage::
        class MyClass(metaclass=SingletonMetaClass):
            def __init__(self, value):
                self.value = value
    
    Note: __init__ is called only on first instantiation.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Intercept instantiation calls."""
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class TSSingletonMetaClass(type):
    """Thread-Safe Singleton Metaclass.
    
    Uses a lock to prevent race conditions in multi-threaded environments.
    """
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        """Intercept instantiation calls with thread safety."""
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

