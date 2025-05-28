#!/usr/bin/env python3
"""Test specifically for Risk Factors content extraction."""

import sys
from pathlib import Path
from dotenv import load_dotenv
import json

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from filing_agent.core.anthropic_client import AnthropicSecAgent


def test_risk_factors_content():
    """Test Risk Factors content extraction specifically."""
    
    print("🎯 Testing Risk Factors Content Extraction")
    print("=" * 50)
    
    agent = AnthropicSecAgent()
    hartford_cik = "0000874766"
    
    # First, let's see what we get from the enhanced agent
    print("1️⃣ Testing enhanced agent Risk Factors extraction:")
    print("-" * 30)
    
    try:
        result = agent.execute_tool("get_filing_section", {
            "cik": hartford_cik,
            "section_path": "Part1.Item1A",
            "form_type": "10-K"
        })
        
        if result["success"]:
            section_data = result["data"]["section"]
            content = section_data['content']
            
            print(f"✅ Enhanced agent found Risk Factors section")
            print(f"   📊 Content Length: {len(content):,} characters")
            print(f"   📄 Title: {section_data['title']}")
            
            print(f"\n📝 Content Preview (first 1000 chars):")
            print(f"   {content[:1000]}")
            
            # Check if this looks like actual Risk Factors content vs table of contents
            risk_indicators = [
                'may result', 'could result', 'risks include', 'uncertainty',
                'may impact', 'could impact', 'potential risks', 'material adverse',
                'business may be', 'operations may be', 'could materially',
                'may materially', 'significant risk', 'substantial risk'
            ]
            
            found_indicators = [indicator for indicator in risk_indicators if indicator in content.lower()]
            
            print(f"\n📊 Risk content indicators found: {len(found_indicators)}/{len(risk_indicators)}")
            if found_indicators:
                print(f"   ✓ Found: {', '.join(found_indicators[:5])}{'...' if len(found_indicators) > 5 else ''}")
                
                if len(found_indicators) >= 3:
                    print(f"   ✅ This appears to be substantial Risk Factors content!")
                else:
                    print(f"   ⚠️ Limited Risk Factors language found - may be TOC or header only")
            else:
                print(f"   ❌ No Risk Factors language found - likely TOC or wrong content")
                
        else:
            print(f"❌ Enhanced agent failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing enhanced agent: {e}")
        return False
    
    # Now let's manually check the raw document for Risk Factors
    print(f"\n2️⃣ Manual verification of Risk Factors in raw document:")
    print("-" * 30)
    
    try:
        # Get the raw filing content
        submissions = agent.edgar_client.get_submissions(cik=hartford_cik)
        filing_info = agent.filing_parser.get_filing_info_from_submissions(submissions, "10-K")
        
        filing_url = agent.filing_parser.construct_filing_url(
            filing_info['cik'], 
            filing_info['accession_number'], 
            filing_info['primary_document']
        )
        
        content = agent.filing_parser.download_filing_content(filing_url)
        print(f"📥 Downloaded {len(content):,} characters")
        
        # Search for Risk Factors patterns in raw content
        content_lower = content.lower()
        
        # Look for different Risk Factors patterns
        patterns = [
            ("Item 1A Risk Factors", "item 1a"),
            ("ITEM 1A. RISK FACTORS", "item 1a"),
            ("Item 1A. Risk Factors", "item 1a"),
            ("RISK FACTORS", "risk factors"),
        ]
        
        best_match = None
        best_content = ""
        
        for pattern_name, pattern in patterns:
            pos = content_lower.find(pattern)
            if pos != -1:
                print(f"   ✓ Found '{pattern_name}' at position {pos:,}")
                
                # Extract substantial content from this position
                risk_start = pos
                
                # Look for the end of Risk Factors (next major section)
                next_sections = [
                    "item 1b", "item 2", "unresolved staff", "properties"
                ]
                
                risk_end = len(content)
                for next_section in next_sections:
                    next_pos = content_lower.find(next_section, risk_start + 1000)
                    if next_pos != -1:
                        risk_end = min(risk_end, next_pos)
                
                extracted_content = content[risk_start:risk_end]
                
                # Check quality of extracted content
                risk_indicators_found = sum(1 for indicator in risk_indicators if indicator in extracted_content.lower())
                
                if risk_indicators_found > len(best_content.lower().split()) / 1000:  # Better content ratio
                    best_match = pattern_name
                    best_content = extracted_content
                
                print(f"     📏 Extracted {len(extracted_content):,} chars")
                print(f"     📊 Risk indicators: {risk_indicators_found}")
        
        if best_content:
            print(f"\n🎯 Best Risk Factors content found via '{best_match}':")
            print(f"   📏 Length: {len(best_content):,} characters")
            
            # Show sample
            print(f"\n📝 Sample content:")
            sample = best_content[:1500].strip()
            print(f"   {sample}...")
            
            # Count risk indicators
            found_indicators = [indicator for indicator in risk_indicators if indicator in best_content.lower()]
            print(f"\n📊 Risk content indicators: {len(found_indicators)}/{len(risk_indicators)}")
            
            if len(found_indicators) >= 5:
                print(f"   ✅ This contains substantial Risk Factors content!")
                print(f"   🔧 The issue is likely in our LLM parsing, not the source document.")
                return True
            else:
                print(f"   ⚠️ Limited Risk Factors language found.")
                return False
        else:
            print(f"   ❌ No substantial Risk Factors content found")
            return False
            
    except Exception as e:
        print(f"❌ Error in manual verification: {e}")
        return False


if __name__ == "__main__":
    success = test_risk_factors_content()
    
    if success:
        print(f"\n🎉 Risk Factors content is available in Hartford's 2024 10-K")
        print(f"   The issue is in our content extraction logic, not the source document.")
        print(f"   Recommendation: Improve LLM prompts or content boundary detection.")
    else:
        print(f"\n❌ Risk Factors content may not be available or accessible")
        print(f"   This could indicate document structure or format issues.") 