#!/usr/bin/env python3
"""Demo script showcasing the SEC filing agent with Anthropic tools."""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from filing_agent.core.anthropic_client import AnthropicSecAgent
from dotenv import load_dotenv


async def demo_agent():
    """Demonstrate the SEC agent capabilities."""
    
    print("🚀 SEC Filing Agent Demo")
    print("=" * 50)
    print("Claude can now directly request SEC data during conversations!")
    print()
    
    # Check environment
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not found")
        print("Please set your API key in .env file")
        return
    
    async with AnthropicSecAgent() as agent:
        
        demos = [
            {
                "title": "🍎 Apple Financial Analysis",
                "request": "What's Apple's latest revenue and how profitable are they?"
            },
            {
                "title": "🔍 Company Lookup",
                "request": "What's Tesla's ticker symbol and CIK?"
            },
            {
                "title": "📊 Quick Financial Check",
                "request": "Show me Microsoft's latest net income"
            }
        ]
        
        for i, demo in enumerate(demos, 1):
            print(f"Demo {i}: {demo['title']}")
            print("-" * 40)
            print(f"Request: '{demo['request']}'")
            print()
            
            try:
                response = await agent.chat(demo['request'])
                print("🤖 Agent Response:")
                print(response)
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("\n" + "="*50 + "\n")
        
        print("✨ Demo completed!")
        print()
        print("🎯 Key Features Demonstrated:")
        print("• Claude directly calls SEC API tools")
        print("• Real-time financial data retrieval")
        print("• Intelligent analysis and insights")
        print("• Conversational interface")


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(demo_agent()) 