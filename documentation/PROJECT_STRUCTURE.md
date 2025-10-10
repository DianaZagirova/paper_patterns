# Project Structure Documentation

## Overview

This document describes the reorganized structure of the paper_patterns project. The codebase has been refactored to improve modularity, maintainability, and clarity.

## Directory Structure

```
paper_patterns/
├── src/                          # Source code modules
│   ├── api/                      # API interaction modules
│   │   ├── ncbi_client.py       # NCBI/Entrez API wrapper with retry logic
│   │   └── rate_limiter.py      # Thread-safe rate limiting
│   ├── parsers/                  # Data parsing modules
│   │   └── xml_parser.py        # XML parsing for PMC articles
│   ├── collectors/               # Data collection modules
│   │   ├── pmc_downloader.py    # PMC full-text downloader
│   │   ├── checkpoint_manager.py # Checkpoint management
│   │   └── paper_collector.py   # Paper data collector (to be migrated)
│   ├── analyzers/                # Analysis modules
│   │   └── paper_analyzer.py    # Paper analysis tools (to be migrated)
│   └── llm/                      # LLM integration
│       ├── system.py             # LLM system (to be migrated)
│       └── prompts.py            # Prompt templates (to be migrated)
├── config/                       # Configuration files
│   └── settings.py              # Centralized settings for all modules
├── scripts/                      # Executable scripts
│   └── download_full_texts.py   # Main download script (NEW)
├── data/                         # Data directories (auto-created)
│   ├── paper_data/
│   ├── negative_examples/
│   ├── paper_full_texts/
│   └── llm_analysis_results/
├── tests/                        # Unit tests (to be added)
├── doi_list.py                  # DOI lists
├── dois_minus_list.py
├── requirements.txt
├── .env.template
├── .gitignore
└── README.md
```

## Module Descriptions

### `src/api/`
**Purpose**: Handle all external API interactions with proper rate limiting and error handling.

- **`ncbi_client.py`**: Wrapper for NCBI Entrez API with:
  - Automatic rate limiting based on API key availability
  - Retry logic with exponential backoff
  - Simplified interface for search and fetch operations

- **`rate_limiter.py`**: Thread-safe rate limiter that:
  - Enforces maximum requests per second
  - Uses semaphores for thread coordination
  - Tracks time between requests

### `src/parsers/`
**Purpose**: Parse and extract structured data from various formats.

- **`xml_parser.py`**: PMC XML parsing with functions for:
  - Extracting article metadata (DOI, PMID, title, journal, etc.)
  - Parsing abstract, body, tables, figures, and references
  - Recursive section extraction with proper formatting

### `src/collectors/`
**Purpose**: Orchestrate data collection from various sources.

- **`pmc_downloader.py`**: PMC full-text downloader that:
  - Downloads articles by PMCID
  - Converts PMIDs to PMCIDs in batches
  - Supports parallel batch processing
  - Tracks failed downloads and multiple PMCIDs

- **`checkpoint_manager.py`**: Checkpoint management for:
  - Saving progress during long-running downloads
  - Loading previous checkpoints
  - Saving final results

### `config/`
**Purpose**: Centralize all configuration settings.

- **`settings.py`**: Contains:
  - Project paths (auto-configured relative to project root)
  - NCBI API configuration (credentials, rate limits, retry settings)
  - Download configuration (batch size, threads, checkpoints)
  - LLM configuration (API keys, model settings)
  - Analysis configuration (clustering, visualization)

## Key Improvements

### 1. **Separation of Concerns**
- API interactions separated from business logic
- Parsing logic isolated in dedicated modules
- Configuration centralized in one location

### 2. **Reusability**
- Modular components can be imported and used independently
- Rate limiter can be used for any API
- XML parser functions can be used standalone

### 3. **Testability**
- Each module has a single responsibility
- Easy to write unit tests for individual functions
- Mock objects can be injected for testing

### 4. **Maintainability**
- Clear module boundaries
- Type hints throughout the codebase
- Comprehensive docstrings
- Configuration changes in one place

### 5. **Scalability**
- Easy to add new data sources
- Simple to extend parsing capabilities
- Straightforward to add new analysis modules

## Usage Examples

### Using the New Download Script

```bash
# Basic usage with default settings
python scripts/download_full_texts.py

# Custom query and settings
python scripts/download_full_texts.py \
    --query '("aging"[Title]) AND (ffrft[Filter])' \
    --max-results 1000 \
    --batch-size 50 \
    --threads 4 \
    --output-dir ./data/my_papers
```

### Using Modules Programmatically

```python
from src.api.ncbi_client import NCBIClient
from src.collectors.pmc_downloader import PMCDownloader

# Initialize
client = NCBIClient()
downloader = PMCDownloader()

# Search PubMed
results = client.search(db="pubmed", term="aging", retmax=100)
pmids = results["IdList"]

# Download articles
documents, failed, multiple = downloader.download_batch_parallel(
    id_list=pmids,
    batch_size=20,
    num_threads=2
)
```

### Using Configuration

```python
from config.settings import NCBIConfig, DownloadConfig, FULL_TEXTS_DIR

# Access configuration
print(f"Rate limit: {NCBIConfig.get_rate_limit()}")
print(f"Batch size: {DownloadConfig.BATCH_SIZE}")
print(f"Output directory: {FULL_TEXTS_DIR}")
```

## Migration Status

### ✅ Completed
- [x] Project structure created
- [x] Configuration module
- [x] API client with rate limiting
- [x] XML parser
- [x] PMC downloader
- [x] Checkpoint manager
- [x] Main download script

### 🔄 In Progress
- [ ] Migrate paper_data_collector.py to src/collectors/
- [ ] Migrate paper_data_analyzer.py to src/analyzers/
- [ ] Migrate paper_llm_system.py to src/llm/
- [ ] Migrate aging_theory_prompt.py to src/llm/prompts.py

### 📋 Planned
- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Add CLI for all scripts
- [ ] Add logging configuration
- [ ] Add documentation generation

## Configuration Management

All configuration is now centralized in `config/settings.py`. To customize:

1. **Environment Variables**: Set in `.env` file
   ```
   NCBI_EMAIL=your.email@example.com
   NCBI_API_KEY=your_api_key
   OPENAI_API_KEY=your_openai_key
   ```

2. **Code Configuration**: Modify `config/settings.py`
   ```python
   class DownloadConfig:
       BATCH_SIZE = 50  # Increase batch size
       NUM_THREADS = 4  # More parallel threads
   ```

3. **Command-line Arguments**: Use script flags
   ```bash
   python scripts/download_full_texts.py --batch-size 50 --threads 4
   ```

## Best Practices

1. **Always use configuration from `config/settings.py`**
   - Don't hardcode paths or settings
   - Use the centralized configuration

2. **Import from src modules**
   ```python
   from src.api.ncbi_client import NCBIClient
   from config.settings import NCBIConfig
   ```

3. **Use type hints**
   ```python
   def process_data(data: Dict[str, Any]) -> List[str]:
       ...
   ```

4. **Add docstrings**
   ```python
   def my_function(param: str) -> int:
       """
       Brief description.
       
       Args:
           param: Parameter description
           
       Returns:
           Return value description
       """
   ```

## Next Steps

1. Run the new download script to verify functionality
2. Migrate remaining modules to new structure
3. Update old scripts to use new modules
4. Add comprehensive tests
5. Update main README.md
