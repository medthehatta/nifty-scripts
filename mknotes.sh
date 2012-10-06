#!/bin/bash

PREFIX="$@"
EDITOR="vim"
EDARGS="+"
TERMCMD="urxvt"

FILE="${PREFIX}/$(date +%m%d-%H%M%S).rst"

echo ":Date: $(date +'%Y-%M-%d %H:%m')" >> "$FILE"
echo -e "\n" >> "$FILE"

if [ -n "$DISPLAY" ]; then
  $TERMCMD -e $EDITOR "$EDARGS" "$FILE"
else
  $EDITOR "$EDARGS" "$FILE"
fi

