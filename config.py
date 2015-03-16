#!/usr/bin/env python3
"""Configurations for github profile crawler"""

config_db_addr  = "127.0.0.1"
config_db_port  = 27017
config_db_name  = "gitcrawl"
config_db_user  = "YOUR_USERNAME"
config_db_pass  = "YOUR_PASSWORD"

config_db_profile   = "profile"
config_queue_crawl  = "queue_crawl"
config_queue_page   = "queue_page"

config_crawl_retry  = 3
config_crawl_sleep  = 10
