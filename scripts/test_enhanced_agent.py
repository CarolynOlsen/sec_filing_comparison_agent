#!/usr/bin/env python3
"""Test the enhanced SEC agent with full filing download and structured analysis."""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from filing_agent.core.anthropic_client import AnthropicSecAgent
from dotenv import load_dotenv


async def test_enhanced_capabilities():
    """Test the enhanced SEC agent capabilities."""
    
    print("🚀 Enhanced SEC Filing Agent Test")
    print("=" * 60)
    print("Testing new capabilities:")
    print("✅ Quantitative analysis (XBRL data)")
    print("✅ Qualitative analysis (narrative sections)")
    print("✅ Visual element identification")
    print("✅ Structured 10-K parsing")
    print()
    
    # Initialize the agent
    agent = AnthropicSecAgent()
    
    print("🧪 Test 1: Comprehensive Analysis with Risk Factors")
    print("-" * 50)
    
    request1 = """Analyze Apple's latest financial performance AND their key risk factors. 
    I want both the quantitative metrics (revenue, profitability, ratios) and the qualitative 
    insights from their 10-K filing about what risks they're most concerned about."""
    
    print(f"Request: {request1}")
    print()
    
    try:
        response1 = await agent.chat(request1)
        print("🤖 Agent Response:")
        print(response1)
        print()
        
    except Exception as e:
        print(f"❌ Error in Test 1: {e}")
        print()
    
    print("=" * 60)
    print("🧪 Test 2: Business Strategy Analysis")
    print("-" * 50)
    
    request2 = """What is Microsoft's business strategy according to their latest 10-K? 
    Look at their Business section and MD&A to understand how they describe their 
    competitive advantages and strategic direction."""
    
    print(f"Request: {request2}")
    print()
    
    try:
        response2 = await agent.chat(request2)
        print("🤖 Agent Response:")
        print(response2)
        print()
        
    except Exception as e:
        print(f"❌ Error in Test 2: {e}")
        print()
    
    print("=" * 60)
    print("🧪 Test 3: Risk Comparison")
    print("-" * 50)
    
    request3 = """Compare the risk factors between Apple and Tesla. What are the main 
    differences in the types of risks each company faces according to their 10-K filings?"""
    
    print(f"Request: {request3}")
    print()
    
    try:
        response3 = await agent.chat(request3)
        print("🤖 Agent Response:")
        print(response3)
        print()
        
    except Exception as e:
        print(f"❌ Error in Test 3: {e}")
        print()
    
    print("=" * 60)
    print("✨ Enhanced Capabilities Demonstrated!")
    print()
    print("🎯 What We Now Have:")
    print("• Quantitative financial analysis (XBRL data)")
    print("• Qualitative narrative analysis (10-K sections)")
    print("• Risk factor identification and analysis")
    print("• Business strategy insights")
    print("• Management discussion and analysis")
    print("• Visual element identification in context")
    print("• Structured document parsing")
    print()
    print("🔥 This gives Claude access to BOTH:")
    print("📊 Numbers: Revenue, profits, ratios, trends")
    print("📝 Narratives: Risks, strategy, outlook, context")


async def test_specific_section():
    """Test extracting a specific section."""
    
    print("\n" + "=" * 60)
    print("🔍 Test: Specific Section Extraction")
    print("-" * 50)
    
    agent = AnthropicSecAgent()
    
    request = """Get just the Risk Factors section from Apple's latest 10-K. 
    What are their top 3 most significant risks?"""
    
    print(f"Request: {request}")
    print()
    
    try:
        response = await agent.chat(request)
        print("🤖 Agent Response:")
        print(response)
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    load_dotenv()
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not found in environment")
        print("Please add it to your .env file")
        sys.exit(1)
    
    print("🔑 API key found, starting tests...")
    print()
    
    # Run the tests
    asyncio.run(test_enhanced_capabilities())
    asyncio.run(test_specific_section()) 