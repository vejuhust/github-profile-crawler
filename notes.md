# github-profile-crawler dev notes


## references

### github
* robots.txt: https://github.com/robots.txt
* profile pages:
    - normal: https://github.com/thankcreate
    - large: https://github.com/wong2
    - anti-spam email: https://github.com/xudifsd
    - no email: https://github.com/torvalds
    - fewer info: https://github.com/facelessuser
    - non-follower: https://github.com/Heatwave
    - non-following: https://github.com/Syndim
* follow pages:
    - normal follower: https://github.com/bluesilence/followers
    - multi page follower: https://github.com/wong2/followers
        + page 2: https://github.com/wong2/followers?page=2
        + page 3: https://github.com/wong2/followers?page=3
        + last page: https://github.com/wong2/followers?page=11
    - normal following: https://github.com/bluesilence/following
    - multi page following: https://github.com/lmmsoft/following
        + page 2: https://github.com/lmmsoft/following?page=2
        + last page: https://github.com/lmmsoft/following?page=3
* org pages:
    - normal: https://github.com/graphlab-code
    - large: https://github.com/SublimeText



## design

### roles
* crawler
* assigner
* worker_profile
* worker_follow

### queues
* queue_crawl
* queue_page

### database/profile
reference - github api response:
```bash
curl -i https://api.github.com/users/wong2
```
* login
* name
* company
* location
* email
* blog
* created_at
* followers
* following
* starred


## mongodb

### setup
download: http://www.mongodb.org/downloads

#### install with package manager (failed on ubuntu 14.10)
```bash
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
```

#### install manually
```bash
mkdir -p ~/mongodb && cd ~/mongodb
curl -O https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1410-clang-3.0.0.tgz
tar -zxvf mongodb-linux-x86_64-ubuntu1410-clang-3.0.0.tgz
mkdir -p /opt/mongodb
cp -R -n mongodb-linux-x86_64-ubuntu1410-clang-3.0.0/* /opt/mongodb
echo 'export PATH=/opt/mongodb/bin:$PATH' >> ~/.bashrc
apt-get install libc++-dev
```

#### run manually
```bash
screen -S mdb
mkdir -p /data/mongodb
mongod --dbpath /data/mongodb
```

#### enable authentication
login via `mongo` to create the administrator and close localhost exception:
```javascript
use admin
db.createUser(
  {
    user: "root",
    pwd: "YOUR_PASSWORD",
    roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
  }
)
```

restart the `mongod` with auth required:
```bash
mongod --dbpath /data/mongodb --bind_ip=0.0.0.0 --auth
```

login as `root` with auth:
```bash
mongo --port 27017 -u root -p YOUR_PASSWORD --authenticationDatabase admin
```

#### python driver
set up devenv for python3
```bash
sudo apt-get install python3-pip python3-dev python3-setuptools
```

install via pip
```bash
sudo pip3 install pymongo
```


### explore

#### connect via mongodb shell
bash:
```bash
mongo
```

status:
```javascript
show dbs
show collections
show users
db.stats()
exit
```

#### create
```javascript
use gitcrawl

db.createCollection("queue_crawl")
db.queue_crawl.insert({ "status": "new", "url": "https://github.com/wong2", "date": new Date() })
db.queue_crawl.insert({ "status": "new", "url": "https://github.com/thankcreate", "date": new Date() })
db.queue_crawl.update(
    { "url": "https://github.com/xudifsd" }, 
    { $setOnInsert: { "url": "https://github.com/xudifsd", "status": "new", "date": new Date() } }, 
    { "upsert": true })
```

#### read
```javascript
db.queue_crawl.find().pretty()
db.queue_crawl.find({ "status": "new" }).pretty()
db.queue_crawl.find({ "url": "https://github.com/wong2" }).pretty()
db.queue_crawl.validate()
```

#### update
```javascript
db.queue_crawl.findAndModify({ query: { "status" : "new" }, sort: {"date": 1 },  update: {$set: { "status" : "process" }}})
```

#### delete
```javascript
db.queue_page.remove({})
db.queue_crawl.remove({})
db.queue_crawl.drop()

db.dropDatabase()
```

