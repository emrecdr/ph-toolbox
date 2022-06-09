import pathlib
import sys

from pytest import fixture, mark, param, raises

from src.ph_toolbox import constants as c
from src.ph_toolbox.config import Config, ConfigError, config


@fixture(autouse=True)
def run_around_tests():
    yield
    Config.delete()


@fixture
def initial_conf():
    path_base = pathlib.Path.cwd()
    return {
        c.CONFIG_SESS_NAME: "",
        c.CONFIG_DEBUG: False,
        c.CONFIG_LOG_LEVEL: "INFO",
        c.CONFIG_DIR_BASE: path_base,
        c.CONFIG_DIR_SRC: path_base / "src",
        c.CONFIG_DIR_MODULE: path_base / "src" / "ph_toolbox",
    }


@mark.parametrize(
    "cli_args,expected_updates",
    [
        param([], {}, id="inital"),
        param(["--debug"], {c.CONFIG_DEBUG: True, c.CONFIG_LOG_LEVEL: "DEBUG"}, id="debugging_only"),
        param(
            ["--debug", "--log-level", "WARNING"],
            {c.CONFIG_DEBUG: True, c.CONFIG_LOG_LEVEL: "WARNING"},
            id="debugging_with_warning_level",
        ),
        param(
            ["--debug", "--log-level", "WARNING", "--"],
            {c.CONFIG_DEBUG: True, c.CONFIG_LOG_LEVEL: "WARNING"},
            id="debugging_with_warning_level",
        ),
    ],
)
def test_cli_args_config(monkeypatch, initial_conf, cli_args, expected_updates):
    with monkeypatch.context() as mpctx:
        mpctx.setattr(sys, "argv", ["config.py", *cli_args])
        expected = {**initial_conf, **expected_updates}
        actual = Config.all()
        assert actual == expected

        for key, value in expected_updates.items():
            assert config(key) == value
            assert Config.get_config(key) == value


def test_getting_non_existing_value():
    actual = config("param_not_exists")
    assert actual is None

    actual = Config.get_config("param_not_exists")
    assert actual is None

    actual = config("param_not_exists", default_val=True)
    assert actual is True

    actual = Config.get_config("param_not_exists", default_val="testing")
    assert actual == "testing"

    with raises(ConfigError):
        config("param_not_exists", required=True)


def test_setting_new_value():
    actual = config("new_param")
    assert actual is None

    Config._initialize()

    Config.set_config("new_param", "testing")
    actual = config("new_param")
    assert actual == "testing"


def test_formatter():
    Config.set_config("new_param", "100")
    actual = Config.get_required_config("new_param")
    assert actual == "100"

    actual = config("new_param", required=True, formatter=int)
    assert actual == 100


def test_tagging():
    Config.set_config("new_param_1", "val_1")
    Config.set_config("new_param_2", "val_2")
    Config.set_config("new_param_3", "val_3")
    Config.set_config("new_param_4", "val_4")
    Config.set_config("new_param_5", "val_5")
    Config.set_config("new_param_6", "val_6")
    Config.set_tag("1_3", ["new_param_1", "new_param_2"])
    Config.set_tag("4_6", ["new_param_4", "new_param_5", "new_param_6"])

    actual = Config.get_tag("1_3")
    assert actual == {"new_param_1": "val_1", "new_param_2": "val_2"}

    actual = Config.get_tag("4_6")
    assert actual == {"new_param_4": "val_4", "new_param_5": "val_5", "new_param_6": "val_6"}

    Config.extend_tag("1_3", ["new_param_3"])
    actual = Config.get_tag("1_3")
    assert actual == {"new_param_1": "val_1", "new_param_2": "val_2", "new_param_3": "val_3"}

    with raises(ConfigError):
        Config.extend_tag("1_3", ["new_param_1000"])


def test_non_existing_tag():
    with raises(ConfigError):
        Config.get_tag("tag_not_exists")

    with raises(ConfigError):
        Config.extend_tag("tag_not_exists", ["new_param_1000"])
