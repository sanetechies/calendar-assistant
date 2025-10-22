"""
Google Calendar Integration - Much easier than self-hosted options
"""

import json
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

class GoogleCalendarAI:
    """Google Calendar AI Integration"""
    
    def __init__(self):
        # Use service account or OAuth credentials
        self.service = self.get_calendar_service()
    
    def get_calendar_service(self):
        """Initialize Google Calendar service"""
        # Option 1: Service Account (recommended for server apps)
        from google.oauth2 import service_account
        
        credentials = service_account.Credentials.from_service_account_info({
            "type": "service_account",
            "project_id": os.environ.get('GOOGLE_PROJECT_ID'),
            "private_key": os.environ.get('GOOGLE_PRIVATE_KEY'),
            "client_email": os.environ.get('GOOGLE_CLIENT_EMAIL'),
            # ... other service account fields
        })
        
        return build('calendar', 'v3', credentials=credentials)
    
    def list_events(self, calendar_id='primary', max_results=10):
        """List calendar events"""
        
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        
        events_result = self.service.events().list(
            calendarId=calendar_id,
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        return {
            "events": [
                {
                    "id": event['id'],
                    "title": event.get('summary', 'No Title'),
                    "start": event['start'].get('dateTime', event['start'].get('date')),
                    "end": event['end'].get('dateTime', event['end'].get('date')),
                    "description": event.get('description', '')
                }
                for event in events
            ],
            "total": len(events)
        }
    
    def create_event(self, event_data):
        """Create a new calendar event"""
        
        event = {
            'summary': event_data.get('title', 'New Event'),
            'description': event_data.get('description', ''),
            'start': {
                'dateTime': event_data.get('start_time'),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': self.calculate_end_time(
                    event_data.get('start_time'), 
                    event_data.get('duration', 60)
                ),
                'timeZone': 'UTC',
            },
        }
        
        created_event = self.service.events().insert(
            calendarId='primary', 
            body=event
        ).execute()
        
        return {
            "success": True,
            "event": created_event,
            "message": f"Event '{event['summary']}' created successfully"
        }
    
    def find_slots(self, params):
        """Find available time slots using Google Calendar freebusy API"""
        
        duration = int(params.get('duration', 60))
        date = params.get('date', 'today')
        
        # Use freebusy query to find actual free slots
        if date == 'today':
            start_time = datetime.datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        elif date == 'tomorrow':
            start_time = datetime.datetime.now() + datetime.timedelta(days=1)
            start_time = start_time.replace(hour=9, minute=0, second=0, microsecond=0)
        else:
            start_time = datetime.datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        end_time = start_time.replace(hour=17)  # 5 PM
        
        freebusy_query = {
            'timeMin': start_time.isoformat() + 'Z',
            'timeMax': end_time.isoformat() + 'Z',
            'items': [{'id': 'primary'}]
        }
        
        freebusy_result = self.service.freebusy().query(body=freebusy_query).execute()
        busy_times = freebusy_result['calendars']['primary']['busy']
        
        # Calculate free slots
        free_slots = self.calculate_free_slots(start_time, end_time, busy_times, duration)
        
        return {
            "available_slots": free_slots[:3],
            "duration_minutes": duration,
            "date": date
        }
    
    def calculate_free_slots(self, start_time, end_time, busy_times, duration_minutes):
        """Calculate free time slots"""
        
        slots = []
        current_time = start_time
        
        for busy_period in busy_times:
            busy_start = datetime.datetime.fromisoformat(busy_period['start'].replace('Z', '+00:00'))
            busy_end = datetime.datetime.fromisoformat(busy_period['end'].replace('Z', '+00:00'))
            
            # Check if there's a free slot before this busy period
            if (busy_start - current_time).total_seconds() >= duration_minutes * 60:
                slots.append({
                    "start": current_time.strftime("%H:%M"),
                    "end": (current_time + datetime.timedelta(minutes=duration_minutes)).strftime("%H:%M"),
                    "date": current_time.strftime("%Y-%m-%d"),
                    "score": 90,
                    "reason": "Free slot detected"
                })
            
            current_time = max(current_time, busy_end)
        
        # Check for slot after last busy period
        if (end_time - current_time).total_seconds() >= duration_minutes * 60:
            slots.append({
                "start": current_time.strftime("%H:%M"),
                "end": (current_time + datetime.timedelta(minutes=duration_minutes)).strftime("%H:%M"),
                "date": current_time.strftime("%Y-%m-%d"),
                "score": 85,
                "reason": "End of day slot"
            })
        
        return slots
    
    def calculate_end_time(self, start_time, duration_minutes):
        """Calculate end time from start time and duration"""
        start = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end = start + datetime.timedelta(minutes=duration_minutes)
        return end.isoformat()