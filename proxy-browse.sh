#!/bin/bash
PROXYPORT=8080
PROXYUSER=tud48344
PROXYHOST=astro.temple.edu

ssh -D $PROXYPORT $PROXYUSER@$PROXYHOST -N &
SSHPID=$!

BROWSERCHECK=$(ps -U $USER -o pid,cmd | grep $BROWSER | grep -v grep)

test "$BROWSERCHECK" || (echo "Browser already running!"; exit 1)

$BROWSER --proxy-server=socks://localhost:$PROXYPORT $@

kill $SSHPID

