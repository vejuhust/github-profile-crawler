#!/usr/bin/env python3
"""Configurations for github profile crawler"""

from time import strftime


config_db_addr  = "127.0.0.1"
config_db_port  = 27017
config_db_name  = "gitcrawl"
config_db_user  = "YOUR_USERNAME"
config_db_pass  = "YOUR_PASSWORD"

config_db_profile   = "profile"
config_queue_crawl  = "queue_crawl"
config_queue_page   = "queue_page"

config_log_file     =  "dev_{}.log".format(strftime("%Y-%m-%d"))

config_crawl_process    = 4
config_crawl_retry      = 3
config_crawl_sleep      = 5
config_crawl_timeout    = 5

config_parse_domain     = "https://github.com"
config_parse_process    = 4

config_report_interval  = 5
