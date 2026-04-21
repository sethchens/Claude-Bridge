import os
import json
import requests
from flask import Flask, request, jsonify
from google.cloud import pubsub_v1

app = Flask(__name__)

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
TOPIC_ID = os.environ.get("PUBSUB_TOPIC", "claude-bridge-tasks")
EXISTING_SERVER_URL = os.environ.get("EXISTING_SERVER_URL")

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID) if PROJECT_ID else None

@app.route("/", methods=["POST", "GET"])
def handle_request():
    payload = request.get_json(silent=True) or {}
    
    # Forward the request to an existing GCP backend if configured
    if EXISTING_SERVER_URL:
        try:
            requests.post(EXISTING_SERVER_URL, json=payload, timeout=10)
        except Exception as e:
            print(f"Warning: Failed to forward to existing server: {e}")
        
    if not topic_path:
        return jsonify({"error": "GOOGLE_CLOUD_PROJECT not set"}), 500

    # Publish task to Pub/Sub for the local Claude Bridge to pick up
    data_str = json.dumps(payload)
    data_bytes = data_str.encode("utf-8")
    
    try:
        future = publisher.publish(topic_path, data=data_bytes)
        message_id = future.result()
        return jsonify({
            "status": "success", 
            "message_id": message_id,
            "note": "Message routed to local Claude Code via Pub/Sub"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
