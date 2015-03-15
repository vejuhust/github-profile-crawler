#!/usr/bin/env python3
"""Database Accessor for github-profile-crawler
"""

from config import *
from pymongo import MongoClient
from contextlib import closing

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


    def close(self):
        self._client.close()


def main():
    with closing(DatabaseAccessor()) as dal:
        pass


if __name__ == '__main__':
    main()
