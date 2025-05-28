"""Anthropic client with SEC filing tools for interactive analysis."""

import json
import os
from typing import Dict, List, Optional, Any

import anthropic
from sec_edgar_api import EdgarClient

# Import our new filing parser
from ..utils.filing_parser import FilingParser
from ..utils.filing_sections import TenKStructureParser


class AnthropicSecAgent:
    """Anthropic agent with SEC filing tools for interactive analysis."""
    
    def __init__(self, api_key: Optional[str] = None, sec_user_agent: Optional[str] = None):
        """Initialize the Anthropic SEC agent."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided or set in environment")
        
        self.sec_user_agent = sec_user_agent or os.getenv("SEC_USER_AGENT", "SEC Filing Agent admin@example.com")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.edgar_client = EdgarClient(user_agent=self.sec_user_agent)
        
        # Initialize filing parsers with Anthropic client for LLM-driven parsing
        self.filing_parser = FilingParser(user_agent=self.sec_user_agent)
        self.structure_parser = TenKStructureParser(user_agent=self.sec_user_agent, anthropic_client=self.client)
        
        # Store current user question for intelligent filtering
        self.current_user_question = None
    
    def _filter_data_with_llm(self, data: Dict[str, Any], user_question: str, data_type: str) -> Dict[str, Any]:
        """Use Claude to intelligently filter large datasets based on the user's question."""
        try:
            # Convert data to JSON string for analysis
            data_str = json.dumps(data, indent=2, default=str)
            
            # If data is too large, take a sample for analysis
            if len(data_str) > 100000:  # 100KB limit for filtering analysis
                print(f"📊 Large {data_type} dataset detected, using LLM to extract relevant information...")
                
                # Create a sample of the data structure for the LLM to understand
                sample_data = self._create_data_sample(data, max_items=10)
                sample_str = json.dumps(sample_data, indent=2, default=str)
                
                filter_prompt = f"""You are analyzing SEC financial data to answer this user question: "{user_question}"

Here's a sample of the available {data_type} data structure:
{sample_str}

Based on the user's question, please identify:
1. Which specific financial metrics/concepts are most relevant
2. Which time periods should be included (e.g., recent years, specific quarters)
3. What calculations or comparisons might be needed
4. Any specific data points that directly answer the question

Respond with a JSON object containing:
{{
    "relevant_concepts": ["list", "of", "relevant", "financial", "concepts"],
    "time_periods": ["recent", "historical", "specific_years"],
    "calculations_needed": ["ratios", "trends", "comparisons"],
    "key_data_points": ["specific", "metrics", "to", "extract"],
    "reasoning": "Brief explanation of why these are relevant"
}}"""

                # Get filtering guidance from Claude
                filter_response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": filter_prompt}]
                )
                
                try:
                    filter_guidance = json.loads(filter_response.content[0].text)
                    print(f"🎯 LLM identified relevant concepts: {filter_guidance.get('relevant_concepts', [])}")
                    
                    # Apply intelligent filtering based on guidance
                    filtered_data = self._apply_intelligent_filter(data, filter_guidance, user_question)
                    return filtered_data
                    
                except json.JSONDecodeError:
                    print("⚠️ Could not parse LLM filtering guidance, using fallback filtering")
                    return self._apply_fallback_filter(data, user_question)
            else:
                # Data is small enough, return as-is
                return data
                
        except Exception as e:
            print(f"⚠️ Error in LLM filtering: {e}, using fallback")
            return self._apply_fallback_filter(data, user_question)
    
    def _create_data_sample(self, data: Dict[str, Any], max_items: int = 10) -> Dict[str, Any]:
        """Create a representative sample of large data for LLM analysis."""
        if isinstance(data, dict):
            sample = {}
            for key, value in list(data.items())[:max_items]:
                if isinstance(value, dict):
                    sample[key] = self._create_data_sample(value, max_items=3)
                elif isinstance(value, list) and len(value) > 0:
                    sample[key] = value[:3] + ["..."] if len(value) > 3 else value
                else:
                    sample[key] = value
            return sample
        return data
    
    def _apply_intelligent_filter(self, data: Dict[str, Any], guidance: Dict[str, Any], user_question: str) -> Dict[str, Any]:
        """Apply intelligent filtering based on LLM guidance."""
        relevant_concepts = guidance.get('relevant_concepts', [])
        
        # For company facts data, filter by relevant concepts
        if 'facts' in data and isinstance(data['facts'], dict):
            filtered_facts = {}
            
            for taxonomy, concepts in data['facts'].items():
                if isinstance(concepts, dict):
                    filtered_concepts = {}
                    
                    for concept_name, concept_data in concepts.items():
                        # Check if this concept is relevant based on guidance
                        if any(relevant.lower() in concept_name.lower() for relevant in relevant_concepts):
                            # Keep recent data only (last 5 years)
                            if isinstance(concept_data, dict) and 'units' in concept_data:
                                filtered_concept = {'units': {}}
                                for unit, values in concept_data['units'].items():
                                    if isinstance(values, list):
                                        # Sort by date and keep recent entries
                                        recent_values = sorted(values, 
                                                             key=lambda x: x.get('end', ''), 
                                                             reverse=True)[:20]  # Last 20 entries
                                        filtered_concept['units'][unit] = recent_values
                                filtered_concepts[concept_name] = filtered_concept
                    
                    if filtered_concepts:
                        filtered_facts[taxonomy] = filtered_concepts
            
            # Return filtered data with metadata
            return {
                'cik': data.get('cik'),
                'entityName': data.get('entityName'),
                'facts': filtered_facts,
                'filter_applied': True,
                'filter_reasoning': guidance.get('reasoning', 'Filtered based on question relevance'),
                'original_concepts_count': sum(len(concepts) for concepts in data.get('facts', {}).values() if isinstance(concepts, dict)),
                'filtered_concepts_count': sum(len(concepts) for concepts in filtered_facts.values())
            }
        
        return data
    
    def _apply_fallback_filter(self, data: Dict[str, Any], user_question: str) -> Dict[str, Any]:
        """Apply simple keyword-based filtering as fallback."""
        # Simple keyword matching for common financial terms
        financial_keywords = [
            'revenue', 'income', 'profit', 'loss', 'assets', 'liabilities', 'equity',
            'cash', 'debt', 'earnings', 'sales', 'expenses', 'margin', 'ratio',
            'combined', 'premium', 'claims', 'reserves'  # Insurance-specific
        ]
        
        question_lower = user_question.lower()
        relevant_keywords = [kw for kw in financial_keywords if kw in question_lower]
        
        if 'facts' in data and relevant_keywords:
            print(f"🔍 Applying fallback filter for keywords: {relevant_keywords}")
            
            # Filter company facts based on keywords
            filtered_facts = {}
            for taxonomy, concepts in data['facts'].items():
                if isinstance(concepts, dict):
                    filtered_concepts = {}
                    
                    for concept_name, concept_data in concepts.items():
                        # Check if concept name contains any relevant keywords
                        concept_lower = concept_name.lower()
                        if any(keyword in concept_lower for keyword in relevant_keywords):
                            # Keep recent data only
                            if isinstance(concept_data, dict) and 'units' in concept_data:
                                filtered_concept = {'units': {}}
                                for unit, values in concept_data['units'].items():
                                    if isinstance(values, list):
                                        # Keep last 10 entries
                                        recent_values = sorted(values, 
                                                             key=lambda x: x.get('end', ''), 
                                                             reverse=True)[:10]
                                        filtered_concept['units'][unit] = recent_values
                                filtered_concepts[concept_name] = filtered_concept
                    
                    if filtered_concepts:
                        filtered_facts[taxonomy] = filtered_concepts
            
            if filtered_facts:
                return {
                    'cik': data.get('cik'),
                    'entityName': data.get('entityName'),
                    'facts': filtered_facts,
                    'filter_applied': True,
                    'filter_type': 'keyword_fallback',
                    'keywords_used': relevant_keywords,
                    'original_concepts_count': sum(len(concepts) for concepts in data.get('facts', {}).values() if isinstance(concepts, dict)),
                    'filtered_concepts_count': sum(len(concepts) for concepts in filtered_facts.values())
                }
        
        # If no filtering applied, return a summary to avoid token limits
        if 'facts' in data:
            print("⚠️ No specific keywords found, returning data summary to avoid token limits")
            summary_facts = {}
            for taxonomy, concepts in data['facts'].items():
                if isinstance(concepts, dict):
                    # Just return concept names and basic info
                    summary_concepts = {}
                    for concept_name, concept_data in list(concepts.items())[:20]:  # Limit to 20 concepts
                        if isinstance(concept_data, dict) and 'units' in concept_data:
                            summary_concepts[concept_name] = {
                                'available_units': list(concept_data['units'].keys()),
                                'data_points_count': sum(len(values) for values in concept_data['units'].values())
                            }
                    summary_facts[taxonomy] = summary_concepts
            
            return {
                'cik': data.get('cik'),
                'entityName': data.get('entityName'),
                'facts_summary': summary_facts,
                'filter_applied': True,
                'filter_type': 'summary_fallback',
                'note': 'Returned summary due to large dataset. Use get_company_concept for specific metrics.'
            }
        
        return data

    def get_tools(self) -> List[Dict[str, Any]]:
        """Define the SEC filing tools available to Claude."""
        return [
            {
                "name": "get_company_submissions",
                "description": "Get SEC submissions (filings) for a company by CIK or ticker. Returns filing history including 10-K, 10-Q, 8-K forms.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "cik": {
                            "type": "string",
                            "description": "Company CIK (Central Index Key) - 10 digit number. Examples: '0000320193' for Apple, '0000789019' for Microsoft"
                        }
                    },
                    "required": ["cik"]
                }
            },
            {
                "name": "get_company_facts",
                "description": "Get comprehensive financial facts for a company from SEC filings. Returns XBRL financial data intelligently filtered based on your question to avoid token limits.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "cik": {
                            "type": "string",
                            "description": "Company CIK (Central Index Key) - 10 digit number"
                        },
                        "user_question": {
                            "type": "string",
                            "description": "The user's question or analysis goal - used to intelligently filter relevant financial data"
                        }
                    },
                    "required": ["cik", "user_question"]
                }
            },
            {
                "name": "get_company_concept",
                "description": "Get specific financial concept data for a company (e.g., just revenue or just assets).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "cik": {
                            "type": "string",
                            "description": "Company CIK (Central Index Key)"
                        },
                        "taxonomy": {
                            "type": "string",
                            "description": "Taxonomy (usually 'us-gaap' for US companies)",
                            "enum": ["us-gaap", "ifrs-full", "dei"]
                        },
                        "tag": {
                            "type": "string",
                            "description": "Financial concept tag (e.g., 'Revenues', 'Assets', 'NetIncomeLoss')"
                        }
                    },
                    "required": ["cik", "taxonomy", "tag"]
                }
            },
            {
                "name": "lookup_company_cik",
                "description": "Helper function to find a company's CIK if you only know the company name or ticker. Note: This is a simplified lookup.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "identifier": {
                            "type": "string",
                            "description": "Company name or ticker symbol to look up"
                        }
                    },
                    "required": ["identifier"]
                }
            },
            {
                "name": "download_structured_filing",
                "description": "Download and parse a complete 10-K filing with comprehensive nested structure (Part I, Part II, etc. with all subsections). Returns complete filing mapped to regulatory structure.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "cik": {
                            "type": "string",
                            "description": "Company CIK (Central Index Key)"
                        },
                        "form_type": {
                            "type": "string",
                            "description": "Form type to download (default: 10-K)",
                            "enum": ["10-K", "10-Q"],
                            "default": "10-K"
                        }
                    },
                    "required": ["cik"]
                }
            },
            {
                "name": "get_filing_section",
                "description": "Get a specific section from a 10-K filing using hierarchical path (e.g., 'part_2.item_7' for MD&A, 'part_1.item_1.item_1a' for Risk Factors under Business).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "cik": {
                            "type": "string",
                            "description": "Company CIK (Central Index Key)"
                        },
                        "section_path": {
                            "type": "string",
                            "description": "Hierarchical path to section. Examples: 'part_2.item_7' (MD&A), 'part_1.item_1.item_1a' (Risk Factors), 'part_2.item_7.item_7a' (Market Risk), 'part_2.item_8' (Financial Statements)",
                            "enum": [
                                "part_1.item_1", "part_1.item_1.item_1a", "part_1.item_1.item_1b", "part_1.item_1.item_1c", 
                                "part_1.item_2", "part_1.item_3", "part_1.item_4",
                                "part_2.item_5", "part_2.item_6", "part_2.item_7", "part_2.item_7.item_7a", 
                                "part_2.item_8", "part_2.item_9", "part_2.item_9.item_9a", "part_2.item_9.item_9b", "part_2.item_9.item_9c",
                                "part_3.item_10", "part_3.item_11", "part_3.item_12", "part_3.item_13", "part_3.item_14",
                                "part_4.item_15", "part_4.item_16", "signatures"
                            ]
                        },
                        "form_type": {
                            "type": "string",
                            "description": "Form type (default: 10-K)",
                            "enum": ["10-K", "10-Q"],
                            "default": "10-K"
                        }
                    },
                    "required": ["cik", "section_path"]
                }
            },
            {
                "name": "search_filing_content",
                "description": "Search for specific content/keywords across all sections of a 10-K filing (e.g., 'combined ratio', 'underwriting', 'cybersecurity').",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "cik": {
                            "type": "string",
                            "description": "Company CIK (Central Index Key)"
                        },
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Keywords to search for (e.g., ['combined ratio', 'underwriting'])"
                        },
                        "form_type": {
                            "type": "string",
                            "description": "Form type (default: 10-K)",
                            "enum": ["10-K", "10-Q"],
                            "default": "10-K"
                        }
                    },
                    "required": ["cik", "keywords"]
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a SEC filing tool and return the result."""
        try:
            if tool_name == "get_company_submissions":
                cik = tool_input["cik"]
                print(f"🔍 Fetching submissions for CIK {cik}...")
                result = self.edgar_client.get_submissions(cik=cik)
                return {"success": True, "data": result}
                
            elif tool_name == "get_company_facts":
                cik = tool_input["cik"]
                user_question = tool_input["user_question"]
                print(f"📊 Fetching company facts for CIK {cik}...")
                
                # Get the raw data from SEC
                raw_result = self.edgar_client.get_company_facts(cik=cik)
                
                # Apply intelligent filtering based on user's question
                print(f"🧠 Applying intelligent filtering for question: '{user_question}'")
                filtered_result = self._filter_data_with_llm(raw_result, user_question, "company_facts")
                
                return {"success": True, "data": filtered_result}
                
            elif tool_name == "get_company_concept":
                cik = tool_input["cik"]
                taxonomy = tool_input["taxonomy"]
                tag = tool_input["tag"]
                print(f"🎯 Fetching {taxonomy}:{tag} for CIK {cik}...")
                result = self.edgar_client.get_company_concept(cik=cik, taxonomy=taxonomy, tag=tag)
                return {"success": True, "data": result}
                
            elif tool_name == "lookup_company_cik":
                identifier = tool_input["identifier"].upper()
                print(f"🔎 Looking up CIK for {identifier}...")
                
                # Simple lookup for common companies
                common_ciks = {
                    "AAPL": "0000320193", "APPLE": "0000320193",
                    "MSFT": "0000789019", "MICROSOFT": "0000789019",
                    "GOOGL": "0001652044", "GOOGLE": "0001652044", "ALPHABET": "0001652044",
                    "AMZN": "0001018724", "AMAZON": "0001018724",
                    "TSLA": "0001318605", "TESLA": "0001318605",
                    "META": "0001326801", "FACEBOOK": "0001326801",
                    "NVDA": "0001045810", "NVIDIA": "0001045810",
                    "HIG": "0000874766", "HARTFORD": "0000874766",
                    "JPM": "0000019617", "JPMORGAN": "0000019617",
                    "BAC": "0000070858", "BANK OF AMERICA": "0000070858"
                }
                
                cik = common_ciks.get(identifier)
                if cik:
                    return {"success": True, "data": {"cik": cik, "identifier": identifier}}
                else:
                    return {"success": False, "error": f"CIK not found for {identifier}. Please provide the 10-digit CIK directly."}
            
            elif tool_name == "download_structured_filing":
                cik = tool_input["cik"]
                form_type = tool_input.get("form_type", "10-K")
                
                print(f"📄 Downloading structured {form_type} filing for CIK {cik}...")
                
                # Get submissions to find the latest filing
                submissions = self.edgar_client.get_submissions(cik=cik)
                filing_info = self.filing_parser.get_filing_info_from_submissions(submissions, form_type)
                
                if not filing_info:
                    return {"success": False, "error": f"No {form_type} filing found for CIK {cik}"}
                
                # Construct filing URL
                filing_url = self.filing_parser.construct_filing_url(
                    filing_info['cik'],
                    filing_info['accession_number'],
                    filing_info['primary_document']
                )
                
                print(f"📡 Downloading from: {filing_url}")
                
                # Download filing content
                filing_content = self.filing_parser.download_filing_content(filing_url)
                
                # Parse structured sections using new nested parser
                parsed_filing = self.structure_parser.parse_structured_filing(filing_content, filing_url)
                
                # Prepare response with summaries to avoid token limits
                response_data = {
                    "filing_info": filing_info,
                    "filing_url": filing_url,
                    "total_length": parsed_filing["total_length"],
                    "parsing_method": parsed_filing.get("parsing_method", "unknown"),
                    "chunks_processed": parsed_filing.get("chunks_processed", 0),
                    "structure": parsed_filing["structure"],  # Include the actual parsed structure
                    "structure_summary": {}
                }
                
                # Create summary of what was found
                for part_id, part_data in parsed_filing["structure"].items():
                    if isinstance(part_data, dict) and "subsections" in part_data:
                        # Get part info from our structure definition
                        part_info = self.structure_parser.FORM_10K_STRUCTURE.get(part_id, {})
                        response_data["structure_summary"][part_id] = {
                            "title": part_info.get("title", f"Part {part_id}"),
                            "purpose": part_info.get("purpose", "Unknown purpose"),
                            "subsections_found": list(part_data["subsections"].keys())
                        }
                    else:
                        response_data["structure_summary"][part_id] = {
                            "title": getattr(part_data, 'title', 'Unknown'),
                            "content_length": len(getattr(part_data, 'content', ''))
                        }
                
                return {"success": True, "data": response_data}
            
            elif tool_name == "get_filing_section":
                cik = tool_input["cik"]
                section_path = tool_input["section_path"]
                form_type = tool_input.get("form_type", "10-K")
                
                print(f"📄 Getting {section_path} from {form_type} filing for CIK {cik}...")
                
                # Get submissions to find the latest filing
                submissions = self.edgar_client.get_submissions(cik=cik)
                filing_info = self.filing_parser.get_filing_info_from_submissions(submissions, form_type)
                
                if not filing_info:
                    return {"success": False, "error": f"No {form_type} filing found for CIK {cik}"}
                
                # Construct filing URL
                filing_url = self.filing_parser.construct_filing_url(
                    filing_info['cik'],
                    filing_info['accession_number'],
                    filing_info['primary_document']
                )
                
                # Download filing content
                filing_content = self.filing_parser.download_filing_content(filing_url)
                
                # Parse structured sections
                parsed_filing = self.structure_parser.parse_structured_filing(filing_content, filing_url)
                
                # Get the specific section using the path
                section = self.structure_parser.get_section_by_path(parsed_filing, section_path)
                
                if not section:
                    return {"success": False, "error": f"Section {section_path} not found in filing"}
                
                response_data = {
                    "filing_info": filing_info,
                    "section": {
                        "path": section_path,
                        "title": section.title,
                        "purpose": section.purpose,
                        "content": section.content[:5000] + "..." if len(section.content) > 5000 else section.content,
                        "full_content_length": len(section.content),
                        "visual_elements": [
                            {
                                "type": elem.element_type.value,
                                "description": elem.description,
                                "context": elem.context
                            }
                            for elem in section.visual_elements
                        ]
                    }
                }
                
                return {"success": True, "data": response_data}
            
            elif tool_name == "search_filing_content":
                cik = tool_input["cik"]
                keywords = tool_input["keywords"]
                form_type = tool_input.get("form_type", "10-K")
                
                print(f"🔍 Searching for keywords: {keywords} in {form_type} filing for CIK {cik}...")
                
                # Get submissions to find the latest filing
                submissions = self.edgar_client.get_submissions(cik=cik)
                filing_info = self.filing_parser.get_filing_info_from_submissions(submissions, form_type)
                
                if not filing_info:
                    return {"success": False, "error": f"No {form_type} filing found for CIK {cik}"}
                
                # Construct filing URL
                filing_url = self.filing_parser.construct_filing_url(
                    filing_info['cik'],
                    filing_info['accession_number'],
                    filing_info['primary_document']
                )
                
                # Download filing content
                filing_content = self.filing_parser.download_filing_content(filing_url)
                
                # Parse structured sections
                parsed_filing = self.structure_parser.parse_structured_filing(filing_content, filing_url)
                
                # Search for keywords using the new method
                found_sections = self.structure_parser.find_content_with_keywords(parsed_filing, keywords)
                
                response_data = {
                    "filing_info": filing_info,
                    "keywords_searched": keywords,
                    "found_sections": []
                }
                
                for section_path, section in found_sections:
                    # Find context around keywords
                    content_lower = section.content.lower()
                    contexts = []
                    
                    for keyword in keywords:
                        if keyword.lower() in content_lower:
                            pos = content_lower.find(keyword.lower())
                            context = section.content[max(0, pos-200):pos+500]
                            contexts.append({
                                "keyword": keyword,
                                "context": context
                            })
                    
                    response_data["found_sections"].append({
                        "section_path": section_path,
                        "section_title": section.title,
                        "content_length": len(section.content),
                        "keyword_contexts": contexts
                    })
                
                return {"success": True, "data": response_data}
            
            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_system_prompt(self) -> str:
        """Create system prompt for SEC filing analysis."""
        return """You are a SEC filing analysis expert with direct access to real SEC EDGAR data through tools.

