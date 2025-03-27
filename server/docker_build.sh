#!/bin/bash

# SET the REGISTRY here, where the docker container should be pushed
REGISTRY=${REGISTRY:-"us-docker.pkg.dev/neoscaffold/images"}

# SET the appname here
PROJECT_NAME="neoscaffold_server"

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
  --build-arg OPENAI_API_KEY=${OPENAI_API_KEY} \
  --build-arg ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY} \
  --build-arg PPL_API_KEY=${PPL_API_KEY} \
  --build-arg CO_API_KEY=${CO_API_KEY} \
  --build-arg CEREBRAS_API_KEY=${CEREBRAS_API_KEY} \
  --build-arg GROQ_API_KEY=${GROQ_API_KEY} \
  --build-arg GOOGLE_SIGN_IN_CLIENT_ID=${GOOGLE_SIGN_IN_CLIENT_ID} \
  .

echo "Docker image built with tag ${TAG}."
