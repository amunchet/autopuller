#!/bin/bash

# Helper setup script for .env and docker-compose.yml file for autopuller
# Basically need to make sure the path matches on docker-compose volume

echo "Please enter your GITHUB key (required for API calls)"
read GITHUBKEY

echo "Please enter github repository (e.g. https://github.com/amunchet/autopuller)"
read REPONAME

echo "Please enter local path to repository (e.g. /home/amunchet/autopuller).  The docker-compose.yml should be in this folder"
echo "NOTE: This must be the full path, not a relative path"
read REPODIR

read -r -p "Please enter docker-compose yml filename FOR THE REPO TO USE TO RESTART(default: docker-compose.yml): " composefile
composefile=${composefile:-docker-compose.yml}

read -r -p "Please enter credentials location (full path) to log into git (e.g. /home/user/.git-credentials): " credentials

read -r -p "Enter watch interval (default is 60)" INTERVAL
INTERVAL=${INTERVAL:-60}


# MODIFY .env.sample
cp .env.sample .env
sed -i "s/{{GITHUBKEY}}/$GITHUBKEY/g" .env
sed -i "s/{{REPONAME}}/${REPONAME//\//\\/}/g" .env
sed -i "s/{{REPODIR}}/${REPODIR//\//\\/}/g" .env
sed -i "s/{{INTERVAL}}/$INTERVAL/g" .env
sed -i "s/{{COMPOSEFILE}}/$composefile/g" .env

# MODIFY docker-compose.yml.template
cp docker-compose.yml.template docker-compose.yml
sed -i "s/{{PATH}}/${REPODIR//\//\\/}/g" docker-compose.yml
sed -i "s/{{CREDENTIALS}}/${credentials//\//\\/}/g" docker-compose.yml

echo "Starting up docker-compose..."
docker-compose up --build -d

echo "Done."
