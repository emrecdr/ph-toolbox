from __future__ import annotations

import argparse
import os
import pathlib
from typing import Any, Callable, Dict, List, Optional, Tuple

from . import constants as c


class ConfigError(Exception):
    pass


# #############################################################################


class Config:
    _INITIALIZED: bool = False
    _CONFIG: Dict[str, Any] = {}
    _TAGS: dict = {}
    _CLI_PARAMS: dict = {"desc": "App description", "args": []}

    @classmethod
    def _get_cli_args(cls):
        """Parse & return command line args"""

        # Create the parser
        parser = argparse.ArgumentParser(
            description=cls._CLI_PARAMS["desc"],
            allow_abbrev=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        # Add the arguments
        parser.add_argument("-d", "--debug", help="Enables debugging mode", action="store_true", required=False)

        parser.add_argument(
            "-ll",
            "--log-level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Logging Level",
            default="INFO",
            required=False,
        )

        for arg in cls._CLI_PARAMS["args"]:
            parser.add_argument(*arg[0], **arg[1])

        cli_args, _ = parser.parse_known_args()
        return cli_args

    @classmethod
    def _initialize(cls):
        if cls._INITIALIZED:
            return
        # Read cli args
        cli_args = vars(cls._get_cli_args())

        dir_module = pathlib.Path(__file__).resolve().parent
        dir_src = dir_module.parent
        dir_base = dir_src.parent

        # Pre-defined, static args
        static_args = {"sess_name": ""}

        # Merge args into 1 config
        cls._CONFIG = static_args | cli_args

        # Turn string directories into path objs
        for key, val in cls._CONFIG.items():
            if not key.startswith("dir_") or val is None or val == "":
                continue

            val = val.replace("\\", os.path.sep)
            val = pathlib.Path(val) if val.startswith(os.path.sep) else dir_base / val

            if not val.exists():
                raise ConfigError(f"Unable to find given {key!r} directory {val!s}.")
            cls._CONFIG[key] = val

        # If debug is set, then debug
        if cls._CONFIG.get(c.CONFIG_DEBUG, False) and cls._CONFIG.get(c.CONFIG_LOG_LEVEL, "INFO") == "INFO":
            cls._CONFIG["log_level"] = "DEBUG"

        # Add base paths
        cls._CONFIG["dir_module"] = dir_module
        cls._CONFIG["dir_src"] = dir_src
        cls._CONFIG["dir_base"] = dir_base

        # Config is ready to use
        cls._INITIALIZED = True

    @classmethod
    def delete(cls) -> None:
        cls._INITIALIZED = False
        cls._CONFIG = {}
        cls._TAGS = {}

    @classmethod
    def all(cls) -> Dict[str, Any]:
        if not cls._INITIALIZED:
            cls._initialize()
        return cls._CONFIG

    @classmethod
    def get_config(
        cls, key: str, default_val=None, required: bool = False, formatter: Optional[Callable] = None
    ) -> Any:
        if not cls._INITIALIZED:
            cls._initialize()

        if required and (not cls._CONFIG or key not in cls._CONFIG):
            raise ConfigError(f"Unable to get config `{key}`. Please set the config variable before use.")

        val = cls._CONFIG.get(key, default_val)

        return val if formatter is None else formatter(val)

    @classmethod
    def get_required_config(cls, key: str) -> Any:
        return cls.get_config(key=key, required=True)

    @classmethod
    def set_config(cls, key: str, val: Any, ignore_if_exists: bool = False) -> None:
        if not cls._INITIALIZED:
            cls._initialize()

        if key in cls._CONFIG and ignore_if_exists:
            return

        cls._CONFIG[key] = val

    @classmethod
    def set_configs(cls, *key_value_pairs: Tuple | List, ignore_if_exists: bool = False) -> None:
        if not cls._INITIALIZED:
            cls._initialize()

        for key, val in key_value_pairs:
            if key in cls._CONFIG and ignore_if_exists:
                continue

            cls._CONFIG[key] = val

    @classmethod
    def set_tag(cls, tag_key: str, config_keys: list, is_new: bool = True) -> None:
        if not cls._INITIALIZED:
            cls._initialize()

        if is_new:
            cls._TAGS[tag_key] = []
        elif tag_key not in cls._TAGS:
            raise ConfigError(f"Please set the `{tag_key}` tag before use.")

        for key in config_keys:
            if key not in cls._CONFIG:
                raise ConfigError(f"Please set the `{key}` config variable before use.")
            cls._TAGS[tag_key].append(key)

    @classmethod
    def extend_tag(cls, tag_key: str, config_keys: list):
        cls.set_tag(tag_key, config_keys, is_new=False)

    @classmethod
    def get_tag(cls, key: str) -> Dict[str, Any]:
        if key not in cls._TAGS:
            raise ConfigError(f"Please set the `{key}` tag before use.")
        return {key: cls._CONFIG[key] for key in cls._TAGS[key]}


# #############################################################################


def config(key: str, default_val=None, required: bool = False, formatter: Optional[Callable] = None):
    return Config.get_config(key, default_val=default_val, required=required, formatter=formatter)
