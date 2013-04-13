#!/bin/bash
eval $(keychain --eval id_rsa)
ssh -t med@mancer.in -p2022 "tmux attach -t remote || tmux new -s remote" 

