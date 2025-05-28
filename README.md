# SEC Filing Comparison Agent

A sophisticated AI agent powered by Claude 4.0 Sonnet that can download, analyze, and compare SEC 10-K filings from EDGAR. The agent provides both quantitative financial analysis and qualitative insights from narrative sections.

## 🚀 Key Features

### **Intelligent Data Filtering** ⭐ NEW!
- **LLM-Powered Filtering**: Uses Claude to intelligently filter massive SEC datasets based on your specific question
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
- **Interactive Chat Interface**: Natural language queries for complex analysis
- **Type-Safe Architecture**: Built with Pydantic for robust data validation
- **Conversation Memory**: Maintains context across multiple queries

## 🧠 How Intelligent Filtering Works

When you ask a question like "What is Hartford's combined ratio?", the system:

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

### Interactive Chat
```python
from filing_agent.core.anthropic_client import AnthropicSecAgent

async def main():
    agent = AnthropicSecAgent()
    
    # Ask complex questions - intelligent filtering handles large datasets
    response = await agent.chat("What is Hartford's combined ratio and how has it changed over time?")
    print(response)
    
    # Multi-company analysis
    response = await agent.chat("Compare Apple and Microsoft's profit margins")
    print(response)

# Run the chat
import asyncio
asyncio.run(main())
```

### Command Line Chat
```bash
python scripts/chat_with_sec_agent.py
```

## 🧪 Testing

### Test Intelligent Filtering
```bash
python scripts/test_intelligent_filtering.py
```

### Test Enhanced Capabilities
```bash
python scripts/test_enhanced_agent.py
```

## 📊 Example Queries

The agent can handle complex questions that previously caused token limit errors:

- **Insurance Metrics**: "What is Hartford's combined ratio and loss ratio trends?"
- **Growth Analysis**: "Analyze Apple's revenue growth over the past 3 years"
- **Profitability**: "Compare Microsoft's profit margins to industry averages"
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

## 🎯 Use Cases

### Financial Analysis
- Calculate and compare financial ratios
- Analyze revenue and profit trends
- Assess financial health and performance

### Risk Assessment
- Extract and analyze risk factors
- Compare risk profiles across companies
- Identify emerging business risks

### Strategic Research
- Understand business models and strategies
- Analyze competitive positioning
- Track strategic changes over time

### Investment Research
- Comprehensive due diligence
- Peer comparison analysis
- Long-term trend identification

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Anthropic Claude**: For powerful LLM capabilities and function calling
- **SEC EDGAR**: For providing free access to financial data
- **Pydantic**: For robust data validation and type safety (not the AI agent framework)

---

## 🧠 Challenges and Learnings

This project tackled common challenges in AI document processing and comparison. Here are the practical methods we tested and what worked:

---

### 🔧 Challenge: Document Format Detection

**Problem**: File extensions don't indicate internal content structure. Documents often mix multiple formats within a single file.

**Example - XBRL Case**:
*XBRL = eXtensible Business Reporting Language, used for financial data*
```
# Hartford's filing: "hig-20241231.htm" 
# Extension suggests: HTML document
# Actual content: Inline XBRL (financial data tags + narrative HTML)
# Problem: Can't tell from .htm extension what's inside
```

**Common Mixed-Format Examples**:
- **PDFs**: Text + embedded images + form fields + tables
- **HTML**: Markup + embedded scripts + multimedia + structured data
- **Word docs**: Text + embedded charts + tables + comments
- **Jupyter notebooks**: Code + markdown + outputs + metadata

**Methods Tested**:
1. **File extension analysis** - Unreliable for mixed formats
2. **Content sampling** - Check first 1000 chars for format indicators
3. **Investigative content analysis** - ✅ **Worked best**
   - **File size check**: The Hartford's 1.1M chars suggested substantial content beyond pure XBRL
   - **Tag presence**: Found both `<ix:` XBRL tags AND `Item 1`, `Item 1A` section headers  
   - **Content sampling**: First few KB showed forward-looking statements (narrative content)
   - **Section count**: Verified 12+ standard 10-K sections present
   - **Conclusion**: Document contains both XBRL structure AND narrative content (Inline XBRL)

**Key Learning**: Always validate document structure through content analysis, not file extensions.

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

**Key Learning**: Use LLMs for pattern recognition, not content measurement. Always implement regex fallbacks.

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

### 🔧 Challenge: Path Mapping and User Interface

**Problem**: Users request sections with friendly names (`Part1.Item1A`) but internal structure uses technical keys (`part_1.item_1a`).

