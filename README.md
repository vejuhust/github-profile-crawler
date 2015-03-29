# github profile crawler

distributed web crawler for *GitHub* user profile pages


## architecture

### message queuing

message queuing of *github profile crawler* is implemented with *MongoDB*, which provides `db.collection.findAndModify()` to modify and return a single document atomically.

all the database related operations are wrapped in **DatabaseAccessor.py**. there are three queues/collections used:

* **queue_crawl** - url of pages that should be downloaded
* **queue_page** - downloaded content and classification of the pages
* **profile** - extracted users' profile from the pages

### worker

### utility

### workflow


## usage

### configuration

### deployment

### number of workers

