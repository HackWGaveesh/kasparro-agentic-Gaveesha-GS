# Multi-Agent Product Content Generation System

A production-ready modular agentic automation system that transforms raw product data into structured, machine-readable content pages. Built for the Kasparro Applied AI Engineer Challenge.

## What This System Does

Given a simple product dataset (like GlowBoost Vitamin C Serum), this system automatically generates:
- **FAQ Page** - 15+ categorized user questions with detailed answers
- **Product Description Page** - Complete product information with structured sections
- **Comparison Page** - Side-by-side comparison with a fictional competing product

All output is clean, machine-readable JSON - ready for integration into any system.

## Why I Built It This Way

After analyzing the assignment requirements, I focused on three core principles:

1. **True Agentic Architecture** - Not a wrapper script. Each agent has a single responsibility and operates independently.
2. **Reusable Logic Blocks** - Content transformation logic is separated from agents, making it composable and testable.
3. **Framework-Based Orchestration** - Using LangGraph for proper DAG workflow, state management, and agent communication.

The system uses **LangGraph** for orchestration (as required), **LangChain** for agent tooling, and **OpenRouter** for LLM access. No hardcoded fallbacks - everything is generated through agents or logic blocks.

## Quick Start

### Prerequisites

- Python 3.9 or higher
- OpenRouter API key (free tier works fine)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd kasparro-agentic-firstname-lastname

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Get OpenRouter API Key**
   - Sign up at https://openrouter.ai
   - Navigate to https://openrouter.ai/settings/privacy
   - Enable "Free model publication" (required for free models)

2. **Set API Key** (required)
   ```bash
   # Option 1: Create .env file (recommended)
   cp .env.example .env
   # Then edit .env and add your API key:
   # OPENROUTER_API_KEY=your-api-key-here
   
   # Option 2: Environment variable
   export OPENROUTER_API_KEY="your-api-key-here"
   ```
   
   **Note**: The `.env` file is already in `.gitignore` and will not be committed to Git.

### Running the System

```bash
python main_product.py
```

The system will:
1. Parse the product data from `main_product.py`
2. Generate all content blocks and questions
3. Assemble the three pages (FAQ, Product, Comparison)
4. Save JSON files to `outputs/` directory

**Expected Output:**
```
outputs/
├── faq.json              # FAQ page with 5+ Q&As
├── product_page.json     # Complete product description
└── comparison_page.json  # Comparison with fictional Product B
```

## System Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Product Data Input                       │
│         (GlowBoost Vitamin C Serum dataset)                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Data Parser Agent                               │
│         Validates & Structures Product Data                  │
└───────────────┬───────────────────────┬─────────────────────┘
                │                       │
        ┌───────▼───────┐       ┌───────▼───────┐
        │   Content     │       │   Question     │
        │   Blocks      │       │   Generator    │
        │   Agent       │       │   Agent        │
        │               │       │               │
        │ Generates:    │       │ Generates:    │
        │ - Benefits    │       │ - 15+ Q&As    │
        │ - Usage       │       │ - Categorized │
        │ - Ingredients │       │ - With Answers│
        │ - Safety      │       │               │
        └───────┬───────┘       └───────┬───────┘
                │                         │
        ┌───────┴───────┐       ┌─────────┴─────────┐
        │               │       │                    │
┌───────▼───────┐ ┌─────▼──────┐ ┌───────▼──────────┐
│   Product     │ │ Comparison │ │   FAQ            │
│   Page        │ │ Generator  │ │   Generator      │
│   Generator   │ │ Agent      │ │   Agent          │
└───────┬───────┘ └─────┬──────┘ └───────┬──────────┘
        │               │                 │
        └───────────────┼─────────────────┘
                        │
                ┌───────▼───────┐
                │  JSON Output  │
                │     Agent     │
                └───────┬───────┘
                        │
                ┌───────▼───────┐
                │  JSON Files   │
                │  (outputs/)   │
                └───────────────┘
