#!/bin/bash

# sfd_file=LibertinusMono-Regular.sfd

# if [ ! -f $sfd_file ]; then
# 	curl -Lo $sfd_file \
# 	https://github.com/alerque/libertinus/raw/refs/heads/master/sources/LibertinusMono-Regular.sfd
# fi

rm -rf fonts/*

fontforge -script modify.py
