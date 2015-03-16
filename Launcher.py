#!/usr/bin/env python3
"""Web crawler for github profile crawler"""

from config import *
from contextlib import closing
from Assigner import Assigner
from Crawler import Crawler
from DatabaseAccessor import DatabaseAccessor
from time import sleep


urls = [
    "https://github.com/bluesilence/followers",
    "https://github.com/bluesilence/following",
    "https://github.com/facelessuser",
    "https://github.com/graphlab-code",
    "https://github.com/Heatwave",
    "https://github.com/Heatwave/followers",
    "https://github.com/lmmsoft/following",
    "https://github.com/lmmsoft/following?page=2",
    "https://github.com/lmmsoft/following?page=3",
    "https://github.com/robots.txt",
    "https://github.com/SublimeText",
    "https://github.com/Syndim",
    "https://github.com/Syndim/following",
    "https://github.com/thankcreate",
    "https://github.com/torvalds",
    "https://github.com/wong2",
    "https://github.com/wong2/followers",
    "https://github.com/wong2/followers?page=11",
    "https://github.com/wong2/followers?page=2",
    "https://github.com/wong2/followers?page=3",
    "https://github.com/xudifsd",
    "https://www.google.com/",
    "https://www.baidu.com/",
    "https://www.bing.com/",
]


def add_urls_to_queue_crawl():
    with closing(DatabaseAccessor()) as dal:
        for url in urls:
            print("add {} - {}".format(url, dal.queue_crawl_create(url)))


def clear_queue_crawl_and_page():
    with closing(DatabaseAccessor()) as dal:
        print("clear crawl - {}".format(dal.queue_crawl_clear()))
        print("clear page - {}".format(dal.queue_page_clear()))


def run_crawler(times=5):
    with closing(Crawler()) as crawler:
        for _ in range(times):
            print("crawl - {}".format(crawler.process()))
            sleep(config_crawl_sleep)


def run_assigner(times=5):
    with closing(Assigner()) as assigner:
        for _ in range(times):
            print("assign - {}".format(assigner.process()))


def main():
    clear_queue_crawl_and_page()
    add_urls_to_queue_crawl()
    run_crawler(len(urls))
    run_assigner(len(urls))


if __name__ == '__main__':
    main()
