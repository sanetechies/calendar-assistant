# 🤖 Intelligent Google Calendar AI Agent

[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange.svg)](https://aws.amazon.com/lambda/)
[![API Gateway](https://img.shields.io/badge/AWS-API%20Gateway-blue.svg)](https://aws.amazon.com/api-gateway/)
[![Google Calendar](https://img.shields.io/badge/Google-Calendar-blue.svg)](https://calendar.google.com/)
[![Claude AI](https://img.shields.io/badge/Claude-3.5%20Sonnet-purple.svg)](https://www.anthropic.com/claude)
[![AWS Secrets](https://img.shields.io/badge/AWS-Secrets%20Manager-green.svg)](https://aws.amazon.com/secrets-manager/)

**AI-powered Google Calendar API with intelligent scheduling and conflict resolution**

> **REST API + AI Chat Interface for smart calendar management**  
> **"Find me a 1-hour slot tomorrow morning"** → Smart slot detection  
> **"Reschedule my 3 PM meeting to later today"** → Intelligent rescheduling  
> **"Move all Friday meetings to next week"** → Bulk operations

## 🚀 Deployment Status

✅ **Successfully Deployed with Amazon Nova AI Integration!**

**API Base URL**: `https://eabzln975h.execute-api.us-east-1.amazonaws.com/prod/`  
**Chat Endpoint**: `https://eabzln975h.execute-api.us-east-1.amazonaws.com/prod/chat`  
**Lambda Function**: `arn:aws:lambda:us-east-1:525856937873:function:nextcloud-calendar-ai-api`  
**Stack**: `nextcloud-calendar-api`  
**Secrets**: `calendar-ai/google-credentials` (AWS Secrets Manager)  

## 🔗 API Endpoints

### REST API
```bash
# Get API info
GET https://eabzln975h.execute-api.us-east-1.amazonaws.com/prod/

# List calendar events
GET https://eabzln975h.execute-api.us-east-1.amazonaws.com/prod/events

# Create new event
POST https://eabzln975h.execute-api.us-east-1.amazonaws.com/prod/events

# Find available slots
GET https://eabzln975h.execute-api.us-east-1.amazonaws.com/prod/slots?duration=60&date=today

# Reschedule meeting
POST https://eabzln975h.execute-api.us-east-1.amazonaws.com/prod/reschedule
```

### AI Chat Interface
```bash
# Chat with AI assistant
POST https://eabzln975h.execute-api.us-east-1.amazonaws.com/prod/chat
```

## 💻 Usage Examples

### 1. Web UI Integration

```html
<!DOCTYPE html>
<html>
<head>
    <title>Calendar AI Assistant</title>
</head>
<body>
    <div id="chat-container">
        <div id="messages"></div>
        <input type="text" id="user-input" placeholder="Ask about your calendar...">
        <button onclick="sendMessage()">Send</button>
    </div>

    <script>
    const API_URL = 'https://eabzln975h.execute-api.us-east-1.amazonaws.com/prod';
    
    async function sendMessage() {
        const input = document.getElementById('user-input');
        const message = input.value;
        
        // Send to AI chat endpoint
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: message})
        });
        
        const result = await response.json();
        displayMessage(result.message);
        input.value = '';
    }
    
    function displayMessage(message) {
        const messages = document.getElementById('messages');
        messages.innerHTML += `<div>${message}</div>`;
    }
    </script>
</body>
</html>
```

### 2. Python Client

```python
import requests
import json

class CalendarAIClient:
    def __init__(self):
        self.base_url = 'https://eabzln975h.execute-api.us-east-1.amazonaws.com/prod'
    
    def chat(self, message):
        """Chat with AI assistant"""
        response = requests.post(
            f'{self.base_url}/chat',
            json={'message': message}
        )
        return response.json()
    
    def list_events(self):
        """Get calendar events"""
        response = requests.get(f'{self.base_url}/events')
        return response.json()
    
    def find_slots(self, duration=60, date='today'):
        """Find available time slots"""
        response = requests.get(
            f'{self.base_url}/slots',
            params={'duration': duration, 'date': date}
        )
        return response.json()
    
    def create_event(self, title, start_time, duration=60):
        """Create new calendar event"""
        response = requests.post(
            f'{self.base_url}/events',
            json={
                'title': title,
                'start_time': start_time,
                'duration': duration
            }
        )
        return response.json()

# Usage
client = CalendarAIClient()

# Chat with AI
result = client.chat("Find me a 1-hour slot tomorrow morning")
print(result['message'])

# List events
events = client.list_events()
print(f"Found {events['total']} events")

# Find slots
slots = client.find_slots(duration=60, date='tomorrow')
print(f"Available slots: {slots['available_slots']}")
```

### 3. Agent-to-Agent Integration

```python
# From another AWS Lambda or Bedrock Agent
import boto3
import json

def invoke_calendar_ai(message):
    """Call Calendar AI from another agent"""
    
    lambda_client = boto3.client('lambda')
    
    # Invoke the calendar AI function directly
    response = lambda_client.invoke(
        FunctionName='nextcloud-calendar-ai-api',
        Payload=json.dumps({
            'httpMethod': 'POST',
            'path': '/chat',
            'body': json.dumps({'message': message})
        })
    )
    
    result = json.loads(response['Payload'].read())
    return json.loads(result['body'])

# Usage in another agent
def my_agent_handler(event, context):
    user_request = event['inputText']
    
    if 'calendar' in user_request.lower():
        # Delegate to Calendar AI
        calendar_response = invoke_calendar_ai(user_request)
        return calendar_response['message']
    
    # Handle other requests...
```

### 4. Replit UI Widget Integration

```javascript
// Replit Calendar Widget for Natasha's Calendar
class NatashaCalendarWidget {
    constructor() {
        this.apiUrl = 'https://eabzln975h.execute-api.us-east-1.amazonaws.com/prod';
        this.init();
    }
    
    init() {
        this.createWidget();
        this.loadEvents();
    }
    
    createWidget() {
        const widget = document.createElement('div');
        widget.innerHTML = `
            <div id="natasha-calendar" style="border:1px solid #ccc; padding:20px; border-radius:8px;">
                <h3>📅 Natasha's Calendar Assistant</h3>
                <div id="calendar-events"></div>
                <input type="text" id="calendar-query" placeholder="Ask about calendar..." style="width:100%; margin:10px 0;">
                <button onclick="this.askCalendar()">Ask AI</button>
                <div id="ai-response" style="margin-top:10px; padding:10px; background:#f5f5f5;"></div>
            </div>
        `;
        document.body.appendChild(widget);
    }
    
    async loadEvents() {
        try {
            const response = await fetch(`${this.apiUrl}/events`);
            const data = await response.json();
            
            const eventsDiv = document.getElementById('calendar-events');
            eventsDiv.innerHTML = `
                <h4>Today's Events (${data.total})</h4>
                ${data.events.map(event => `
                    <div style="margin:5px 0; padding:5px; border-left:3px solid #007bff;">
                        <strong>${event.title}</strong><br>
                        <small>${new Date(event.start).toLocaleString()}</small>
                    </div>
                `).join('')}
            `;
        } catch (error) {
            console.error('Failed to load events:', error);
        }
    }
    
    async askCalendar() {
        const query = document.getElementById('calendar-query').value;
        const responseDiv = document.getElementById('ai-response');
        
        if (!query) return;
        
        responseDiv.innerHTML = 'Thinking...';
        
        try {
            const response = await fetch(`${this.apiUrl}/chat`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: query})
            });
            
            const data = await response.json();
            responseDiv.innerHTML = `<strong>AI:</strong> ${data.message}`;
            
            // Reload events if AI performed actions
            if (data.message.includes('created') || data.message.includes('scheduled')) {
                this.loadEvents();
            }
        } catch (error) {
            responseDiv.innerHTML = `Error: ${error.message}`;
        }
        
        document.getElementById('calendar-query').value = '';
    }
}

// Initialize widget when page loads
window.addEventListener('load', () => {
    new NatashaCalendarWidget();
});
```

**Replit Setup Instructions:**
1. Create new HTML/CSS/JS Repl
2. Add the widget code to your `script.js`
3. Widget automatically connects to Natasha's calendar via the API
4. Users can view events and chat with AI assistant
5. No authentication needed - API handles Google Calendar access

### 5. cURL Examples

```bash
# Chat with AI
curl -X POST https://eabzln975h.execute-api.us-east-1.amazonaws.com/prod/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What meetings do I have today?"}'

# List events
curl https://eabzln975h.execute-api.us-east-1.amazonaws.com/prod/events

# Find slots
curl "https://eabzln975h.execute-api.us-east-1.amazonaws.com/prod/slots?duration=60&date=tomorrow"

# Create event
curl -X POST https://eabzln975h.execute-api.us-east-1.amazonaws.com/prod/events \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Meeting",
    "start_time": "2024-01-15T14:00:00Z",
    "duration": 60
  }'
```

## 🧪 Test Queries

**AI Chat Examples:**
- *"What's on my calendar today?"*
- *"Find me a 1-hour slot tomorrow morning"*
- *"Reschedule my 3 PM meeting to 4 PM"*
- *"Analyze my calendar this week"*
- *"Create a team standup for tomorrow at 9 AM"*
- *"Move all Friday meetings to next week"*  

## 🔧 Configuration

### Google Calendar Setup

1. **Create Google Service Account**:
   ```bash
   # Run setup script
   python3 setup_google_secrets.py
   ```

2. **Configure Google Cloud**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create project → Enable Calendar API
   - Create service account → Download JSON key
   - Share your calendar with service account email

3. **Update AWS Secrets**:
   ```bash
   python3 update_google_secrets.py
   ```

4. **Deploy Updated Function**:
   ```bash
   sam build && sam deploy
   ```

### API Response Format

```json
{
  "message": "AI response or data",
  "timestamp": "2024-01-15T10:30:00Z",
  "status": "success"
}
```

## 🛡️ Security & Architecture

- **Serverless**: AWS Lambda + API Gateway
- **AI Integration**: Amazon Nova via Bedrock
- **Calendar Backend**: Google Calendar API
- **Secure Credentials**: AWS Secrets Manager
- **CORS Enabled**: Cross-origin requests supported
- **IAM Roles**: Least privilege access


## 🔍 Troubleshooting

**"Access denied when calling Bedrock"**
- Amazon Nova models are enabled by default
- No marketplace permissions required

**"Google Calendar connection failed"**
- Check AWS Secrets Manager for `calendar-ai/google-credentials`
- Verify service account JSON is valid
- Ensure calendar is shared with service account email

**"API Gateway timeout"**
- Check Lambda function logs in CloudWatch
- Verify Google Calendar API is enabled
- Check service account permissions

## 🧹 Cleanup

To remove all resources:
```bash
# Delete SAM stack
sam delete --stack-name nextcloud-calendar-api

# Or use CloudFormation
aws cloudformation delete-stack --stack-name nextcloud-calendar-api
```

## 🎉 Success

✅ **API Gateway**: REST endpoints deployed  
✅ **Lambda Functions**: Calendar AI + Chat handlers  
✅ **Nova Integration**: AI-powered responses  
✅ **Google Calendar**: API integration with secure credentials  
✅ **AWS Secrets**: Secure credential management  
✅ **CORS Enabled**: Web UI integration supported  
  

---

**Your Google Calendar AI API is ready!** 🚀

**Base URL**: `https://eabzln975h.execute-api.us-east-1.amazonaws.com/prod/`  
**Chat**: `https://eabzln975h.execute-api.us-east-1.amazonaws.com/prod/chat`  
**Lambda**: `arn:aws:lambda:us-east-1:525856937873:function:nextcloud-calendar-ai-api`  
**Calendar**: [View Calendar](https://calendar.google.com/calendar/u/1?cid=aHVtYW5lYWV5ZUBnbWFpbC5jb20)

## 📋 **Current Status**

- 🔐 **Secrets Manager**: `calendar-ai/google-credentials` created
- 🚀 **Deployment**: All endpoints active and responding
- 🤖 **AI Chat**: Amazon Nova integration ready
- 📅 **Calendar**: Google Calendar API integration (configure credentials)