**Methods Tested**:
1. **String normalization** - Failed with complex variations
2. **Hardcoded mapping tables** - Brittle for new formats
3. **LLM-driven mapping** - ✅ **Worked best**
   ```python
   def get_section_by_path(self, parsed_filing, user_path):
       # Use LLM to map user path to internal structure
       # Fallback to normalized string matching
       # Return FilingSection object
   ```

---

### 📊 Common AI Document Processing Patterns

Based on this project, here are reusable patterns for AI document processing:

#### **1. Multi-Stage Content Validation**
```python
def validate_document_content(content):
    # Stage 1: Format detection
    # Stage 2: Structure validation  
    # Stage 3: Content sampling
    # Stage 4: Expected section verification
```

#### **2. Hierarchical Boundary Detection**
```python
def find_section_boundary(content, section_id):
    # Primary: LLM pattern recognition
    # Fallback: Regex with format-specific patterns
    # Safety: Position-based extraction
```

#### **3. Intelligent Pre-processing Pipeline**
```python
def preprocess_document(raw_content):
    # 1. Remove metadata and boilerplate
    # 2. Clean HTML/markup noise
    # 3. Identify content vs navigation elements
    # 4. Apply format-specific cleanup
```

#### **4. Token-Aware Content Extraction**
```python
def extract_with_token_management(document, target_sections):
    # Calculate content priorities
    # Process high-priority chunks first
    # Summarize metadata, extract full narrative
    # Progressive loading for complete coverage
```

---

### 📈 Performance Results

| Approach | Before | After | Key Improvement |
|----------|--------|-------|-----------------|
| **Content Accuracy** | TOC extraction (736 chars) | Narrative content (42k chars) | Found actual content vs references |
| **Boundary Detection** | Fixed-size chunks | Section-aware boundaries | Preserved section integrity |
| **Processing Efficiency** | 100% of raw content | 77% after cleanup | 23% noise reduction |
| **Token Management** | Context overflow errors | Targeted extraction | Eliminated token limits |

---

### 🔄 Reusable Techniques for Other Document Types

These methods apply to many AI document processing tasks:

- **Legal Contracts**: Section detection, clause boundaries, standard format leverage
- **Academic Papers**: Abstract vs content, citation cleanup, figure handling
- **Technical Documentation**: API section detection, code block boundaries, cross-references
- **Medical Records**: Structured data vs narratives, standard form knowledge
- **Financial Reports**: Beyond SEC to international formats, table extraction

**Core Pattern**: Combine LLM intelligence for pattern recognition with format-specific knowledge and robust fallback mechanisms.

---

**Note**: This agent provides analysis based on publicly available SEC filings. Always verify important financial information and consult with financial professionals for investment decisions.

## Visual Content Extraction Implementation ✅

The agent successfully implements visual content extraction and summarization from 10-K filings. Here's what was accomplished:

### 🎯 Implementation Results

**Visual Elements Successfully Extracted:**
- ✅ **Risk Factors**: Table of contents, financial report indices
- ✅ **Business**: Insurance coverage descriptions, product categories, investment fund details  
- ✅ **Item 5**: Share repurchase data, financial performance metrics
- ✅ **MD&A**: Financial performance tables with millions/billions in metrics

**Performance Metrics:**
- 📄 **Document Size**: 10.3M characters (Hartford 2024 10-K)
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

### 📊 Content Quality Examples

**Risk Factors Section:**
- Table of contents with page numbers (38-114)
- Financial report structure and organization

**Business Section:**
- Workers' Compensation coverage descriptions
- Hartford Funds investment categories (60 mutual funds)
- Product definitions across insurance lines

**MD&A Section (Item 7):**
- Share repurchase data: 3.46M shares at $117.57/share
- $3.15B remaining in authorized repurchase programs
- Prior accident year development tables
- Financial metrics in millions/billions

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

### ✅ Success Metrics

The implementation successfully addresses the original requirement:
> "Visual content (images/tables in 10-Ks) wasn't being summarized as originally intended"

**Achievements:**
- ✅ Visual elements detected and summarized using LLM
- ✅ Section-specific content (no more duplicate securities tables)
- ✅ Meaningful financial data extraction (share repurchases, performance metrics)
- ✅ Integrated visual summaries in section content
- ✅ Scalable across different 10-K filings and sections

**Future Enhancements:**
- Extract visual elements from section text chunks (for non-HTML table data)
- Support for charts and images (currently focuses on tables)
- Enhanced financial keyword detection for specialized industries
- Direct image processing for chart data extraction 

