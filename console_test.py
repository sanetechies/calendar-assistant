#!/usr/bin/env python3
"""
Instructions for testing via AWS Console
"""

def console_instructions():
    print("🎯 Test your Calendar Assistant via AWS Console:")
    print("=" * 50)
    print()
    print("1. Go to: https://console.aws.amazon.com/bedrock/")
    print("2. Navigate to: Agents → calendar-assistant")
    print("3. Click 'Test' button")
    print("4. Try these queries:")
    print("   • 'What's on my calendar today?'")
    print("   • 'Schedule a meeting tomorrow at 2 PM'")
    print("   • 'Hello'")
    print()
    print("If it works in console but not via API:")
    print("• Your AWS user needs bedrock:InvokeAgent permission")
    print("• Go to IAM → Users → Your User → Add permissions")
    print("• Attach policy: AmazonBedrockFullAccess")
    print()
    print("Agent Details:")
    print(f"• Agent ID: KIW1YTWQH6")
    print(f"• Alias ID: TSTALIASID")
    print(f"• Region: us-east-1")

if __name__ == "__main__":
    console_instructions()