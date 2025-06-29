#!/bin/bash

# Fail on error
set -e

echo "Creating Azure Container Instance..."

az container create \
  --resource-group trueshorts-backend \
  --name trueshorts-backend \
  --image shubhthecoder/trueshorts_backend:latest \
  --registry-login-server index.docker.io \
  --registry-username "$DOCKER_USERNAME" \
  --registry-password "$DOCKER_PASSWORD" \
  --cpu 2 \
  --memory 4 \
  --ports 8000 \
  --dns-name-label trueshorts-api \
  --environment-variables \
    GNEWS_API_KEY="$GNEWS_API_KEY" \
    SECRET_KEY="$SECRET_KEY" \
    MONGO_URI="$MONGO_URI" \
    SERPER_API_KEY="$SERPER_API_KEY" \
    GOOGLE_FACT_CHECK_API_KEY="$GOOGLE_FACT_CHECK_API_KEY" \
    GROQ_API_KEY="$GROQ_API_KEY" \
  --os-type Linux \
  --restart-policy OnFailure

echo "Deployment to Azure successful."
