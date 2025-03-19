#!/bin/bash

# SET the REGISTRY here, where the docker container should be pushed
REGISTRY=${REGISTRY:-"us-docker.pkg.dev/neoscaffold/images"}

# SET the appname here
PROJECT_NAME="neoscaffold"

VERSION=$(date +%s)$(git rev-parse HEAD)

TAG=${PROJECT_NAME}:${VERSION}
if [ -z "${REGISTRY}" ]; then
  echo "No registry set, creating tag ${TAG}"
else
 TAG="${REGISTRY}/${TAG}"
 echo "Registry set: creating tag ${TAG}"
fi

# Should be run in the folder that has Dockerfile
docker build --platform linux/amd64 --tag ${TAG} \
  --build-arg NEOSCAFFOLD_URL=${NEOSCAFFOLD_URL} \
  --build-arg GOOGLE_SIGN_IN_CLIENT_ID=${GOOGLE_SIGN_IN_CLIENT_ID} \
  .

echo "Docker image built with tag ${TAG}."
