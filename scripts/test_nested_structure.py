#!/usr/bin/env python3
"""Test script for the new nested filing structure."""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from filing_agent.core.anthropic_client import AnthropicSecAgent


async def test_nested_structure():
    """Test the new nested filing structure with Hartford."""
    agent = AnthropicSecAgent()
    
    print("🧪 Testing Nested Filing Structure")
    print("=" * 60)
    
    # Test 1: Download full structured filing
    print("📄 Test 1: Download full structured filing...")
    result = agent.execute_tool('download_structured_filing', {
        'cik': '0000874766'
    })
    
    if result['success']:
        data = result['data']
        print(f"✅ Successfully parsed filing")
        print(f"📄 Total content length: {data['total_length']:,} characters")
        print(f"📋 Structure found:")
        
        for part_id, part_info in data['structure_summary'].items():
            print(f"  - {part_id}: {part_info['title']}")
            if 'subsections_found' in part_info:
                for subsection in part_info['subsections_found']:
                    print(f"    └─ {subsection}")
        print()
    else:
        print(f"❌ Error: {result['error']}")
        return
    
    # Test 2: Get specific section (MD&A)
    print("📄 Test 2: Get MD&A section (part_2.item_7)...")
    result = agent.execute_tool('get_filing_section', {
        'cik': '0000874766',
        'section_path': 'part_2.item_7'
    })
    
    if result['success']:
        section_data = result['data']['section']
        print(f"✅ Found section: {section_data['title']}")
        print(f"📄 Content length: {section_data['full_content_length']:,} characters")
        print(f"🎯 Purpose: {section_data['purpose']}")
        
        # Check if Combined Ratio is in the content
        content = section_data['content']
        if 'combined ratio' in content.lower():
            print("✅ Found 'Combined Ratio' in MD&A content!")
            pos = content.lower().find('combined ratio')
            context = content[max(0, pos-200):pos+500]
            print("📊 Combined Ratio context:")
            print("-" * 40)
            print(context)
            print("-" * 40)
        else:
            print("❌ 'Combined Ratio' not found in MD&A content")
        print()
    else:
        print(f"❌ Error: {result['error']}")
    
    # Test 3: Search for Combined Ratio across all sections
    print("🔍 Test 3: Search for 'Combined Ratio' across all sections...")
    result = agent.execute_tool('search_filing_content', {
        'cik': '0000874766',
        'keywords': ['combined ratio', 'underwriting ratio']
    })
    
    if result['success']:
        data = result['data']
        print(f"✅ Search completed")
        print(f"🔍 Keywords searched: {data['keywords_searched']}")
        print(f"📋 Found in {len(data['found_sections'])} sections:")
        
        for section_info in data['found_sections']:
            print(f"  - {section_info['section_path']}: {section_info['section_title']}")
            print(f"    Content length: {section_info['content_length']:,} characters")
            
            for context_info in section_info['keyword_contexts']:
                print(f"    🎯 Found '{context_info['keyword']}':")
                print(f"       {context_info['context'][:300]}...")
                print()
    else:
        print(f"❌ Error: {result['error']}")


if __name__ == "__main__":
    asyncio.run(test_nested_structure()) 