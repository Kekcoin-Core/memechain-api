"""
Basic OP_RETURN data storage tool for Memechain.
"""
from bitcoinrpc.authproxy import AuthServiceProxy
import logging
import sys
import json
import os
from binascii import hexlify, unhexlify

# Debug settings
debug = True
if debug:
    logging.basicConfig()
    logging.getLogger("BitcoinRPC").setLevel(logging.DEBUG)

# Load configuration file
with open(os.path.abspath(os.path.join(__file__, "../../config.json")), "r") as f:
    config = json.loads(f.read())

# OP_RETURN configuration
TX_FEE_AMOUNT = 0.0001
MAX_OP_RETURN_BYTES = 500

# Define RPC object
rpc = AuthServiceProxy(("http://%s:%s@127.0.0.1:%s/") %
                       (config['RPC_USER'], config['RPC_PASS'], config['RPC_PORT']))


def get_block_height():
    """
    Method used to get block height

    Returns:
            Block height (int)
    """
    return rpc.getblockcount()


def get_block_txs(height):
    """
    Method used to get tx hashes from block

    Args:
            block height (int)

    Returns:
            List of transaction ids (array)
    """
    block_hash = rpc.getblockhash(height)
    block = rpc.getblock(block_hash)

    return block['tx']


def get_input():
    """
    Method used to get unspent inputs

    Returns:
            Transaction object (dict)
    """
    unspent = rpc.listunspent()

    for tx in unspent:
        if float(tx["amount"]) > 0.001:
            return tx
    else:
        raise Exception(
            "No valid inputs, inputs must be greater than 0.001 KEK")


def create_raw_op_return_transaction(metadata):
    """
    Method used to create a transaction with embedded data through OP_RETURN

    Args:
            metadata (str)

    Returns:
            Raw transaction (hex)
    """
    if sys.getsizeof(metadata) > MAX_OP_RETURN_BYTES:
        raise Exception("Metadata size is over MAX_OP_RETURN_BYTES")

    if len(metadata) < 4:
        raise Exception(
            "This tool set does not currently support reading op_return data with less than 4 chars")

    input_tx = get_input()

    init_raw_tx = rpc.createrawtransaction([{"txid": input_tx["txid"], "vout": input_tx["vout"]}], {
                                           input_tx["address"]: 0.1 * TX_FEE_AMOUNT, rpc.getnewaddress(): float(input_tx["amount"]) - 1.1 * TX_FEE_AMOUNT})

    oldScriptPubKey = init_raw_tx[len(init_raw_tx) - 60:len(init_raw_tx) - 8]
    newScriptPubKey = "6a" + hexlify(chr(len(metadata))) + hexlify(metadata)
    newScriptPubKey = hexlify(
        chr(len(unhexlify(newScriptPubKey)))) + newScriptPubKey

    if oldScriptPubKey not in init_raw_tx:
        raise Exception("Something broke!")

    op_return_tx = init_raw_tx.replace(oldScriptPubKey, newScriptPubKey)

    return op_return_tx


def sign_raw_transaction(tx):
    """
    Method used to sign raw transaction

    Args:
            Raw transaction (hex)

    Returns:
            Signed raw transaction (hex)
    """
    return rpc.signrawtransaction(tx)["hex"]


def send_raw_transaction(tx_hex):
    """
    Method used to send raw transaction to the Kekcoin chain

    Args:
            Signed raw transaction (hex)

    Returns:
            Transaction id (str)
    """
    return rpc.sendrawtransaction(tx_hex)


def get_op_return_data(txid):
    """
    Method used to get op_return data from transaction

    Args:
            Transaction id (str)

    Returns:
            Embedded metadata (str)
    """
    raw_tx = rpc.getrawtransaction(txid)
    tx_data = rpc.decoderawtransaction(raw_tx)

    for data in tx_data["vout"]:
        if data["scriptPubKey"]["asm"][:9] == "OP_RETURN":
            op_return_data = unhexlify(data["scriptPubKey"]["asm"][10:])
        else:
            op_return_data = None

    return op_return_data
