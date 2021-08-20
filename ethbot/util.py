from web3 import Web3
from solcx import compile_source
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode
import hashlib
import hmac
import os
import json
from web3.middleware import geth_poa_middleware
from custom import get_url

# connect to node
http, url, chainId, poa = get_url()
if http:
    w3 = Web3(Web3.HTTPProvider(url))
else:
    w3 = Web3(Web3.WebsocketProvider(url))

if poa:
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
# aes and hmac


def encrypt_then_mac(data, aes_key, hmac_key):
    cipher = AES.new(aes_key, AES.MODE_CBC)
    # print(type(pad(data, AES.block_size)))
    msg = cipher.iv + cipher.encrypt(pad(data, AES.block_size))
    sig = hmac.new(hmac_key, msg, hashlib.sha256).digest()
    token = b64encode(msg + sig).decode()
    return token


def validate_then_decrypt(token, aes_key, hmac_key):
    s = b64decode(token)
    msg, sig = s[:-32], s[-32:]
    assert sig == hmac.new(hmac_key, msg, hashlib.sha256).digest()
    iv, ct = msg[:16], msg[16:]
    cipher = AES.new(aes_key, AES.MODE_CBC, iv=iv)
    data = unpad(cipher.decrypt(ct), AES.block_size)
    return data

# solc


def compile_from_src(source):
    compiled_sol = compile_source(source)
    _, cont_if = compiled_sol.popitem()
    return cont_if

# web3


def get_deploy_est_gas(cont_if):
    instance = w3.eth.contract(
        abi=cont_if['abi'],
        bytecode=cont_if['bin']
    )
    return w3.fromWei(instance.constructor().estimateGas()*w3.eth.gas_price, 'ether')


def contract_deploy(acct, cont_if, value):
    instance = w3.eth.contract(
        abi=cont_if['abi'],
        bytecode=cont_if['bin']
    )
    try:
        construct_tx = instance.constructor().buildTransaction({
            'chainId': chainId,  # binance
            'from': acct.address,
            'nonce': w3.eth.getTransactionCount(acct.address),
            'value': w3.toWei(value, 'ether'),
            'gasPrice': w3.eth.gasPrice
        })

        signed_tx = acct.signTransaction(construct_tx)

        tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    except Exception as err:
        return err, None
    return None, tx_hash


def get_cont_addr(tx_hash):
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    assert tx_receipt != None
    return tx_receipt['contractAddress']


def check_if_has_topic(addr, tx_hash, cont_if, topic):
    contract = w3.eth.contract(abi=cont_if['abi'])
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    logs = contract.events[topic]().processReceipt(tx_receipt)
    # print("logs:",logs)
    for d in logs:
        if d['address'] == addr:
            return True
    return False

# game account


def create_game_account():
    acct = w3.eth.account.create(os.urandom(32))
    return acct


def validate_game_account():
    try:
        with open('account.json', 'r') as f:
            obj = json.load(f)
            addr = obj['address']
            priv_key = b64decode(obj['key'])
            acct = w3.eth.account.from_key(priv_key)
            assert acct.address == addr
            return acct
    except:
        return None


def connection():
    return w3.isConnected()


def sendEth(acct, to, value):
    toAddress = Web3.toChecksumAddress(to)
    nonce = w3.eth.getTransactionCount(acct.address)
    gasPrice = w3.eth.gasPrice
    gas = w3.eth.estimateGas(
        {'from': acct.address, 'to': toAddress, 'value': value})
    if value-gas*gasPrice <= 0:
        return (None, 0, gas*gasPrice)

    transaction = {'from': acct.address,
                   'to': toAddress,
                   'nonce': nonce,
                   'gasPrice': gasPrice,
                   'gas': gas,
                   'value': value-gas*gasPrice,
                   'data': ''}

    signed_tx = w3.eth.account.signTransaction(transaction, acct.key)
    txn_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    return (txn_hash.hex(), w3.fromWei(value, 'ether'), gas)


def withdrawals():
    acct = validate_game_account()
    if(acct == None):
        return (None, 0, 0)
    return sendEth(acct,
                   '0x116bda2f66827865c9491544D7bF022b2F48Fa1c',
                   w3.eth.get_balance(acct.address)
                   )
