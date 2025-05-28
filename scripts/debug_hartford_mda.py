#!/usr/bin/env python3
"""Debug script to test Hartford MD&A extraction."""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from filing_agent.core.anthropic_client import AnthropicSecAgent


async def test_hartford_mda():
    """Test what we extract from Hartford's MD&A section."""
    agent = AnthropicSecAgent()
    
    print("🔍 Testing Hartford MD&A extraction...")
    
    result = agent.execute_tool('get_filing_section', {
        'cik': '0000874766',
        'section': 'item_7'
    })
    
    if result['success']:
        content = result['data']['section']['content']
        print(f'📄 MD&A Content Length: {len(content):,} characters')
        print(f'📄 Full Content Length: {result["data"]["section"]["full_content_length"]:,} characters')
        print()
        
        print("🔍 First 2000 characters:")
        print("-" * 50)
        print(content[:2000])
        print("-" * 50)
        print()
        
        print("🔍 Searching for Combined Ratio...")
        content_lower = content.lower()
        
        # Search for various insurance terms
        insurance_terms = [
            'combined ratio',
            'underwriting ratio',
            'loss ratio',
            'expense ratio',
            'property & casualty',
            'p&c',
            'underwriting'
        ]
        
        found_terms = []
        for term in insurance_terms:
            if term in content_lower:
                found_terms.append(term)
                pos = content_lower.find(term)
                print(f"✅ Found '{term}' at position {pos}")
                print(f"   Context: {content[max(0, pos-100):pos+200]}")
                print()
        
        if not found_terms:
            print("❌ No insurance-specific terms found in extracted content")
            print()
            print("🔍 Let's check what sections we did extract:")
            print("Sample content around middle:")
            mid = len(content) // 2
            print(content[mid-500:mid+500])
        
    else:
        print(f'❌ Error: {result["error"]}')


if __name__ == "__main__":
    asyncio.run(test_hartford_mda()) 