```

### The 7 Agents

Each agent has a **single, well-defined responsibility** and **uses LangChain tools for reasoning**:

1. **DataParserAgent** - Validates and structures raw product data using `validate_data_structure` and `analyze_product_data` tools
2. **ContentBlocksAgent** - Generates reusable content logic blocks using `analyze_content_needs` tool to reason about block requirements
3. **QuestionGeneratorAgent** - Generates 15+ categorized questions using `categorize_question`, `generate_answer_for_question`, and `validate_question_structure` tools
4. **FAQGeneratorAgent** - Assembles FAQ page using `select_best_questions` and `validate_faq_structure` tools for quality assurance
5. **ProductPageGeneratorAgent** - Assembles product description using `analyze_page_structure` tool to optimize page sections
6. **ComparisonGeneratorAgent** - Creates fictional Product B and generates comparison using `validate_product_structure` and `compare_products` tools
7. **JSONOutputAgent** - Formats and saves JSON files using `validate_json_structure` tool to ensure valid output

**Key Feature**: All agents use **LangChain tools** for reasoning and decision-making, not just API wrappers. Tools enable agents to validate, analyze, and make informed decisions.

### Content Logic Blocks

Reusable transformation functions (not agents) that convert data into structured content:

- **Benefits Block** - Transforms product benefits into structured format
- **Usage Block** - Extracts and structures usage instructions
- **Ingredients Block** - Organizes ingredient information
- **Safety Block** - Structures safety and side effect information

These blocks are **pure functions** - no LLM calls, just data transformation logic.

### Template Engine

A custom template system that defines:
- **Fields** - What data is needed
- **Rules** - How to structure the output
- **Dependencies** - Which content blocks to use

Three templates implemented:
- **FAQ Template** - Structures Q&As into FAQ format
- **Product Description Template** - Creates complete product page
- **Comparison Template** - Generates side-by-side comparison

## Design Decisions

### Why LangGraph?

The assignment required a framework-based approach. LangGraph provides:
- **DAG orchestration** - Clear workflow definition
- **State management** - TypedDict for type-safe state
- **Checkpointing** - MemorySaver for state persistence
- **Agent communication** - Proper message passing between agents

### Why Separate Content Blocks from Agents?

Content blocks are **reusable logic** that can be:
- Tested independently
- Used by multiple agents
- Extended without modifying agents

This separation makes the system more maintainable and follows the assignment requirement for "reusable content logic blocks."

### Why No Hardcoded Fallbacks?

The evaluation explicitly flagged hardcoded fallbacks as a failure. Every piece of content is either:
- Generated by an LLM (questions, answers, fictional products)
- Transformed by logic blocks (structured data)
- Assembled by templates (page structure)

No shortcuts, no defaults, no fake content.

### Why JSON Output?

The assignment requires "machine-readable JSON." This makes the output:
- Easy to integrate into other systems
- Validatable and testable
- Clear and structured

## Project Structure

```
.
├── agents/                      # 7 specialized agents
│   ├── data_parser_agent.py
│   ├── content_blocks_agent.py
│   ├── question_generator_agent.py
│   ├── faq_generator_agent.py
│   ├── product_page_generator_agent.py
│   ├── comparison_generator_agent.py
│   └── json_output_agent.py
│
├── content_blocks/             # Reusable content logic
│   ├── benefits_block.py
│   ├── usage_block.py
│   ├── ingredients_block.py
│   └── safety_block.py
│
├── templates/                  # Template engine
│   └── template_engine.py
│
├── workflow/                   # LangGraph orchestration
│   └── product_workflow.py
│
├── state/                     # State schema
│   └── product_state_schema.py
│
├── models/                    # Data models
│   └── product_model.py
│
├── tools/                     # Agent tools (LangChain)
│   └── product_tools.py
│
├── config/                    # Configuration
│   └── llm_config.py
│
├── outputs/                   # Generated JSON files
│   ├── faq.json
│   ├── product_page.json
│   └── comparison_page.json
│
├── docs/                      # Documentation
│   └── projectdocumentation.md
│
├── main_product.py           # Entry point
└── requirements.txt          # Dependencies
```

## How It Works

### Step-by-Step Execution

1. **Input** - Product data loaded from `main_product.py`
2. **Parsing** - DataParserAgent validates and structures the data
3. **Parallel Generation**:
   - ContentBlocksAgent generates all content blocks
   - QuestionGeneratorAgent generates 15+ categorized questions
4. **Page Assembly**:
   - FAQGeneratorAgent creates FAQ page (5+ Q&As)
   - ProductPageGeneratorAgent creates product description
   - ComparisonGeneratorAgent creates Product B and comparison
5. **Output** - JSONOutputAgent saves all pages as JSON files

### State Flow

The workflow uses LangGraph's state management:

```python
ProductState = {
    "raw_product_data": {...},      # Input
    "parsed_product": {...},        # After parsing
    "content_blocks": {...},        # After content blocks
    "questions": [...],             # After question generation
    "faq_page": {...},             # After FAQ generation
    "product_page": {...},         # After product page generation
    "comparison_page": {...},       # After comparison generation
    "files_created": [...],         # After JSON output
    "errors": [...]                 # Any errors collected
}
```

Each agent reads from and writes to this shared state, enabling proper agent communication.

## Key Features

✅ **Framework-Based** - Uses LangGraph for orchestration (not custom scripts)  
✅ **Tool-Based Reasoning** - All 7 agents use LangChain tools for independent reasoning  
✅ **No Hardcoded Content** - All content generated via agents or logic blocks  
✅ **Modular Design** - Clear agent boundaries, reusable blocks  
✅ **Type Safety** - Pydantic models for validation  
✅ **Structured Output** - Clean JSON files  
✅ **API Optimized** - Minimizes API calls by using pure function tools where possible  
✅ **Extensible** - Easy to add new agents, blocks, or templates  

## Testing

Run the system and verify output:

```bash
python main_product.py
```

Check that all three JSON files are generated in `outputs/`:
- `faq.json` - Should have at least 5 Q&As
- `product_page.json` - Should have complete product information
- `comparison_page.json` - Should compare GlowBoost with fictional Product B

## Documentation

Complete system design documentation: [`docs/projectdocumentation.md`](docs/projectdocumentation.md)

Includes:
- Problem statement and solution overview
- Detailed system architecture
- Agent responsibilities
- Content block specifications
- Template engine design
- Workflow orchestration details

## Requirements

- Python 3.9+
- LangGraph >= 0.2.0
- LangChain >= 0.3.0
- OpenAI SDK >= 1.0.0
- Pydantic >= 2.0.0

See `requirements.txt` for complete dependency list.

## Challenges & Solutions

### Challenge: Avoiding Hardcoded Fallbacks

**Problem**: Previous submission failed because of hardcoded fallback responses.

**Solution**: 
- Removed all hardcoded responses
- `generate_answer_for_question` tool now uses LLM for every answer
- Template engine infers categories from question text (no defaults)
- All content generation goes through agents or logic blocks

### Challenge: Agents as API Wrappers

**Problem**: Evaluators flagged that agents were simple wrappers without independent reasoning.

**Solution**:
- Added LangChain tools to ALL 7 agents
- Each agent now uses tools for validation, analysis, and decision-making
- Tools enable agents to reason independently, not just call functions
- Optimized API usage: pure function tools (no API calls) + LLM reasoning only when needed

### Challenge: Framework Integration

**Problem**: LangChain API changes broke agent initialization.

**Solution**:
- Switched to direct LLM calls with tool binding
- Used LangGraph's state management for agent communication
- Simplified agent implementation while maintaining framework usage

### Challenge: OpenRouter Configuration

**Problem**: Free models require privacy settings configuration.

**Solution**:
- Added clear error messages guiding users to privacy settings
- Documented the configuration step in README
- Provided fallback API key for testing

## Future Enhancements

If I were to extend this system:

- **Multi-Product Support** - Process multiple products in batch
- **Template Customization** - Allow users to define custom templates
- **Quality Scoring** - Add agent to score content quality
- **A/B Testing** - Generate multiple variations for testing
- **Caching** - Cache LLM responses for repeated runs
- **Validation** - Add schema validation for JSON output

## License

This project is part of the Kasparro Applied AI Engineer Challenge submission.

---

**Built with clarity, curiosity, and pride** 🚀
