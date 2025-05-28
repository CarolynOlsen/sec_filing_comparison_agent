#!/usr/bin/env python3
"""Debug script to see what sections are found in Hartford's 10-K."""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from filing_agent.core.anthropic_client import AnthropicSecAgent


async def debug_hartford_sections():
    """Debug what sections we can find in Hartford's 10-K."""
    agent = AnthropicSecAgent()
    
    print("🔍 Debugging Hartford 10-K section extraction...")
    
    # First, let's try to download the full structured filing
    result = agent.execute_tool('download_structured_filing', {
        'cik': '0000874766',
        'include_sections': ['all']
    })
    
    if result['success']:
        data = result['data']
        print(f"✅ Successfully downloaded filing from: {data['filing_url']}")
        print(f"📄 Filing Date: {data['filing_info']['filing_date']}")
        print()
        
        sections = data['sections']
        print(f"📋 Found {len(sections)} sections:")
        for section_id, section_data in sections.items():
            content_length = len(section_data.get('content', '')) if isinstance(section_data, dict) else len(str(section_data))
            title = section_data.get('title', 'Unknown') if isinstance(section_data, dict) else 'Unknown'
            print(f"  - {section_id}: {title} ({content_length:,} chars)")
        print()
        
        if not sections:
            print("❌ No sections found! Let's check the raw content...")
            
            # Let's manually check what's in the filing
            filing_url = data['filing_url']
            filing_content = agent.filing_parser.download_filing_content(filing_url)
            
            print(f"📄 Raw filing content length: {len(filing_content):,} characters")
            print()
            print("🔍 First 3000 characters of raw content:")
            print("-" * 60)
            print(filing_content[:3000])
            print("-" * 60)
            print()
            
            # Search for section patterns manually
            content_lower = filing_content.lower()
            
            section_patterns = [
                'item 1',
                'item 1.',
                'item 1a',
                'item 1a.',
                'item 7',
                'item 7.',
                'management.*discussion',
                'md&a',
                'business',
                'risk factors',
                'combined ratio',
                'underwriting'
            ]
            
            print("🔍 Searching for section patterns in raw content:")
            for pattern in section_patterns:
                if pattern in content_lower:
                    pos = content_lower.find(pattern)
                    print(f"✅ Found '{pattern}' at position {pos:,}")
                    # Show context
                    context = filing_content[max(0, pos-100):pos+300]
                    print(f"   Context: {context[:200]}...")
                    print()
                else:
                    print(f"❌ '{pattern}' not found")
        
    else:
        print(f'❌ Error downloading filing: {result["error"]}')


if __name__ == "__main__":
    asyncio.run(debug_hartford_sections()) 