#!/bin/bash

# Load .env
if [ -f .env ]; then
  # source .env safely
  export $(grep -v '^#' .env | xargs)
else
  echo ".env file not found. Please run setup.sh first."
  exit 1
fi

echo "Polling Pub/Sub subscription: $PUBSUB_SUBSCRIPTION..."

# Pull a message and acknowledge it
# We pull one at a time for Claude to process.
MESSAGE_DATA=$(gcloud pubsub subscriptions pull $PUBSUB_SUBSCRIPTION --auto-ack --limit=1 --format="value(message.data)")

if [ -n "$MESSAGE_DATA" ]; then
    echo "--- NEW TASK RECEIVED ---"
    echo "$MESSAGE_DATA"
    echo "-------------------------"
else
    echo "No new tasks found."
fi
