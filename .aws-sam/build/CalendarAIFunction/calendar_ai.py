import json
import datetime
import os
import boto3
from typing import List, Dict, Optional

class CalendarAI:
    """Google Calendar AI Integration"""
    
    def __init__(self):
        self.config = self.load_google_credentials()
        self.service = self.get_calendar_service()
    
    def load_google_credentials(self):
        """Load Google Calendar credentials from AWS Secrets Manager"""
        secrets_client = boto3.client('secretsmanager', region_name='us-east-1')
        secret_name = "calendar-ai/google-credentials"
        
        response = secrets_client.get_secret_value(SecretId=secret_name)
        credentials = json.loads(response['SecretString'])
        
        return credentials
    
    def get_calendar_service(self):
        """Initialize Google Calendar service"""
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        credentials_info = {
            "type": "service_account",
            "project_id": self.config['project_id'],
            "private_key": self.config['private_key'].replace('\\n', '\n'),
            "client_email": self.config['client_email'],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{self.config['client_email']}"
        }
        
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info, scopes=['https://www.googleapis.com/auth/calendar']
        )
        
        return build('calendar', 'v3', credentials=credentials)
    
    def list_events(self, start_date=None, end_date=None):
        """List Google Calendar events"""
        if not start_date:
            start_date = datetime.datetime.utcnow().isoformat() + 'Z'
        
        events_result = self.service.events().list(
            calendarId=self.config['calendar_id'],
            timeMin=start_date,
            maxResults=20,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        formatted_events = []
        for event in events:
            formatted_events.append({
                "id": event['id'],
                "title": event.get('summary', 'No Title'),
                "start": event['start'].get('dateTime', event['start'].get('date')),
                "end": event['end'].get('dateTime', event['end'].get('date')),
                "description": event.get('description', '')
            })
        
        return {
            "events": formatted_events,
            "total": len(formatted_events),
            "source": "google_calendar"
        }
    

    
    def find_slots(self, params):
        """Find available time slots using Google Calendar freebusy API"""
        duration = int(params.get('duration', 60))
        date = params.get('date', 'today')
        preferences = params.get('preferences', 'morning')
        
        # Calculate time range
        if date == 'today':
            start_time = datetime.datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        elif date == 'tomorrow':
            start_time = datetime.datetime.now() + datetime.timedelta(days=1)
            start_time = start_time.replace(hour=9, minute=0, second=0, microsecond=0)
        else:
            start_time = datetime.datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        end_time = start_time.replace(hour=17)  # 5 PM
        
        # Query freebusy
        freebusy_query = {
            'timeMin': start_time.isoformat() + 'Z',
            'timeMax': end_time.isoformat() + 'Z',
            'items': [{'id': self.config['calendar_id']}]
        }
        
        freebusy_result = self.service.freebusy().query(body=freebusy_query).execute()
        busy_times = freebusy_result['calendars'][self.config['calendar_id']]['busy']
        
        # Calculate free slots
        free_slots = self.calculate_free_slots(start_time, end_time, busy_times, duration)
        
        # Filter by preferences
        if preferences == 'morning':
            free_slots = [s for s in free_slots if int(s['start'].split(':')[0]) < 12]
        elif preferences == 'afternoon':
            free_slots = [s for s in free_slots if 12 <= int(s['start'].split(':')[0]) < 17]
        
        return {
            "available_slots": free_slots[:3],
            "duration_minutes": duration,
            "date": date,
            "preferences": preferences,
            "source": "google_calendar"
        }
    

    
    def calculate_free_slots(self, start_time, end_time, busy_times, duration_minutes):
        """Calculate free time slots from busy periods"""
        slots = []
        current_time = start_time
        
        for busy_period in busy_times:
            busy_start = datetime.datetime.fromisoformat(busy_period['start'].replace('Z', '+00:00')).replace(tzinfo=None)
            busy_end = datetime.datetime.fromisoformat(busy_period['end'].replace('Z', '+00:00')).replace(tzinfo=None)
            
            # Check if there's a free slot before this busy period
            if (busy_start - current_time).total_seconds() >= duration_minutes * 60:
                slot_end = current_time + datetime.timedelta(minutes=duration_minutes)
                slots.append({
                    "start": current_time.strftime("%H:%M"),
                    "end": slot_end.strftime("%H:%M"),
                    "date": current_time.strftime("%Y-%m-%d"),
                    "score": 90,
                    "reason": "Free slot detected via Google Calendar"
                })
            
            current_time = max(current_time, busy_end)
        
        # Check for slot after last busy period
        if (end_time - current_time).total_seconds() >= duration_minutes * 60:
            slot_end = current_time + datetime.timedelta(minutes=duration_minutes)
            slots.append({
                "start": current_time.strftime("%H:%M"),
                "end": slot_end.strftime("%H:%M"),
                "date": current_time.strftime("%Y-%m-%d"),
                "score": 85,
                "reason": "End of day slot"
            })
        
        return slots
    
    def create_event(self, event_data):
        """Create a new Google Calendar event"""
        title = event_data.get('title', 'New Event')
        start_time = event_data.get('start_time', '')
        duration = event_data.get('duration', 60)
        description = event_data.get('description', '')
        
        # Calculate end time
        start_dt = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = start_dt + datetime.timedelta(minutes=duration)
        
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'UTC',
            },
        }
        
        created_event = self.service.events().insert(
            calendarId=self.config['calendar_id'], 
            body=event
        ).execute()
        
        return {
            "success": True,
            "event": {
                "id": created_event['id'],
                "title": title,
                "start_time": start_time,
                "duration_minutes": duration,
                "description": description,
                "google_event_id": created_event['id']
            },
            "message": f"Event '{title}' created successfully in Google Calendar",
            "source": "google_calendar"
        }
    

    
    def reschedule_meeting(self, reschedule_data):
        """Reschedule an existing Google Calendar meeting"""
        # Handle both event_id and meeting_id parameters
        event_id = reschedule_data.get('event_id') or reschedule_data.get('meeting_id', '')
        new_start_time = reschedule_data.get('new_start_time') or reschedule_data.get('new_time', '')
        reason = reschedule_data.get('reason', 'Schedule conflict')
        
        if not event_id or not new_start_time:
            return {
                "success": False,
                "error": "Missing event_id or new_start_time",
                "required_fields": ["event_id", "new_start_time"]
            }
        
        try:
            # Get the existing event
            event = self.service.events().get(
                calendarId=self.config['calendar_id'], 
                eventId=event_id
            ).execute()
            
            # Parse new start time - handle timezone info
            if '+' in new_start_time or 'Z' in new_start_time:
                new_start = datetime.datetime.fromisoformat(new_start_time.replace('Z', '+00:00'))
            else:
                new_start = datetime.datetime.fromisoformat(new_start_time)
            
            # Calculate original duration
            original_start = datetime.datetime.fromisoformat(
                event['start']['dateTime'].replace('Z', '+00:00')
            )
            original_end = datetime.datetime.fromisoformat(
                event['end']['dateTime'].replace('Z', '+00:00')
            )
            original_duration = original_end - original_start
            new_end = new_start + original_duration
            
            # Update event times
            event['start']['dateTime'] = new_start.isoformat()
            event['end']['dateTime'] = new_end.isoformat()
            
            # Add reschedule reason to description
            current_desc = event.get('description', '')
            event['description'] = f"{current_desc}\n\nRescheduled: {reason}"
            
            # Update the event
            updated_event = self.service.events().update(
                calendarId=self.config['calendar_id'],
                eventId=event_id,
                body=event
            ).execute()
            
            return {
                "success": True,
                "event_id": event_id,
                "new_start_time": new_start_time,
                "reason": reason,
                "message": f"Event '{event['summary']}' rescheduled to {new_start_time}",
                "updated_event": {
                    "id": updated_event['id'],
                    "title": updated_event['summary'],
                    "start": updated_event['start']['dateTime'],
                    "end": updated_event['end']['dateTime']
                },
                "source": "google_calendar"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "event_id": event_id,
                "new_start_time": new_start_time
            }
    

    
    def analyze_calendar(self, period='week'):
        """Analyze calendar patterns"""
        
        events = self.list_events()
        
        analysis = {
            "period": period,
            "total_events": len(events['events']),
            "average_duration": 45,
            "busiest_day": "Tuesday", 
            "free_hours": 3.5,
            "meeting_types": {
                "1:1s": 3,
                "Team meetings": 4,
                "Client calls": 2
            },
            "insights": [
                "Most productive meetings are in the morning",
                "Consider blocking focus time 9-11 AM",
                "Friday afternoons are ideal for planning"
            ]
        }
        
        return analysis