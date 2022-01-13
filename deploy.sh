#!/bin/bash

docker context use default
docker compose build api
docker push madaosik/teamorg-repo:latest
docker context use myecscontext
ecs-cli compose -f docker-compose-aws.yml --project-name teamorg-api --cluster teamorg-api-cluster service up --launch-type FARGATE
docker context use default
