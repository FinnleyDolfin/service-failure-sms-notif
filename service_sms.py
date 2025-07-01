import subprocess
import time
import json
import argparse
from pathlib import Path
from datetime import datetime
import requests

SETTINGS_FILE = Path("settings.json")

class VoipMS:
    def __init__(self, username: str, password: str):
        self.params: dict[str, str] = {
            "api_username": username,
            "api_password": password,
            "format": "json"
        }
        self.url = "https://voip.ms/api/v1/rest.php"

    def send_sms(self, did: str, destination: str, message: str) -> dict:
        sms_params = {
            "method": "sendSMS",
            "did": did,
            "dst": destination,
            "message": message
        }
        all_params = self.params.copy()
        all_params.update(sms_params)
        try:
            response = requests.get(self.url, params=all_params)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

def list_running_services() -> list[str]:
    result = subprocess.run([
        "systemctl", "list-units", "--type=service", "--state=running", "--no-legend", "--no-pager"
    ], capture_output=True, text=True)
    return [line.split()[0] for line in result.stdout.strip().splitlines()]

def load_settings() -> dict:
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text())
        except json.JSONDecodeError:
            print("WARNING: settings.json is invalid. Reinitializing.")
            SETTINGS_FILE.unlink()
    return {}

def save_settings(settings: dict):
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2))

def interactive_setup():
    settings = load_settings()

    print("== VoIP.ms SMS Service Monitor Setup ==")

    settings["api_username"] = input(f"VoIP.ms API username [{settings.get('api_username', '')}]: ").strip() or settings.get("api_username", "")
    settings["api_password"] = input(f"VoIP.ms API password [{settings.get('api_password', '')}]: ").strip() or settings.get("api_password", "")
    settings["from_did"] = input(f"Your SMS-enabled DID (e.g., 1XXXXXXXXXX) [{settings.get('from_did', '')}]: ").strip() or settings.get("from_did", "")
    settings["to_number"] = input(f"Destination number to receive alerts [{settings.get('to_number', '')}]: ").strip() or settings.get("to_number", "")

    print("\nSelect services to monitor:")
    services = list_running_services()
    for idx, svc in enumerate(services):
        print(f"[{idx}] {svc}")
    choices = input("Enter comma-separated numbers (e.g. 0,2,5): ").split(",")

    selected_services = []
    for c in choices:
        c = c.strip()
        if c.isdigit():
            idx = int(c)
            if 0 <= idx < len(services):
                selected_services.append(services[idx])

    settings["services"] = selected_services
    settings["last_status"] = {svc: "running" for svc in selected_services}
    settings["last_heartbeat"] = str(datetime.now().date())

    save_settings(settings)

    print("Setup complete. Sending test SMS...")

    voip = VoipMS(settings["api_username"], settings["api_password"])
    response = voip.send_sms(settings["from_did"], settings["to_number"],
        "[TEST] This is a test from the service monitor. If received, it is configured correctly.")

    if response.get("status") == "success":
        print("Test SMS sent successfully. Please check your phone.")
    else:
        print("Failed to send test SMS.")
        print("Reason:", response.get("message", "Unknown error"))

    while True:
        choice = input("\nDo you want to start monitoring now?\n[1] Start monitoring\n[2] Exit\nChoice: ").strip()
        if choice == "1":
            return settings
        elif choice == "2":
            print("Exiting. You can run the program later without --setup to begin monitoring.")
            exit(0)
        else:
            print("Invalid choice. Please enter 1 or 2.")

def check_services(config):
    if not config:
        print("No configuration found. Run with --setup.")
        interactive_setup()
        return

    voip = VoipMS(config["api_username"], config["api_password"])
    from_did = config["from_did"]
    to_number = config["to_number"]
    monitored = config["services"]
    last_status = config.get("last_status", {})
    running = set(list_running_services())
    changed = False

    for svc in monitored:
        current = "running" if svc in running else "stopped"
        previous = last_status.get(svc, "unknown")
        if previous == "running" and current == "stopped":
            voip.send_sms(from_did, to_number, f"[ALERT] Service {svc} has stopped.")
            last_status[svc] = current
            changed = True
        elif previous == "stopped" and current == "running":
            voip.send_sms(from_did, to_number, f"[RECOVERY] Service {svc} is running again.")
            last_status[svc] = current
            changed = True

    today = str(datetime.now().date())
    if config.get("last_heartbeat") != today:
        voip.send_sms(from_did, to_number, f"[HEARTBEAT] Monitoring active. {datetime.now().isoformat(timespec='minutes')}")
        config["last_heartbeat"] = today
        changed = True

    if changed:
        config["last_status"] = last_status
        save_settings(config)

def send_test_sms():
    config = load_settings()
    if not config:
        print("No configuration found. Run with --setup.")
        return

    voip = VoipMS(config["api_username"], config["api_password"])
    from_did = config["from_did"]
    dst = input("Enter destination number (e.g., 1XXXXXXXXXX): ").strip()
    msg = input("Enter message to send (max 160 characters): ").strip()
    if len(msg) > 160:
        print("Message exceeds 160 characters and will be truncated.")
        msg = msg[:160]

    response = voip.send_sms(from_did, dst, msg)
    print("Response:", response)

def monitor_loop(config):
    try:
        while True:
            check_services(config)
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")


def run():
    parser = argparse.ArgumentParser(description="Monitor systemd services and send SMS alerts using VoIP.ms")
    parser.add_argument("--setup", action="store_true", help="Run initial setup and select services to monitor")
    parser.add_argument("--test", action="store_true", help="Send a test SMS message")
    args = parser.parse_args()

    if args.setup:
        config = interactive_setup()
        monitor_loop(config)
    elif args.test:
        send_test_sms()
    else:
        config = load_settings()
        if not config:
            print("No valid configuration found. Starting setup...")
            config = interactive_setup()
        monitor_loop(config)

run()
