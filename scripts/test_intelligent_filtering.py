#!/usr/bin/env python3
"""Test script for intelligent LLM-powered filtering of SEC data."""

import asyncio
import os
import sys
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from filing_agent.core.anthropic_client import AnthropicSecAgent


async def test_intelligent_filtering():
    """Test the intelligent filtering capability with Hartford's combined ratio question."""
    
    print("🧪 Testing Intelligent LLM-Powered SEC Data Filtering")
    print("=" * 60)
    
    # Initialize the agent
    agent = AnthropicSecAgent()
    
    # Test cases that previously caused token limit errors
    test_cases = [
        {
            "question": "What is Hartford's combined ratio and how has it changed over time?",
            "description": "Insurance-specific metric that previously caused token overflow"
        },
        {
            "question": "Analyze Apple's revenue growth trends over the past 3 years",
            "description": "Revenue-focused analysis"
        },
        {
            "question": "What are Microsoft's main profit margins and how do they compare to industry averages?",
            "description": "Profitability analysis"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔬 Test Case {i}: {test_case['description']}")
        print(f"Question: {test_case['question']}")
        print("-" * 50)
        
        try:
            # This should now use intelligent filtering instead of returning massive datasets
            response = await agent.chat(test_case['question'])
            
            print(f"✅ Success! Response length: {len(response)} characters")
            print(f"📝 Response preview: {response[:300]}...")
            
            if len(response) > 500:
                print("🎯 Intelligent filtering appears to be working - got detailed analysis without token overflow")
            
        except Exception as e:
            if "context length" in str(e).lower() or "token" in str(e).lower():
                print(f"❌ Token limit error still occurred: {e}")
            else:
                print(f"⚠️ Other error: {e}")
        
        print()
    
    print("🏁 Intelligent filtering test completed!")
    print("\nKey improvements:")
    print("• LLM analyzes user question to identify relevant financial concepts")
    print("• Only relevant data is extracted from massive SEC datasets")
    print("• Fallback filtering for edge cases")
    print("• Automatic question context injection for get_company_facts calls")


async def test_filtering_comparison():
    """Compare old vs new approach with a specific example."""
    
    print("\n🔄 Testing Filtering Comparison")
    print("=" * 40)
    
    agent = AnthropicSecAgent()
    
    # Test the Hartford combined ratio question that previously failed
    print("Testing Hartford combined ratio question...")
    print("(This previously caused: 'prompt is too long: 220211 tokens > 200000 maximum')")
    
    try:
        response = await agent.chat("What is Hartford's combined ratio and how has it changed over recent years?")
        print(f"✅ Success! Got response of {len(response)} characters")
        print("🎯 The intelligent filtering successfully handled the large dataset!")
        
        # Show a preview of the response
        print(f"\n📋 Response preview:\n{response[:500]}...")
        
    except Exception as e:
        print(f"❌ Still failed: {e}")


if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable is required")
        print("Please set it in your .env file or environment")
        sys.exit(1)
    
    print("🚀 Starting intelligent filtering tests...")
    asyncio.run(test_intelligent_filtering())
    asyncio.run(test_filtering_comparison()) 