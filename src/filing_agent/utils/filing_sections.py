"""Clean LLM-driven 10-K filing structure parser with Pydantic structured output."""

import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field


class SectionType(Enum):
    """Types of content sections in 10-K filings."""
    TEXT = "text"
    TABLE = "table"
    CHART = "chart"
    FINANCIAL_STATEMENT = "financial_statement"
    EXHIBIT = "exhibit"


@dataclass
class VisualElement:
    """Represents a visual element (chart, table, etc.) in a filing."""
    section_id: str
    section_title: str
    element_type: SectionType
    page_number: Optional[int]
    description: str
    context: str
    image_data: Optional[bytes] = None
    extracted_text: Optional[str] = None


@dataclass
class FilingSection:
    """Represents a structured section of a 10-K filing."""
    section_id: str
    title: str
    description: str
    purpose: str
    content: str
    visual_elements: List[VisualElement]
    key_contents: List[str]
    page_range: Optional[Tuple[int, int]] = None
    subsections: Optional[Dict[str, 'FilingSection']] = None


# Pydantic models for structured LLM output
class SectionFound(BaseModel):
    """Represents a section found in a filing chunk."""
    section_id: str = Field(description="Section identifier like 'item_7' or 'item_1a'")
    part: str = Field(description="Part identifier like 'part_1' or 'part_2'")
    title: str = Field(description="Full section title")
    content_start: str = Field(description="First few words where this section starts in the chunk")
    content_length: int = Field(description="Estimated character count of this section")
    contains_key_info: List[str] = Field(default=[], description="Key terms or metrics found in this section")


class ChunkAnalysis(BaseModel):
    """Analysis result for a filing chunk."""
    sections_found: List[SectionFound] = Field(description="List of sections identified in this chunk")
    chunk_summary: str = Field(description="Brief description of what this chunk contains")


