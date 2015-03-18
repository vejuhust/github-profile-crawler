#!/usr/bin/env python3
"""Basic logger to support other workers for github profile crawler"""

from sys import stdout
from logging import INFO, DEBUG, Formatter, getLogger, FileHandler, StreamHandler, shutdown
from config import config_log_file


class BaseLogger():
    def __init__(self, caller_name="%(module)s", level=None):
        if level == None:
            level = INFO
        log_formatter = Formatter("[%(asctime)s.%(msecs)-3.3d][{}][%(process)d][%(levelname)s] %(message)s".format(caller_name), datefmt="%Y-%m-%d,%H:%M:%S")
        self._root_logger = getLogger(caller_name)
        self._root_logger.setLevel(level)
        self._root_logger.addHandler(self._file_handler(log_formatter))
        self._root_logger.addHandler(self._console_handler(log_formatter))


    def _file_handler(self, log_formatter):
        file_handler = FileHandler(config_log_file)
        file_handler.setFormatter(log_formatter)
        return file_handler


    def _console_handler(self, log_formatter):
        console_handler = StreamHandler(stdout)
        console_handler.setFormatter(log_formatter)
        return console_handler


    def _log_critical(self, msg, *args, **kwargs):
        self._root_logger.critical(msg, *args, **kwargs)


    def _log_error(self, msg, *args, **kwargs):
        self._root_logger.error(msg, *args, **kwargs)


    def _log_exception(self, msg, *args, **kwargs):
        self._root_logger.exception("Exception: {}".format(msg, *args, **kwargs))


    def _log_warning(self, msg, *args, **kwargs):
        self._root_logger.warning(msg, *args, **kwargs)


    def _log_info(self, msg, *args, **kwargs):
        self._root_logger.info(msg, *args, **kwargs)


    def _log_debug(self, msg, *args, **kwargs):
        self._root_logger.debug(msg, *args, **kwargs)


    def _close_logger(self):
        shutdown()


def main():
    pass


if __name__ == '__main__':
    main()
