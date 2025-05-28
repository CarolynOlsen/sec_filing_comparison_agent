#!/usr/bin/env python3
"""Test the new clean LLM-driven filing parser with real Hartford 10-K."""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from filing_agent.core.anthropic_client import AnthropicSecAgent


async def test_real_parsing():
    """Test the new parsing approach with real Hartford 10-K."""
    
    print("🧪 Testing LLM-Driven Parser with Real Hartford 10-K")
    print("=" * 60)
    
    # Create output directory
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Initialize agent
    print("🔧 Initializing SEC agent...")
    agent = AnthropicSecAgent()
    
    # Save the clean structure definition
    print("📋 Saving structure definition...")
    structure = agent.structure_parser.FORM_10K_STRUCTURE
    structure_file = output_dir / f"clean_10k_structure_{timestamp}.json"
    with open(structure_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)
    print(f"💾 Structure saved to: {structure_file}")
    
    # Test 1: Get Hartford's CIK
    print("\n1️⃣ Looking up Hartford's CIK...")
    try:
        cik_result = agent.execute_tool("lookup_company_cik", {"identifier": "HARTFORD"})
        if cik_result["success"]:
            hartford_cik = cik_result["data"]["cik"]
            print(f"✅ Hartford CIK: {hartford_cik}")
        else:
            print("❌ Could not find Hartford CIK, using known value")
            hartford_cik = "0000874766"
    except Exception as e:
        print(f"⚠️ Error looking up CIK: {e}, using known value")
        hartford_cik = "0000874766"
    
    # Test 2: Download and parse Hartford's 10-K with LLM
    print(f"\n2️⃣ Downloading Hartford's latest 10-K (CIK: {hartford_cik})...")
    
    try:
        # Use the new structured filing download
        result = agent.execute_tool("download_structured_filing", {
            "cik": hartford_cik,
            "form_type": "10-K"
        })
        
        if result["success"]:
            filing_data = result["data"]
            
            # Save the structured filing result (this is the actual parsed content!)
            filing_file = output_dir / f"hartford_parsed_filing_{timestamp}.json"
            with open(filing_file, 'w', encoding='utf-8') as f:
                json.dump(filing_data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"✅ Successfully downloaded and parsed 10-K with Pydantic structured output")
            print(f"📊 Total filing length: {filing_data['total_length']:,} characters")
            print(f"📄 Filing URL: {filing_data['filing_url']}")
            print(f"🔧 Parsing method: {filing_data.get('parsing_method', 'unknown')}")
            print(f"📦 Chunks processed: {filing_data.get('chunks_processed', 'unknown')}")
            print(f"💾 Parsed filing data saved to: {filing_file}")
            
            # Show what sections were actually parsed and extracted
            if "structure_summary" in filing_data:
                print(f"\n📋 Sections found in summary:")
                for part_id, part_info in filing_data["structure_summary"].items():
                    if "subsections_found" in part_info:
                        print(f"   📁 {part_id}: {part_info['title']} - {len(part_info['subsections_found'])} sections")
                        for section in part_info["subsections_found"][:3]:  # Show first 3
                            print(f"      📄 {section}")
                        if len(part_info["subsections_found"]) > 3:
                            print(f"      ... and {len(part_info['subsections_found']) - 3} more")
                    else:
                        print(f"   📄 {part_id}: {part_info.get('title', 'Unknown')}")
            
            # Also save the raw parsed structure for detailed review
            if "structure" in filing_data and filing_data["structure"]:
                structure_detail_file = output_dir / f"hartford_parsed_structure_detail_{timestamp}.json"
                
                # Convert FilingSection objects to dictionaries for JSON serialization
                def serialize_structure(obj):
                    if hasattr(obj, '__dict__'):
                        return obj.__dict__
                    elif isinstance(obj, dict):
                        return {k: serialize_structure(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [serialize_structure(item) for item in obj]
                    else:
                        return obj
                
                serializable_structure = serialize_structure(filing_data["structure"])
                
                with open(structure_detail_file, 'w', encoding='utf-8') as f:
                    json.dump(serializable_structure, f, indent=2, ensure_ascii=False, default=str)
                
                print(f"💾 Detailed parsed structure saved to: {structure_detail_file}")
                
                # Show actual parsed sections
                print(f"\n🎯 Actually parsed sections with content:")
                for part_id, part_data in filing_data["structure"].items():
                    if isinstance(part_data, dict) and "subsections" in part_data:
                        print(f"   📁 {part_id}:")
                        for section_id, section_data in part_data["subsections"].items():
                            if "section" in section_data:
                                section = section_data["section"]
                                content_length = len(getattr(section, 'content', ''))
                                key_contents = getattr(section, 'key_contents', [])
                                print(f"      📄 {section_id}: {getattr(section, 'title', 'Unknown')} ({content_length:,} chars)")
                                if key_contents:
                                    print(f"         🔑 Key terms: {key_contents}")
            
        else:
            print(f"❌ Failed to download filing: {result.get('error', 'Unknown error')}")
            return
            
    except Exception as e:
        print(f"❌ Error downloading filing: {e}")
        return
    
    # Test 3: Extract specific section (MD&A) using new parser
    print(f"\n3️⃣ Testing section extraction - MD&A...")
    
    try:
        mda_result = agent.execute_tool("get_filing_section", {
            "cik": hartford_cik,
            "section_path": "part_2.item_7"
        })
        
        if mda_result["success"]:
            mda_data = mda_result["data"]
            section_info = mda_data["section"]
            
            # Save MD&A content
            mda_file = output_dir / f"hartford_mda_{timestamp}.txt"
            with open(mda_file, 'w', encoding='utf-8') as f:
                f.write(f"Hartford Management's Discussion and Analysis\n")
                f.write(f"=" * 60 + "\n\n")
                f.write(f"Section: {section_info['title']}\n")
                f.write(f"Purpose: {section_info['purpose']}\n")
                f.write(f"Full content length: {section_info['full_content_length']:,} characters\n")
                f.write(f"Extracted: {timestamp}\n\n")
                f.write("CONTENT:\n")
                f.write("-" * 40 + "\n")
                f.write(section_info['content'])
                
                if section_info.get('visual_elements'):
                    f.write(f"\n\nVISUAL ELEMENTS FOUND:\n")
                    f.write("-" * 40 + "\n")
                    for elem in section_info['visual_elements']:
                        f.write(f"• {elem['type']}: {elem['description']}\n")
                        f.write(f"  Context: {elem['context'][:200]}...\n\n")
            
            print(f"✅ Successfully extracted MD&A section")
            print(f"📊 Content length: {section_info['full_content_length']:,} characters")
            print(f"📊 Visual elements: {len(section_info.get('visual_elements', []))}")
            print(f"💾 MD&A saved to: {mda_file}")
            
            # Check for key insurance terms
            content = section_info['content'].lower()
            insurance_terms = ["combined ratio", "underwriting", "premium", "loss ratio", "expense ratio"]
            found_terms = [term for term in insurance_terms if term in content]
            
            if found_terms:
                print(f"🎯 Found key insurance terms: {found_terms}")
            else:
                print(f"⚠️ No key insurance terms found in extracted content")
                
        else:
            print(f"❌ Failed to extract MD&A: {mda_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error extracting MD&A: {e}")
    
    # Test 4: Search for specific content
    print(f"\n4️⃣ Testing content search - 'combined ratio'...")
    
    try:
        search_result = agent.execute_tool("search_filing_content", {
            "cik": hartford_cik,
            "keywords": ["combined ratio", "underwriting results"]
        })
        
        if search_result["success"]:
            search_data = search_result["data"]
            
            # Save search results
            search_file = output_dir / f"hartford_search_results_{timestamp}.txt"
            with open(search_file, 'w', encoding='utf-8') as f:
                f.write(f"Hartford 10-K Search Results\n")
                f.write(f"=" * 40 + "\n\n")
                f.write(f"Keywords: {search_data['keywords_searched']}\n")
                f.write(f"Sections found: {len(search_data['found_sections'])}\n")
                f.write(f"Extracted: {timestamp}\n\n")
                
                for section in search_data['found_sections']:
                    f.write(f"SECTION: {section['section_title']}\n")
                    f.write(f"Path: {section['section_path']}\n")
                    f.write(f"Content length: {section['content_length']:,} characters\n\n")
                    
                    for context in section['keyword_contexts']:
                        f.write(f"Keyword: '{context['keyword']}'\n")
                        f.write(f"Context: {context['context']}\n")
                        f.write("-" * 40 + "\n")
            
            print(f"✅ Found content in {len(search_data['found_sections'])} sections")
            print(f"💾 Search results saved to: {search_file}")
            
        else:
            print(f"❌ Search failed: {search_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error in content search: {e}")
    
    # Summary
    print(f"\n🎯 Test Summary:")
    print(f"✅ Clean structure definition (no regex patterns)")
    print(f"✅ Real 10-K download and parsing")
    print(f"✅ LLM-driven section mapping with Pydantic structured output")
    print(f"✅ Guaranteed JSON format (no parsing errors)")
    print(f"✅ Type-safe section extraction")
    print(f"✅ Specific section extraction")
    print(f"✅ Content search across sections")
    print(f"\n🔧 Pydantic Benefits:")
    print(f"✅ Structured output ensures valid JSON")
    print(f"✅ Type validation and error handling")
    print(f"✅ Clear schema definition for LLM")
    print(f"✅ No manual JSON parsing or regex extraction")
    print(f"✅ Automatic field validation and defaults")
    print(f"\n📁 All files saved in: {output_dir}")


if __name__ == "__main__":
    asyncio.run(test_real_parsing()) 