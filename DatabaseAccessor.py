#!/usr/bin/env python3
"""Database Accessor for github-profile-crawler
"""

from config import *
from pymongo import MongoClient
from contextlib import closing
from pprint import pprint as pp
from datetime import datetime


class DatabaseAccessor():
    """Database Accessor for connecting MongoDB"""
    def __init__(self):
        self._client = MongoClient(host=config_db_addr, port=config_db_port)
        self._db = self._client[config_db_name]
        if not self._db.authenticate(config_db_user, config_db_pass):
            raise RuntimeError("Failed to authenticate for {}@{}".format(config_db_user, config_db_addr))
        self._validate_queue()


    def _validate_queue(self):
        names = self._db.collection_names()
        queues = [config_queue_crawl, config_queue_page]
        for queue in queues:
            if queue not in names:
                self._db.create_collection(queue)


    def _job_create(self, queue_name, content):
        content['status'] = "new"
        content['date'] = datetime.utcnow()
        return None == self._db[queue_name].find_and_modify(
            query={ 'url': content['url'] },
            update={ '$setOnInsert': content },
            upsert=True)


    def _job_update(self, queue_name, status_old=None, status_new=None, url=None):
        query = {}
        if url != None:
            query['url'] = url
        if status_old != None:
            query['status'] = status_old
        return self._db[queue_name].find_and_modify(
            query=query,
            update={ '$set': { 'status': status_new } },
            sort={ 'date': 1 })


    def _job_take(self, queue_name):
        return self._job_update(queue_name, "new", "process")


    def _job_done(self, queue_name, url):
        return None != self._job_update(queue_name, "process", "done", url)


    def _job_fail(self, queue_name, url):
        return None != self._job_update(queue_name, "process", "fail", url)


    def queue_crawl_create(self, url):
        return self._job_create(config_queue_crawl, { 'url': url })


    def queue_crawl_take(self):
        return self._job_take(config_queue_crawl)


    def queue_crawl_done(self, url):
        return self._job_done(config_queue_crawl, url)


    def queue_crawl_fail(self, url):
        return self._job_fail(config_queue_crawl, url)


    def close(self):
        self._client.close()


def main():
    with closing(DatabaseAccessor()) as dal:
        pp(dal.queue_crawl_create("https://github.com/wong2"))
        pp(dal.queue_crawl_create("https://github.com/thankcreate"))
        pp(dal.queue_crawl_create("https://github.com/xudifsd"))
        pp(dal.queue_crawl_take())
        pp(dal.queue_crawl_done("https://github.com/wong2"))
        pp(dal.queue_crawl_done("https://github.com/thankcreate"))
        pp(dal.queue_crawl_fail("https://github.com/xudifsd"))


if __name__ == '__main__':
    main()