---

## 📝 TODO: Performance & Memory Improvements

### 🧠 Priority 1: Add Conversation Memory

**Problem**: Chat has no memory - re-downloads same filings and forgets previous context.

**Implementation Tasks**:

#### **1.1 Filing Cache System**
```python
# Create persistent filing cache
class FilingCache:
    def __init__(self, cache_dir="./cache/filings"):
        self.cache_dir = cache_dir
        self.memory_cache = {}  # In-memory for current session
    
    def get_filing(self, company_cik: str, form_type: str, year: int):
        # Check memory first, then disk, then download
        cache_key = f"{company_cik}_{form_type}_{year}"
        
        # Memory cache (fastest)
        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key]
        
        # Disk cache (fast)
        cache_file = f"{self.cache_dir}/{cache_key}.json"
        if os.path.exists(cache_file):
            filing = json.load(open(cache_file))
            self.memory_cache[cache_key] = filing  # Store in memory too
            return filing
        
        # Download and cache (slow)
        filing = self._download_filing(company_cik, form_type, year)
        self._save_to_cache(cache_key, filing)
        return filing
```

#### **1.2 Conversation Context Manager**
```python
# Add conversation memory to AnthropicSecAgent
class ConversationMemory:
    def __init__(self):
        self.conversation_history = []
        self.active_companies = {}  # company_name -> cached_data
        self.active_filings = {}    # filing_url -> parsed_sections
    
    def add_exchange(self, question: str, answer: str, companies_mentioned: List[str]):
        self.conversation_history.append({
            "question": question,
            "answer": answer, 
            "companies": companies_mentioned,
            "timestamp": datetime.now()
        })
    
    def get_context_for_question(self, question: str) -> str:
        # Return relevant previous context
        relevant_context = []
        for exchange in self.conversation_history[-5:]:  # Last 5 exchanges
            if any(company in question.lower() for company in exchange["companies"]):
                relevant_context.append(f"Previous Q: {exchange['question']}\nA: {exchange['answer'][:200]}...")
        return "\n\n".join(relevant_context)
```

#### **1.3 Smart Context Injection**
```python
# Modify AnthropicSecAgent.chat() method
async def chat(self, message: str) -> str:
    # 1. Check if we have relevant cached data
    companies_mentioned = self._extract_companies_from_message(message)
    
    # 2. Inject previous context
    context = self.memory.get_context_for_question(message)
    if context:
        enhanced_message = f"Previous context:\n{context}\n\nCurrent question: {message}"
    else:
        enhanced_message = message
    
    # 3. Use cached filings if available
    for company in companies_mentioned:
        if company in self.memory.active_companies:
            # Inject cached company data into tools
            self._inject_cached_data(company)
    
    # 4. Process with memory-aware tools
    response = await self._process_with_memory(enhanced_message)
    
    # 5. Update conversation memory
    self.memory.add_exchange(message, response, companies_mentioned)
    
    return response
```

### ⚡ Priority 2: Performance Optimization

**Problem**: Taking 60+ seconds to answer "What is Hartford's combined ratio?" - unacceptable UX.

**Performance Targets**:
- Simple metrics (combined ratio): < 5 seconds
- Complex analysis: < 15 seconds  
- Multi-company comparison: < 20 seconds

#### **2.1 Implement MCP Server Architecture**
```python
# Create dedicated MCP server for SEC data
# Benefits: Faster tool calling, persistent connections, optimized data structures

class SECMCPServer:
    def __init__(self):
        self.filing_cache = FilingCache()
        self.metrics_cache = {}  # Pre-computed common metrics
        self.xbrl_parser = OptimizedXBRLParser()
    
    @mcp_tool
    async def get_quick_metric(self, company: str, metric: str, year: int) -> dict:
        """Ultra-fast metric retrieval with aggressive caching"""
        cache_key = f"{company}_{metric}_{year}"
        
        if cache_key in self.metrics_cache:
            return self.metrics_cache[cache_key]  # Sub-second response
        
        # Parallel processing for cache miss
        filing_task = asyncio.create_task(self._get_filing(company, year))
        xbrl_task = asyncio.create_task(self._get_xbrl_facts(company, year))
        
        filing, xbrl_data = await asyncio.gather(filing_task, xbrl_task)
        
        metric_value = self._extract_metric(metric, filing, xbrl_data)
        self.metrics_cache[cache_key] = metric_value
        
        return metric_value
```

