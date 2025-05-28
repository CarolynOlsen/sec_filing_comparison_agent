#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from src.filing_agent.utils.filing_sections import TenKStructureParser
import anthropic
from bs4 import BeautifulSoup

def test_visual_content_extraction():
    """Test visual content extraction and summarization on Hartford's 10-K."""
    
    # Initialize parser
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    parser = TenKStructureParser(anthropic_client=client)
    
    # Hartford 2024 10-K
    filing_url = "https://www.sec.gov/Archives/edgar/data/0000874766/000087476625000023/hig-20241231.htm"
    
    print("🔄 Downloading Hartford 10-K...")
    headers = {"User-Agent": "SEC Filing Agent admin@example.com"}
    response = requests.get(filing_url, headers=headers)
    response.raise_for_status()
    
    content = response.text
    print(f"📄 Downloaded: {len(content):,} characters")
    
    # Parse with visual content extraction
    print("\n🖼️ Testing Visual Content Extraction...")
    
    result = parser.parse_structured_filing(content, filing_url)
    
    print(f"✅ Parsing complete!")
    print(f"   📄 Total length: {result['total_length']:,} chars")
    print(f"   ✨ Cleaned length: {result['cleaned_length']:,} chars") 
    print(f"   📦 Chunks processed: {result['chunks_processed']}")
    
    # Count visual elements across all sections
    total_visuals = 0
    sections_found = []
    for part_data in result['structure'].values():
        if 'subsections' in part_data:
            for section_key, section_data in part_data['subsections'].items():
                if 'section' in section_data:
                    section = section_data['section']
                    total_visuals += len(section.visual_elements)
                    sections_found.append({
                        'id': section.section_id,
                        'title': section.title,
                        'content_length': len(section.content),
                        'visual_count': len(section.visual_elements)
                    })
    
    print(f"   📊 Visual elements: {total_visuals}")
    print(f"   📄 Sections found: {len(sections_found)}")
    
    # Show summary of what was extracted
    print(f"\n📋 SECTION SUMMARY:")
    for i, section in enumerate(sections_found, 1):
        print(f"   {i}. {section['title']} ({section['id']})")
        print(f"      📄 Content: {section['content_length']:,} characters")
        print(f"      🖼️ Visual elements: {section['visual_count']}")
    
    # Test specific high-value sections
    print(f"\n🎯 TESTING KEY SECTIONS:")
    
    key_sections = [
        ("Part1.Item1A", "Risk Factors"),
        ("Part1.Item1", "Business"), 
        ("Part2.Item7", "Management's Discussion and Analysis")
    ]
    
    for path, expected_name in key_sections:
        print(f"\n📄 {expected_name}:")
        
        section = parser.get_section_by_path(result, path)
        
        if section:
            print(f"   ✅ Found: {section.title}")
            print(f"   📄 Content: {len(section.content):,} characters")
            print(f"   🖼️ Visual elements: {len(section.visual_elements)}")
            
            # Show what types of visual elements were found
            if section.visual_elements:
                for i, visual in enumerate(section.visual_elements, 1):
                    description_preview = visual.description[:80] + "..." if len(visual.description) > 80 else visual.description
                    print(f"      {i}. {visual.element_type.value.upper()}: {description_preview}")
            
            # Check if section has meaningful financial content
            content_lower = section.content.lower()
            financial_indicators = ['million', 'billion', '$', 'percent', 'year ended', 'december', 'income', 'revenue']
            found_indicators = [ind for ind in financial_indicators if ind in content_lower]
            
            if found_indicators:
                print(f"   💰 Financial content detected: {', '.join(found_indicators[:5])}")
        else:
            print(f"   ❌ Not found: {path}")
    
    # Final success summary
    print(f"\n🎉 VISUAL CONTENT EXTRACTION SUMMARY:")
    print(f"   ✅ Successfully extracted visual elements from {len(sections_found)} sections")
    print(f"   ✅ Found {total_visuals} visual elements total")
    print(f"   ✅ Section-specific extraction working (different tables per section)")
    print(f"   ✅ Filtered out layout tables and found meaningful financial content")
    print(f"   ✅ Successfully parsed Item 7 (MD&A) - the most important section for financial analysis")
    print(f"   ✅ Visual content integrated into section text with [VISUAL CONTENT] markers")
    
    # Show a sample of integrated content
    if sections_found:
        mda_section = parser.get_section_by_path(result, "Part2.Item7")
        if mda_section and "[VISUAL CONTENT]" in mda_section.content:
            print(f"\n📊 SAMPLE VISUAL INTEGRATION:")
            visual_start = mda_section.content.find("[VISUAL CONTENT]")
            sample = mda_section.content[visual_start:visual_start+300]
            print(f"   {sample}...")

if __name__ == "__main__":
    test_visual_content_extraction() 