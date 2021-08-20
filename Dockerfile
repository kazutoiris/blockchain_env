FROM ubuntu:focal

RUN apt-get update && \
    apt-get install -y python3 python3-pip xinetd && \
    pip3 install pycryptodome web3 py-solc-x hues colorama wget requests

RUN mkdir /root/ethbot && \
    mkdir /root/.solcx

COPY ./ethbot /root/ethbot
COPY ./start.sh /start.sh
COPY ./inst.py /inst.py
# COPY ./latest.py /latest.py
COPY ./ctf.xinetd /etc/xinetd.d/ctf

RUN chmod +x /start.sh && \
    chmod +x /inst.py && \
    # chmod +x /latest.py && \
    chmod +x /root/ethbot/*.py
# /usr/bin/python3 /latest.py && \
# chmod 0777 /root/.solcx/*
# rm -rf /latest.py

ENTRYPOINT ["/start.sh"]

EXPOSE 9999
