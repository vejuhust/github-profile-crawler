#!/usr/bin/env python3
"""Assign parsing page jobs in queue_page for github profile crawler"""

from BaseLogger import BaseLogger
from DatabaseAccessor import DatabaseAccessor
from bs4 import BeautifulSoup
from config import config_parse_process
from contextlib import closing
from multiprocessing import Process
from platform import node


class Assigner(BaseLogger):
    def __init__(self, log_level=None):
        BaseLogger.__init__(self, self.__class__.__name__, log_level)
        self._db_conn = DatabaseAccessor()
        self._log_info("assigner start @%s", node())


    def process(self):
        url = None
        flag = None
        job = self._db_conn.queue_page_take()
        if job != None:
            url = job['url']
            text = job.get('text', "")
            flag = self._classify(url, text)
            self._log_info("%s is classified as '%s'", url, flag)
            if not self._db_conn.queue_page_done(url, flag):
                self._log_warning("fail to mark %s as '%s' in queue_page", url, flag)
        else:
            self._log_warning("grab no jobs to assign")
        return url, flag


    def _classify(self, url, text):
        soup = BeautifulSoup(text)
        flag = "unknown"
        if soup.find_all(class_="vcard-names"):
            flag ="profile"
        elif soup.find_all(class_="org-name"):
            flag = "org"
        elif soup.find_all(class_="follow-list"):
            flag = "follow"
        elif soup.find_all(class_="blankslate"):
            flag = "alone"
        return flag


    def close(self):
        self._db_conn.close()
        self._log_info("assigner exit")
        self._close_logger()


def main(times=10):
    with closing(Assigner()) as assigner:
        for _ in range(times):
            assigner.process()


if __name__ == '__main__':
    for _ in range(config_parse_process):
        Process(target=main, args=(20,)).start()
