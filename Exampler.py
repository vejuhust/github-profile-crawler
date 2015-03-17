#!/usr/bin/env python3
"""Example for logger for github profile crawler"""

from BaseLogger import BaseLogger


class Exampler(BaseLogger):
    def __init__(self):
        BaseLogger.__init__(self, self.__class__.__name__)


    def process(self):
        self._log_critical("hello critical %s", "yes!")
        self._log_error("hello error")
        try:
            x = 5 / 0
        except Exception as e:
            self._log_exception("hello exception %s", "oops!")
        self._log_warning("hello warning")
        self._log_info("hello info - hao%d", 123)
        self._log_debug("hello debug")


def main():
    ex = Exampler()
    ex.process()


if __name__ == '__main__':
    main()
