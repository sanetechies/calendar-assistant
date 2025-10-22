#!/usr/bin/env python3

import json
import boto3
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

def test_calendar_connection():
    """Test Google Calendar connection directly"""
    
    print("🔍 Testing Google Calendar Connection...")
    
    try:
        # Load credentials from AWS Secrets Manager
        print("📡 Loading credentials from AWS Secrets Manager...")
        secrets_client = boto3.client('secretsmanager', region_name='us-east-1')
        response = secrets_client.get_secret_value(SecretId='calendar-ai/google-credentials')
        config = json.loads(response['SecretString'])
        
        print(f"✅ Credentials loaded for: {config['client_email']}")
        print(f"📅 Calendar ID: {config['calendar_id']}")
        
        # Build service account credentials
        print("🔑 Building service account credentials...")
        credentials_info = {
            "type": "service_account",
            "project_id": config['project_id'],
            "private_key": config['private_key'].replace('\\n', '\n'),
            "client_email": config['client_email'],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{config['client_email']}"
        }
        
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info, scopes=['https://www.googleapis.com/auth/calendar']
        )
        
        # Build Calendar service
        print("🏗️ Building Google Calendar service...")
        service = build('calendar', 'v3', credentials=credentials)
        
        # Test calendar access
        print("📋 Testing calendar list access...")
        calendar_list = service.calendarList().list().execute()
        print(f"✅ Found {len(calendar_list.get('items', []))} calendars")
        
        for cal in calendar_list.get('items', []):
            print(f"  📅 {cal['summary']} (ID: {cal['id']})")
        
        # Test events for today
        print(f"\n📅 Testing events for calendar: {config['calendar_id']}")
        
        # Get today's date range
        today_start = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + datetime.timedelta(days=1)
        
        print(f"🕐 Date range: {today_start.isoformat()}Z to {today_end.isoformat()}Z")
        
        events_result = service.events().list(
            calendarId=config['calendar_id'],
            timeMin=today_start.isoformat() + 'Z',
            timeMax=today_end.isoformat() + 'Z',
            maxResults=20,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"📊 Found {len(events)} events for today")
        
        if events:
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(f"  🎯 {event.get('summary', 'No Title')} at {start}")
        else:
            print("  📭 No events found for today")
            
        # Test broader date range
        print(f"\n📅 Testing events for this week...")
        week_start = today_start - datetime.timedelta(days=3)
        week_end = today_start + datetime.timedelta(days=4)
        
        events_result = service.events().list(
            calendarId=config['calendar_id'],
            timeMin=week_start.isoformat() + 'Z',
            timeMax=week_end.isoformat() + 'Z',
            maxResults=50,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"📊 Found {len(events)} events this week")
        
        if events:
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(f"  🎯 {event.get('summary', 'No Title')} at {start}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_calendar_connection()