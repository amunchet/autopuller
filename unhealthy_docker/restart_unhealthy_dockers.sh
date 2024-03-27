#!/bin/bash

# Restarts unhealthy dockers

source .env

HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME")

if [ "$HEALTH_STATUS" = "unhealthy" ]; then
	# docker restart $CONTAINER_NAME
	echo "docker restart $CONTAINER_NAME"
fi
