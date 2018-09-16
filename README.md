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

After initializing the API you will need to ensure that the sync script is running via the blocknotify RPC configuration of Kekcoin. In order to do this place the following line as the last line in your Kekcoin RPC configuration file

```
blocknotify=cd /path/to/memechain-api && python sync.py
```

## How to Use the Memechain API

Usage instructions coming soon.

## Social Channels

| Site | link |
|:-----------|:-----------|
| Bitcointalk | https://bitcointalk.org/index.php?topic=2026344.0 |
| Twitter | https://twitter.com/KekCore |
| Reddit | http://www.reddit.com/r/KekcoinOfficial |
| Telegram | https://t.me/KekcoinOfficial |