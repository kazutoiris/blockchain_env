#!/usr/bin/python3
import colorama
# from colorama import colorama.Fore, colorama.Back, Style
import base64
import sys
import signal
import hashlib
import os
from Crypto.Util.number import bytes_to_long, long_to_bytes
from util import *
from custom import *
import random
import string
import time
from Crypto.Cipher import AES
import json

alarmsecs = 60
workdir = "/root/ethbot"
pow_difficult = 21

os.chdir(workdir)


class Colored(object):

    def __init__(self):
        colorama.init(autoreset=True)

    def red(self, s):
        return colorama.Fore.RED + s + colorama.Fore.RESET

    def green(self, s):
        return colorama.Fore.GREEN + s + colorama.Fore.RESET

    def yellow(self, s):
        return colorama.Fore.YELLOW + s + colorama.Fore.RESET

    def blue(self, s):
        return colorama.Fore.BLUE + s + colorama.Fore.RESET

    def magenta(self, s):
        return colorama.Fore.MAGENTA + s + colorama.Fore.RESET

    def cyan(self, s):
        return colorama.Fore.CYAN + s + colorama.Fore.RESET

    def white(self, s):
        return colorama.Fore.WHITE + s + colorama.Fore.RESET

    def black(self, s):
        return colorama.Fore.BLACK

    def white_green(self, s):
        return colorama.Fore.WHITE + colorama.Back.GREEN + s + colorama.Fore.RESET + colorama.Back.RESET


cr = Colored()


class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


sys.stdout = Unbuffered(sys.stdout)
signal.alarm(alarmsecs)
os.chdir(workdir)


def getflag():
    with open("/root/ethbot/flag", "r") as f:
        return f.read().strip()


def generatepow(difficulty):
    prefix = ''.join(random.choice(string.ascii_letters + string.digits)
                     for i in range(8))
    msg = "sha256("+prefix+"+?).binary.endswith('"+"0"*difficulty+"')"
    return prefix, msg


def pow(prefix, difficulty, answer):
    hashresult = hashlib.sha256((prefix+answer).encode()).digest()
    bits = bin(
        int(hashlib.sha256((prefix+answer).encode()).hexdigest(), 16))[2:]
    if bits.endswith("0"*difficulty):
        return True
    else:
        return False


def destroy():
    tx, val, txn = withdrawals()
    if tx != None:
        print(cr.green("✔️ Account destruct successfully!"))
        print(cr.green(
            "🔔 Transaction hash: {}\nWithdrawl {} (t)BNB\nUsed Gas: {}".format(tx, val, txn)))
    else:
        print(cr.red("💸 You don't seem to have money."))


if(connection()):
    print(cr.green("✔️ Connected to the testnet"))
else:
    print(cr.red("⭕ Failed to connect the testnet"))
    sys.exit(0)


def printMENU():
    print(cr.cyan("We design a pretty easy contract game. Enjoy it! 👍"))
    print()
    print(cr.yellow('Game environment:'),
          cr.magenta("Binance Smart Chain Testnet"))
    print()
    print(cr.yellow('Explorer:'),
          cr.magenta("🔗 https://testnet.bscscan.com/"))
    print()
    print(cr.yellow('Faucet:'), cr.magenta(
        "🔗 https://testnet.binance.org/faucet-smart"))
    print()
    print(cr.magenta('1.'), cr.green("Create/Review a game account"))
    print(cr.magenta('2.'), cr.green("(Re)Deploy a game contract"))
    print(cr.magenta('3.'), cr.green("Request for flag"))
    print(cr.magenta('4.'), cr.green("Get source code"))
    print(cr.magenta('5.'), cr.green("Account destruction"))
    print()


printMENU()
try:
    choice = int(input(cr.blue("🤞 input your choice: ")).strip())
except:
    choice = 0
print()

if choice == 1:
    # create game account
    if os.path.exists('account.json'):
        acct = acct = validate_game_account()
    else:
        acct = create_game_account()
        # save account
        with open('account.json', 'w') as f:
            json.dump({
                "address": acct.address,
                "key": base64.b64encode(acct.key).decode('utf-8')
            }, f)

    cont_if = compile_from_src(code(False))
    est_gas = get_deploy_est_gas(cont_if)

    print(cr.cyan("👉 Your game account:{}".format(acct.address)))
    print(cr.yellow("📒 Deploy will cost {:.4f} (t)BNB".format(est_gas)))
    print(cr.red("📒 You need to deposit some Ξ before you deploy!"))

elif choice == 2:
    acct = validate_game_account()
    if acct == None:
        print(cr.red("💸 You don't seem to have an account. Apply for it before this step!"))
        sys.exit(0)

    # deploy game contract
    cont_if = compile_from_src(code(False))
    err, tx_hash = contract_deploy(acct, cont_if, 10**(-18))

    # check if got error when sending transaction
    if err:
        if err.args[0]['code'] == -32000:
            print(
                cr.red("💸 You don't seem to have money. Deposit some Ξ before this step!"))
        else:
            msg = 'Error: ' + err.args[0]['message'] + '\n'
            print(cr.red("Some error occurred\n{}".format(msg)))
        sys.exit(0)

    # generate new token
    print(cr.green("🔔 Try to achieve the goal!"))
    print()
    print(cr.magenta("🔔 Transaction hash:"),
          cr.green(" {}".format(tx_hash.hex())))
elif choice == 3:
    try:
        with open('transaction.json', 'r') as f:
            tx_hash = f.read().strip()
        acct = validate_game_account()
        addr = get_cont_addr(tx_hash)
    except:
        print(
            cr.red("💸 You don't seem to have a transaction. Get it before this step!"))
        sys.exit(0)
    tx_hash = input(
        cr.green("💡 input tx_hash that achieved the goal: "))
    tx_hash = tx_hash.strip()

    CONT_IF = compile_from_src(code(False))
    res = check(addr, tx_hash, CONT_IF)
    if res:
        flag = getflag()
        print(cr.green("✔️ You have reached the goal!"))
        print()
        print(cr.green("🔑 "+flag))
        print()
        destroy()
        print(cr.green("✔️ Account destruct successfully!"))
    else:
        print(
            cr.red("💸 You don't seem to reach the goal! Try again!"))

elif choice == 4:
    print(code(True))

elif choice == 5:
    destroy()

else:
    print(cr.red("⭕ Invalid option"))
sys.exit(0)
