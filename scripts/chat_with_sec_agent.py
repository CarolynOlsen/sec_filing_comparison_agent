#!/usr/bin/env python3
"""Interactive chat with the SEC filing agent using Anthropic tools."""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from filing_agent.core.anthropic_client import AnthropicSecAgent
from dotenv import load_dotenv


async def demo_conversations():
    """Demonstrate various conversations with the SEC agent."""
    
    print("🚀 SEC Filing Agent with Anthropic Tools")
    print("=" * 60)
    print("Claude can now directly request SEC data during conversations!")
    print()
    
    async with AnthropicSecAgent() as agent:
        
        # Demo 1: Simple company analysis
        print("💬 Demo 1: Analyzing Apple")
        print("-" * 40)
        response1 = await agent.chat("Analyze Apple's latest financial performance")
        print("🤖 Agent:", response1)
        print("\n" + "="*60 + "\n")
        
        # Demo 2: Company comparison
        print("💬 Demo 2: Comparing companies")
        print("-" * 40)
        response2 = await agent.chat("Compare Microsoft and Google's profitability")
        print("🤖 Agent:", response2)
        print("\n" + "="*60 + "\n")
        
        # Demo 3: Specific metric request
        print("💬 Demo 3: Specific financial metric")
        print("-" * 40)
        response3 = await agent.chat("What's Tesla's revenue growth over the past few years?")
        print("🤖 Agent:", response3)
        print("\n" + "="*60 + "\n")


async def interactive_chat():
    """Interactive chat session with the SEC agent."""
    
    print("🚀 Interactive SEC Filing Agent")
    print("=" * 50)
    print("Ask me anything about SEC filings! Examples:")
    print("• 'Analyze Apple's financials'")
    print("• 'Compare Microsoft and Amazon'") 
    print("• 'What's Tesla's profit margin?'")
    print("• 'Show me Google's revenue trends'")
    print()
    print("Type 'quit' to exit")
    print("-" * 50)
    
    conversation_history = []
    
    async with AnthropicSecAgent() as agent:
        while True:
            try:
                # Get user input
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("🤖 Agent: ", end="", flush=True)
                
                # Get response from agent
                response = await agent.chat(user_input, conversation_history)
                print(response)
                
                # Update conversation history
                conversation_history.append({"role": "user", "content": user_input})
                conversation_history.append({"role": "assistant", "content": response})
                
                # Keep conversation history manageable
                if len(conversation_history) > 10:
                    conversation_history = conversation_history[-8:]
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


async def quick_test():
    """Quick test to verify the agent works."""
    
    print("🧪 Quick Test: SEC Agent with Tools")
    print("=" * 40)
    
    async with AnthropicSecAgent() as agent:
        # Simple test
        print("Testing with: 'What's Apple's ticker symbol and latest revenue?'")
        print()
        
        response = await agent.chat("What's Apple's ticker symbol and latest revenue?")
        print("🤖 Response:")
        print(response)


async def main():
    """Main function to choose demo mode."""
    
    # Check environment
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not found in environment")
        print("Please set your API key in .env file")
        return
    
    if not os.getenv("SEC_USER_AGENT"):
        print("⚠️  SEC_USER_AGENT not set, using default")
        print("For production, set SEC_USER_AGENT in .env file")
        print()
    
    print("Choose a mode:")
    print("1. Quick test")
    print("2. Demo conversations")
    print("3. Interactive chat")
    print()
    
    try:
        choice = input("Enter choice (1-3): ").strip()
        print()
        
        if choice == "1":
            await quick_test()
        elif choice == "2":
            await demo_conversations()
        elif choice == "3":
            await interactive_chat()
        else:
            print("Invalid choice. Running quick test...")
            await quick_test()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main()) 