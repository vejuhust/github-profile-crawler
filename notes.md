# github-profile-crawler dev notes


## references

### github
* robots.txt: https://github.com/robots.txt
* profile pages:
    - normal: https://github.com/thankcreate
    - large: https://github.com/wong2
    - anti-spam email: https://github.com/xudifsd
    - no email: https://github.com/torvalds
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
* classifer
* worker_profile
* worker_follow

### queues
* queue_crawl
* queue_page

### database
github api response:
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

#### python driver
set up devenv for python3
```bash
sudo apt-get install python3-pip python3-dev python3-setuptools
```

install via pip
```bash
sudo pip3 install pymongo
```

