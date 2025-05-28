#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from src.filing_agent.utils.filing_sections import TenKStructureParser
import anthropic

def test_preprocessing():
    """Test pre-processing to remove boilerplate and focus on narrative content."""
    
    # Initialize parser
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    parser = TenKStructureParser(anthropic_client=client)
    
    # Hartford 2024 10-K - using correct URL format
    cik = "0000874766"
    accession = "0000874766-25-000023"
    primary_doc = "hig-20241231.htm"
    accession_clean = accession.replace('-', '')
    base_url = "https://www.sec.gov/Archives/edgar/data"
    filing_url = f"{base_url}/{cik}/{accession_clean}/{primary_doc}"
    
    print("🔄 Downloading Hartford 10-K...")
    headers = {"User-Agent": "SEC Filing Agent admin@example.com"}
    response = requests.get(filing_url, headers=headers)
    response.raise_for_status()
    
    content = response.text
    
    print(f"📄 Downloaded: {len(content):,} characters")
    
    # Test pre-processing
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    raw_text = soup.get_text(separator='\n', strip=True)
    
    print(f"📝 Raw text: {len(raw_text):,} characters")
    
    # Apply pre-processing
    cleaned_content = parser._preprocess_filing_content(raw_text)
    
    print(f"✨ Cleaned content: {len(cleaned_content):,} characters")
    print(f"🗑️ Removed: {len(raw_text) - len(cleaned_content):,} characters ({(len(raw_text) - len(cleaned_content))/len(raw_text)*100:.1f}%)")
    
    # Show first 2000 chars of cleaned content
    print("\n" + "="*80)
    print("🔍 FIRST 2000 CHARS OF CLEANED CONTENT:")
    print("="*80)
    print(cleaned_content[:2000])
    print("="*80)
    
    # Look for key sections in cleaned content
    print("\n🔍 SECTION DETECTION IN CLEANED CONTENT:")
    sections_to_find = [
        ("Item 1", "item 1"),
        ("Business", "business"),
        ("Risk Factors", "risk factors"), 
        ("Item 1A", "item 1a"),
        ("Item 7", "item 7"),
        ("MD&A", "management"),
        ("Table of Contents", "table of contents")
    ]
    
    for section_name, search_term in sections_to_find:
        pos = cleaned_content.lower().find(search_term)
        if pos != -1:
            print(f"   ✅ {section_name}: found at position {pos:,}")
            # Show context around the finding
            context_start = max(0, pos - 100)
            context_end = min(len(cleaned_content), pos + 200)
            context = cleaned_content[context_start:context_end].replace('\n', ' ')
            print(f"      Context: ...{context}...")
        else:
            print(f"   ❌ {section_name}: not found")
    
    # Test chunking on cleaned content
    print(f"\n🔧 TESTING CHUNKING ON CLEANED CONTENT:")
    chunks = parser._split_content_intelligently(cleaned_content)
    print(f"   📦 Created {len(chunks)} chunks")
    
    for i, chunk in enumerate(chunks[:3]):
        print(f"   📄 Chunk {i+1}: {len(chunk):,} chars")
        # Show first 200 chars of each chunk
        preview = chunk[:200].replace('\n', ' ')
        print(f"      Preview: {preview}...")

if __name__ == "__main__":
    test_preprocessing() 