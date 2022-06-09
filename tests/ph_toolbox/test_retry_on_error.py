import io
from contextlib import redirect_stdout

import pytest

from src.ph_toolbox.retry_on_error import RetryOnError, RetryOnErrorArgs


class DemoAppError(Exception):
    pass


class MockLogger:
    def __init__(self):
        self.logs = {}
        self.reset()

    def reset(self):
        self.logs = {
            "info": [],
            "success": [],
            "error": [],
            "fatal": [],
        }

    def log(self, level: str, msg: str):
        # print(f"{level} log: {msg}")
        self.logs[level].append(msg)

    def info(self, msg):
        self.log("info", msg)

    def success(self, msg):
        self.log("success", msg)

    def error(self, msg):
        self.log("error", msg)

    def fatal(self, msg):
        self.log("fatal", msg)


roe_logger = MockLogger()
roe_params1 = RetryOnErrorArgs(n_max_try=5,
                               delay=0.01,
                               on_error=roe_logger.error,
                               on_error_resolved=roe_logger.info,
                               on_fatal_error=roe_logger.fatal)

roe_params2 = RetryOnErrorArgs(n_max_try=3,
                               delay=0.01,
                               on_fatal_error=roe_logger.fatal)


roe_params3 = RetryOnErrorArgs(n_max_try=5,
                               delay=0.01,
                               on_error=True,
                               on_error_resolved=True,
                               on_fatal_error=True)


class DemoApp1:
    def __init__(self):
        self.n_fail = None
        self.logger = MockLogger()

    def check_val(self, val):
        return bool(val)

    @RetryOnError(roe_params1)
    def action_fail_n_times(self, x1, x2):
        """This is the documentation of action_fail_n_times"""
        self.logger.info("Starting action_fail_n_times")

        if self.n_fail > 0:
            self.n_fail -= 1
            self.logger.error(f"Failed action_fail_n_times ({self.n_fail})")
            raise DemoAppError("Sorry, try again.")

        self.logger.success("Success action_fail_n_times")
        return "Executed: action_fail_n_times"

    @RetryOnError(roe_params3)
    def action_fail_n_times_2(self, x1, x2):
        """This is the documentation of action_fail_n_times_2"""
        self.logger.info("Starting action_fail_n_times_2")

        if self.n_fail > 0:
            self.n_fail -= 1
            self.logger.error(f"Failed action_fail_n_times_2 ({self.n_fail})")
            raise DemoAppError("Sorry, try again.")

        self.logger.success("Success action_fail_n_times_2")
        return "Executed: action_fail_n_times_2"

    @RetryOnError(roe_params1)
    def action_pass_if_param_is_ok(self, is_ok, x1, x2):
        """This is the documentation of action_pass_if_param_is_ok"""
        self.logger.info("Starting action_pass_if_param_is_ok")
        if not self.check_val(is_ok):
            self.logger.error("Failed action_pass_if_param_is_ok")
            raise DemoAppError("Sorry, try again.")

        self.logger.success("Success action_pass_if_param_is_ok")
        return "Executed: action_pass_if_param_is_ok"

    @RetryOnError(roe_params2)
    def action_pass_if_param_is_ok_2(self, is_ok, x1, x2):
        """This is the documentation of action_pass_if_param_is_ok"""
        self.logger.info("Starting action_pass_if_param_is_ok_2")
        if not self.check_val(is_ok):
            self.logger.error("Failed action_pass_if_param_is_ok_2")
            raise DemoAppError("Sorry, try again.")

        self.logger.success("Success action_pass_if_param_is_ok_2")
        return "Executed: action_pass_if_param_is_ok_2"

    @RetryOnError(roe_params3)
    def action_pass_if_param_is_ok_3(self, is_ok, x1, x2):
        """This is the documentation of action_pass_if_param_is_ok"""
        self.logger.info("Starting action_pass_if_param_is_ok_3")
        if not self.check_val(is_ok):
            self.logger.error("Failed action_pass_if_param_is_ok_3")
            raise DemoAppError("Sorry, try again.")

        self.logger.success("Success action_pass_if_param_is_ok_3")
        return "Executed: action_pass_if_param_is_ok_3"



