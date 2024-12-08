#!/bin/bash

. ./docker_build.sh && \
echo $TAG && \
docker push $TAG && \
docker run -p 6166:6166 $TAG