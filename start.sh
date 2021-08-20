#!/bin/sh
# Add your startup script

# DO NOT DELETE
echo $FLAG >/root/ethbot/flag && export FLAG=not_flag && FLAG=not_flag
/etc/init.d/xinetd start
sleep infinity
