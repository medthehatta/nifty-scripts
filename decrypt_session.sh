#!/bin/bash

OUTDIR='/tmp'

if [ ! -z $@ ] && [ -f "$@" ]; then
    CYPHER="$@"
    echo "Decrypting session: '$CYPHER'"
else
    echo "Invalid session: '$@'"
    exit 1
fi

gpg -d "$CYPHER" | tar xJ -C "$OUTDIR"

if [ $? -eq 0 ]; then
    echo "Session decrypted to: '$OUTDIR'"
else
    echo "Failed to decrypt session."
    exit 1
fi


