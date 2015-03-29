# github profile crawler

[![Build Status](https://travis-ci.org/vejuhust/github-profile-crawler.svg?branch=master)](https://travis-ci.org/vejuhust/github-profile-crawler)
[![Codacy Badge](https://www.codacy.com/project/badge/7cf40af8475b45c5b95cfe1b69f49634)](https://www.codacy.com/app/vejuhust/github-profile-crawler)

distributed web crawler for *GitHub* user profile pages


## architecture

### message queuing

message queuing of *github profile crawler* is implemented with *MongoDB*, which provides `db.collection.findAndModify()` to modify and return a single document atomically.

all the operations on database are wrapped in **DatabaseAccessor.py**. there are three queues/collections in the system:

* **queue_crawl** - url of pages that should be downloaded
* **queue_page** - downloaded content and classification of the pages
* **profile** - parsed users' profile from the pages


### worker

there are four type of workers, and all of them can work independently on separate machines.

* crawler
    - take crawling jobs from **queue_crawl**
    - download the pages and store them in **queue_page**
* assigner
    - take newly downloaded pages from **queue_page**
    - classify and mark the pages in **queue_page**
* parser_follow
    - take following/follower pages from **queue_page**
    - parse url of profile pages and next following/follower pages from the pages
    - add all the parsed urls to **queue_crawl** as crawling jobs
* parser_profile
    - take profile pages from **queue_page**
    - parse users' profile from the pages
    - store the users' profile in **profile**


### utility

* watchdog
    - monitor and record the status of the database
    - draw charts based on recent status records
* reporter
    - host a web page to render database status charts
* exporter
    - dump all the profiles in json and csv formats
* launcher
    - verify if the system works with minimal targets 


### workflow

![figure of workflow](https://cloud.githubusercontent.com/assets/2491781/6884681/78b668c2-d62f-11e4-8a3f-731455edd08b.png)



## usage

### configuration

before you deploy, don't forget to change the database settings in **config.py**:

| property | default | note |
| :---- | :---- | :---- |
| config_db_addr | 127.0.0.1 | ip of the database host |
| config_db_port | 27017 | port of the database host  |
| config_db_name | gitcrawl | the database to authenticate |
| config_db_user | YOUR_USERNAME | the name of the user to authenticate |
| config_db_pass | YOUR_PASSWORD | the password of the user to authenticate |


### deployment

install the project's dependencies with:
```bash
pip3 install -r requirements.txt
```

and then you may verify if it works with `python3 Launcher.py` before you launch all the workers with *screen* or *tmux*:
```bash
python3 Crawler.py
python3 Assigner.py
python3 ParserFollow.py
python3 ParserProfile.py
```

also the utilities to monitor the progress:
```bash
python3 WatchDog.py
python3 Reporter.py
```

after it stopped, export the profiles:
```bash
python3 Exporter.py
```

### number of workers

