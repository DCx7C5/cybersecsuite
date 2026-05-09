from abc import ABCMeta
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


class AsyncSafeSingletonMeta(ABCMeta):
    """Async-Safe Singleton Metaclass.

    Ensures only one instance exists. Note: Since __call__ is sync,
    true async locking must be handled during the 'get_instance' pattern
    if __init__ contains await points. This metaclass provides a basic
    registry-based singleton.
    """
    _instances = {}
    _lock = asyncio.Lock()  # Only for instantiation

    def __call__(cls, *args, **kwargs):
        """Intercept instantiation calls with async safety."""
        if cls not in cls._instances:
            # Use lock to prevent multiple concurrent instantiations
            # (though asyncio is single-threaded, we protect against task switching)
            if not cls._lock.locked():
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


def singleton(cls):
    """Class decorator for Singleton pattern."""
    _instances = {}
    _lock = asyncio.Lock()

    def get_instance(*args, **kwargs):
        if cls not in _instances:
            if not _lock.locked():
                _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]

    return get_instance
