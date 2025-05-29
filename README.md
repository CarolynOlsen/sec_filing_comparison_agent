# SEC Filing Comparison Agent

An AI agent powered by Claude 4.0 Sonnet that can download, analyze, and compare SEC 10-K filings from EDGAR. The agent provides both quantitative financial analysis and qualitative insights from narrative sections.

**Note**: This agent provides analysis based on publicly available SEC filings, and LLMs make mistakes. Always verify important financial information and consult with financial professionals for investment decisions.

## 🚀 Key Features

### **Intelligent Data Filtering** 
- **LLM-Powered Filtering**: Uses Claude to intelligently filter large SEC datasets based on your specific question
- **Context-Aware Analysis**: Automatically identifies relevant financial concepts, time periods, and metrics
- **Token Limit Prevention**: Eliminates "context length exceeded" errors by extracting only relevant data
- **Fallback Mechanisms**: Multiple filtering strategies ensure robust operation

### **Comprehensive SEC Analysis**
- **Real-time EDGAR Access**: Direct integration with SEC EDGAR API for live data
- **Quantitative Analysis**: Financial ratios, trends, and comparisons using XBRL data
- **Qualitative Analysis**: Risk factors, business strategy, and management discussion
- **Multi-company Comparisons**: Side-by-side analysis of different companies
- **Visual Element Identification**: Charts, tables, and graphs within proper context

### **Advanced Capabilities**
- **Structured 10-K Parsing**: Extracts specific sections (Business, Risk Factors, MD&A, Financials)
- **Chat Interface**: Natural language queries for complex analysis -- Currently does _not_ have memory across questions; that is an area for future improvement
- **Type-Safe Architecture**: Built with Pydantic for robust data validation

## 🧠 How Intelligent Filtering Works

When you ask a question like "What is State Farm's combined ratio?", the system:

1. **Analyzes Your Question**: Claude examines your query to identify relevant financial concepts
2. **Samples Large Datasets**: Takes a representative sample of massive SEC data for analysis
3. **Identifies Relevant Metrics**: Determines which specific financial concepts are needed
4. **Filters Intelligently**: Extracts only the data points that answer your question
5. **Provides Focused Analysis**: Returns detailed insights without token overflow

### Before vs After
- **Before**: `"prompt is too long: 220,211 tokens > 200,000 maximum"` ❌
- **After**: Intelligent analysis with relevant data extraction ✅

## 🛠️ Installation

```bash
# Clone the repository
git clone <repository-url>
cd sec_filing_comparison_agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## 📋 Environment Variables

Create a `.env` file with:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SEC_USER_AGENT=Your Company Name admin@yourcompany.com
```

## 🚀 Quick Start

```bash
python scripts/quick_chat.py
```

## 📊 Example Queries

The agent can handle complex questions that previously caused token limit errors:

- **Growth Analysis**: "Analyze Apple's revenue growth over the past 3 years"
- **Profitability**: "Compare Microsoft's profit margins to industry averages"
- **Insurance Metrics**: "What is State Farm's combined ratio and loss ratio trends?"
- **Risk Assessment**: "What are Tesla's main business risks according to their 10-K?"
- **Strategic Analysis**: "How has Amazon's business strategy evolved based on their filings?"

## 🏗️ Architecture

### Core Components

- **`AnthropicSecAgent`**: Main agent class with intelligent filtering
- **`FilingParser`**: Downloads and parses SEC filing content
- **`TenKStructureParser`**: Extracts structured 10-K sections
- **`EdgarClient`**: SEC EDGAR API integration

### Intelligent Filtering Pipeline

```
User Question → LLM Analysis → Concept Identification → Data Filtering → Focused Response
```

### Key Methods

- **`_filter_data_with_llm()`**: Core intelligent filtering logic
- **`_apply_intelligent_filter()`**: Applies LLM-guided filtering
- **`_apply_fallback_filter()`**: Keyword-based fallback filtering

## 🔧 Configuration

### Tool Configuration
The agent automatically configures tools based on your questions:

