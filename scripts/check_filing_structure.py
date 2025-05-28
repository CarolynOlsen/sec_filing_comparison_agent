#!/usr/bin/env python3
"""Check what documents are available in Hartford's 10-K submission."""

import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from filing_agent.core.anthropic_client import AnthropicSecAgent


def check_filing_structure():
    """Check what documents are available in Hartford's 10-K submission."""
    
    print("🔍 Checking Hartford's filing structure...")
    print("Using CIK: 0000874766 (The Hartford Financial Services Group)")
    
    agent = AnthropicSecAgent()
    
    # Get submissions using the correct CIK
    submissions = agent.edgar_client.get_submissions(cik="0000874766")
    recent = submissions['filings']['recent']
    
    print(f"\n📋 Recent forms available (last 20):")
    for i, form in enumerate(recent['form'][:20]):
        filing_date = recent['filingDate'][i]
        accession = recent['accessionNumber'][i]
        primary_doc = recent['primaryDocument'][i]
        print(f"  {i+1:2d}. {form:10s} | {filing_date} | {accession} | {primary_doc}")
    
    # Look specifically for 10-K filings
    print(f"\n📑 10-K filings found:")
    found_10k = False
    for i, form in enumerate(recent['form']):
        if form == '10-K':
            found_10k = True
            filing_date = recent['filingDate'][i]
            accession = recent['accessionNumber'][i]
            primary_doc = recent['primaryDocument'][i]
            print(f"  • {form} filed {filing_date}")
            print(f"    Accession: {accession}")
            print(f"    Primary Document: {primary_doc}")
            
            # Check if this looks like XBRL vs narrative document
            if 'htm' in primary_doc.lower() and len(primary_doc) < 20:
                print(f"    ⚠️  This appears to be an XBRL document (short .htm filename)")
            elif 'txt' in primary_doc.lower() or len(primary_doc) > 20:
                print(f"    ✅ This appears to be a narrative document")
            
            # Let's also check what other documents are in this submission
            print(f"    📁 Checking submission {accession} for all documents...")
            
            # Get the submission details
            base_url = f"https://data.sec.gov/submissions/CIK{submissions['cik']}.json"
            accession_clean = accession.replace('-', '')
            
            try:
                import requests
                headers = {'User-Agent': 'SEC Filing Agent admin@example.com'}
                filing_url = f"https://www.sec.gov/Archives/edgar/data/{submissions['cik']}/{accession_clean}/{accession}-index.htm"
                print(f"    🔗 Full filing index: {filing_url}")
                
                # Try to get the filing summary to see all documents
                summary_url = f"https://www.sec.gov/Archives/edgar/data/{submissions['cik']}/{accession_clean}/FilingSummary.xml"
                print(f"    📄 Filing summary: {summary_url}")
                
            except Exception as e:
                print(f"    ❌ Error getting filing details: {e}")
            
            print()
    
    if not found_10k:
        print("  ❌ No 10-K filings found in recent submissions")
    
    return found_10k


if __name__ == "__main__":
    check_filing_structure() 