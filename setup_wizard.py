import os
import sys
import shutil
import subprocess

def resource_path(relative_path):
    """
    Get absolute path to resource. This is required because PyInstaller
    extracts the bundled files into a temporary _MEIPASS directory at runtime.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def run_cmd(cmd, capture=False):
    print(f"> {' '.join(cmd)}")
    if capture:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout
    else:
        result = subprocess.run(cmd)
        return result.returncode == 0, ""

def main():
    print("==================================================")
    print("      Claude Bridge - Remote Automation Setup     ")
    print("==================================================")
    
    # 1. Check for gcloud CLI
    success, stdout = run_cmd(["gcloud", "--version"], capture=True)
    if not success:
        print("\n[ERROR] Google Cloud CLI (gcloud) is not installed or not in your PATH.")
        print("Please install it from: https://cloud.google.com/sdk/docs/install")
        input("\nPress Enter to exit...")
        sys.exit(1)
        
    # 2. Authenticate
    print("\n--- Step 1: Authenticating with Google Cloud ---")
    run_cmd(["gcloud", "auth", "login", "--update-adc"])
    
    # 3. Project Configuration
    print("\n--- Step 2: Selecting Project ---")
    project_id = input("Enter your existing GCP Project ID: ").strip()
    if not project_id:
        print("Error: Project ID is required.")
        input("\nPress Enter to exit...")
        sys.exit(1)
        
    run_cmd(["gcloud", "config", "set", "project", project_id])
    
    # 4. Provision Pub/Sub
    topic_name = "claude-bridge-tasks"
    sub_name = "claude-bridge-sub"
    print("\n--- Step 3: Provisioning System Queues ---")
    run_cmd(["gcloud", "pubsub", "topics", "create", topic_name])
    run_cmd(["gcloud", "pubsub", "subscriptions", "create", sub_name, "--topic", topic_name])
    
    # 5. Deploy Cloud Run Wrapper from bundled resources
    print("\n--- Step 4: Deploying Cloud Run Wrapper ---")
    wrapper_path = resource_path("wrapper")
    print(f"Uploading source from bundled data: {wrapper_path}")
    
    # Needs shell=True on Windows if passing a giant command string, or careful list usage.
    # We will use the list format.
    run_cmd([
        "gcloud", "run", "deploy", "claude-bridge-wrapper",
        "--source", wrapper_path,
        "--region", "us-central1",
        "--allow-unauthenticated",
        f"--set-env-vars=GOOGLE_CLOUD_PROJECT={project_id},PUBSUB_TOPIC={topic_name}"
    ])
    
    # 6. Drop Local Workflow Tools
    print("\n--- Step 5: Preparing Local Environment ---")
    target_dir = os.path.join(os.environ.get("USERPROFILE", "."), "Desktop", "Claude-Workspace")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    print(f"Extracting tools to: {target_dir}")
    shutil.copy(resource_path("poll_pubsub.sh"), target_dir)
    shutil.copy(resource_path("CLAUDE.md"), target_dir)
    
    env_content = f"GCP_PROJECT_ID={project_id}\nPUBSUB_TOPIC={topic_name}\nPUBSUB_SUBSCRIPTION={sub_name}\n"
    with open(os.path.join(target_dir, ".env"), "w") as f:
        f.write(env_content)
        
    print("\n==================================================")
    print("                  SETUP COMPLETE!                 ")
    print("==================================================")
    print(f"Your Claude Code bridge is ready at:")
    print(f"{target_dir}")
    print("\nTo begin automation, simply navigate to that folder")
    print("in your terminal and start Claude Code!")
    input("\nPress Enter to finish and close...")

if __name__ == "__main__":
    main()