class TenKStructureParser:
    """Clean LLM-driven parser for 10-K filings with Pydantic structured output."""
    
    def __init__(self, user_agent: str = "SEC Filing Agent admin@example.com", anthropic_client=None):
        """Initialize the parser."""
        self.user_agent = user_agent
        self.anthropic_client = anthropic_client
        
        # Simple, clean 10-K structure definition
        self.FORM_10K_STRUCTURE = {
            "part_1": {
                "title": "Part I - Business Information",
                "sections": {
                    "item_1": {"title": "Business", "purpose": "Company operations and strategy"},
                    "item_1a": {"title": "Risk Factors", "purpose": "Material risks", "parent": "item_1"},
                    "item_1b": {"title": "Unresolved Staff Comments", "purpose": "SEC comments", "parent": "item_1"},
                    "item_1c": {"title": "Cybersecurity", "purpose": "Cyber risk management", "parent": "item_1"},
                    "item_2": {"title": "Properties", "purpose": "Physical assets"},
                    "item_3": {"title": "Legal Proceedings", "purpose": "Material litigation"},
                    "item_4": {"title": "Mine Safety Disclosures", "purpose": "Mining safety (if applicable)"}
                }
            },
            "part_2": {
                "title": "Part II - Financial Information", 
                "sections": {
                    "item_5": {"title": "Market for Common Equity", "purpose": "Stock and shareholder info"},
                    "item_6": {"title": "Reserved", "purpose": "Reserved section"},
                    "item_7": {"title": "Management's Discussion and Analysis", "purpose": "Financial performance analysis", "key_metrics": ["combined ratio", "underwriting", "revenue", "margins"]},
                    "item_7a": {"title": "Market Risk Disclosures", "purpose": "Market risk exposure", "parent": "item_7"},
                    "item_8": {"title": "Financial Statements", "purpose": "Audited financials"},
                    "item_9": {"title": "Changes in Accountants", "purpose": "Auditor changes"},
                    "item_9a": {"title": "Controls and Procedures", "purpose": "Internal controls", "parent": "item_9"},
                    "item_9b": {"title": "Other Information", "purpose": "Additional disclosures", "parent": "item_9"},
                    "item_9c": {"title": "Foreign Jurisdiction Inspections", "purpose": "Audit inspection issues", "parent": "item_9"}
                }
            },
            "part_3": {
                "title": "Part III - Corporate Governance",
                "sections": {
                    "item_10": {"title": "Directors and Officers", "purpose": "Leadership information"},
                    "item_11": {"title": "Executive Compensation", "purpose": "Pay disclosures"},
                    "item_12": {"title": "Security Ownership", "purpose": "Stock ownership"},
                    "item_13": {"title": "Related Transactions", "purpose": "Related party deals"},
                    "item_14": {"title": "Accountant Fees", "purpose": "Auditor compensation"}
                }
            },
            "part_4": {
                "title": "Part IV - Exhibits and Signatures",
                "sections": {
                    "item_15": {"title": "Exhibits and Schedules", "purpose": "Document index"},
                    "item_16": {"title": "Form 10-K Summary", "purpose": "Optional summary"}
                }
            },
            "signatures": {"title": "Signatures", "purpose": "Required signatures"}
        }
    
    def parse_structured_filing(self, filing_content: str, filing_url: str) -> Dict[str, Any]:
        """Parse a 10-K filing using LLM intelligence with structured output."""
        
        # Extract clean text from HTML/XBRL
        soup = BeautifulSoup(filing_content, 'html.parser')
        text_content = soup.get_text(separator='\n', strip=True)
        
        # Store soup for visual element extraction during section processing
        self.current_soup = soup
        self.current_filing_url = filing_url
        
        # Pre-process to remove boilerplate and focus on narrative content
        cleaned_content = self._preprocess_filing_content(text_content)
        
        # Split into manageable chunks for LLM processing
        chunks = self._split_content_intelligently(cleaned_content)
        
        result = {
            "filing_url": filing_url,
            "total_length": len(text_content),
            "cleaned_length": len(cleaned_content),
            "structure": {},
            "parsing_method": "llm_driven_pydantic",
            "chunks_processed": len(chunks)
        }
        
        if self.anthropic_client:
            # Use LLM with structured output to map content to structure
            result["structure"] = self._llm_parse_structure_pydantic(chunks)
        else:
            # Fallback to simple text search
            result["structure"] = self._fallback_parse_structure(cleaned_content)
        
        return result
    
    def _preprocess_filing_content(self, text_content: str) -> str:
        """Pre-process filing content to remove boilerplate and focus on narrative sections."""
        
        lines = text_content.split('\n')
        cleaned_lines = []
        
        # Flags to track what we're skipping
        in_xbrl_section = False
        in_toc_section = False
        found_narrative_start = False
        
        for i, line in enumerate(lines):
            line_lower = line.strip().lower()
            
            # Skip XBRL metadata sections
            if any(indicator in line_lower for indicator in [
                'context id=', 'xbrl', 'taxonomy', 'namespace', 'schema', 'entity identifier'
            ]):
                in_xbrl_section = True
                continue
            
            # Stop skipping XBRL when we hit actual content
            if in_xbrl_section and any(indicator in line_lower for indicator in [
                'part i', 'item 1', 'business', 'table of contents'
            ]):
                in_xbrl_section = False
            
            if in_xbrl_section:
                continue
            
            # Identify and skip table of contents
            if not found_narrative_start and any(indicator in line_lower for indicator in [
                'table of contents', 'index', 'part i', 'part ii', 'part iii'
            ]):
                in_toc_section = True
                continue
            
            # Skip lines that look like TOC entries (page numbers)
            if in_toc_section:
                # Look for patterns like "BUSINESS    6" or "RISK FACTORS    21"
                if any(char.isdigit() for char in line) and len(line.strip()) < 100:
                    continue
                
                # Look for the start of actual narrative content
                if any(indicator in line_lower for indicator in [
                    'forward-looking statements',
                    'item 1.',
                    'part i - item 1',
                    'business\nthe company'
                ]) and len(line.strip()) > 20:
                    in_toc_section = False
                    found_narrative_start = True
                    cleaned_lines.append(line)
                    continue
                
                if in_toc_section:
                    continue
            
            # Once we find narrative content, include everything
            if found_narrative_start:
                cleaned_lines.append(line)
            
            # Alternative way to detect narrative start if TOC detection fails
            elif not found_narrative_start and any(indicator in line_lower for indicator in [
                'item 1. business',
                'part i - item 1',
                'underwriting for',
                'the company operates'
            ]) and len(line.strip()) > 15:
                found_narrative_start = True
                cleaned_lines.append(line)
        
        # If we didn't find clear narrative start, use a position-based approach
        if not found_narrative_start and len(cleaned_lines) < 1000:
            print("⚠️ Narrative start not detected, using position-based approach")
            
            # Look for the first substantial content after position 20% of document
            start_pos = int(len(lines) * 0.2)
            
            for i in range(start_pos, min(start_pos + 1000, len(lines))):
                line = lines[i]
                if len(line.strip()) > 50 and any(word in line.lower() for word in [
                    'company', 'business', 'operations', 'insurance', 'financial'
                ]):
                    cleaned_lines = lines[i:]
                    break
        
        cleaned_content = '\n'.join(cleaned_lines)
        
        print(f"📝 Pre-processing: {len(text_content):,} → {len(cleaned_content):,} chars")
        print(f"   🗑️ Removed {len(text_content) - len(cleaned_content):,} chars of boilerplate")
        
        return cleaned_content
    
    def _extract_visual_elements(self, soup: BeautifulSoup, filing_url: str) -> List[VisualElement]:
        """Extract and summarize visual elements (images, tables, charts) from the filing."""
        
        visual_elements = []
        
        # Extract images
        images = soup.find_all('img')
        for i, img in enumerate(images[:10]):  # Limit to first 10 images
            try:
                src = img.get('src', '')
                alt_text = img.get('alt', '')
                title = img.get('title', '')
                
                # Skip small decorative images
                width = img.get('width', '0')
                height = img.get('height', '0')
                if width.isdigit() and height.isdigit():
                    if int(width) < 50 or int(height) < 50:
                        continue
                
                # Determine section context
                section_context = self._find_section_context(img)
                
                # Generate description using LLM if available
                description = self._describe_visual_element(img, 'image', alt_text + ' ' + title)
                
                visual_element = VisualElement(
                    section_id=f"image_{i}",
                    section_title=section_context,
                    element_type=SectionType.CHART,
                    page_number=None,
                    description=description,
                    context=section_context,
                    image_data=None,  # Would download if needed
                    extracted_text=alt_text + ' ' + title
                )
                
                visual_elements.append(visual_element)
                
            except Exception as e:
                print(f"⚠️ Error processing image {i}: {e}")
                continue
        
        # Extract tables
        tables = soup.find_all('table')
        for i, table in enumerate(tables[:10]):  # Limit to first 10 tables
            try:
                # Skip very small tables (likely layout tables)
                rows = table.find_all('tr')
                if len(rows) < 2:
                    continue
                
                # Extract table data
                table_text = self._extract_table_text(table)
                section_context = self._find_section_context(table)
                
                # Generate table summary using LLM
                description = self._describe_visual_element(table, 'table', table_text[:500])
                
                visual_element = VisualElement(
                    section_id=f"table_{i}",
                    section_title=section_context,
                    element_type=SectionType.TABLE,
                    page_number=None,
                    description=description,
                    context=section_context,
                    image_data=None,
                    extracted_text=table_text
                )
                
                visual_elements.append(visual_element)
                
            except Exception as e:
                print(f"⚠️ Error processing table {i}: {e}")
                continue
        
        print(f"📊 Extracted {len(visual_elements)} visual elements")
        return visual_elements
    
    def _find_section_context(self, element) -> str:
        """Find which 10-K section this visual element belongs to."""
        
        # Look for section headers in parent elements
        current = element.parent
        for _ in range(10):  # Search up to 10 parent levels
            if current is None:
                break
                
            text = current.get_text()
            if text:
                # Look for 10-K section patterns
                section_match = re.search(r'(Item \d+[A-Z]*|Part [IV]+)', text[:200], re.IGNORECASE)
                if section_match:
                    return section_match.group(1)
            
            current = current.parent
        
        return "Unknown Section"
    
    def _extract_table_text(self, table) -> str:
        """Extract readable text from HTML table."""
        
        rows = table.find_all('tr')
        table_data = []
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            row_text = ' | '.join([cell.get_text().strip() for cell in cells])
            if row_text.strip():
                table_data.append(row_text)
        
        return '\n'.join(table_data[:20])  # Limit to first 20 rows
    
    def _describe_visual_element(self, element, element_type: str, content_sample: str) -> str:
        """Generate description of visual element using LLM."""
        
        if not self.anthropic_client:
            return f"{element_type.title()}: {content_sample[:100]}..."
        
        try:
            if element_type == 'table':
                prompt = f"""Summarize this financial table in 1-2 sentences:

{content_sample}

Focus on what financial data is shown and key metrics. Be concise."""
            else:
                prompt = f"""Describe this image/chart in 1-2 sentences based on context:

Alt text/title: {content_sample}

Focus on what financial information it likely shows. Be concise."""
            
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            
            if response.content and len(response.content) > 0:
                return response.content[0].text.strip()
            
        except Exception as e:
            print(f"⚠️ Error generating visual description: {e}")
        
        return f"{element_type.title()}: {content_sample[:100]}..."
    
    def _split_content_intelligently(self, text_content: str, max_chunk_size: int = 50000) -> List[str]:
        """Split content into chunks that preserve section boundaries."""
        
        # Look for obvious section breaks
        section_markers = [
            "PART I", "PART II", "PART III", "PART IV",
            "Item 1.", "Item 2.", "Item 3.", "Item 4.", "Item 5.", "Item 6.", "Item 7.", "Item 8.", "Item 9.",
            "Item 10.", "Item 11.", "Item 12.", "Item 13.", "Item 14.", "Item 15.", "Item 16.",
            "SIGNATURES"
        ]
        
        chunks = []
        current_chunk = ""
        
        lines = text_content.split('\n')
        
        for line in lines:
            # Check if this line starts a new major section
            line_upper = line.strip().upper()
            is_section_break = any(marker in line_upper for marker in section_markers)
            
            # If adding this line would exceed chunk size and we're at a section break
            if len(current_chunk) + len(line) > max_chunk_size and is_section_break and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = line + '\n'
            else:
                current_chunk += line + '\n'
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _llm_parse_structure_pydantic(self, chunks: List[str]) -> Dict[str, Any]:
        """Use LLM with Pydantic structured output to map content chunks to 10-K structure."""
        
        parsed_sections = {}
        
        # Process more chunks to find Item 7 (MD&A) which is usually later in the filing
        for i, chunk in enumerate(chunks[:6]):  # Increased from 3 to 6 chunks
            try:
                print(f"🔍 Processing chunk {i+1}/{min(6, len(chunks))} with Pydantic...")
                
                # Create structured prompt
                prompt = f"""Analyze this SEC 10-K filing chunk and identify which sections it contains.

10-K sections appear SEQUENTIALLY:
- Part I: Items 1, 1A, 1B, 1C, 2, 3, 4
- Part II: Items 5, 6, 7, 7A, 8, 9, 9A, 9B, 9C  
- Part III: Items 10, 11, 12, 13, 14
- Part IV: Items 15, 16
- Signatures

For each section found, provide:
- section_id: like "item_7" or "item_1a"
- part: like "part_1" or "part_2"
- title: full section title
- content_start: first few words where section begins
- content_length: estimated character count
- contains_key_info: any key terms found (especially for insurance: combined ratio, underwriting, etc.)

CHUNK {i+1}:
{chunk[:8000]}"""

                # Use Anthropic with structured output (tool calling)
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1500,
                    tools=[{
                        "name": "analyze_chunk",
                        "description": "Analyze a 10-K filing chunk and identify sections",
                        "input_schema": ChunkAnalysis.model_json_schema()
                    }],
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Extract structured result
                if response.content and len(response.content) > 0:
                    for content_block in response.content:
                        if hasattr(content_block, 'type') and content_block.type == "tool_use":
                            if content_block.name == "analyze_chunk":
                                # Parse the structured output
                                chunk_analysis = ChunkAnalysis.model_validate(content_block.input)
                                
                                print(f"✅ Parsed chunk {i+1}: {chunk_analysis.chunk_summary}")
                                print(f"   Found {len(chunk_analysis.sections_found)} sections")
                                
                                # Process each section found
                                for section_info in chunk_analysis.sections_found:
                                    section_id = section_info.section_id
                                    part_id = section_info.part
                                    
                                    print(f"   📄 Found section: {section_id} in {part_id}")
                                    
                                    # Extract the actual content for this section from the chunk
                                    section_content = self._extract_section_content_from_chunk(
                                        chunk, section_info.model_dump()
                                    )
                                    
                                    if section_content:
                                        # Find relevant visual elements for this section
                                        section_visuals = self._find_visuals_for_section(
                                            self.current_soup, self.current_filing_url, section_id, section_info.title
                                        )
                                        
                                        # Integrate visual summaries into content
                                        if section_visuals:
                                            visual_summaries = "\n\n[VISUAL CONTENT]\n" + "\n".join([
                                                f"• {visual.description}" for visual in section_visuals
                                            ])
                                            section_content += visual_summaries
                                        
                                        # Create FilingSection object
                                        filing_section = FilingSection(
                                            section_id=section_id,
                                            title=section_info.title,
                                            description=self._get_section_description(section_id),
                                            purpose=self._get_section_purpose(section_id),
                                            content=section_content,
                                            visual_elements=section_visuals,
                                            key_contents=section_info.contains_key_info
                                        )
                                        
                                        # Store in hierarchical structure
                                        if part_id not in parsed_sections:
                                            parsed_sections[part_id] = {"subsections": {}}
                                        
                                        parsed_sections[part_id]["subsections"][section_id] = {"section": filing_section}
                                        print(f"   ✅ Stored section {section_id} ({len(section_content)} chars)")
                                
                                break
                
            except Exception as e:
                print(f"⚠️ Error parsing chunk {i+1} with Pydantic: {e}")
                continue
        
        return parsed_sections
    
    def _fallback_parse_structure(self, text_content: str) -> Dict[str, Any]:
        """Simple fallback parsing when LLM is not available."""
        
        # Basic text search for major sections
        sections_found = {}
        
        # Look for MD&A (most important for insurance metrics)
        mda_start = text_content.lower().find("management's discussion and analysis")
        if mda_start != -1:
            # Find end (look for next major section)
            mda_end = text_content.lower().find("financial statements", mda_start)
            if mda_end == -1:
                mda_end = mda_start + 50000  # Default chunk size
            
            mda_content = text_content[mda_start:mda_end]
            
            filing_section = FilingSection(
                section_id="item_7",
                title="Management's Discussion and Analysis",
                description="Management's analysis of financial performance",
                purpose="Financial performance analysis",
                content=mda_content,
                visual_elements=[],
                key_contents=[]
            )
            
            sections_found["part_2"] = {
                "subsections": {
                    "item_7": {"section": filing_section}
                }
            }
        
        return sections_found
    
    def _extract_section_content_from_chunk(self, chunk: str, section_info: Dict) -> str:
        """Extract specific section content from a chunk using LLM-driven boundary detection."""
        
        # Use the LLM's guidance about where content starts
        content_start_hint = section_info.get("content_start", "")
        section_id = section_info.get("section_id", "")
        
        if content_start_hint:
            # Find the approximate location where this section starts
            start_pos = chunk.lower().find(content_start_hint.lower()[:50])
            if start_pos != -1:
                
                # Extract a large chunk from the section start (up to 50k chars)
                chunk_from_start = chunk[start_pos:start_pos + 50000]
                
                # Use LLM to intelligently find where the next section begins
                if self.anthropic_client and len(chunk_from_start) > 1000:
                    section_content = self._llm_find_section_boundary(chunk_from_start, section_id)
                    if section_content:
                        return section_content
                
                # Fallback: try regex patterns for next section
                section_content = self._regex_find_section_boundary(chunk_from_start, section_id)
                if section_content:
                    return section_content
        
        # Enhanced fallback: try to find the section by ID patterns
        section_patterns = {
            "item_1a": [r"item\s+1a", r"risk\s+factors"],
            "item_7": [r"item\s+7", r"management.*discussion.*analysis", r"md&a"],
            "item_1": [r"item\s+1[^a-z]", r"\bbusiness\b"],
            "item_8": [r"item\s+8", r"financial\s+statements"],
        }
        
        if section_id in section_patterns:
            import re
            for pattern in section_patterns[section_id]:
                match = re.search(pattern, chunk.lower())
                if match:
                    start_pos = match.start()
                    # Take substantial content from this position
                    return chunk[start_pos:start_pos + 15000].strip()
        
        # Final fallback: return a portion of the chunk
        return chunk[:10000].strip()
    
    def _llm_find_section_boundary(self, chunk: str, current_section_id: str) -> Optional[str]:
        """Use LLM to intelligently find where the current section ends and next section begins."""
        
        # Define the expected sequence of 10-K sections
        section_sequence = [
            "item_1", "item_1a", "item_1b", "item_1c", "item_2", "item_3", "item_4",  # Part I
            "item_5", "item_6", "item_7", "item_7a", "item_8", "item_9", "item_9a", "item_9b", "item_9c",  # Part II
            "item_10", "item_11", "item_12", "item_13", "item_14",  # Part III
            "item_15", "item_16", "signatures"  # Part IV
        ]
        
        # Find what the next expected section should be
        try:
            current_index = section_sequence.index(current_section_id)
            next_sections = section_sequence[current_index + 1:current_index + 4]  # Check next 3 sections
        except ValueError:
            next_sections = ["item_1b", "item_2", "item_3"]  # Default fallback
        
        # Create LLM prompt to find section boundary
        prompt = f"""Find where section {current_section_id.upper().replace('_', ' ')} ends and the next section begins.

Current section: {current_section_id.upper().replace('_', ' ')}
Look for these next sections: {', '.join([s.upper().replace('_', ' ') for s in next_sections])}

In this content, find where the current section ends. Look for patterns like:
- "Item 1B" or "ITEM 1B" (for next section)
- "Unresolved Staff Comments" (next section title)
- "Item 2" or "ITEM 2" (for next section)
- "Properties" (next section title)

The content may be HTML-encoded, so look for headers in <div>, <span>, or other tags.

Content:
{chunk[:8000]}

Return ONLY the character position where the next section header begins, or "NOT_FOUND" if no clear boundary is found. Just return a number like "1205" or "NOT_FOUND"."""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=50,
                messages=[{"role": "user", "content": prompt}]
            )
            
            if response.content and len(response.content) > 0:
                boundary_result = response.content[0].text.strip()
                
                if boundary_result.isdigit():
                    boundary_pos = int(boundary_result)
                    if 0 < boundary_pos < len(chunk):
                        section_content = chunk[:boundary_pos].strip()
                        
                        # Ensure we have substantial content
                        if len(section_content) >= 500:
                            return section_content
            
        except Exception as e:
            print(f"⚠️ Error in LLM boundary detection: {e}")
        
        return None
    
    def _regex_find_section_boundary(self, chunk: str, section_id: str) -> Optional[str]:
        """Fallback regex-based boundary detection."""
        
        # Look for patterns that indicate the next section starts
        next_section_patterns = [
            r'\n\s*ITEM\s+\d+[A-Z]*\.?\s*[A-Z\s]+\n',  # "ITEM 2. PROPERTIES"
            r'\n\s*Item\s+\d+[A-Z]*\.?\s*[A-Z\s]+\n',  # "Item 2. Properties"
            r'\n\s*PART\s+(I{1,4}|[1-4])\s*\n',       # "PART II"
            r'\n\s*Part\s+(I{1,4}|[1-4])\s*\n',       # "Part II"
            r'\n\s*SIGNATURES\s*\n',                   # "SIGNATURES"
            r'<[^>]*>\s*ITEM\s+\d+[A-Z]*',             # HTML-encoded "ITEM 1B"
            r'<[^>]*>\s*Item\s+\d+[A-Z]*',             # HTML-encoded "Item 1B"
        ]
        
        import re
        min_end_pos = len(chunk)  # Default to end of chunk
        
        for pattern in next_section_patterns:
            # Look for the pattern starting at least 500 chars after section start
            # (to avoid catching the current section's header)
            search_text = chunk[500:]
            match = re.search(pattern, search_text, re.IGNORECASE | re.MULTILINE)
            if match:
                end_pos = 500 + match.start()
                min_end_pos = min(min_end_pos, end_pos)
        
        # Extract content from section start to next section (or end of chunk)
        section_content = chunk[:min_end_pos].strip()
        
        # Ensure we have substantial content (at least 100 chars)
        if len(section_content) >= 100:
            return section_content
        else:
            # Fallback: take at least 5000 chars if the section seems too short
            return chunk[:min(5000, len(chunk))].strip()
        
        return None
    
    def _get_section_description(self, section_id: str) -> str:
        """Get description for a section ID."""
        for part_info in self.FORM_10K_STRUCTURE.values():
            if isinstance(part_info, dict) and "sections" in part_info:
                if section_id in part_info["sections"]:
                    return part_info["sections"][section_id].get("purpose", "")
        return ""
    
    def _get_section_purpose(self, section_id: str) -> str:
        """Get purpose for a section ID."""
        return self._get_section_description(section_id)  # Same for now
    
    def get_section_by_path(self, parsed_filing: Dict, path: str) -> Optional[FilingSection]:
        """Get a section by path using LLM intelligence to map user-friendly paths to internal structure."""
        
        if not self.anthropic_client:
            # Fallback to simple mapping if no LLM available
            return self._fallback_path_lookup(parsed_filing, path)
        
        # Use LLM to intelligently map the path to our internal structure
        available_paths = []
        
        def collect_paths(current_path: str, structure: Dict):
            for key, value in structure.items():
                new_path = f"{current_path}.{key}" if current_path else key
                
                if isinstance(value, dict):
                    if "section" in value and isinstance(value["section"], FilingSection):
                        section = value["section"]
                        available_paths.append({
                            "internal_path": new_path,
                            "section_id": section.section_id,
                            "title": section.title,
                            "description": section.description
                        })
                    
                    if "subsections" in value:
                        collect_paths(new_path, value["subsections"])
        
        collect_paths("", parsed_filing["structure"])
        
        if not available_paths:
            return None
        
        # Create LLM prompt for path mapping
        paths_info = "\n".join([
            f"- {p['internal_path']}: {p['title']} ({p['description']})"
            for p in available_paths[:20]  # Limit to avoid token issues
        ])
        
        prompt = f"""Map the user's section path to the correct internal path.

User requested path: "{path}"

Available sections:
{paths_info}

Common mappings:
- Part1 or PartI → part_1
- Part2 or PartII → part_2  
- Item1A → item_1a
- Item7 → item_7

Return just the exact internal path that matches the user's request, or "NOT_FOUND" if no match."""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            
            if response.content and len(response.content) > 0:
                mapped_path = response.content[0].text.strip()
                
                if mapped_path and mapped_path != "NOT_FOUND":
                    # Now use the mapped path to find the section
                    return self._get_section_by_internal_path(parsed_filing, mapped_path)
            
        except Exception as e:
            print(f"⚠️ Error in LLM path mapping: {e}")
        
        # Fallback to simple mapping
        return self._fallback_path_lookup(parsed_filing, path)
    
    def _get_section_by_internal_path(self, parsed_filing: Dict, internal_path: str) -> Optional[FilingSection]:
        """Get section using exact internal path like 'part_1.item_1a'."""
        parts = internal_path.split('.')
        current = parsed_filing["structure"]
        
        for part in parts:
            if part in current:
                current = current[part]
                if "subsections" in current:
                    current = current["subsections"]
            else:
                return None
        
        # Extract the FilingSection
        if isinstance(current, dict) and "section" in current:
            return current["section"]
        
        return None
    
    def _fallback_path_lookup(self, parsed_filing: Dict, path: str) -> Optional[FilingSection]:
        """Simple fallback path mapping when LLM is not available."""
        
        # Basic transformations
        path_lower = path.lower()
        
        # Convert common formats
        path_lower = path_lower.replace("part1", "part_1")
        path_lower = path_lower.replace("parti", "part_1") 
        path_lower = path_lower.replace("part2", "part_2")
        path_lower = path_lower.replace("partii", "part_2")
        path_lower = path_lower.replace("item1a", "item_1a")
        path_lower = path_lower.replace("item7", "item_7")
        path_lower = path_lower.replace("item1", "item_1")
        
        return self._get_section_by_internal_path(parsed_filing, path_lower)
    
    def find_content_with_keywords(self, parsed_filing: Dict, keywords: List[str]) -> List[Tuple[str, FilingSection]]:
        """Find all sections containing specific keywords."""
        results = []
        
        def search_structure(current_path: str, structure: Dict):
            for key, value in structure.items():
                new_path = f"{current_path}.{key}" if current_path else key
                
                if isinstance(value, dict):
                    if "section" in value and isinstance(value["section"], FilingSection):
                        section = value["section"]
                        content_lower = section.content.lower()
                        
                        for keyword in keywords:
                            if keyword.lower() in content_lower:
                                results.append((new_path, section))
                                break
                    
                    if "subsections" in value:
                        search_structure(new_path, value["subsections"])
        
        search_structure("", parsed_filing["structure"])
        return results

    def _find_visuals_for_section(self, soup: BeautifulSoup, filing_url: str, section_id: str, section_title: str) -> List[VisualElement]:
        """Extract visual elements from the current section chunk with better filtering for meaningful tables."""
        
        # Get the section's text content to understand what we're looking for
        section_visuals = []
        
        # Instead of searching the entire document, we need to extract from the section content
        # But since we only have the soup of the entire document, we'll try a different approach
        
        # Look for section-specific content by finding the section header and extracting tables after it
        section_patterns = [
            f"item {section_id.split('_')[1]}" if 'item_' in section_id else section_id,
            section_title.lower()
        ]
        
        # Find where this section starts in the document
        section_start_element = None
        for pattern in section_patterns:
            # Look for headers that match this section
            headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'div', 'span', 'p'])
            for header in headers:
                header_text = header.get_text().lower()
                if pattern.lower() in header_text and len(header_text) < 200:  # Reasonable header length
                    section_start_element = header
                    break
            if section_start_element:
                break
        
        if not section_start_element:
            print(f"   ⚠️ Could not locate section header for {section_id}")
            return []
        
        # Find tables that appear after this section header
        current_element = section_start_element
        tables_found = 0
        
        # Traverse forward from the section header to find tables in this section
        for _ in range(2000):  # Limit search to prevent infinite loops
            if current_element is None:
                break
                
            current_element = current_element.find_next()
            
            if current_element is None:
                break
            
            # Stop if we hit the next major section
            if current_element.name in ['h1', 'h2', 'h3'] and current_element.get_text():
                next_section_text = current_element.get_text().lower()
                if any(indicator in next_section_text for indicator in [
                    'item ', 'part ', 'signatures'
                ]) and len(next_section_text) < 200:
                    break
            
            # Check if this element is a table
            if current_element.name == 'table':
                try:
                    rows = current_element.find_all('tr')
                    if len(rows) < 3:  # Need at least 3 rows
                        continue
                    
                    table_text = self._extract_table_text(current_element)
                    
                    # Check if this table is meaningful and relevant to this section
                    if self._is_meaningful_table(table_text) and self._is_section_relevant_table(table_text, section_id):
                        description = self._describe_visual_element(current_element, 'table', table_text[:1000])
                        
                        visual_element = VisualElement(
                            section_id=f"{section_id}_table_{tables_found}",
                            section_title=section_title,
                            element_type=SectionType.TABLE,
                            page_number=None,
                            description=description,
                            context=f"Found in {section_title}",
                            image_data=None,
                            extracted_text=table_text
                        )
                        section_visuals.append(visual_element)
                        tables_found += 1
                        
                        print(f"   📊 Found table {tables_found} in {section_id}: {description[:100]}...")
                        
                        # Limit to 3 meaningful tables per section
                        if tables_found >= 3:
                            break
                except Exception as e:
                    print(f"   ⚠️ Error processing table in {section_id}: {e}")
                    continue
        
        print(f"   📋 Found {len(section_visuals)} visual elements for {section_id}")
        return section_visuals

    def _is_section_relevant_table(self, table_text: str, section_id: str) -> bool:
        """Check if a table is relevant to the specific section."""
        
        text_lower = table_text.lower()
        
        # Section-specific keywords
        section_keywords = {
            'item_1a': ['risk', 'factor', 'exposure', 'impact'],
            'item_1': ['business', 'operation', 'product', 'service', 'coverage'],
            'item_7': ['year ended', 'december', 'million', 'income', 'revenue', 'expense', 
                      'prior accident', 'development', 'catastrophe', 'loss', 'ratio', 'premium'],
            'item_5': ['share', 'stock', 'dividend', 'repurchase', 'market'],
            'item_8': ['balance sheet', 'statement', 'cash flow', 'equity']
        }
        
        # Skip the securities listing table that keeps appearing
        if 'trading symbol' in text_lower and 'new york stock exchange' in text_lower:
            return False
        
        relevant_keywords = section_keywords.get(section_id, [])
        if not relevant_keywords:
            return True  # Allow tables for sections we don't have specific keywords for
        
        # Check if table has at least 2 relevant keywords
        keyword_count = sum(1 for keyword in relevant_keywords if keyword in text_lower)
        return keyword_count >= 2

    def _is_meaningful_table(self, table_text: str) -> bool:
        """Check if a table contains meaningful financial data rather than layout elements."""
        
        if not table_text or len(table_text) < 50:
            return False
        
        # Skip tables that are mostly empty cells or layout tables
        lines = table_text.split('\n')
        non_empty_lines = [line for line in lines if line.strip() and line.strip() != '|']
        
        if len(non_empty_lines) < 3:
            return False
        
        # Look for financial indicators
        financial_keywords = [
            'million', 'billion', 'thousand', '$', 'percent', '%',
            'revenue', 'income', 'loss', 'assets', 'liabilities',
            'ratio', 'premium', 'claim', 'underwriting', 'investment',
            'year ended', 'december', 'quarter', 'fiscal'
        ]
        
        text_lower = table_text.lower()
        keyword_count = sum(1 for keyword in financial_keywords if keyword in text_lower)
        
        # Skip if it looks like a form header/checkbox table
        if any(skip_phrase in text_lower for skip_phrase in [
            'annual report pursuant',
            'securities exchange act',
            'check one',
            'commission file number'
        ]):
            return False
        
        # Table must have at least 2 financial keywords to be considered meaningful
        return keyword_count >= 2 