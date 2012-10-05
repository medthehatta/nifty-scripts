#!/bin/bash

PREFIX="$@"
EDITOR="vim"
TERMCMD="urxvt"

FILE="${PREFIX}/$(date +%m%d-%H%M%S).rst"

echo "##############################" > "$FILE"
date >> "$FILE"
echo "##############################" >> "$FILE"
echo >> "$FILE"

if [ -n "$DISPLAY" ]; then
  $TERMCMD -e $EDITOR "$FILE"
else
  $EDITOR "$FILE"
fi

