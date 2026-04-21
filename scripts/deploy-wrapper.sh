#!/bin/bash
set -e

PROJECT_ID=$1
if [ -z "$PROJECT_ID" ]; then
    echo "Usage: deploy-wrapper.sh <GCP_PROJECT_ID>"
    exit 1
fi

SERVICE_NAME="claude-bridge-wrapper"
REGION="us-central1"

echo "Deploying Cloud Run service: $SERVICE_NAME to $REGION..."

gcloud run deploy $SERVICE_NAME \
  --source ./wrapper \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT="$PROJECT_ID",PUBSUB_TOPIC="claude-bridge-tasks"

echo "Deployment complete!"
