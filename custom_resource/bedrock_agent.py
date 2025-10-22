import json
import boto3
import cfnresponse
import time

def handler(event, context):
    """Custom resource handler for Bedrock Agent creation"""
    
    print(f"Custom Resource Event: {json.dumps(event)}")
    
    bedrock_agent = boto3.client('bedrock-agent')
    
    try:
        if event['RequestType'] == 'Create':
            response_data = create_bedrock_agent(event['ResourceProperties'], bedrock_agent)
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)
            
        elif event['RequestType'] == 'Update':
            response_data = update_bedrock_agent(event['ResourceProperties'], bedrock_agent)
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)
            
        elif event['RequestType'] == 'Delete':
            delete_bedrock_agent(event['ResourceProperties'], bedrock_agent)
            cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
            
    except Exception as e:
        print(f"Error: {str(e)}")
        cfnresponse.send(event, context, cfnresponse.FAILED, {})

def create_bedrock_agent(properties, bedrock_agent):
    """Create Bedrock Agent and Action Groups"""
    
    # Create agent
    agent_response = bedrock_agent.create_agent(
        agentName=properties['AgentName'],
        description=properties['AgentDescription'],
        foundationModel=properties['FoundationModel'],
        instruction="""You are an intelligent Nextcloud Calendar AI assistant with advanced scheduling capabilities:

🎯 CORE FUNCTIONS:
1. SMART SLOT FINDING: Analyze calendar patterns to find optimal meeting times
2. INTELLIGENT RESCHEDULING: Move meetings with minimal workflow disruption  
3. CONFLICT RESOLUTION: Proactively identify and resolve scheduling conflicts
4. PATTERN ANALYSIS: Learn user preferences and suggest improvements

🧠 INTELLIGENCE FEATURES:
- Understand context and urgency of meetings
- Consider attendee availability and time zones
- Optimize for productivity and work-life balance
- Suggest bulk operations for efficiency

Always be proactive, explain your reasoning, and provide multiple options when possible.""",
        agentResourceRoleArn=properties['AgentRoleArn']
    )
    
    agent_id = agent_response['agent']['agentId']
    print(f"Created agent: {agent_id}")
    
    # Wait for agent creation
    time.sleep(20)
    
    # Create action group
    bedrock_agent.create_agent_action_group(
        agentId=agent_id,
        agentVersion="DRAFT",
        actionGroupName="NextcloudCalendarActions",
        description="Intelligent Nextcloud Calendar management actions",
        actionGroupExecutor={
            "lambda": properties['LambdaFunctionArn']
        },
        functionSchema={
            "functions": [
                {
                    "name": "findAvailableSlots",
                    "description": "Find available time slots with intelligent scheduling",
                    "parameters": {
                        "duration": {"type": "string", "description": "Meeting duration in minutes"},
                        "date": {"type": "string", "description": "Preferred date"},
                        "preferences": {"type": "string", "description": "Time preferences"}
                    }
                },
                {
                    "name": "rescheduleMeeting",
                    "description": "Intelligently reschedule existing meetings",
                    "parameters": {
                        "meeting_id": {"type": "string", "description": "Meeting title or ID"},
                        "new_time": {"type": "string", "description": "New preferred time"},
                        "reason": {"type": "string", "description": "Reason for rescheduling"}
                    }
                },
                {
                    "name": "analyzeCalendar",
                    "description": "Analyze calendar patterns and provide insights",
                    "parameters": {
                        "period": {"type": "string", "description": "Analysis period"}
                    }
                },
                {
                    "name": "suggestOptimalTime",
                    "description": "AI-powered optimal meeting time suggestions",
                    "parameters": {
                        "attendees": {"type": "string", "description": "Attendee list"},
                        "duration": {"type": "string", "description": "Meeting duration"},
                        "urgency": {"type": "string", "description": "Meeting urgency"}
                    }
                },
                {
                    "name": "listEvents",
                    "description": "List calendar events",
                    "parameters": {
                        "date": {"type": "string", "description": "Date to list events"}
                    }
                },
                {
                    "name": "createEvent",
                    "description": "Create new calendar events",
                    "parameters": {
                        "title": {"type": "string", "description": "Event title"},
                        "start_time": {"type": "string", "description": "Start time"},
                        "duration": {"type": "string", "description": "Duration"}
                    }
                }
            ]
        }
    )
    
    print("Created action group")
    
    # Prepare agent
    bedrock_agent.prepare_agent(agentId=agent_id)
    print("Agent prepared")
    
    return {"AgentId": agent_id}

def update_bedrock_agent(properties, bedrock_agent):
    """Update existing Bedrock Agent"""
    # Implementation for updates
    return {"AgentId": properties.get('AgentId', '')}

def delete_bedrock_agent(properties, bedrock_agent):
    """Delete Bedrock Agent"""
    agent_id = properties.get('AgentId')
    if agent_id:
        try:
            bedrock_agent.delete_agent(agentId=agent_id)
            print(f"Deleted agent: {agent_id}")
        except Exception as e:
            print(f"Error deleting agent: {e}")