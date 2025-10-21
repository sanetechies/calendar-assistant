import json
import boto3
from calendar_ai import CalendarAI

def lambda_handler(event, context):
    """Chat handler with Amazon Nova integration"""
    
    print(f"Chat Event: {json.dumps(event)}")
    
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        user_message = body.get('message', '')
        
        if not user_message:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Message is required'})
            }
        
        # Initialize services
        calendar_ai = CalendarAI()
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Get calendar context
        events = calendar_ai.list_events()
        calendar_context = f"Current calendar events: {json.dumps(events, indent=2)}"
        
        # Prepare Nova prompt
        system_prompt = """You are an intelligent Calendar AI assistant. You help users manage their calendar with these capabilities:

🔍 FIND SLOTS: Analyze calendar to find optimal meeting times
🔄 RESCHEDULE: Move meetings with minimal disruption
📊 ANALYZE: Provide calendar insights and patterns
📅 MANAGE: Create, update, and delete events

Available functions:
- list_events(): Get current calendar events
- find_slots(duration, date, preferences): Find available time slots
- create_event(title, start_time, duration): Create new events
- reschedule_meeting(meeting_id, new_time): Move existing meetings

Always be helpful, proactive, and explain your reasoning. Suggest specific actions when possible."""
        
        # Create Nova request
        nova_request = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": f"System: {system_prompt}\n\nCalendar Context:\n{calendar_context}\n\nUser Request: {user_message}"
                        }
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 1000,
                "temperature": 0.7
            }
        }
        
        # Call Amazon Nova
        response = bedrock.invoke_model(
            modelId='amazon.nova-lite-v1:0',
            body=json.dumps(nova_request)
        )
        
        # Parse Nova response
        response_body = json.loads(response['body'].read())
        ai_message = response_body['output']['message']['content'][0]['text']
        
        # Check if AI wants to perform actions
        ai_response = process_ai_actions(ai_message, calendar_ai)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': ai_response,
                'timestamp': context.aws_request_id
            })
        }
        
    except Exception as e:
        print(f"Chat Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }

def process_ai_actions(ai_message, calendar_ai):
    """Process any actions the AI wants to perform"""
    
    # Simple action detection (in production, use more sophisticated parsing)
    if "find_slots" in ai_message.lower():
        # Extract parameters and call find_slots
        slots = calendar_ai.find_slots({'duration': '60', 'date': 'today'})
        return f"{ai_message}\n\nAvailable slots: {json.dumps(slots, indent=2)}"
    
    elif "create_event" in ai_message.lower():
        # In production, extract event details from AI message
        return f"{ai_message}\n\n(Event creation would be processed here)"
    
    return ai_message