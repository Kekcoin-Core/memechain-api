# MemeChain Client API

This is the development repository for the Kekcoin MemeChain API. 

## Installation

This installation guide will be using Linux/Unix and Python 3.5 throughout.

### Python Dependencies

Python will need to be installed on your system. To install python-pip run

```
sudo apt install python-pip3
```
If it is already installed, it may need to be upgraded by running

```
pip3 install —upgrade pip
```
Once you have python-pip installed you will need to install the python dependencies by running

```
pip3 install tinydb falcon ipfshttpclient python-bitcoinrpc gunicorn
```

### Other Dependencies

There are some other dependencies that need to be installed.

- The Kekcoin Core blockchain software should be running as a daemon. The simplest way to get this running is to download the pre-compiled binaries here https://github.com/Kekcoin-Core/kekcoin-segwit/releases. Once downloaded, navigate to the folder containing kekcoin-linux-2.0.5.tar.gz and extract the contents with
```
tar -xf kekcoin-linux-2.0.5.tar.gz
```
Then to run the daemon, navigate into the kekcoin-linux-2.0.5 folder and run 
```
./kekcoind
```
The following kekcoin configuration file is recommended
```
rpcuser=user
rpcpassword=pass
server=1
listen=1
daemon=1
txindex=1
prune=0
maxconnections=100
```
- The IPFS software should also be running as a daemon. To install IPFS we recommend using ipfs-update, you can find instructions here https://docs.ipfs.io/guides/guides/install/#installing-with-ipfs-update. Once you have installed IPFS you need to initialize your IPFS node, to do this use
```
mkdir /data && mkdir /data/ipfs
export IPFS_PATH=/data/ipfs
ipfs init
```
After having installed IPFS and initialized your IPFS node you can run it as a daemon using supervisord. First ensure you have installed supervisor and then enter into the config file
```
sudo apt install supervisor
cp /etc/supervisor/supervisord.conf /etc/supervisor/supervisord.conf.bak && nano /etc/supervisor/supervisord.conf
```
At the bottom of the config file enter the following
```
[program:ipfs]
environment=IPFS_PATH=/data/ipfs
command=ipfs daemon
autorestart=true
```
Then enter
```
sudo supervisorctl reread && sudo supervisorctl update
```
If you want to monitor the status of IPFS you can use
```
sudo supervisorctl status
```
To start or stop the IPFS daemon you can use
```
sudo supervisorctl start ipfs
sudo supervisorctl stop ipfs
```

### How to Run the Memechain API

Once you have installed the above python dependencies and are running both the Kekcoin and IPFS daemons you will need to run the Memechain Falcon API. You will first want to set up the necessary configuration details in the file ```config.json```. Once you have set up the config file you can run the API as a process within a screen by running the following commands

```
cd memechain-api/
screen -d -m -S memechain /bin/bash -c "gunicorn -b 0.0.0.0:1337 --reload api"
```

Before uploading memes ensure you have run the sync.py manually once

```
cd memechain-api/
python3 sync.py
```
Note that this may take some time to complete, the console output will be blank whilst it is processing but debug output is available at /path/to/memechain-api/data/debug.log. 

After initializing the API and having finished the initial sync you will need to ensure that the sync script is running via the blocknotify RPC configuration of Kekcoin. In order to do this place the following line as the last line in your Kekcoin RPC configuration file

```
blocknotify=cd /path/to/memechain-api && python3 sync.py
```

## How to Use the Memechain API

Here we will show you how to send requests to the API via the command line. First lets install httpie

```
sudo apt install httpie
```

We refer users and developers to the API reference for more details to the various API calls. With httpie installed you can run the following commands.

To get information about your memechain node run
```
http localhost:1337/api/getinfo
```

Example result:

```
{
    "result": {
        "blockchain_balance": 0.98731,
        "blockchain_height": 604005,
        "last_meme_metadata": {
            "author": "KP84V1wwcguCDf2PZYbkaWFnhUBAHc1sNu",
            "block": 604000,
            "hashlink": "068ad67230034336",
            "imgformat": "jpg",
            "ipfs_id": "QmRxdjrDRbUPZpxaCL51gkAAPbPvF6FQcnTBwgXSMR9bhP",
            "txid": "d3940afe92c0c64ccf28841a1715458e411c306942445a53d100f0e6476fdae0"
        },
        "memechain_block_sync_height": 604005,
        "memechain_height": 19,
        "memechain_version": "0.1-beta"
    },
    "success": true
}
```

Note: To ensure proper functionality ```memechain_block_sync_height``` and ```blockchain_height``` should be at most 1-5 blocks apart.

To find the current height of the memechain 

```
http localhost:1337/api/getheight
```

Example result:

```
{
    "result": 2,
    "success": true
}
```

To upload a meme onto the Memechain

```
http POST localhost:1337/api/addmeme Content-Type:image/jpeg < /path/to/image.jpg
```

Example result:

```
{
    "result": {
        "hashlink": "9d1e43fa4d13a72c",
        "ipfs_id": "QmX2TTmAyoLFsexSeVt5geRWwXM7PgusxchqMKgwwRx7W9",
        "txid": "afe938e0fe7e0e62596f52cbafe27a28c63acdc9f2c6ab97298210b6263859d3"
    },
    "success": true
}
```

To get the metadata for a particular meme using the height parameter

```
http localhost:1337/api/getmemedatabyheight/2
```

Example result:

```
{
    "result": {
        "block": 587045,
        "hashlink": "220d8dda1ba25e98",
        "imgformat": "jpg",
        "ipfs_id": "QmZX8t34x2gUoERqDTNVqqVvNfFNhZpwaWQt9cj8Jc5mga",
        "txid": "ceb5881bf95e6cb8a172e1baa244cf9c7949ee67919d2a602065c523d22e4813"
    },
    "success": true
}
```

To get a meme from the Memechain using the IPFS ID parameter

```
http localhost:1337/api/getmemeimgbyheight/2 > /path/to/save/image.extension
```

## API Reference

A detailed API reference coming soon.

## Social Channels

| Site | link |
|:-----------|:-----------|
| Bitcointalk | https://bitcointalk.org/index.php?topic=2026344.0 |
| Twitter | https://twitter.com/KekcoinCore |
| Reddit | http://www.reddit.com/r/KekcoinOfficial |
| Telegram | https://t.me/KekcoinOfficial |
