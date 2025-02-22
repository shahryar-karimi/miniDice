#!/bin/sh

docker-compose stop dashboard
docker-compose build dashboard
docker-compose up -d dashboard