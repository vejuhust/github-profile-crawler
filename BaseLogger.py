#!/usr/bin/env python3
"""Basic logger to support other workers for github profile crawler"""

import sys
import logging
from contextlib import closing
from config import config_log_file


class BaseLogger():
    def __init__(self, level=logging.INFO):
        self._log_formatter = logging.Formatter("%(asctime)s [%(module)s][%(process)d][%(levelname)s] %(message)s")
        self._root_logger = logging.getLogger()
        self._root_logger.setLevel(level)
        self._root_logger.addHandler(self._file_handler())
        self._root_logger.addHandler(self._console_handler())


    def _file_handler(self):
        file_handler = logging.FileHandler(config_log_file)
        file_handler.setFormatter(self._log_formatter)
        return file_handler


    def _console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self._log_formatter)
        return console_handler


    def critical(self, message):
        self._root_logger.critical(message)


    def error(self, message):
        self._root_logger.error(message)


    def exception(self, message):
        self._root_logger.exception("Exception: {}".format(message))


    def warning(self, message):
        self._root_logger.warning(message)


    def info(self, message):
        self._root_logger.info(message)


    def debug(self, message):
        self._root_logger.debug(message)


class Example(BaseLogger):
    def __init__(self):
        BaseLogger.__init__(self, logging.DEBUG)


    def process(self):
        self.critical("hello critical")
        self.error("hello error")
        try:
            x = 5 / 0
        except Exception as e:
            self.exception("hello exception")
        self.warning("hello warning")
        self.info("hello info")
        self.debug("hello debug")


def main():
    ex = Example()
    ex.process()


if __name__ == '__main__':
    main()
