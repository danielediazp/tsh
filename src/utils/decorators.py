import logging
from functools import wraps

LOGGER = logging.getLogger(__name__)


def singleton(cls: type) -> type:
    """
    Class decorator that makes a class a singleton by caching
    the first created instance and returning it on subsequent calls.
    """

    instances: dict[type, object] = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls.__new__(cls, *args, **kwargs)
            cls.__init__(instances[cls], *args, **kwargs)
            LOGGER.info(f"Successfully created singleton instances of {cls.__name__}")
        else:
            LOGGER.warning(
                f"Attempted to create second instance of singleton {cls.__name__}, returning existing one"
            )
        return instances[cls]

    return get_instance  # replaces the class with our factory
