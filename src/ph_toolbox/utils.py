import logging
import re
import sys
from logging.handlers import TimedRotatingFileHandler
from typing import Dict, Optional

from .config import config

# List of already registered loggers
LOGGERS: Dict[str, logging.Logger] = {}


def format_headers(title: str, ch: str = "=", align: str = "^", width: int = 120) -> str:
    return "{:{ch}{align}{width}s}".format(f" {title} ", ch=ch, align=align, width=width)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    global LOGGERS

    if name is None:
        name = config("dir_module").stem

    if name in LOGGERS:
        return LOGGERS[name]

    logger = logging.getLogger(name)
    log_level_name = logging.getLevelName(config("log_level"))
    logger.setLevel(log_level_name)

    handler_stream = logging.StreamHandler(sys.stdout)
    handler_stream.setLevel(log_level_name)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s")
    handler_file_rotating_error = TimedRotatingFileHandler(filename="logs/errors", when="D", interval=1, backupCount=5)
    handler_file_rotating_error.suffix = "%Y-%m-%d.log"
    handler_file_rotating_error.setLevel(logging.WARNING)
    handler_file_rotating_error.setFormatter(formatter)

    logger.addHandler(handler_stream)
    logger.addHandler(handler_file_rotating_error)
    logger.propagate = False

    LOGGERS[name] = logger

    return logger


def slugify(s):
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    s = re.sub(r"^-+|-+$", "", s)
    return s
