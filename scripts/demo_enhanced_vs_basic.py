#!/usr/bin/env python3
"""Demo: Enhanced vs Basic SEC Analysis Capabilities."""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from filing_agent.core.anthropic_client import AnthropicSecAgent
from dotenv import load_dotenv


async def demo_comparison():
    """Demonstrate the difference between basic and enhanced analysis."""
    
    print("🔍 SEC Analysis: Basic vs Enhanced Capabilities")
    print("=" * 70)
    
    agent = AnthropicSecAgent()
    
    print("📊 BASIC ANALYSIS (XBRL Data Only)")
    print("-" * 40)
    print("What we could do before:")
    print("• Financial ratios and trends")
    print("• Revenue, profit, asset analysis")
    print("• Quantitative comparisons")
    print()
    
    basic_request = "What's Apple's latest revenue and profit margin?"
    print(f"Example request: {basic_request}")
    print()
    
    try:
        basic_response = await agent.chat(basic_request)
        print("🤖 Basic Response:")
        print(basic_response[:500] + "..." if len(basic_response) > 500 else basic_response)
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
    
    print("=" * 70)
    print("🚀 ENHANCED ANALYSIS (XBRL + Full 10-K)")
    print("-" * 40)
    print("What we can do now:")
    print("• Everything above PLUS:")
    print("• Risk factor analysis")
    print("• Business strategy insights")
    print("• Management commentary")
    print("• Competitive analysis")
    print("• Forward-looking statements")
    print("• Visual element identification")
    print()
    
    enhanced_request = """Analyze Apple comprehensively: their financial performance, 
    key risk factors, and business strategy. What are their main competitive advantages 
    and biggest concerns according to their latest 10-K?"""
    
    print(f"Example request: {enhanced_request}")
    print()
    
    try:
        enhanced_response = await agent.chat(enhanced_request)
        print("🤖 Enhanced Response:")
        print(enhanced_response)
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
    
    print("=" * 70)
    print("🎯 KEY DIFFERENCES")
    print("-" * 40)
    print("Basic Analysis:")
    print("• ✅ 'Apple's revenue is $96.995B with 24.3% profit margin'")
    print("• ❌ No context on WHY or WHAT RISKS affect this")
    print()
    print("Enhanced Analysis:")
    print("• ✅ 'Apple's revenue is $96.995B with 24.3% profit margin'")
    print("• ✅ 'Key risks include supply chain disruption, China regulations...'")
    print("• ✅ 'Management strategy focuses on services growth...'")
    print("• ✅ 'Competitive advantages include ecosystem lock-in...'")
    print()
    print("🔥 Result: Complete investment analysis, not just numbers!")


if __name__ == "__main__":
    load_dotenv()
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not found in environment")
        print("Please add it to your .env file")
        sys.exit(1)
    
    print("🔑 Starting enhanced vs basic demo...")
    print()
    
    asyncio.run(demo_comparison()) 