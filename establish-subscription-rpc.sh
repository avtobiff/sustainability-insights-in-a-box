#!/bin/sh
netconf-console -s all --user=admin --password=admin --port 12022 \
    establish-subscription-rpc.xml
