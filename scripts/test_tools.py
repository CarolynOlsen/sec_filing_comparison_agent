#!/usr/bin/env python3
"""Simple test for the tool-enabled SEC agent."""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from filing_agent.core.anthropic_client import AnthropicSecAgent
from dotenv import load_dotenv


async def test_tools():
    """Test the SEC agent with tools."""
    
    print("🧪 Testing SEC Agent with Anthropic Tools")
    print("=" * 50)
    
    # Check environment
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not found")
        return
    
    print("✅ Environment configured")
    print("🤖 Creating SEC agent...")
    
    try:
        async with AnthropicSecAgent() as agent:
            print("✅ Agent created successfully")
            print()
            
            # Test 1: Simple lookup
            print("📝 Test 1: Company lookup")
            print("Request: 'What's Apple's ticker symbol?'")
            print()
            
            response1 = await agent.chat("What's Apple's ticker symbol?")
            print("🤖 Response:")
            print(response1)
            print("\n" + "="*50 + "\n")
            
            # Test 2: Financial analysis
            print("📝 Test 2: Financial analysis")
            print("Request: 'Analyze Apple's latest revenue and profitability'")
            print()
            
            response2 = await agent.chat("Analyze Apple's latest revenue and profitability")
            print("🤖 Response:")
            print(response2)
            print("\n" + "="*50 + "\n")
            
            # Test 3: Company comparison
            print("📝 Test 3: Company comparison")
            print("Request: 'Compare Apple and Microsoft profit margins'")
            print()
            
            response3 = await agent.chat("Compare Apple and Microsoft profit margins")
            print("🤖 Response:")
            print(response3)
            print("\n" + "="*50 + "\n")
            
            print("✅ All tests completed successfully!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(test_tools()) 