#!/bin/bash

P="$@"
NUM=5
TMP=$(mktemp)
PAGER="less"
CAT="cat"

FILES=$(find "$P" -type f | grep -iv swp | sort -r | head -n${NUM} | sort)
$CAT ${FILES} | $PAGER


