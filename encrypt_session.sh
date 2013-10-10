#!/bin/bash

OUTDIR='/home/med/ark'
OUTFILE="p$(date -Ih)"
DEFAULT_SESS='/tmp/xx'


if [ ! -z $@ ] && [ -d "$@" ]; then
    SESS="$@"
    echo "Encrypting provided session directory: '$SESS'"
elif [ -d "$DEFAULT_SESS" ]; then
    SESS="DEFAULT_SESS"
    echo "Encrypting default session directory: '$SESS'"
else
    echo "Invalid session directory: '$@'"
    exit 1
fi

ARCHIVE=$(mktemp)

tar cJ "$SESS" > "$ARCHIVE"
gpg -e -r 60BB639A -r 69837299 "$ARCHIVE" > "$OUTDIR/$OUTFILE"

rm "$ARCHIVE"

if [ $? -eq 0 ]; then
    echo "Session encrypted to: '$OUTDIR/$OUTFILE'"
else
    echo "Failed to encrypt session."
    exit 1
fi