- **`get_company_facts`**: Now includes intelligent filtering
- **`get_company_concept`**: For specific financial metrics
- **`download_structured_filing`**: For narrative analysis
- **`get_filing_section`**: For specific 10-K sections

### Filtering Parameters
- **Sample Size**: 10 items for LLM analysis
- **Time Window**: Recent 5 years for financial data
- **Token Limits**: 100KB threshold for filtering activation
- **Fallback Keywords**: Insurance, revenue, profit, and other financial terms

---

## 🧠 Challenges and Learnings

This project tackled common challenges in AI document processing and comparison. Here are the practical methods we tested and what worked:

---

### 🔧 Challenge: Content Boundary Detection

**Problem**: Identifying where document sections start and end

**Methods Tested**:
1. **Simple regex patterns** - Failed with variations
2. **LLM length estimation** - Unreliable, often 10x off actual length
   ```python
   # What we tried: Ask LLM to estimate section length
   prompt = "How many characters is the Risk Factors section?"
   llm_response = "approximately 2000 characters"
   extracted_content = chunk[start_pos:start_pos + 2000]  # Only got partial content
   
   # Problem: Actual Risk Factors was 88,000 chars, LLM estimated 2,000
   # Result: Extracted 2.3% of actual section content
   ```
3. **Sequential boundary detection** - ✅ **Worked best**
   ```python
   # Method: Use LLM to find next section start, extract everything before it
   def _llm_find_section_boundary(chunk, current_section):
       # LLM identifies next section header pattern
       # Extract content until that boundary
   ```
4. **Fallback regex with HTML patterns** - Essential backup
   ```python
   patterns = [
       r'<[^>]*>\s*ITEM\s+\d+[A-Z]*',  # HTML-encoded headers
       r'\n\s*ITEM\s+\d+[A-Z]*\.?\s*[A-Z\s]+\n'  # Plain text headers
   ]
   ```
   **Why needed**: LLM boundary detection failed when:
   - API rate limits or timeouts occurred
   - Document chunks were too large for LLM context
   - Standard patterns were present but LLM gave inconsistent responses

**Key Learning**: Use LLMs for pattern recognition, not content measurement. Implement regex fallbacks.

---

### 🔧 Challenge: HTML Content Cleanup

**Problem**: SEC filings contain extensive HTML markup, XBRL tags, and metadata that interfere with content extraction.

**Methods Tested**:
1. **BeautifulSoup get_text()** - Strips tags but keeps all content including noise
2. **Regex tag removal** - Too aggressive, removes important structure
3. **Intelligent pre-processing** - ✅ **Worked best**
   ```python
   def _preprocess_filing_content(self, text_content):
       # 1. Remove XBRL metadata sections
       # 2. Identify and skip table of contents
       # 3. Find actual narrative content start
       # 4. Remove repetitive boilerplate
   ```

**Specific Techniques That Worked**:
- Skip lines with XBRL context tags (`context id=`, `taxonomy`)
- Detect TOC by page number patterns (`BUSINESS    6`)
- Find narrative start with substantial content indicators
- Use position-based fallback (start at 20% of document)

---

### 🔧 Challenge: Token Limit Management

**Problem**: Large documents exceed LLM context limits, requiring intelligent content selection.

**Methods Tested**:
1. **Chunking by size** - Cuts sections arbitrarily
2. **Processing all chunks** - Hits token limits with large filings
3. **Intelligent chunk filtering** - ✅ **Worked best**
   ```python
   # Process only chunks likely to contain target content
   # Use document structure knowledge (10-K section sequence)
   # Summarize metadata, extract full narrative sections
   ```

**Token Management Strategies**:
- **Pre-filtering**: Remove 20-30% of boilerplate content before LLM processing
- **Targeted chunking**: Process chunks containing specific sections
- **Summary + detail**: Provide section summaries with full content extraction
- **Progressive loading**: Process more chunks only if content not found

---

### 🔧 Challenge: Leveraging Document Format Knowledge

**Problem**: Generic text extraction ignores document-specific structure and patterns.

**Methods Tested**:
1. **Generic text parsing** - Misses document structure
2. **Format-specific parsing** - ✅ **Worked best**

