#!/usr/bin/env python3
"""Web crawler for github profile crawler"""

from Assigner import Assigner
from Crawler import Crawler
from ParserProfile import ParserProfile
from ParserFollow import ParserFollow
from DatabaseAccessor import DatabaseAccessor
from config import *
from contextlib import closing
from time import sleep


urls = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://www.baidu.com/",
    "https://github.com/wong2/followers?page=3",
    "https://github.com/wong2/followers?page=2",
    "https://github.com/wong2/followers?page=11",
    "https://github.com/wong2/followers",
    "https://github.com/wong2",
    "https://github.com/xudifsd",
    "https://github.com/torvalds",
    "https://github.com/thankcreate",
    # "https://github.com/Syndim/following",
    # "https://github.com/Syndim",
    # "https://github.com/SBeator",
    # "https://github.com/SublimeText",
    # "https://github.com/robots.txt",
    # "https://github.com/lmmsoft/following?page=3",
    # "https://github.com/lmmsoft/following?page=2",
    # "https://github.com/lmmsoft/following",
    # "https://github.com/Heatwave/followers",
    # "https://github.com/Heatwave",
    # "https://github.com/graphlab-code",
    # "https://github.com/facelessuser",
    # "https://github.com/bluesilence/following",
    # "https://github.com/bluesilence/followers",
]


class Launcher():
    def __init__(self):
        pass


    def process(self, urls):
        self.clear_queue_crawl_page_profile()
        self.add_urls_to_queue_crawl(urls)
        self.run_crawler(len(urls))
        self.run_assigner(len(urls))
        self.run_parser_profile(len(urls))
        self.run_parser_follow(len(urls))


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
                print("crawl - {}".format(crawler.process()))
                sleep(config_crawl_sleep)


    def run_assigner(self, times=5):
        with closing(Assigner()) as assigner:
            for _ in range(times):
                print("assign - {}".format(assigner.process()))


    def run_parser_profile(self, times=5):
        with closing(ParserProfile()) as parser:
            for _ in range(times):
                print("parse profile - {}".format(parser.process()))


    def run_parser_follow(self, times=5):
        with closing(ParserFollow()) as parser:
            for _ in range(times):
                print("parse follow - {}".format(parser.process()))


    def close(self):
        pass


def main():
    with closing(Launcher()) as launcher:
        launcher.process(urls)


if __name__ == '__main__':
    main()
