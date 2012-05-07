#!/bin/bash

PREFIX="$@"
EDITOR="vim"
TERMCMD="urxvt"

# Yeah yeah, this is ugly.  Deal.
FILE="$(mktemp --tmpdir="$PREFIX")"
mv "$FILE" "${FILE}.rst"
FILE="${FILE}.rst"

echo "##############################" > "$FILE"
date >> "$FILE"
echo "##############################" >> "$FILE"
echo >> "$FILE"

$TERMCMD -e $EDITOR "$FILE"

#is that all?
