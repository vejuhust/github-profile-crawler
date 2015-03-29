# github profile crawler

distributed web crawler for *GitHub* user profile pages


## architecture

### message queuing

message queuing of *github profile crawler* is implemented with *MongoDB*, which provides `db.collection.findAndModify()` to modify and return a single document atomically.

all the database related operations are wrapped in **DatabaseAccessor.py**. there are three queues/collections used:

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

### workflow


## usage

### configuration

### deployment

### number of workers

