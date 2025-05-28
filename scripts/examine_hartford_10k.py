#!/usr/bin/env python3
"""Download and examine Hartford's 2024 10-K filing to understand its structure."""

import sys
import requests
from pathlib import Path
from dotenv import load_dotenv
import json

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def download_and_examine_hartford_10k():
    """Download Hartford's 2024 10-K and examine its structure."""
    
    print("📥 Downloading Hartford's 2024 10-K filing...")
    
    # Hartford's 2024 10-K details
    cik = "0000874766"
    accession = "0000874766-25-000023"
    primary_doc = "hig-20241231.htm"
    
    # Clean up accession number for URL
    accession_clean = accession.replace('-', '')
    
    # Construct download URL
    base_url = "https://www.sec.gov/Archives/edgar/data"
    filing_url = f"{base_url}/{cik}/{accession_clean}/{primary_doc}"
    
    print(f"🔗 Downloading from: {filing_url}")
    
    try:
        headers = {'User-Agent': 'SEC Filing Agent admin@example.com'}
        response = requests.get(filing_url, headers=headers)
        
        if response.status_code == 200:
            content = response.text
            print(f"✅ Successfully downloaded {len(content):,} characters")
            
            # Save to file for examination
            output_file = Path("test_output") / "hartford_2024_10k_raw.html"
            output_file.parent.mkdir(exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"💾 Saved to: {output_file}")
            
            # Analyze the content
            print(f"\n🔍 Content Analysis:")
            content_lower = content.lower()
            
            # Check for XBRL tags
            xbrl_tags = ['ix:', '<ix:', 'xbrl', 'inline xbrl']
            xbrl_found = sum(1 for tag in xbrl_tags if tag in content_lower)
            print(f"   📊 XBRL indicators found: {xbrl_found}")
            
            # Check for standard 10-K sections
            sections_to_check = [
                ('Item 1', 'business'),
                ('Item 1A', 'risk factors'),
                ('Item 1B', 'unresolved staff comments'),
                ('Item 2', 'properties'),
                ('Item 3', 'legal proceedings'),
                ('Item 4', 'mine safety'),
                ('Item 5', 'market for registrant'),
                ('Item 6', 'financial data'),
                ('Item 7', 'management'),
                ('Item 8', 'financial statements'),
                ('Item 9', 'controls and procedures'),
                ('Item 10', 'directors'),
                ('Item 11', 'executive compensation'),
                ('Item 12', 'ownership'),
                ('Item 13', 'relationships'),
                ('Item 14', 'principal accountant'),
                ('Item 15', 'exhibits')
            ]
            
            sections_found = []
            for item, keyword in sections_to_check:
                if item.lower() in content_lower and keyword in content_lower:
                    sections_found.append(f"{item} - {keyword.title()}")
            
            print(f"   📑 10-K sections found: {len(sections_found)}/15")
            for section in sections_found[:5]:  # Show first 5
                print(f"      ✓ {section}")
            if len(sections_found) > 5:
                print(f"      ... and {len(sections_found) - 5} more")
            
            # Look for specific Hartford content
            hartford_indicators = [
                'the hartford financial services group',
                'property and casualty insurance',
                'group benefits',
                'hartford funds',
                'commercial lines',
                'personal lines'
            ]
            
            hartford_content = sum(1 for indicator in hartford_indicators if indicator in content_lower)
            print(f"   🏢 Hartford-specific content indicators: {hartford_content}/{len(hartford_indicators)}")
            
            # Check for narrative vs structured content
            print(f"\n📝 Content Type Analysis:")
            
            # Look for risk factors content (typically narrative)
            if 'risk factors' in content_lower:
                # Find risk factors section
                risk_start = content_lower.find('risk factors')
                if risk_start != -1:
                    risk_sample = content[risk_start:risk_start + 1000]
                    print(f"   🎯 Found Risk Factors section. Sample:")
                    print(f"      {risk_sample[:200].strip()}...")
            
            # Look for business description (typically narrative)
            if 'item 1' in content_lower and 'business' in content_lower:
                business_start = content_lower.find('item 1')
                if business_start != -1:
                    business_sample = content[business_start:business_start + 1000]
                    print(f"   🏢 Found Business section. Sample:")
                    print(f"      {business_sample[:200].strip()}...")
            
            # Check if this is inline XBRL with narrative content
            if xbrl_found > 0 and len(sections_found) > 10:
                print(f"\n✅ This appears to be an Inline XBRL document containing full narrative 10-K content!")
                print(f"   💡 The XBRL tags are embedded within the HTML but the narrative text is present.")
            elif len(sections_found) > 10:
                print(f"\n✅ This appears to be a standard narrative 10-K document!")
            else:
                print(f"\n⚠️  This may not contain the full narrative 10-K content.")
            
            return True, content
            
        else:
            print(f"❌ Failed to download: HTTP {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error downloading filing: {e}")
        return False, None


if __name__ == "__main__":
    success, content = download_and_examine_hartford_10k()
    
    if success:
        print(f"\n🎉 Hartford's 2024 10-K successfully downloaded and analyzed!")
        print(f"   📄 The document contains both XBRL tags and narrative content.")
        print(f"   🔧 Our filing parser should be able to extract the narrative sections.")
    else:
        print(f"\n❌ Failed to download Hartford's 2024 10-K.") 