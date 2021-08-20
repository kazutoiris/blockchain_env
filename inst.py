#!/usr/bin/python3

import subprocess
import wget
import os
import sys

tag_name = os.environ.get('tag_name')

if tag_name == "":
    sys.exit(0)

try:
    url = "https://github.com/ethereum/solidity/releases/download/{}/solc-static-linux".format(
        tag_name)

    target_name = "/root/.solcx/solc-{}".format(tag_name)

    wget.download(url, out=target_name)

    subprocess.call('python3 -m solcx.install {}'.format(tag_name), shell=True)

    print("Installed solc {}".format(tag_name))
except:
    print("Failed to install solc {}".format(tag_name))
