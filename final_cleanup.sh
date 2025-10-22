#!/bin/bash

echo "🔥 Final cleanup - Manual resource deletion"
echo "=========================================="

# Delete any remaining Lambda functions
echo "Deleting remaining Lambda functions..."
aws lambda list-functions --query 'Functions[?contains(FunctionName, `nextcloud`) || contains(FunctionName, `calendar`) || contains(FunctionName, `bedrock`)].FunctionName' --output text | xargs -I {} aws lambda delete-function --function-name {} 2>/dev/null

# Delete any remaining Bedrock agents
echo "Deleting remaining Bedrock agents..."
aws bedrock-agent list-agents --query 'agentSummaries[?contains(agentName, `nextcloud`) || contains(agentName, `calendar`)].agentId' --output text | xargs -I {} aws bedrock-agent delete-agent --agent-id {} 2>/dev/null

# Force delete the CloudFormation stack (ignore failures)
echo "Force deleting CloudFormation stack..."
aws cloudformation delete-stack --stack-name nextcloud-calendar-ai 2>/dev/null

# Wait and check
sleep 30
aws cloudformation describe-stacks --stack-name nextcloud-calendar-ai 2>/dev/null || echo "✅ Stack successfully deleted!"

echo "🎉 Cleanup complete!"