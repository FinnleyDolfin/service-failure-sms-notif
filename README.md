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
* **Device type:** **ATA device, IP Phone or Softphone**
* **Dialing Mode:** Use Main Account Setting
* **CallerID Number:** Select "I use a system capable of passing its own DID"
* **Allow International Calls:** No
* **Allow *225 for Balance:** No
* **Music on Hold:** No Music
* **Language:** English

**Skip or leave default for:**
* Call Transcription, Parking Lot, Voicemail, Internal Extension

Click **Create Account** when done.

### 3. **Order and Assign a DID (SMS-Only)**

1. Visit: [https://voip.ms/m/dids.php](https://voip.ms/m/dids.php)
2. Choose "United States" under **Local Numbers**
3. Search by state or digits and select a DID with the SMS icon
4. Choose **Per Minute Plan**
5. In **Routing Settings**, select your sub-account
6. Click **Order DID**

### 4. **Enable SMS on Your DID**

* Go to: [https://voip.ms/m/managedid.php](https://voip.ms/m/managedid.php)
* Click **Edit** next to your DID
* Scroll to **Message Service (SMS/MMS)** and enable it
* Click **Apply changes**

### 5. **Enable API Access**

* Go to: [https://voip.ms/m/api.php](https://voip.ms/m/api.php)
* Set and save an **API password**
* Enable API access
* Add your public IP address to the allowed list
* Click **Save IP Addresses**

---

## Script Usage

### Initial Setup

To run initial setup, use the `--setup` option:

```
python3 service_sms.py --setup
```

This will:

* Prompt for your VoIP.ms credentials, DID, and alert destination number
* Show a list of running systemd services to select for monitoring
* Save all information to `settings.json`
* Send a test SMS message
* Ask if you'd like to start monitoring immediately

If `settings.json` is missing or corrupted, setup will automatically run again.

### Test Mode

To send a manual test SMS message:

```
python3 service_sms.py --test
```

You will be prompted for:

* Destination number
* Message text (up to 160 characters)

### Start Monitoring

If you already ran `--setup`, you can launch monitoring like this:

```
python3 service_sms.py
```

The script will:

- Check all monitored services every 30 seconds  
- Send SMS alert when a service **stops**  
- Send SMS recovery when it **starts again**  
- Send a **daily heartbeat** message

---

## Run as a Background Service

### 1. Create a systemd unit file

Save the following to `/etc/systemd/system/voipms-monitor.service`:

```
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

Replace `/path/to/service_sms.py` and `your_linux_user` with your actual script path and username.

### 2. Enable and start the service

```
sudo systemctl daemon-reexec
sudo systemctl enable voipms-monitor.service
sudo systemctl start voipms-monitor.service
```

Check the status:

```
sudo systemctl status voipms-monitor.service
```

---

## Security Reminder

Never commit your real API password or phone numbers to a public repository. Always use placeholders in shared code:

```
voip = VoipMS("your_email@example.com", "your_secure_api_password")
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
