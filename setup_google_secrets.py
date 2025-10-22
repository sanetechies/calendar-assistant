#!/usr/bin/env python3
"""
Setup Google Calendar credentials in AWS Secrets Manager
"""

import boto3
import json

def setup_google_secrets():
    """Create AWS secret for Google Calendar credentials"""
    
    secrets_client = boto3.client('secretsmanager', region_name='us-east-1')
    
    print("🔐 Setting up Google Calendar credentials in AWS Secrets Manager")
    print("=" * 60)
    
    # You'll need to fill these in after creating the Google service account
    google_credentials = {
        "project_id": "your-google-project-id",
        "client_email": "calendar-ai@your-project.iam.gserviceaccount.com",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
        "calendar_id": "primary"
    }
    
    secret_name = "calendar-ai/google-credentials"
    
    try:
        # Create the secret
        response = secrets_client.create_secret(
            Name=secret_name,
            Description="Google Calendar API credentials for Calendar AI",
            SecretString=json.dumps(google_credentials)
        )
        
        print(f"✅ Secret created: {secret_name}")
        print(f"📋 Secret ARN: {response['ARN']}")
        
    except secrets_client.exceptions.ResourceExistsException:
        # Update existing secret
        secrets_client.update_secret(
            SecretId=secret_name,
            SecretString=json.dumps(google_credentials)
        )
        print(f"✅ Secret updated: {secret_name}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print("\n📝 Next steps:")
    print("1. Go to Google Cloud Console (opened in browser)")
    print("2. Create service account and download JSON key")
    print("3. Run: python3 update_google_secrets.py")
    print("4. Deploy updated Lambda with secrets access")

def create_google_project_instructions():
    """Print Google Cloud setup instructions"""
    
    print("\n🔧 Google Cloud Setup Instructions:")
    print("=" * 40)
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Create new project or select existing")
    print("3. Enable Google Calendar API:")
    print("   - APIs & Services → Library")
    print("   - Search 'Google Calendar API'")
    print("   - Click Enable")
    print("4. Create Service Account:")
    print("   - APIs & Services → Credentials")
    print("   - Create Credentials → Service Account")
    print("   - Name: calendar-ai-service")
    print("   - Create & Continue → Done")
    print("5. Generate Key:")
    print("   - Click service account email")
    print("   - Keys tab → Add Key → Create New Key")
    print("   - Select JSON → Create")
    print("6. Share Calendar:")
    print("   - Open Google Calendar")
    print("   - Settings → Share with specific people")
    print("   - Add service account email")
    print("   - Give 'Make changes to events' permission")

if __name__ == "__main__":
    setup_google_secrets()
    create_google_project_instructions()