#### **2.2 Parallel Data Processing**
```python
# Implement concurrent filing processing
async def process_multiple_filings_parallel(companies: List[str], years: List[int]):
    tasks = []
    
    for company in companies:
        for year in years:
            task = asyncio.create_task(download_and_parse_filing(company, year))
            tasks.append(task)
    
    # Process all filings concurrently (10x faster for multi-company analysis)
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return [r for r in results if not isinstance(r, Exception)]

# Use ThreadPoolExecutor for CPU-intensive parsing
import concurrent.futures

def parallel_section_parsing(filing_content: str) -> dict:
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(parse_risk_factors, filing_content): 'risk_factors',
            executor.submit(parse_mda, filing_content): 'mda', 
            executor.submit(parse_business, filing_content): 'business',
            executor.submit(parse_financials, filing_content): 'financials'
        }
        
        results = {}
        for future in concurrent.futures.as_completed(futures):
            section_name = futures[future]
            results[section_name] = future.result()
        
        return results
```

#### **2.3 Smart Metric Pre-computation**
```python
# Pre-compute common insurance metrics for instant responses
class InsuranceMetricsCache:
    def __init__(self):
        self.precomputed_metrics = {}
    
    async def warm_cache_for_company(self, company_cik: str):
        """Pre-compute common metrics in background"""
        filing = await self._get_latest_filing(company_cik)
        
        # Common insurance metrics - compute once, serve many times
        metrics_to_compute = [
            'combined_ratio',
            'loss_ratio', 
            'expense_ratio',
            'premium_growth',
            'roe',
            'book_value_per_share'
        ]
        
        # Parallel computation
        tasks = [self._compute_metric(filing, metric) for metric in metrics_to_compute]
        computed_values = await asyncio.gather(*tasks)
        
        # Cache results
        for metric, value in zip(metrics_to_compute, computed_values):
            cache_key = f"{company_cik}_{metric}_{filing.year}"
            self.precomputed_metrics[cache_key] = value
```

#### **2.4 Optimized LLM Usage**
```python
# Reduce LLM calls with smarter caching and batching
class OptimizedLLMProcessor:
    def __init__(self):
        self.response_cache = {}  # Cache LLM responses
        self.batch_queue = []     # Batch multiple requests
    
    async def get_metric_with_cache(self, question: str, context: str) -> str:
        # Hash question + context for cache key
        cache_key = hashlib.md5(f"{question}_{context}".encode()).hexdigest()
        
        if cache_key in self.response_cache:
            return self.response_cache[cache_key]  # Instant response
        
        # Add to batch queue for processing
        self.batch_queue.append((question, context, cache_key))
        
        # Process batch when queue is full or timeout reached
        if len(self.batch_queue) >= 5:  # Batch size
            await self._process_batch()
        
        return self.response_cache[cache_key]
    
    async def _process_batch(self):
        # Send multiple questions in single LLM call
        batch_prompt = self._create_batch_prompt(self.batch_queue)
        response = await self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": batch_prompt}]
        )
        
        # Parse batch response and cache individual answers
        answers = self._parse_batch_response(response.content[0].text)
        for (question, context, cache_key), answer in zip(self.batch_queue, answers):
            self.response_cache[cache_key] = answer
        
        self.batch_queue.clear()
```

#### **2.5 Implementation Priority Order**

**Week 1: Quick Wins**
1. Add filing cache system (FilingCache class)
2. Implement response caching for identical questions
3. Pre-compute Hartford metrics (combined ratio, loss ratio) for instant demo

**Week 2: Architecture**  
1. Set up MCP server with optimized tool calling
2. Implement parallel filing processing
3. Add conversation memory to AnthropicSecAgent

**Week 3: Performance**
1. Background metric pre-computation for popular companies
2. Batch LLM processing for efficiency
3. Database storage for persistent caching

#### **2.6 Success Metrics**

**Performance Benchmarks**:
- "What is Hartford's combined ratio?" → Target: < 3 seconds (Currently: 60+ seconds)
- "Compare Hartford vs Chubb loss ratios" → Target: < 10 seconds  
- Subsequent questions about same company → Target: < 1 second (cached)

**Memory Benchmarks**:
- Maintain context across 10+ question conversation
- Remember company data across entire session
- Smart context injection (only relevant previous answers)

**Implementation Files to Create**:
- `src/filing_agent/core/filing_cache.py`
- `src/filing_agent/core/conversation_memory.py` 
- `src/filing_agent/mcp/sec_mcp_server.py`
- `src/filing_agent/core/parallel_processor.py`
- `scripts/benchmark_performance.py`

--- 