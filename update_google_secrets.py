#!/usr/bin/env python3
"""
Update Google Calendar credentials in AWS Secrets Manager
"""

import boto3
import json
import os

def update_google_secrets():
    """Update AWS secret with real Google Calendar credentials"""
    
    secrets_client = boto3.client('secretsmanager', region_name='us-east-1')
    secret_name = "calendar-ai/google-credentials"
    
    print("🔐 Updating Google Calendar credentials")
    print("=" * 50)
    
    # Check if service account JSON file exists
    json_file = input("📁 Enter path to downloaded service account JSON file: ").strip()
    
    if not os.path.exists(json_file):
        print(f"❌ File not found: {json_file}")
        return
    
    try:
        # Read the service account JSON
        with open(json_file, 'r') as f:
            service_account_data = json.load(f)
        
        # Extract required fields
        google_credentials = {
            "project_id": service_account_data["project_id"],
            "client_email": service_account_data["client_email"],
            "private_key": service_account_data["private_key"],
            "calendar_id": "primary"  # or specific calendar ID
        }
        
        # Update the secret
        secrets_client.update_secret(
            SecretId=secret_name,
            SecretString=json.dumps(google_credentials)
        )
        
        print("✅ Google Calendar credentials updated in AWS Secrets Manager")
        print(f"📧 Service Account: {google_credentials['client_email']}")
        print(f"🆔 Project ID: {google_credentials['project_id']}")
        
        print("\n📝 Next steps:")
        print("1. Share your Google Calendar with the service account email")
        print("2. Deploy updated Lambda function")
        print("3. Test the integration")
        
        # Clean up - optionally delete the JSON file
        delete_file = input("\n🗑️ Delete the JSON file for security? (y/n): ").lower()
        if delete_file == 'y':
            os.remove(json_file)
            print("✅ JSON file deleted")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def share_calendar_instructions():
    """Print calendar sharing instructions"""
    
    print("\n📅 Calendar Sharing Instructions:")
    print("=" * 35)
    print("1. Open Google Calendar: https://calendar.google.com/")
    print("2. Click Settings (gear icon) → Settings")
    print("3. Select your calendar → 'Share with specific people'")
    print("4. Click 'Add people'")
    print("5. Enter the service account email")
    print("6. Set permission to 'Make changes to events'")
    print("7. Click 'Send'")

if __name__ == "__main__":
    update_google_secrets()
    share_calendar_instructions()