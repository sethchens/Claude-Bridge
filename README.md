# Claude Bridge

A lightweight, portable toolkit to bridge webhooks and standard cloud tasks into local **Claude Code** agents via Google Cloud Pub/Sub.

## How It Works

Instead of letting an end-to-end cloud infrastructure run complex and brittle automation sequences directly, **Claude Bridge** runs a lightweight proxy ("wrapper") on Google Cloud Run. This wrapper receives the webhooks/triggers and safely puts them in a Pub/Sub queue. Your local Claude Code agent pulls from this queue and completes the task dynamically using the full context of your local browser and workstation.

## Directory Structure
- `setup.sh`: The master install script (run exactly once per new machine).
- `poll_pubsub.sh`: Polling script used by Claude Code to check for new tasks.
- `CLAUDE.md`: System prompt ensuring Claude Code knows how to use this repository.
- `wrapper/`: A lightweight Python Cloud Run service that receives tasks via HTTP and ships them to Pub/Sub.

---

## 🚀 Getting Started

### 1. Initial Setup
On any new machine (laptop or workstation), clone this repository and run the setup script:

```bash
cd "Claude Bridge"
bash setup.sh
```

**What this does:**
- Validates GCP CLI access.
- Asks for your existing GCP Project ID.
- Creates the necessary Pub/Sub `claude-bridge-tasks` Topic and Subscription automatically.
- Deploys the lightweight python `wrapper` up to Cloud Run securely.
- Generates a local `.env` containing your specific variables.

### 2. Using Claude Code

Once setup is complete, you simply let Claude Code run inside this directory! The provided `CLAUDE.md` automatically injects instructions into Claude Code so it knows it should be acting as an automation agent.

If a trigger fires in the Cloud, the wrapper puts the webhook data in Pub/Sub. Next time Claude Code runs `./poll_pubsub.sh`, it will grab the payload, read the task details, and execute the work using your local Chrome profile and workstation.

### Advanced: Integrating with existing APIs
The wrapper (`wrapper/main.py`) supports an `EXISTING_SERVER_URL` environment variable. If set via the dashboard, incoming webhooks can also be simultaneously mirrored/forwarded to your old legacy backend while *also* sending tasks to your local Claude agent!
