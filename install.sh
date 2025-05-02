#!/bin/bash

sudo rm -rf /usr/share/fonts/MakiLibertinusMono/
sudo mkdir -p /usr/share/fonts/MakiLibertinusMono/
sudo cp fonts/*.otf /usr/share/fonts/MakiLibertinusMono/

sudo fc-cache -f