You can:
1. Look up company CIKs if given tickers or company names
2. Fetch SEC submissions (filing history) for any company
3. Get comprehensive financial facts from SEC filings (XBRL data)
4. Retrieve specific financial concepts (revenue, assets, etc.)
5. **NEW**: Download and analyze complete 10-K filings with structured sections
6. **NEW**: Extract specific narrative sections (Risk Factors, MD&A, Business, etc.)

**Enhanced Capabilities:**
- **Quantitative Analysis**: Financial ratios, trends, comparisons using XBRL data
- **Qualitative Analysis**: Risk factors, business strategy, management discussion
- **Visual Element Identification**: Charts, tables, and graphs within context
- **Structured Section Analysis**: Understand 10-K structure and extract relevant content

**10-K Section Guide:**
- **Item 1 (Business)**: Company operations, products, markets, competition
- **Item 1A (Risk Factors)**: Key risks facing the company
- **Item 7 (MD&A)**: Management's discussion and analysis of financial performance
- **Item 8 (Financial Statements)**: Audited financial statements and notes

When analyzing companies:
- Always fetch real data using the tools before providing analysis
- For comprehensive analysis, use both XBRL data AND narrative sections
- Calculate key financial ratios (ROE, ROA, profit margins, etc.)
- Analyze risk factors and management commentary
- Identify and interpret visual elements (charts, tables) within their proper context
- Provide industry context and comparisons
- Cite specific filing dates and values
- Explain trends and changes over time
- Give investment insights based on both quantitative and qualitative data

