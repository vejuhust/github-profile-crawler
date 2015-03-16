#!/usr/bin/env python3
"""Assign parsing page jobs in queue_page for github profile crawler"""

from contextlib import closing
from bs4 import BeautifulSoup
from DatabaseAccessor import DatabaseAccessor


class Assigner():
    def __init__(self):
        self._db_conn = DatabaseAccessor()


    def process(self):
        url = None
        flag = None
        job = self._db_conn.queue_page_take()
        if job != None:
            url = job['url']
            text = job.get('text', "")
            flag = self._classify(url, text)
            self._db_conn.queue_page_done(url, flag)
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


def main():
    pass


if __name__ == '__main__':
    main()
