#!/usr/bin/env python3
"""Quick interactive chat with the enhanced SEC filing agent."""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from filing_agent.core.anthropic_client import AnthropicSecAgent
from dotenv import load_dotenv


async def quick_chat():
    """Simple interactive chat with the SEC agent."""
    
    print("🚀 Enhanced SEC Filing Agent - Quick Chat")
    print("=" * 60)
    print("✨ NEW: Now with full 10-K analysis capabilities!")
    print()
    print("💡 Try these enhanced requests:")
    print("• 'Analyze Apple's financial performance AND risk factors'")
    print("• 'What are Tesla's main business risks according to their 10-K?'")
    print("• 'Compare Microsoft and Google's business strategies'")
    print("• 'Show me Amazon's revenue trends and management outlook'")
    print()
    print("📊 Or stick with quantitative analysis:")
    print("• 'What's Apple's profit margin?'")
    print("• 'Compare Microsoft and Amazon profitability'")
    print()
    print("Type 'quit' to exit")
    print("-" * 60)
    
    # Initialize agent
    agent = AnthropicSecAgent()
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 Agent: ", end="", flush=True)
            
            # Get response from agent
            response = await agent.chat(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'quit' to exit.")


if __name__ == "__main__":
    load_dotenv()
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not found in environment")
        print("Please add it to your .env file")
        sys.exit(1)
    
    print("🔑 API key found, starting chat...")
    asyncio.run(quick_chat()) 