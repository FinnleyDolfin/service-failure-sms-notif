import subprocess
import time
import json
from pathlib import Path
from datetime import datetime
import requests

CONFIG_FILE = Path("monitored_services.json")

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

def setup_monitoring():
    services = list_running_services()
    print("Select services to monitor:")
    for idx, svc in enumerate(services):
        print(f"[{idx}] {svc}")

    choices = input("Enter comma-separated numbers (e.g. 0,2,5): ").split(",")
    selected = [services[int(choice.strip())] for choice in choices if choice.strip().isdigit()]

    config = {
        "services": selected,
        "last_status": {svc: "running" for svc in selected},
        "last_heartbeat": str(datetime.now().date())
    }
    CONFIG_FILE.write_text(json.dumps(config, indent=2))
    print("Monitoring setup complete. Re-run the script to begin monitoring.")

def check_services(voip: VoipMS, from_did: str, to_number: str):
    if not CONFIG_FILE.exists():
        print("No config file found. Run setup first.")
        return

    config = json.loads(CONFIG_FILE.read_text())
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
        CONFIG_FILE.write_text(json.dumps(config, indent=2))

def main():
    voip = VoipMS("your_email@example.com", "r(your_secure_api_password")
    from_did = "1XXXXXXXXXX"     # Your SMS-enabled VoIP.ms DID
    to_number = "1YYYYYYYYYY"    # Destination number to receive alerts

    while True:
        check_services(voip, from_did, to_number)
        time.sleep(5)  # Monitor every 5 seconds for testing - set to 30

if __name__ == "__main__":
    if not CONFIG_FILE.exists():
        setup_monitoring()
    else:
        main()
