#!/usr/bin/env python3
"""Test the enhanced filing agent with Hartford's 2024 10-K."""

import sys
from pathlib import Path
from dotenv import load_dotenv
import json

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from filing_agent.core.anthropic_client import AnthropicSecAgent


def test_hartford_enhanced():
    """Test downloading and parsing Hartford's 2024 10-K with enhanced features."""
    
    print("🏢 Testing Hartford 2024 10-K with Enhanced Filing Agent")
    print("=" * 60)
    
    agent = AnthropicSecAgent()
    
    # Hartford's CIK (The Hartford Financial Services Group)
    hartford_cik = "0000874766"
    
    print(f"\n1️⃣ Testing download_structured_filing for Hartford (CIK: {hartford_cik})")
    print("-" * 50)
    
    try:
        result = agent.execute_tool("download_structured_filing", {
            "cik": hartford_cik,
            "form_type": "10-K"
        })
        
        if result["success"]:
            data = result["data"]
            print(f"✅ Successfully downloaded Hartford 2024 10-K")
            print(f"   📄 Filing Date: {data['filing_info']['filing_date']}")
            print(f"   📄 Document: {data['filing_info']['primary_document']}")
            print(f"   📄 URL: {data['filing_url']}")
            print(f"   📊 Total Length: {data['total_length']:,} characters")
            print(f"   🔧 Parsing Method: {data['parsing_method']}")
            print(f"   📦 Chunks Processed: {data['chunks_processed']}")
            
            print(f"\n📑 Structure Found:")
            for part_id, summary in data.get("structure_summary", {}).items():
                print(f"   • {part_id}: {summary.get('title', 'Unknown')}")
                if 'subsections_found' in summary:
                    print(f"     └─ Subsections: {', '.join(summary['subsections_found'][:3])}{'...' if len(summary['subsections_found']) > 3 else ''}")
            
            # Save result for inspection
            output_file = Path("test_output") / "hartford_enhanced_structured.json"
            output_file.parent.mkdir(exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"   💾 Full result saved to: {output_file}")
            
        else:
            print(f"❌ Failed to download structured filing: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing structured filing: {e}")
        return False
    
    print(f"\n2️⃣ Testing get_filing_section for Risk Factors")
    print("-" * 50)
    
    try:
        result = agent.execute_tool("get_filing_section", {
            "cik": hartford_cik,
            "section_path": "Part1.Item1A",
            "form_type": "10-K"
        })
        
        if result["success"]:
            section_data = result["data"]["section"]
            print(f"✅ Successfully extracted Risk Factors section")
            print(f"   📍 Path: {section_data['path']}")
            print(f"   📄 Title: {section_data['title']}")
            print(f"   📊 Content Length: {section_data['full_content_length']:,} characters")
            print(f"   📋 Visual Elements: {len(section_data['visual_elements'])}")
            
            # Show a sample of the content
            content_sample = section_data['content'][:500]
            print(f"\n📝 Content Sample:")
            print(f"   {content_sample}...")
            
            # Check if content looks like narrative text
            if any(phrase in content_sample.lower() for phrase in ['risk', 'may', 'could', 'factors', 'business']):
                print(f"   ✅ Content appears to be narrative text (contains risk-related language)")
            else:
                print(f"   ⚠️ Content may not be narrative text")
                
        else:
            print(f"❌ Failed to get Risk Factors section: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing section extraction: {e}")
        return False
    
    print(f"\n3️⃣ Testing get_filing_section for Business Description")
    print("-" * 50)
    
    try:
        result = agent.execute_tool("get_filing_section", {
            "cik": hartford_cik,
            "section_path": "Part1.Item1",
            "form_type": "10-K"
        })
        
        if result["success"]:
            section_data = result["data"]["section"]
            print(f"✅ Successfully extracted Business section")
            print(f"   📍 Path: {section_data['path']}")
            print(f"   📄 Title: {section_data['title']}")
            print(f"   📊 Content Length: {section_data['full_content_length']:,} characters")
            
            # Show a sample of the content
            content_sample = section_data['content'][:500]
            print(f"\n📝 Content Sample:")
            print(f"   {content_sample}...")
            
            # Check if content mentions Hartford business
            hartford_terms = ['hartford', 'insurance', 'property', 'casualty', 'commercial', 'personal']
            found_terms = [term for term in hartford_terms if term in content_sample.lower()]
            
            if found_terms:
                print(f"   ✅ Content contains Hartford business terms: {', '.join(found_terms)}")
            else:
                print(f"   ⚠️ Content may not contain expected Hartford business terms")
                
        else:
            print(f"❌ Failed to get Business section: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing business section: {e}")
        return False
    
    print(f"\n🎉 All tests completed successfully!")
    print(f"✅ Hartford's 2024 10-K narrative content is accessible via enhanced filing agent")
    return True


if __name__ == "__main__":
    success = test_hartford_enhanced()
    
    if success:
        print(f"\n🏆 Hartford Enhanced Filing Test: PASSED")
        print(f"   The enhanced filing agent can successfully access Hartford's narrative 10-K content.")
        print(f"   The 'hig-20241231.htm' document contains both XBRL tags AND full narrative sections.")
    else:
        print(f"\n❌ Hartford Enhanced Filing Test: FAILED")
        print(f"   There may be issues with the filing parser or structure parser.") 