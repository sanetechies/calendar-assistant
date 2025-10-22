# 🔧 Google Calendar API Setup Guide

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your **Project ID**

## Step 2: Enable Calendar API

1. Go to **APIs & Services** → **Library**
2. Search for "Google Calendar API"
3. Click **Enable**

## Step 3: Create Service Account

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **Service Account**
3. Fill in details:
   - **Name**: `calendar-ai-service`
   - **Description**: `Service account for Calendar AI`
4. Click **Create and Continue**
5. Skip role assignment (click **Continue**)
6. Click **Done**

## Step 4: Generate Service Account Key

1. Click on your service account email
2. Go to **Keys** tab
3. Click **Add Key** → **Create New Key**
4. Select **JSON** format
5. Click **Create** (downloads JSON file)

## Step 5: Share Calendar with Service Account

1. Open [Google Calendar](https://calendar.google.com/)
2. Go to **Settings** → **Settings for my calendars**
3. Select your calendar → **Share with specific people**
4. Add your service account email with **Make changes to events** permission

## Step 6: Configure Lambda Environment Variables

```bash
# Extract from downloaded JSON file:
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_CLIENT_EMAIL=your-service-account@project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n
GOOGLE_CALENDAR_ID=primary
```

## Step 7: Update SAM Configuration

Edit `samconfig.toml`:
```toml
parameter_overrides = [
    "GoogleProjectId=your-project-id",
    "GoogleClientEmail=your-service-account@project.iam.gserviceaccount.com"
]
```

## Step 8: Deploy Updated Stack

```bash
sam build
sam deploy
```

## Step 9: Set Private Key via AWS Console

1. Go to AWS Lambda Console
2. Find `nextcloud-calendar-ai-api` function
3. Go to **Configuration** → **Environment variables**
4. Add `GOOGLE_PRIVATE_KEY` with the private key from JSON file

## 🧪 Test Integration

```bash
python3 test_api.py
```

The API will now use real Google Calendar data when credentials are configured, and fall back to mock data otherwise.

## 🔍 Troubleshooting

**"Service account not found"**
- Check project ID and client email are correct
- Verify service account exists in Google Cloud Console

**"Calendar not accessible"**
- Make sure calendar is shared with service account email
- Check service account has "Make changes to events" permission

**"Private key format error"**
- Ensure newlines are properly escaped as `\\n`
- Copy the entire key including BEGIN/END lines