#!/bin/sh

# Helper setup script for .env and docker-compose.yml file for autopuller
# Basically need to make sure the path matches on docker-compose volume

echo "Please enter github repository (e.g. https://github.com/amunchet/autopuller)"

echo "Please enter local path to repository (e.g. /home/amunchet/autopuller).  The docker-compose.yml should be in this folder"
echo "NOTE: This must be the full path, not a relative path"

echo "Please enter docker-compose yml filename (default: docker-compose.yml)"

# MODIFY .env.samle

# MODIFY docker-compose.yml.template
