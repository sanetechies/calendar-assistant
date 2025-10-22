import json
import os
from calendar_ai import CalendarAI

def lambda_handler(event, context):
    """API Gateway handler for Calendar AI"""
    
    print(f"API Event: {json.dumps(event)}")
    
    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    # Handle OPTIONS request for CORS
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'CORS preflight'})
        }
    
    try:
        # Initialize Calendar AI
        calendar_ai = CalendarAI()
        
        # Get path and method
        path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        
        # Parse request body
        body = {}
        if event.get('body'):
            try:
                body = json.loads(event['body'])
            except:
                body = {}
        
        # Route requests
        if path == '/' and method == 'GET':
            response_data = {
                'message': 'Nextcloud Calendar AI API',
                'version': '1.0',
                'endpoints': {
                    'POST /chat': 'Chat with AI assistant',
                    'GET /events': 'List calendar events',
                    'POST /events': 'Create calendar event',
                    'GET /slots': 'Find available slots',
                    'POST /reschedule': 'Reschedule meeting'
                }
            }
        
        elif path == '/events' and method == 'GET':
            response_data = calendar_ai.list_events()
        
        elif path == '/events' and method == 'POST':
            response_data = calendar_ai.create_event(body)
        
        elif path == '/slots' and method == 'GET':
            params = event.get('queryStringParameters', {}) or {}
            response_data = calendar_ai.find_slots(params)
        
        elif path == '/reschedule' and method == 'POST':
            response_data = calendar_ai.reschedule_meeting(body)
        
        else:
            response_data = {'error': 'Endpoint not found', 'path': path, 'method': method}
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps(response_data)
            }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        print(f"API Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }