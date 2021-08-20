# Blockchain Environment

## Abstract

This repository is designed for `CTFd`. The functions support is below.

+ Dynamic Flag

  Tips: Use with `CTFd-Whale`

+ Every challenger has their own environment

## Usage

You can build your own container by yourself.

You can use `cjlu/blockchainenv` as base image. The things you need to custom is below.

+ Specify solc version in `Dockerfile`
+ Implement `check` and `code` function in `custom.py`.
+ Place `eth.sol`

You can refer to [blockchain-template](https://github.com/kazutoiris/blockchain-template) for more information.

Expose 9999/tcp

## Notice

In default settings, Docker containers can’t connect to the Internet. So, you have some ways to access to Blockchain.

+ You can add a proxy container to connect the Internet and Intranet
+ Or you can build a private Blockchain using `Geth`
+ Also, you can open Internet for all Docker containers. But it’s not recommended.

## Final

Feel free to pull requests or create an issue.
