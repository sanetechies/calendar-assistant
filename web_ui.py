#!/usr/bin/env python3
"""
Simple web UI for Calendar Assistant
"""

from flask import Flask, render_template, request, jsonify
import boto3
import uuid

app = Flask(__name__)

def call_calendar_agent(user_input):
    """Call the Calendar Assistant agent"""
    
    bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name="us-east-1")
    
    agent_id = "KIW1YTWQH6"  # Replace with your agent ID
    agent_alias_id = "TSTALIASID"  # Replace with your alias ID
    session_id = str(uuid.uuid4())
    
    try:
        response = bedrock_agent_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=user_input
        )
        
        result = ""
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    result += chunk['bytes'].decode('utf-8')
        
        return result
        
    except Exception as e:
        return f"Error: {e}"

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Calendar Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .chat-container { border: 1px solid #ddd; height: 400px; overflow-y: auto; padding: 10px; margin: 10px 0; }
            .input-container { display: flex; gap: 10px; }
            input[type="text"] { flex: 1; padding: 10px; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user { background: #e3f2fd; text-align: right; }
            .agent { background: #f5f5f5; }
        </style>
    </head>
    <body>
        <h1>🗓️ Calendar Assistant</h1>
        <div id="chat" class="chat-container"></div>
        <div class="input-container">
            <input type="text" id="userInput" placeholder="Ask about your calendar..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()">Send</button>
        </div>
        
        <script>
            function sendMessage() {
                const input = document.getElementById('userInput');
                const message = input.value.trim();
                if (!message) return;
                
                addMessage(message, 'user');
                input.value = '';
                
                fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                })
                .then(response => response.json())
                .then(data => addMessage(data.response, 'agent'));
            }
            
            function addMessage(text, sender) {
                const chat = document.getElementById('chat');
                const div = document.createElement('div');
                div.className = `message ${sender}`;
                div.textContent = text;
                chat.appendChild(div);
                chat.scrollTop = chat.scrollHeight;
            }
        </script>
    </body>
    </html>
    '''

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    agent_response = call_calendar_agent(user_message)
    return jsonify({'response': agent_response})

if __name__ == '__main__':
    print("Starting Calendar Assistant Web UI...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)