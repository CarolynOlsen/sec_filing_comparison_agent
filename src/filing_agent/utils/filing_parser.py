"""Utilities for parsing SEC filing documents and extracting narrative sections."""

import re
import requests
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
import html2text


class FilingParser:
    """Parser for SEC filing documents to extract narrative sections."""
    
    def __init__(self, user_agent: str = "SEC Filing Agent admin@example.com"):
        """Initialize the filing parser."""
        self.user_agent = user_agent
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = True
        self.html_converter.ignore_images = True
        
    def download_filing_content(self, filing_url: str) -> str:
        """Download the content of a SEC filing document."""
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(filing_url, headers=headers)
        response.raise_for_status()
        
        return response.text
    
    def extract_sections(self, filing_content: str) -> Dict[str, str]:
        """Extract key narrative sections from a SEC filing."""
        
        # Parse HTML content
        soup = BeautifulSoup(filing_content, 'html.parser')
        
        # Convert to text while preserving some structure
        text_content = self.html_converter.handle(str(soup))
        
        sections = {}
        
        # Extract Risk Factors
        risk_factors = self._extract_section(
            text_content, 
            ["risk factors", "item 1a", "item 1a.", "item 1a risk factors"],
            ["item 1b", "item 2", "unresolved staff comments"]
        )
        if risk_factors:
            sections["risk_factors"] = risk_factors
        
        # Extract Business Description
        business = self._extract_section(
            text_content,
            ["business", "item 1", "item 1.", "item 1 business"],
            ["item 1a", "item 2", "risk factors"]
        )
        if business:
            sections["business"] = business
        
        # Extract Management Discussion & Analysis
        mda = self._extract_section(
            text_content,
            ["management.*discussion.*analysis", "md&a", "item 7", "item 7."],
            ["item 8", "item 7a", "financial statements"]
        )
        if mda:
            sections["mda"] = mda
        
        # Extract Legal Proceedings
        legal = self._extract_section(
            text_content,
            ["legal proceedings", "item 3", "item 3."],
            ["item 4", "item 3a", "mine safety"]
        )
        if legal:
            sections["legal_proceedings"] = legal
        
        # Extract Controls and Procedures
        controls = self._extract_section(
            text_content,
            ["controls.*procedures", "item 9a", "item 9a."],
            ["item 9b", "item 10", "other information"]
        )
        if controls:
            sections["controls_procedures"] = controls
        
        return sections
    
    def _extract_section(self, content: str, start_patterns: List[str], end_patterns: List[str]) -> Optional[str]:
        """Extract a specific section from filing content."""
        
        content_lower = content.lower()
        
        # Find section start
        start_pos = None
        for pattern in start_patterns:
            # Look for the pattern at the beginning of a line or after whitespace
            regex_pattern = rf'(?:^|\n)\s*{pattern}(?:\s|\.|\n|$)'
            match = re.search(regex_pattern, content_lower, re.MULTILINE | re.IGNORECASE)
            if match:
                start_pos = match.start()
                break
        
        if start_pos is None:
            return None
        
        # Find section end
        end_pos = len(content)
        for pattern in end_patterns:
            regex_pattern = rf'(?:^|\n)\s*{pattern}(?:\s|\.|\n|$)'
            match = re.search(regex_pattern, content_lower[start_pos + 100:], re.MULTILINE | re.IGNORECASE)
            if match:
                end_pos = start_pos + 100 + match.start()
                break
        
        # Extract and clean the section
        section_content = content[start_pos:end_pos]
        
        # Clean up the content
        section_content = self._clean_section_content(section_content)
        
        # Return only if we have substantial content
        if len(section_content.strip()) > 200:
            return section_content.strip()
        
        return None
    
    def _clean_section_content(self, content: str) -> str:
        """Clean and format section content."""
        
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        # Remove page numbers and headers/footers
        content = re.sub(r'\n\s*\d+\s*\n', '\n', content)
        content = re.sub(r'\n\s*page \d+.*?\n', '\n', content, flags=re.IGNORECASE)
        
        # Remove table of contents references
        content = re.sub(r'\.{3,}\s*\d+', '', content)
        
        return content
    
    def summarize_section(self, section_content: str, max_length: int = 2000) -> str:
        """Summarize a section to fit within token limits."""
        
        if len(section_content) <= max_length:
            return section_content
        
        # Split into paragraphs
        paragraphs = section_content.split('\n\n')
        
        # Keep the first few paragraphs and add a summary note
        summary_parts = []
        current_length = 0
        
        for paragraph in paragraphs:
            if current_length + len(paragraph) > max_length - 200:
                break
            summary_parts.append(paragraph)
            current_length += len(paragraph)
        
        summary = '\n\n'.join(summary_parts)
        summary += f"\n\n[Note: This is a summary of the first {len(summary_parts)} paragraphs. Full section is {len(section_content):,} characters.]"
        
        return summary
    
    def construct_filing_url(self, cik: str, accession_number: str, primary_document: str) -> str:
        """Construct the URL to download a specific filing document."""
        
        # Remove dashes from accession number for URL
        accession_clean = accession_number.replace('-', '')
        
        # Ensure CIK is properly formatted (remove leading zeros for URL)
        cik_clean = str(int(cik))
        
        return f"https://www.sec.gov/Archives/edgar/data/{cik_clean}/{accession_clean}/{primary_document}"
    
    def get_filing_info_from_submissions(self, submissions: Dict, form_type: str = "10-K") -> Optional[Dict]:
        """Extract filing information from submissions data."""
        
        recent_filings = submissions.get('filings', {}).get('recent', {})
        
        if not recent_filings:
            return None
        
        # Find the most recent filing of the specified type
        forms = recent_filings.get('form', [])
        
        for i, form in enumerate(forms):
            if form == form_type:
                return {
                    'accession_number': recent_filings['accessionNumber'][i],
                    'filing_date': recent_filings['filingDate'][i],
                    'primary_document': recent_filings['primaryDocument'][i],
                    'report_date': recent_filings.get('reportDate', [None] * len(forms))[i],
                    'cik': submissions['cik']
                }
        
        return None 