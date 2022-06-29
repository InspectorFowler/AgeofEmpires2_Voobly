# libraries
import os
import sys

from functools import reduce
import re

import logging
from typing import Optional, Dict
from colorama import Fore, Back, Style
log = logging.getLogger("aoe-logger")

# -----------------------------------------------------------------------------------------------------------

# Logging
class ColoredFormatter(logging.Formatter):
    """Colored log formatter."""

    def __init__(self, *args, colors: Optional[Dict[str, str]]=None, **kwargs) -> None:
        """Initialize the formatter with specified format strings."""

        super().__init__(*args, **kwargs)

        self.colors = colors if colors else {}

    def format(self, record) -> str:
        """Format the specified record as text."""

        record.color = self.colors.get(record.levelname, '')
        record.reset = Style.RESET_ALL

        return super().format(record)

class LoggingRegexFilter(logging.Filter):
    """
    Regex based log filter
    """

    def __init__(self, pattern):
        self._matcher = re.compile(pattern)

    def filter(self, record):
        return not bool(self._matcher.match(record.funcName))

formatter = ColoredFormatter(
    '{asctime} |{color} {levelname:8} {reset} | {message}',
    style='{', datefmt='%Y-%m-%d %H:%M:%S',
    colors={
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE + Style.BRIGHT
    }
)

# Create loggers
# -- console
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
# -- file
file_handler = logging.FileHandler('../../artifacts/run.log')
file_handler.setFormatter(formatter)

# Set up logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Add loggers
logger.handlers[:] = []
logger.addHandler(handler)
# logger.addHandler(file_handler) -- file handler may be turned on if needed