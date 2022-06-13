import functools
import sys
import time
import traceback
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional


class RetryOnErrorEventType(Enum):
    ERROR_RESOLVED = "Error resolved"
    RECOVERABLE_ERROR = "Recoverable error"
    FATAL_ERROR = "Fatal error"

    def __str__(self):
        return self.value


# #######################################################################################


@dataclass(init=True, repr=True, eq=False, order=False, unsafe_hash=False, frozen=False)
class RetryOnErrorEventHandlerArgs:
    type: RetryOnErrorEventType
    n_try: int
    class_name: str
    func_name: str
    msg: str
    func_args: Optional[Any] = None
    exception_name: Optional[str] = None
    error_data: Optional[Any] = None

    def __str__(self):
        return self.msg


# #######################################################################################


@dataclass(init=True, repr=False, eq=False, order=False, unsafe_hash=False, frozen=False)
class RetryOnErrorArgs:
    n_max_try: int = 6
    delay: float = 0.14
    on_error: Optional[Callable] = field(default=None)
    on_error_resolved: Optional[Callable] = field(default=None)
    on_fatal_error: Optional[Callable] = print

    def __post_init__(self):
        if self.on_error is not None and not callable(self.on_error):
            self.on_error = print

        if self.on_error_resolved is not None and not callable(self.on_error_resolved):
            self.on_error_resolved = print

        if self.on_fatal_error is not None and not callable(self.on_fatal_error):
            self.on_fatal_error = print

    # on_error: Callable
    # _on_error: Callable = field(init=False, repr=False, default=print)
    #
    # @property
    # def on_error(self) -> Callable:
    #     return self._on_error
    #
    # @on_error.setter
    # def on_error(self, on_error: Callable):
    #     if on_error is not None and not callable(on_error):
    #         self.on_error = print
    #     self._on_error = on_error


# #######################################################################################


class RetryOnError:
    def __init__(self, args: RetryOnErrorArgs):
        self._args: RetryOnErrorArgs = args
        self._root_dir: Optional[Path] = None

    def __call__(self, fn):
        def wrapper(instance, *args, **kwargs):
            if "retry_on_error" in kwargs and isinstance(kwargs["retry_on_error"], RetryOnErrorArgs):
                self._args = kwargs.pop("retry_on_error", None)
            n_try = 0
            keep_trying = True
            while keep_trying:
                n_try += 1
                try:
                    resp = fn(instance, *args, **kwargs)
                    self.error_resolved_handler(n_try, instance.__class__.__name__, fn.__name__)
                    return resp
                except Exception as exc:
                    keep_trying = n_try < self._args.n_max_try
                    self.error_handler(exc, n_try, keep_trying, args, kwargs, instance.__class__.__name__, fn.__name__)
                    if keep_trying:
                        # recoverable error
                        self.delay_process(n_try)

        functools.update_wrapper(wrapper, fn)
        return wrapper

    @property
    def root_dir(self):
        if self._root_dir is None:
            self._root_dir = str(Path(__file__).resolve().parent.parent)
        return self._root_dir

    def delay_process(self, n_try: int = 1):
        wait_time = pow(2, n_try) * self._args.delay
        time.sleep(wait_time)

    def clean_dir(self, err_dir: str):
        return err_dir.replace(self.root_dir, "")

    def get_last_err_data(self):
        exception_type, exception_obj, exception_traceback = sys.exc_info()
        if exception_traceback is None:
            return [None]
        return [
            self.clean_dir(tb.replace("\n", ",").rstrip(",").strip())
            for tb in traceback.format_tb(exception_traceback, -6)
        ][::-1]

    def error_handler(
        self, exc: Exception, n_try: int, is_recoverable: bool, args, kwargs, cls_name: str, fn_name: str
    ):
        if is_recoverable and self._args.on_error is None:
            return

        if not is_recoverable and self._args.on_fatal_error is None:
            return

        error_type = RetryOnErrorEventType.RECOVERABLE_ERROR if is_recoverable else RetryOnErrorEventType.FATAL_ERROR

        params = RetryOnErrorEventHandlerArgs(
            type=error_type,
            n_try=n_try,
            class_name=cls_name,
            func_name=fn_name,
            msg=f"{error_type} (#{n_try} @ {cls_name}.{fn_name}) {exc.__class__.__name__}: {exc!s}",
            exception_name=exc.__class__.__name__,
            error_data=self.get_last_err_data(),
        )

        if is_recoverable and self._args.on_error is not None:
            self._args.on_error(params)

        if not is_recoverable and self._args.on_fatal_error is not None:
            args_ = [str(a) for a in args]
            kwargs_ = ["{0}={1}".format(k, v) for (k, v) in kwargs.items()]
            fn_params = args_ + kwargs_
            str_args = ", ".join(fn_params)
            params.func_args = str_args
            self._args.on_fatal_error(params)

    def error_resolved_handler(self, n_try: int, cls_name: str, fn_name: str):
        if n_try <= 1 or self._args.on_error_resolved is None:
            return

        # recovered/resolved error
        self._args.on_error_resolved(
            RetryOnErrorEventHandlerArgs(
                type=RetryOnErrorEventType.ERROR_RESOLVED,
                n_try=n_try,
                class_name=cls_name,
                func_name=fn_name,
                msg=f"Error resolved (#{n_try} @ {cls_name}.{fn_name})",
            )
        )
