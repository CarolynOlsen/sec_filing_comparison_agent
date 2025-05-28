#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from src.filing_agent.utils.filing_sections import TenKStructureParser
import anthropic

def test_enhanced_with_preprocessing():
    """Test enhanced filing agent with pre-processing on Hartford's 10-K."""
    
    # Initialize parser
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    parser = TenKStructureParser(anthropic_client=client)
    
    # Hartford 2024 10-K
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
    
    # Parse with enhanced agent (includes pre-processing)
    print("\n🚀 Running Enhanced Filing Agent with Pre-processing...")
    
    result = parser.parse_structured_filing(content, filing_url)
    
    print(f"✅ Parsing complete!")
    print(f"   📄 Total length: {result['total_length']:,} chars")
    print(f"   ✨ Cleaned length: {result['cleaned_length']:,} chars") 
    print(f"   🗑️ Removed: {result['total_length'] - result['cleaned_length']:,} chars")
    print(f"   📦 Chunks processed: {result['chunks_processed']}")
    
    # Test specific section retrieval
    print(f"\n🔍 TESTING SECTION RETRIEVAL:")
    
    sections_to_test = [
        ("Part1.Item1A", "Risk Factors"),
        ("Part1.Item1", "Business"), 
        ("Part2.Item7", "Management's Discussion and Analysis"),
        ("Part1.Item1B", "Unresolved Staff Comments")
    ]
    
    for path, expected_name in sections_to_test:
        print(f"\n📋 Testing: {path} ({expected_name})")
        
        section = parser.get_section_by_path(result, path)
        
        if section:
            print(f"   ✅ Found: {section.title}")
            print(f"   📄 Content length: {len(section.content):,} chars")
            print(f"   🎯 Key contents: {section.key_contents}")
            
            # Show content preview
            preview = section.content[:300].replace('\n', ' ')
            print(f"   📝 Preview: {preview}...")
            
            # For Risk Factors, do deeper analysis
            if "risk" in path.lower():
                print(f"   🔍 Risk Factors Analysis:")
                content_lower = section.content.lower()
                
                # Check for actual risk content
                risk_indicators = [
                    "catastrophe", "insurance", "underwriting", "claims", 
                    "economic", "competition", "regulation", "investment"
                ]
                
                found_indicators = [ind for ind in risk_indicators if ind in content_lower]
                print(f"      🎯 Risk indicators found: {found_indicators}")
                
                # Check for substantial content
                if len(section.content) > 10000:
                    print(f"      ✅ Substantial Risk Factors content detected!")
                else:
                    print(f"      ⚠️ Risk Factors content seems short")
            
        else:
            print(f"   ❌ Not found: {path}")
    
    # Search for keywords
    print(f"\n🔍 KEYWORD SEARCH TEST:")
    
    insurance_keywords = ["combined ratio", "underwriting", "catastrophe", "claims"]
    results = parser.find_content_with_keywords(result, insurance_keywords)
    
    print(f"   🎯 Found {len(results)} sections with insurance keywords:")
    for path, section in results[:3]:  # Show first 3
        print(f"      📄 {path}: {section.title} ({len(section.content):,} chars)")

if __name__ == "__main__":
    test_enhanced_with_preprocessing() 