#### add user
```javascript
use gitcrawl
db.createUser(
  {
    user: "YOUR_USERNAME",
    pwd: "YOUR_PASSWORD",
    roles: [ { role: "dbOwner", db: "gitcrawl" } ]
  }
)
```

try to login with auth:
```bash
mongo --port 27017 -u YOUR_USERNAME -p YOUR_PASSWORD --authenticationDatabase gitcrawl
```


## implement

### python package
```bash
sudo pip3 install pymongo
sudo pip3 install requests
```



## deploy

### database

#### node
```
Welcome to Ubuntu 14.04.1 LTS (GNU/Linux 3.13.0-44-generic x86_64)
Linux suzvm-linux02 3.13.0-44-generic #73-Ubuntu SMP Tue Dec 16 00:22:43 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux
ssh root@stcaraa
172.26.100.57
```

#### setup
environment:
```bash
apt-get install --assume-yes --force-yes vim git screen unzip p7zip-full iftop vnstat fail2ban
apt-get install --assume-yes --force-yes gcc g++ build-essential python-dev python-pip python-setuptools python3-pip python3-dev python3-setuptools
curl -s https://raw.githubusercontent.com/vejuhust/config-box/master/linux/bash_aliases.sh > ~/.bash_aliases
```

install mongodb:
```bash
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list
apt-get update
apt-get install -y mongodb-org
```

create root in mongodb
```javascript
use admin
db.createUser(
  {
    user: "root",
    pwd: "1M4C3dBCHX2J8siW",
    roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
  }
)

db.updateUser("root", { pwd: "M4C3dBCX2J8siW" })
```

edit `/etc/mongod.conf` to enable **auth** and disable **bind_ip**, and restart the service:
```bash
service mongod restart
```

try to login with auth:
```bash
mongo -u root -p M4C3dBCX2J8siW --port 27017 --host 127.0.0.1 admin
```

create add user for **gitcrawl** database:
```javascript
use gitcrawl
db.createUser(
  {
    user: "vej",
    pwd: "dZb3ZJZawIQxdlwO",
    roles: [ { role: "dbOwner", db: "gitcrawl" } ]
  }
)
```

try to login remotely with auth:
```bash
mongo -u vej -p dZb3ZJZawIQxdlwO --port 27017 --host 172.26.100.57 gitcrawl
```


### crawler

#### nodes
node1:
```
Welcome to Ubuntu 14.04.2 LTS (GNU/Linux 3.13.0-46-generic x86_64)
Linux stcvm-linux11 3.13.0-46-generic #79-Ubuntu SMP Tue Mar 10 20:06:50 UTC 2015 x86_64 x86_64 x86_64 GNU/Linux
ssh root@szgeek
172.22.174.58
```

node2:
```
Linux szgeek-pi03 3.18.7+ #755 PREEMPT Thu Feb 12 17:14:31 GMT 2015 armv6l GNU/Linux
ssh root@szgeek-pi03
10.168.186.87
```

#### setup
```bash
apt-get install --assume-yes --force-yes gcc g++ build-essential python-dev python-pip python-setuptools python3-pip python3-dev python3-setuptools

# on node 1
pip3 install pymongo
pip3 install requests

# on node 2
pip-3.2 install pymongo
pip-3.2 install requests
```

#### source code
transit:
```bash
scp release1.zip root@szgeek-pi03:/tmp/
scp /tmp/release1.zip root@szgeek:~/crawl/
```

up and run:
```bash
mkdir ~/crawl && cd ~/crawl
unzip release1.zip && cd release1
python3 Crawler.py
```

#### on windows devbox
download
* python3: https://www.python.org/downloads/
* pycharm: https://www.jetbrains.com/pycharm/download/

install python3 and packages
```cmd
C:\Python34\python.exe  C:\Python34\Tools\Scripts\win_add2path.py
C:\Python34\Scripts\pip3.4.exe install pymongo
C:\Python34\Scripts\pip3.4.exe install requests
C:\Python34\Scripts\pip3.4.exe install beautifulsoup4
```

up and run
```cmd
cd D:\UserWei\Desktop\github-profile-crawler-master\release1
C:\Python34\python.exe Crawler.py
```

