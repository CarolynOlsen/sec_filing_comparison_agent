#!/usr/bin/env python3
"""Check the raw Hartford filing content for Risk Factors section."""

import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from filing_agent.core.anthropic_client import AnthropicSecAgent


def check_hartford_raw_content():
    """Check Hartford's raw filing content for proper Risk Factors section."""
    
    print("🔍 Checking Hartford's raw 2024 10-K content for Risk Factors...")
    print("=" * 60)
    
    agent = AnthropicSecAgent()
    
    # Get the filing
    submissions = agent.edgar_client.get_submissions(cik="0000874766")
    filing_info = agent.filing_parser.get_filing_info_from_submissions(submissions, "10-K")
    
    if not filing_info:
        print("❌ No 10-K filing found")
        return False
    
    # Download the raw content
    filing_url = agent.filing_parser.construct_filing_url(
        filing_info['cik'], 
        filing_info['accession_number'], 
        filing_info['primary_document']
    )
    
    print(f"📥 Downloading: {filing_url}")
    content = agent.filing_parser.download_filing_content(filing_url)
    
    print(f"✅ Downloaded {len(content):,} characters")
    
    # Look for Risk Factors patterns
    content_lower = content.lower()
    
    # Search for various Risk Factors patterns
    patterns = [
        "item 1a",
        "item 1a.",
        "risk factors",
        "item 1a risk factors",
        "item 1a. risk factors"
    ]
    
    print(f"\n🔍 Searching for Risk Factors patterns:")
    risk_positions = []
    
    for pattern in patterns:
        pos = content_lower.find(pattern)
        if pos != -1:
            # Get context around the found pattern
            start = max(0, pos - 100)
            end = min(len(content), pos + 500)
            context = content[start:end]
            
            print(f"   ✓ Found '{pattern}' at position {pos:,}")
            print(f"     Context: ...{context}...")
            print()
            
            risk_positions.append((pattern, pos))
    
    if not risk_positions:
        print("❌ No Risk Factors patterns found!")
        return False
    
    # Find the best Risk Factors section
    best_pattern, best_pos = risk_positions[0]  # Take the first one found
    
    print(f"🎯 Using '{best_pattern}' at position {best_pos:,}")
    
    # Extract a larger sample around this position
    start = max(0, best_pos - 200)
    end = min(len(content), best_pos + 2000)
    sample = content[start:end]
    
    print(f"\n📝 Risk Factors Section Sample ({len(sample)} chars):")
    print("-" * 50)
    print(sample)
    print("-" * 50)
    
    # Check if this looks like substantial Risk Factors content
    risk_indicators = [
        'may result', 'could result', 'risks include', 'uncertainty', 'factors',
        'may impact', 'could impact', 'potential risks', 'material adverse',
        'business may be', 'operations may be'
    ]
    
    found_indicators = [indicator for indicator in risk_indicators if indicator in sample.lower()]
    
    print(f"\n📊 Risk content indicators found: {len(found_indicators)}/{len(risk_indicators)}")
    if found_indicators:
        print(f"   ✓ Found: {', '.join(found_indicators[:5])}{'...' if len(found_indicators) > 5 else ''}")
        
        print(f"\n✅ This appears to contain substantial Risk Factors content!")
        return True
    else:
        print(f"\n⚠️ This may not contain substantial Risk Factors content.")
        return False


if __name__ == "__main__":
    success = check_hartford_raw_content()
    
    if success:
        print(f"\n🎉 Hartford's 2024 10-K contains accessible Risk Factors content")
        print(f"   The issue is likely in our section parsing, not the source document.")
    else:
        print(f"\n❌ Hartford's 2024 10-K may not contain proper Risk Factors content")
        print(f"   This could indicate a different filing structure or format.") 