#!/bin/bash
MSGS=/tmp/msgs

while read INP; do
  REP="[$(date +%H:%M:%S)]   ${INP}"
  echo -e "${REP}" | tee "${MSGS}" | dzen2 -fn cure -p 3
done

