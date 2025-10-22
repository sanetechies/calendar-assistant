# 🚀 Calendar Assistant Deployment Guide

## Current Status
✅ **Agent Created**: ID `AE2NL4BTR0`  
✅ **Model**: Claude 3.5 Sonnet (latest available)  
✅ **Permissions**: Enhanced with marketplace access  
✅ **Lambda**: Function deployed  

## Step-by-Step Deployment

### 1. Enable Model Access (REQUIRED)
```bash
# Go to AWS Bedrock Console
open https://console.aws.amazon.com/bedrock/
```

**In the console:**
1. Click **"Model access"** in left sidebar
2. Click **"Request model access"** 
3. Find **"Claude 3.5 Sonnet"** and enable it
4. Click **"Submit"** (approved instantly)

### 2. Test the Agent
```bash
# Test with bhagyesh credentials
python3 test_bhagyesh_calendar.py
```

### 3. AWS Console Test (Alternative)
1. Go to: https://console.aws.amazon.com/bedrock/
2. Navigate: **Agents** → **bhagyesh-calendar-assistant**
3. Click **"Test"**
4. Try: **"Hello bhagyesh!"**

## Test Queries
- "Hello bhagyesh!"
- "What's on my calendar today?"
- "Add a team meeting tomorrow at 2 PM"
- "Delete my 3 PM appointment"

## Files Created
- `bhagyesh_aws_credentials.json` - AWS credentials
- `bhagyesh_setup_complete.json` - Setup info
- `test_bhagyesh_calendar.py` - Test script

## Agent Details
- **Agent ID**: AE2NL4BTR0
- **Model**: anthropic.claude-3-5-sonnet-20241022-v2:0
- **Lambda**: bhagyesh-calendar-function
- **User**: bhagyesh (full permissions)

## If Issues Occur
```bash
# Clean up and redeploy
python3 cleanup_all.py
python3 setup_bhagyesh_complete.py
```