**10-K Specific Techniques**:
```python
# Use known section sequence for boundary detection
section_sequence = [
    "item_1", "item_1a", "item_1b", "item_1c", "item_2", "item_3", "item_4",
    "item_5", "item_6", "item_7", "item_7a", "item_8", "item_9", "item_9a"
]

# Predict next section for boundary detection
current_index = section_sequence.index(current_section_id)
next_sections = section_sequence[current_index + 1:current_index + 4]
```

**Format Knowledge Applications**:
- **Section sequences**: Predict what comes next for boundary detection
- **Standard headers**: Use known patterns (`Part I`, `Item 1A`)
- **Content expectations**: Risk factors should be substantial (>10k chars)
- **Cross-references**: Validate section extraction against document structure

---

## Visual Content Extraction Implementation ✅

The agent successfully implements visual content extraction and summarization from 10-K filings. Here's what was accomplished:

### 🎯 Implementation Results

**Visual Elements Successfully Extracted:**
- ✅ **Risk Factors**: Table of contents, financial report indices
- ✅ **Business**: Insurance coverage descriptions, product categories, investment fund details  
- ✅ **Item 5**: Share repurchase data, financial performance metrics
- ✅ **MD&A**: Financial performance tables with millions/billions in metrics

**Performance Metrics:**
- 📄 **Document Size**: 10.3M characters (The Hartford 2024 10-K)
- 🧹 **Pre-processing**: Removed 262K characters (23.7%) of boilerplate
- 📊 **Visual Elements**: 8 meaningful tables extracted across 4 sections
- 🔍 **Section Detection**: Successfully parsed 6 chunks to find Item 7 (MD&A)

### 🛠️ Technical Implementation

**Section-Specific Visual Extraction:**
```python
# Enhanced table filtering by section relevance
def _is_section_relevant_table(self, table_text: str, section_id: str) -> bool:
    section_keywords = {
        'item_7': ['year ended', 'december', 'million', 'income', 'revenue', 
                   'prior accident', 'development', 'catastrophe', 'loss', 'ratio'],
        'item_1a': ['risk', 'factor', 'exposure', 'impact'],
        'item_1': ['business', 'operation', 'product', 'service', 'coverage']
    }
```

**Smart Table Detection:**
- 🚫 Filters out layout tables (securities listings, form headers)
- ✅ Identifies meaningful financial tables (≥3 rows, ≥2 financial keywords)
- 📍 Section-specific search starting from section headers
- 🎯 Limits to 3 relevant tables per section for performance

**Visual Content Integration:**
```python
# Visual summaries integrated into section content
if section_visuals:
    visual_summaries = "\n\n[VISUAL CONTENT]\n" + "\n".join([
        f"• {visual.description}" for visual in section_visuals
    ])
    section_content += visual_summaries
```

### 🔧 Configuration Options

**Chunk Processing:**
- Default: 6 chunks processed (increased from 3 to find Item 7)
- Configurable via `chunks[:6]` parameter
- Each chunk: up to 50K characters with intelligent splitting

**Visual Element Limits:**
- Maximum 3 tables per section
- Minimum 3 rows per table
- Requires ≥2 financial keywords for relevance

**Section Detection:**
- LLM-driven with Pydantic structured output
- Regex fallback for reliability
- Sequential boundary detection vs unreliable length estimation

### 🚀 Usage Example

```python
# Initialize with visual content extraction
parser = TenKStructureParser(anthropic_client=client)
result = parser.parse_structured_filing(content, filing_url)

# Access section with integrated visual content
section = parser.get_section_by_path(result, "Part2.Item7")
print(f"Visual elements: {len(section.visual_elements)}")
print(f"Content with visuals: {section.content}")
```

---

## 📝 TODO: Performance & Memory Improvements

**Problem**: Chat has no memory - re-downloads same filings and forgets previous context.

Potential action:
- Create persistent filing cache
- Add conversation memory to `AnthropicSecAgent`
- Smarter context injection

**Problem**: Taking 60+ seconds to answer "What is State Farm's combined ratio?" - unacceptable UX.

Potential actions:
- Implement MCP Server Architecture
- Reduce LLM usage with caching and batching