# #########################################################


@pytest.fixture
def app() -> DemoApp1:
    roe_logger.reset()
    return DemoApp1()


def test_success(app: DemoApp1):
    resp = app.action_pass_if_param_is_ok(True, "param1", x2="param2")

    assert len(roe_logger.logs["info"]) == 0
    assert len(roe_logger.logs["success"]) == 0
    assert len(roe_logger.logs["error"]) == 0
    assert len(roe_logger.logs["fatal"]) == 0

    assert len(app.logger.logs["info"]) == 1
    assert len(app.logger.logs["success"]) == 1
    assert len(app.logger.logs["error"]) == 0
    assert len(app.logger.logs["fatal"]) == 0

    assert resp == "Executed: action_pass_if_param_is_ok"


def test_failing(app: DemoApp1):
    app.n_fail = 10
    resp = app.action_fail_n_times("param1", x2="param2")

    assert len(roe_logger.logs["info"]) == 0
    assert len(roe_logger.logs["success"]) == 0
    assert len(roe_logger.logs["error"]) == 4
    assert len(roe_logger.logs["fatal"]) == 1

    assert len(app.logger.logs["info"]) == 5
    assert len(app.logger.logs["success"]) == 0
    assert len(app.logger.logs["error"]) == 5
    assert len(app.logger.logs["fatal"]) == 0

    assert resp is None


def test_fail_3_times_then_success(app: DemoApp1):
    app.n_fail = 3
    resp = app.action_fail_n_times("param1", x2="param2")

    assert len(roe_logger.logs["info"]) == 1
    assert len(roe_logger.logs["success"]) == 0
    assert len(roe_logger.logs["error"]) == 3
    assert len(roe_logger.logs["fatal"]) == 0

    assert len(app.logger.logs["info"]) == 4
    assert len(app.logger.logs["success"]) == 1
    assert len(app.logger.logs["error"]) == 3
    assert len(app.logger.logs["fatal"]) == 0
    assert resp == "Executed: action_fail_n_times"

    out = io.StringIO()
    with redirect_stdout(out):
        help(app.action_fail_n_times)

    output = [str_out.strip() for str_out in (out.getvalue()).splitlines() if str_out != ""]
    assert output[-1] == "This is the documentation of action_fail_n_times"


def test_failing_with_roe_params2(app: DemoApp1):
    resp = app.action_pass_if_param_is_ok_2(False, "param1", x2="param2")

    assert len(roe_logger.logs["info"]) == 0
    assert len(roe_logger.logs["success"]) == 0
    assert len(roe_logger.logs["error"]) == 0
    assert len(roe_logger.logs["fatal"]) == 1

    assert len(app.logger.logs["info"]) == 3
    assert len(app.logger.logs["success"]) == 0
    assert len(app.logger.logs["error"]) == 3
    assert len(app.logger.logs["fatal"]) == 0

    assert resp is None


def test_fail_3_times_then_success_with_incorrect_logger(app: DemoApp1):
    app.n_fail = 3
    out = io.StringIO()
    with redirect_stdout(out):
        resp = app.action_fail_n_times_2("param1", x2="param2")

    output = [str_out.strip() for str_out in (out.getvalue()).splitlines() if str_out != ""]
    assert output == [
        "Recoverable error (#1 @ DemoApp1.action_fail_n_times_2) DemoAppError: Sorry, try again.",
        "Recoverable error (#2 @ DemoApp1.action_fail_n_times_2) DemoAppError: Sorry, try again.",
        "Recoverable error (#3 @ DemoApp1.action_fail_n_times_2) DemoAppError: Sorry, try again.",
        "Error resolved (#4 @ DemoApp1.action_fail_n_times_2)"
    ]

    assert len(roe_logger.logs["info"]) == 0
    assert len(roe_logger.logs["success"]) == 0
    assert len(roe_logger.logs["error"]) == 0
    assert len(roe_logger.logs["fatal"]) == 0

    assert len(app.logger.logs["info"]) == 4
    assert len(app.logger.logs["success"]) == 1
    assert len(app.logger.logs["error"]) == 3
    assert len(app.logger.logs["fatal"]) == 0
