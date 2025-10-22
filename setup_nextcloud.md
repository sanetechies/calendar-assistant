# 🔧 Nextcloud Calendar Setup Guide

## 1. Nextcloud Installation

### Option A: Docker (Recommended)
```bash
# Quick Nextcloud setup with Docker
docker run -d \
  --name nextcloud \
  -p 8080:80 \
  -v nextcloud_data:/var/www/html \
  nextcloud:latest

# Access at http://localhost:8080
```

### Option B: Hosted Nextcloud
- Use a hosted provider (Nextcloud.com, DigitalOcean, etc.)
- Or install on your own server

## 2. Enable Calendar App

1. Login to Nextcloud admin panel
2. Go to **Apps** → **Office & text**
3. Enable **Calendar** app
4. Go to **Calendar** in the main menu

## 3. Create App Password

1. Go to **Settings** → **Security**
2. Scroll to **App passwords**
3. Enter name: "Calendar AI Agent"
4. Click **Create new app password**
5. Copy the generated password

## 4. Configure the AI Agent

Edit `config.json`:
```json
{
  "nextcloud": {
    "url": "https://your-nextcloud-instance.com",
    "username": "your-username",
    "app_password": "generated-app-password",
    "calendar_name": "personal"
  }
}
```

## 5. Test CalDAV Connection

```bash
# Test CalDAV endpoint
curl -X PROPFIND \
  -H "Authorization: Basic $(echo -n 'username:app-password' | base64)" \
  -H "Depth: 1" \
  https://your-nextcloud.com/remote.php/dav/calendars/username/
```

## 6. Deploy AI Agent

```bash
# Deploy the agent
python3 deploy.py

# Test functionality
python3 test_agent.py
```

## 🔍 Troubleshooting

**CalDAV not working?**
- Check app password is correct
- Verify calendar name exists
- Ensure Calendar app is enabled

**Connection timeout?**
- Check Nextcloud URL is accessible
- Verify firewall settings
- Test with curl first

**No events showing?**
- Create test events in Nextcloud Calendar
- Check calendar permissions
- Verify date ranges in queries