If you need a company's CIK, use lookup_company_cik first, then use the other tools.

Be conversational and helpful - users can ask things like:
- "Analyze Apple's latest financials and risk factors"
- "Compare Microsoft and Google's business strategies"
- "What are Tesla's main risks according to their 10-K?"
- "Show me Amazon's revenue trends and management outlook"

Always fetch fresh data for each request to ensure accuracy."""
    
    async def chat(self, message: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """Have a conversation with the SEC filing agent."""
        
        # Store current user question for intelligent filtering
        self.current_user_question = message
        
        # Build conversation history
        messages = conversation_history or []
        messages.append({"role": "user", "content": message})
        
        try:
            # Keep making requests until we get a final text response
            max_iterations = 10  # Increased for complex filing analysis
            iteration = 0
            
            while iteration < max_iterations:
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4000,
                    system=self.create_system_prompt(),
                    messages=messages,
                    tools=self.get_tools()
                )
                
                # Handle tool calls
                if response.stop_reason == "tool_use":
                    # Execute tools and continue conversation
                    tool_results = []
                    
                    for content_block in response.content:
                        if hasattr(content_block, 'type') and content_block.type == "tool_use":
                            # Auto-inject user question for get_company_facts calls
                            tool_input = content_block.input
                            if content_block.name == "get_company_facts" and "user_question" not in tool_input:
                                tool_input["user_question"] = self.current_user_question
                            
                            tool_result = self.execute_tool(content_block.name, tool_input)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": content_block.id,
                                "content": json.dumps(tool_result)
                            })
                    
                    # Add assistant message and tool results to conversation
                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({"role": "user", "content": tool_results})
                    
                    iteration += 1
                    continue
                
                # Return final response
                final_response = ""
                for content_block in response.content:
                    if hasattr(content_block, 'text'):
                        final_response += content_block.text
                    elif hasattr(content_block, 'type') and content_block.type == "text":
                        final_response += content_block.text
                
                return final_response
            
            return "Maximum tool iterations reached. Please try a simpler request."
            
        except Exception as e:
            return f"Error: {e}"
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass 