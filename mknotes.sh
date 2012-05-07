#!/bin/bash

PREFIX="$@"
EDITOR="vim"
TERMCMD="urxvt"

FILE="${PREFIX}/$(date +%m%d-%H%M%S).rst"

echo "##############################" > "$FILE"
date >> "$FILE"
echo "##############################" >> "$FILE"
echo >> "$FILE"

$TERMCMD -e $EDITOR "$FILE"

#is that all?
