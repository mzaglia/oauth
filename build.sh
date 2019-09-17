#!/bin/bash

##### DEPLOY

echo
echo "BUILD STARTED"
echo

echo
echo "NEW TAG - API OAUTH:"
read API_OAUTH_TAG

IMAGE_API_OAUTH="registry.dpi.inpe.br/dpi/oauth"

IMAGE_API_OAUTH_FULL="${IMAGE_API_OAUTH}:${API_OAUTH_TAG}"

docker build -t ${IMAGE_API_OAUTH_FULL} -f docker/Dockerfile .

docker push ${IMAGE_API_OAUTH_FULL}
