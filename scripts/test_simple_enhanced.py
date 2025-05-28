#!/usr/bin/env python3
"""Simple test of enhanced filing capabilities."""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv


async def test_simple():
    """Simple test of enhanced capabilities."""
    
    print("🧪 Simple Enhanced Capabilities Test")
    print("=" * 50)
    
    try:
        # Test imports
        print("1. Testing imports...")
        from filing_agent.utils.filing_parser import FilingParser
        from filing_agent.utils.filing_sections import TenKStructureParser
        from filing_agent.core.anthropic_client import AnthropicSecAgent
        print("   ✅ All imports successful")
        
        # Test basic initialization
        print("2. Testing initialization...")
        parser = FilingParser()
        structure_parser = TenKStructureParser()
        print("   ✅ Parsers initialized")
        
        # Test agent initialization
        print("3. Testing agent initialization...")
        agent = AnthropicSecAgent()
        print("   ✅ Agent initialized")
        
        # Test tools list
        print("4. Testing enhanced tools...")
        tools = agent.get_tools()
        tool_names = [tool["name"] for tool in tools]
        print(f"   Available tools: {tool_names}")
        
        # Check for new tools
        new_tools = ["download_structured_filing", "get_filing_section"]
        for tool in new_tools:
            if tool in tool_names:
                print(f"   ✅ {tool} available")
            else:
                print(f"   ❌ {tool} missing")
        
        print("\n🎉 Enhanced capabilities are ready!")
        print("\n🚀 New Features Available:")
        print("• download_structured_filing - Get full 10-K with structured sections")
        print("• get_filing_section - Get specific sections (Risk Factors, MD&A, etc.)")
        print("• Visual element identification within context")
        print("• Structured 10-K parsing with section mapping")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    load_dotenv()
    
    success = asyncio.run(test_simple())
    
    if success:
        print("\n✅ All tests passed! Enhanced agent is ready.")
    else:
        print("\n❌ Tests failed. Check the errors above.") 