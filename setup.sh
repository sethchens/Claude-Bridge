#!/bin/bash
set -e

# Claude Bridge Initial Setup Script
echo "Starting Claude Bridge Setup..."

# 1. Check for gcloud
if ! command -v gcloud &> /dev/null; then
    echo "gcloud could not be found. Please install the Google Cloud CLI."
    exit 1
fi

echo "Please ensure you are authenticated. Running 'gcloud auth login' (if needed)..."
gcloud auth login --update-adc

echo "Enter your GCP Project ID:"
read -r PROJECT_ID
gcloud config set project "$PROJECT_ID"

echo "Setting up Pub/Sub..."
TOPIC_NAME="claude-bridge-tasks"
SUB_NAME="claude-bridge-sub"

# Create topic if it doesn't exist
if ! gcloud pubsub topics describe $TOPIC_NAME &> /dev/null; then
    gcloud pubsub topics create $TOPIC_NAME
    echo "Created topic: $TOPIC_NAME"
fi

# Create subscription if it doesn't exist
if ! gcloud pubsub subscriptions describe $SUB_NAME &> /dev/null; then
    gcloud pubsub subscriptions create $SUB_NAME --topic=$TOPIC_NAME
    echo "Created subscription: $SUB_NAME"
fi

# Deploy the wrapper
echo "Deploying the wrapper service to Cloud Run..."
bash scripts/deploy-wrapper.sh "$PROJECT_ID"

# Setup local env
echo "Creating .env file for local configuration..."
cat <<EOF > .env
GCP_PROJECT_ID=$PROJECT_ID
PUBSUB_TOPIC=$TOPIC_NAME
PUBSUB_SUBSCRIPTION=$SUB_NAME
EOF

echo "Checking node/npm for playwright-mcp installation..."
if command -v npm &> /dev/null; then
    echo "To use playwright-mcp for browser automation, you can run:"
    echo "npm install -g @smithery/playwright-mcp"
else
    echo "npm not found. Please install Node.js."
fi

echo "Setup complete! You can now use Claude Code with this bridge."
