from __future__ import annotations

import logging
import sys
from enum import Enum
from typing import Callable, Dict, List, Tuple


class EventError(Exception):
    pass


# #############################################################################


class EventTypeLog(Enum):
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)


# #############################################################################


class Event:
    _instances: Dict[str, object] = {}
    _thresholds: Dict[str, object] = {}

    def __new__(cls, event_type, *args, **kwargs):
        event_family = event_type.__class__.__name__
        event_type = f"{event_family}_{event_type}"
        if event_family not in cls._thresholds:
            cls._thresholds[event_family] = EventTypeLog.NOTSET.value
        if event_type not in cls._instances:
            cls._instances[event_type] = super().__new__(cls)
        return cls._instances[event_type]

    def __init__(self, event_type, *args, **kwargs):
        if hasattr(self, "_initialized"):
            return
        self.family = event_type.__class__.__name__
        self.type = event_type
        self._callbacks = {}
        self._initialized = True

    def __repr__(self):
        return f"<{self.__class__.__name__!s}({self.__dict__!r})>"

    def __str__(self) -> str:
        return f"{self.__class__.__name__!s}.{self.family!s}.{self.type.name!s}"

    @classmethod
    def delete(cls) -> None:
        cls._instances = {}
        cls._thresholds = {}

    @classmethod
    def set_threshold(cls, val: Enum):
        event_family = val.__class__.__name__
        cls._thresholds[event_family] = val.value

    def register(self, key: str, callback: Callable):
        self._callbacks[key] = callback

    def register_all(self, *callback_key_pairs: Tuple | List):
        for key, callback in callback_key_pairs:
            self.register(key, callback)

    def unregister(self, key: str):
        if key in self._callbacks:
            del self._callbacks[key]

    def fire(self, *args, **kwargs):
        if self._thresholds[self.family] > self.type.value:
            return
        if not self._callbacks:
            raise EventError(f"{self.type.name!r} event fired before setting callbacks.")
        for _, callback in self._callbacks.items():
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(
                    "Event Error:",
                    f"{self.type.name} unable to run {callback.__name__} - {e.__class__.__name__}: {e!s}",
                    file=sys.stderr,
                )
