#!/usr/bin/env python3
"""Usability verification tool for github profile crawler"""

from Assigner import Assigner
from Crawler import Crawler
from DatabaseAccessor import DatabaseAccessor
from ParserFollow import ParserFollow
from ParserProfile import ParserProfile
from config import *
from contextlib import closing
from pprint import pprint
from time import sleep


urls = [
    "https://www.bing.com/",
    "https://github.com/xudifsd",
    "https://github.com/wong2/followers?page=3",
    "https://github.com/wong2/followers?page=11",
    "https://github.com/wong2/followers",
    "https://github.com/wong2",
    "https://github.com/torvalds",
    "https://github.com/thankcreate",
    "https://github.com/lmmsoft/following",
    "https://github.com/graphlab-code",
    "https://github.com/facelessuser",
    "https://github.com/bluesilence/following",
    "https://github.com/bluesilence/followers",
    "https://github.com/Syndim/following",
    "https://github.com/Syndim",
    "https://github.com/SublimeText",
    "https://github.com/SBeator",
    "https://github.com/Heatwave/followers",
    "https://github.com/Heatwave",
]


class Launcher():
    def __init__(self):
        pass


    def process(self, urls):
        # self.clear_queue_crawl_page_profile()
        self.add_urls_to_queue_crawl(urls)
        self.run_crawler(len(urls) + 3)
        self.run_assigner(len(urls) + 3)
        self.run_parser_profile(len(urls) + 3)
        self.run_parser_follow(len(urls) + 3)
        self.read_all_profile()


    def add_urls_to_queue_crawl(self, urls):
        with closing(DatabaseAccessor()) as dal:
            for url in urls:
                print("add {} - {}".format(url, dal.queue_crawl_create(url)))


    def clear_queue_crawl_page_profile(self):
        with closing(DatabaseAccessor()) as dal:
            print("clear crawl - {}".format(dal.queue_crawl_clear()))
            print("clear page - {}".format(dal.queue_page_clear()))
            print("clear profile - {}".format(dal.profile_clear()))


    def run_crawler(self, times=5):
        with closing(Crawler()) as crawler:
            for _ in range(times):
                crawler.process()
                sleep(config_crawl_sleep)


    def run_assigner(self, times=5):
        with closing(Assigner()) as assigner:
            for _ in range(times):
                assigner.process()


    def run_parser_profile(self, times=5):
        with closing(ParserProfile()) as parser:
            for _ in range(times):
                parser.process()


    def run_parser_follow(self, times=5):
        with closing(ParserFollow()) as parser:
            for _ in range(times):
                parser.process()


    def read_all_profile(self):
        with closing(DatabaseAccessor()) as dal:
            pprint(dal.profile_read())


    def close(self):
        pass


def main():
    with closing(Launcher()) as launcher:
        launcher.process(urls)


if __name__ == '__main__':
    main()
