import logging
from typing import Optional

from .utils import get_logger


class Base:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self._log = logger
        # Fully qualified name of the class
        self._fqn = self.__class__.__module__ if self.__class__.__module__ != "__main__" else __name__
        self.log.debug(f"{self.__class__.__name__} class instance created.")

    @property
    def log(self):
        if self._log is None:
            self._log = get_logger(self._fqn)
        return self._log

    def __repr__(self):
        return f"<{self.__class__.__name__!s}({self.__dict__!r})>"

    def __str__(self) -> str:
        return f"{self.__class__.__name__!s}"
