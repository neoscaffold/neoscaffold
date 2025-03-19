#!/bin/bash

. ./docker_build.sh && \
echo $TAG && \
docker push $TAG && \
docker run -p 4200:4200 $TAG