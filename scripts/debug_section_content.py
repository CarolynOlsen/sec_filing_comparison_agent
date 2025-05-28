#!/usr/bin/env python3
"""Debug script to see what's happening with section content extraction."""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from filing_agent.core.anthropic_client import AnthropicSecAgent


async def debug_section_content():
    """Debug section content extraction in detail."""
    agent = AnthropicSecAgent()
    
    print("🔍 Debugging section content extraction...")
    
    # Get the filing info first
    submissions = agent.edgar_client.get_submissions(cik="0000874766")
    filing_info = agent.filing_parser.get_filing_info_from_submissions(submissions, "10-K")
    
    if not filing_info:
        print("❌ No 10-K filing found")
        return
    
    # Construct filing URL
    filing_url = agent.filing_parser.construct_filing_url(
        filing_info['cik'],
        filing_info['accession_number'],
        filing_info['primary_document']
    )
    
    print(f"📄 Filing URL: {filing_url}")
    
    # Download filing content
    filing_content = agent.filing_parser.download_filing_content(filing_url)
    print(f"📄 Raw content length: {len(filing_content):,} characters")
    
    # Test the structure parser directly
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(filing_content, 'html.parser')
    text_content = soup.get_text(separator='\n', strip=True)
    
    print(f"📄 Extracted text length: {len(text_content):,} characters")
    print()
    
    # Test Item 7 (MD&A) extraction specifically
    print("🔍 Testing Item 7 (MD&A) extraction...")
    
    content_lower = text_content.lower()
    
    # Look for Item 7 patterns
    item7_patterns = [
        r'(?:^|\n)\s*part\s+[iv]+\s*-\s*item\s+7(?:\s|\.|\n|$)',
        r'(?:^|\n)\s*item\s+7(?:\s|\.|\n|$)',
        r'item\s+7[^\w]',
        r'management.*discussion.*analysis',
        r'md&a'
    ]
    
    for i, pattern in enumerate(item7_patterns):
        import re
        match = re.search(pattern, content_lower, re.MULTILINE | re.IGNORECASE)
        if match:
            start_pos = match.start()
            print(f"✅ Pattern {i+1} found at position {start_pos:,}")
            print(f"   Pattern: {pattern}")
            print(f"   Context: {text_content[max(0, start_pos-100):start_pos+300]}")
            print()
            
            # Try to find the end
            end_patterns = [
                r'part\s+[iv]+\s*-\s*item\s+8\.',
                r'item\s+8\.',
                r'part\s+[iv]+',
                r'signatures',
                r'exhibits'
            ]
            
            end_pos = len(text_content)
            for j, end_pattern in enumerate(end_patterns):
                end_match = re.search(end_pattern, content_lower[start_pos + 500:], re.MULTILINE | re.IGNORECASE)
                if end_match:
                    end_pos = start_pos + 500 + end_match.start()
                    print(f"✅ End pattern {j+1} found at position {end_pos:,}")
                    print(f"   End pattern: {end_pattern}")
                    break
            
            section_text = text_content[start_pos:end_pos]
            print(f"📄 Extracted section length: {len(section_text):,} characters")
            
            if len(section_text) > 0:
                print("🔍 First 1000 characters of extracted section:")
                print("-" * 60)
                print(section_text[:1000])
                print("-" * 60)
                print()
                
                # Look for Combined Ratio in this section
                if 'combined ratio' in section_text.lower():
                    print("✅ Found 'combined ratio' in extracted section!")
                    pos = section_text.lower().find('combined ratio')
                    print(f"Combined Ratio context:")
                    print(section_text[max(0, pos-200):pos+500])
                else:
                    print("❌ 'combined ratio' not found in extracted section")
            
            break
        else:
            print(f"❌ Pattern {i+1} not found: {pattern}")


if __name__ == "__main__":
    asyncio.run(debug_section_content()) 