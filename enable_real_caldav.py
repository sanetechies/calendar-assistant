#!/usr/bin/env python3
"""
Enable real CalDAV integration by updating Lambda environment variables
"""

import boto3
import json

def enable_real_caldav():
    """Update Lambda function to use real Nextcloud CalDAV"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Your Nextcloud configuration
    nextcloud_config = {
        'NEXTCLOUD_URL': 'https://your-nextcloud-instance.com',
        'NEXTCLOUD_USERNAME': 'your-username',
        'NEXTCLOUD_PASSWORD': 'your-app-password',  # Use app password, not login password
        'NEXTCLOUD_CALENDAR': 'personal'
    }
    
    print("🔧 Updating Lambda environment variables for real CalDAV...")
    
    try:
        # Update environment variables
        response = lambda_client.update_function_configuration(
            FunctionName='nextcloud-calendar-ai-api',
            Environment={
                'Variables': nextcloud_config
            }
        )
        
        print("✅ Environment variables updated!")
        print("📋 Configuration:")
        for key, value in nextcloud_config.items():
            if 'PASSWORD' in key:
                print(f"   {key}: {'*' * len(value)}")
            else:
                print(f"   {key}: {value}")
        
        print("\n🔄 Now update the calendar_ai.py to use real CalDAV calls")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    enable_real_caldav()