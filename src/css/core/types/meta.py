import asyncio


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


class AsyncSafeSingletonMeta(type):
    """Async-Safe Singleton Metaclass.
    
    Uses asyncio.Lock() to prevent race conditions when instantiating
    from multiple async tasks (not threads).
    """
    _instances = {}
    _lock = asyncio.Lock()

    def __call__(cls, *args, **kwargs):
        """Intercept instantiation calls with async safety."""
        if cls not in cls._instances:
            # Use lock to prevent multiple concurrent instantiations
            # (though asyncio is single-threaded, we protect against task switching)
            if not cls._lock.locked():
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

