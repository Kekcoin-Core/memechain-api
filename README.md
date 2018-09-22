# MemeChain Client API

This is the development repository for the Kekcoin MemeChain API. 

## Installation

This installation guide will be using Linux/Unix throughout.

### Python Dependencies

Python will need to be installed on your system. To install python-pip run

```
sudo apt install python-pip
```

Once you have python-pip installed you will need to install the python dependencies by running

```
pip install tinydb ujson falcon ipfsapi python-bitcoinrpc
```

### Other Dependencies

There are some other dependencies that need to be installed.

- The Kekcoin Core blockchain software should be running as a daemon. The repository can be found here https://github.com/Kekcoin-Core/kekcoin-segwit/. You can follow any guide on how to install and run bitcoind as a reference.

- The IPFS software should also be running as a daemon. To install IPFS please follow the instructions found here https://ipfs.io/docs/install/. To initialize your IPFS node please follow https://ipfs.io/docs/getting-started/. After having installed IPFS and initialized your IPFS node you can run it as a daemon within a screen by using

```
screen -d -m -S ipfs /bin/bash -c "ipfs daemon"
```

### How to Run the Memechain API

Once you have installed the above python dependencies and are running both the Kekcoin and IPFS daemons you will need to run the Memechain Falcon API. To do so as a process within a screen you need to run the following commands

```
cd memechain-api/
screen -d -m -S memechain /bin/bash -c "python api.py"
```

Note if you want to host the Memechain API as a public HTTP endpoint for more scalable applications make sure you have gunicorn installed with ```pip install gunicorn``` and replace the last line above with

```
screen -d -m -S memechain /bin/bash -c "gunicorn -b 0.0.0.0:1337 --reload api"
```

Before uploading memes ensure you have run the sync.py manually once

```
cd memechain-api/
python sync.py
```

After initializing the API and having finished the initial sync you will need to ensure that the sync script is running via the blocknotify RPC configuration of Kekcoin. In order to do this place the following line as the last line in your Kekcoin RPC configuration file

```
blocknotify=cd /path/to/memechain-api && python sync.py
```

## How to Use the Memechain API

Here we will show you how to send requests to the API via the command line. First lets install httpie

```
sudo apt install httpie
```

We refer users and developers to the API reference for more details to the various API calls. With httpie installed you can run the following commands 

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
| Twitter | https://twitter.com/KekCore |
| Reddit | http://www.reddit.com/r/KekcoinOfficial |
| Telegram | https://t.me/KekcoinOfficial |