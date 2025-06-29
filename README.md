# VoIP.ms SMS Service Monitor

This Python program monitors selected system services and sends SMS alerts via [VoIP.ms](https://voip.ms) if any service stops or recovers. It also sends a daily heartbeat message to confirm the monitor is working.

---

## Requirements

* A funded VoIP.ms account
* A configured sub-account
* An SMS-enabled DID
* API access enabled in VoIP.ms
* Python 3.9+

---

## Setup Guide

### 1. **Sign Up and Fund Your VoIP.ms Account**

* Create an account: [https://voip.ms/SignUp](https://voip.ms/SignUp)
* Add funds: [https://voip.ms/m/payment.php](https://voip.ms/m/payment.php)

### 2. **Create a Sub Account (for SMS, no voice)**

Go to: [https://voip.ms/m/subaccount.php](https://voip.ms/m/subaccount.php)

**Minimum configuration for SMS-only setup:**

* **Protocol:** SIP (Recommended)
* **Authentication type:** User/Password Authentication
* **Username:** Choose a unique name (max 12 characters)
* **Password:** Set a secure password
* **Device type:** **ATA device, IP Phone or Softphone** (this must be selected even for SMS-only usage)
* **Dialing Mode:** Use Main Account Setting
* **CallerID Number:** Select "I use a system capable of passing its own DID"
* **Canada Routing / International Route:** Leave defaults
* **Allow International Calls:** No
* \**Allow *225 for Balance:** No
* **Music on Hold:** No Music
* **Language:** English

**Skip/leave default for these:**

* Call Transcription, Parking Lot, Voicemail, Internal Extension

Click **Create Account** when done.

### 3. **Order and Assign a DID (SMS-Only)**

1. Visit: [https://voip.ms/m/dids.php](https://voip.ms/m/dids.php)
2. Choose "United States" under **Local Numbers**.
3. Use one of two search options:

   * **Browse DIDs by State**: Select a state to see available rate centers.
   * **Browse DIDs by Search Criteria**: Search for specific digits for vanity numbers (optional).
4. Click **View Numbers** next to a rate center.
5. Select a DID with the SMS icon and choose **Per Minute Plan**.
6. In the **Routing Settings**, select the sub-account you created from the dropdown.
7. Click **Order DID**.

### 4. **Enable SMS on Your DID**

* Go to: [https://voip.ms/m/managedid.php](https://voip.ms/m/managedid.php)
* Click **Edit** next to your DID.
* Scroll to **Message Service (SMS/MMS)**.
* Check **Enable SMS/MMS**.
* Click **Click here to apply changes**.

### 5. **Enable API Access**

* Go to: [https://voip.ms/m/api.php](https://voip.ms/m/api.php)
* Set an **API password**.
* Click **Save API Password**.
* Enable API by clicking **Enable/Disable API**.
* Add your public IP address to the allowed list.
* Click **Save IP Addresses**.

---

## Python Script Setup

### Configuration

In the `main()` function near the bottom of `service_sms.py`, update the following values with your actual credentials:

```python
    voip = VoipMS("your_email@example.com", "r(your_secure_api_password")
    from_did = "1XXXXXXXXXX"     # Your SMS-enabled VoIP.ms DID
    to_number = "1YYYYYYYYYY"    # Destination number to receive alerts
```

### Initial Setup

Run the script once to select services to monitor:

```bash
python3 service_sms.py
```

You will be prompted with a list of detected running services like this:

```bash
Select services to monitor:
[0] avahi-daemon.service
[1] bluetooth.service
[2] cups.service
...
Enter comma-separated numbers (e.g. 0,2,5):
```

Choose the services you want to monitor and press Enter. This will save your preferences for future runs in `monitored_services.json`.

**To change the selected services later, delete `monitored_services.json` and rerun the script.**

### Start Monitoring

After initial setup:

```bash
python3 service_sms.py
```

The script will:

* Check all monitored services every 30 seconds
* Send SMS alert when a service **stops**
* Send SMS recovery when it **starts again**
* Send a **daily heartbeat** to show it's still running

---

## Run as a Background Service

To run continuously in the background and start automatically after reboot:

### 1. Create the systemd unit file

Save the following to `/etc/systemd/system/voipms-monitor.service`:

```ini
[Unit]
Description=VoIP.ms SMS Service Monitor
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/service_sms.py
WorkingDirectory=/path/to/
Restart=always
User=your_linux_user

[Install]
WantedBy=multi-user.target
```

Replace `/path/to/service_sms.py` and `your_linux_user` with your actual script path and user.

### 2. Enable and start the service

```bash
sudo systemctl daemon-reexec
sudo systemctl enable voipms-monitor.service
sudo systemctl start voipms-monitor.service
```

To check the status:

```bash
sudo systemctl status voipms-monitor.service
```

---

## Security Reminder

Never commit your real API password or phone numbers to a public repository. Always use placeholders in shared code:

```python
voip = VoipMS("your_email@example.com", "r(your_secure_api_password")
from_did = "1XXXXXXXXXX"
to_number = "1YYYYYYYYYY"
```

---

## Support

If your SMS messages aren't working:

* Ensure the DID is SMS-enabled
* Confirm the destination number is in **NANPA format** (e.g., 1XXXXXXXXXX)
* Double-check API IP address and password settings

---

Happy monitoring!
# service-failure-sms-notif
