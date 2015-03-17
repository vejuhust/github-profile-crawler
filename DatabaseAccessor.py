#!/usr/bin/env python3
"""Database Accessor for github profile crawler"""

from config import *
from pymongo import MongoClient
from contextlib import closing
from datetime import datetime


class DatabaseAccessor():
    """Database Accessor for connecting MongoDB"""
    def __init__(self):
        self._client = MongoClient(host=config_db_addr, port=config_db_port)
        self._db = self._client[config_db_name]
        if not self._db.authenticate(config_db_user, config_db_pass):
            raise RuntimeError("Failed to authenticate for {}@{}".format(config_db_user, config_db_addr))
        self._validate_collections()


    def _validate_collections(self):
        names = self._db.collection_names()
        collections = [config_db_profile, config_queue_crawl, config_queue_page]
        for collection in collections:
            if collection not in names:
                self._db.create_collection(collection)


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
        else:
            query['url'] = { '$exists': True, '$ne': None }
        if status_old != None:
            query['status'] = status_old
        return self._db[queue_name].find_and_modify(
            query=query,
            update={ '$set': { 'status': status_new } },
            sort={ 'date': 1 })


    def _job_delete(self, queue_name, filter={}):
        return self._db[queue_name].remove(filter).get('ok', 0) == 1


    def queue_crawl_create(self, url):
        return self._job_create(config_queue_crawl, { 'url': url })


    def queue_crawl_take(self):
        return self._job_update(config_queue_crawl, "new", "process")


    def queue_crawl_done(self, url):
        return None != self._job_update(config_queue_crawl, "process", "done", url)


    def queue_crawl_fail(self, url):
        return None != self._job_update(config_queue_crawl, "process", "fail", url)


    def queue_crawl_renew(self, url):
        return None != self._job_update(config_queue_crawl, None, "new", url)


    def queue_crawl_clear(self):
        return self._job_delete(config_queue_crawl)


    def queue_page_create(self, url, text):
        return self._job_create(config_queue_page, { 'url': url, 'text': text })


    def queue_page_take(self):
        return self._job_update(config_queue_page, "new", "process")


    def queue_page_take_profile(self):
        return self._job_update(config_queue_page, "profile", "parse")


    def queue_page_take_follow(self):
        return self._job_update(config_queue_page, "follow", "parse")


    def queue_page_done(self, url, flag):
        return None != self._job_update(config_queue_page, "process", flag, url)


    def queue_page_fail(self, url):
        return None != self._job_update(config_queue_page, "process", "fail", url)


    def queue_page_renew(self, url):
        return None != self._job_update(config_queue_page, None, "new", url)


    def queue_page_clear(self):
        return self._job_delete(config_queue_page)


    def close(self):
        self._client.close()


def main():
    pass


if __name__ == '__main__':
    main()
