# Quick Start Guide

## New Project Structure Overview

```
paper_patterns/
│
├── 📁 src/                    # Core source code (NEW)
│   ├── 📁 api/               # API clients & rate limiting
│   ├── 📁 parsers/           # XML & data parsing
│   ├── 📁 collectors/        # Data collection & checkpointing
│   ├── 📁 analyzers/         # Analysis tools
│   └── 📁 llm/               # LLM integration
│
├── 📁 config/                # Configuration (NEW)
│   └── settings.py          # All settings in one place
│
├── 📁 scripts/               # Executable scripts (NEW)
│   └── download_full_texts.py
│
├── 📁 data/                  # All data files
│   ├── paper_data/
│   ├── paper_full_texts/
│   └── llm_analysis_results/
│
└── 📄 Old files (still functional)
    ├── download_papers_full_texts.py
    ├── paper_data_collector.py
    ├── paper_data_analyzer.py
    └── paper_llm_system.py
```

## Using the New Download Script

### Basic Usage
```bash
# Run with default settings
python scripts/download_full_texts.py
```

### Custom Query
```bash
python scripts/download_full_texts.py \
    --query '("aging"[Title]) AND (ffrft[Filter])' \
    --max-results 1000
```

### Adjust Performance
```bash
python scripts/download_full_texts.py \
    --batch-size 50 \
    --threads 4 \
    --checkpoint-interval 20
```

### Custom Output Directory
```bash
python scripts/download_full_texts.py \
    --output-dir ./data/my_custom_papers
```

### View All Options
```bash
python scripts/download_full_texts.py --help
```

## Using Modules in Your Code

### Example 1: Download Specific Articles
```python
from src.collectors.pmc_downloader import PMCDownloader

# Initialize downloader
downloader = PMCDownloader()

# Download single article
doc = downloader.download_article("PMC8765432")
print(doc['metadata']['Title'])
print(doc['page_content'][:500])
```

### Example 2: Search and Download
```python
from src.api.ncbi_client import NCBIClient
from src.collectors.pmc_downloader import PMCDownloader

# Search PubMed
client = NCBIClient()
results = client.search(db="pubmed", term="CRISPR", retmax=50)
pmids = results["IdList"]

# Download articles
downloader = PMCDownloader()
docs, failed, multiple = downloader.download_batch_parallel(
    id_list=pmids,
    batch_size=10,
    num_threads=2
)

print(f"Downloaded: {len(docs)}, Failed: {len(failed)}")
```

### Example 3: Parse XML Directly
```python
from src.parsers.xml_parser import parse_pmc_xml

# If you have XML content
xml_content = """<article>...</article>"""
doc = parse_pmc_xml(xml_content, pmcid="8765432")
```

## Configuration

### Environment Variables (.env file)
```bash
NCBI_EMAIL=your.email@example.com
NCBI_API_KEY=your_api_key_here
OPENAI_API_KEY=your_openai_key_here
```

### Programmatic Configuration
```python
from config.settings import NCBIConfig, DownloadConfig

# Check current settings
print(f"Rate limit: {NCBIConfig.get_rate_limit()}")
print(f"Batch size: {DownloadConfig.BATCH_SIZE}")

# Modify settings (affects all modules)
DownloadConfig.BATCH_SIZE = 50
DownloadConfig.NUM_THREADS = 4
```

## Key Improvements

| Feature | Old Code | New Code |
|---------|----------|----------|
| **Structure** | Single 321-line file | Modular components |
| **Configuration** | Hardcoded values | Centralized in `config/` |
| **Rate Limiting** | Inline semaphore | Reusable `RateLimiter` class |
| **XML Parsing** | Nested functions | Separate testable functions |
| **Error Handling** | Basic try/catch | Comprehensive with retries |
| **Type Hints** | Minimal | Throughout codebase |
| **Reusability** | Copy/paste code | Import modules |
| **Testing** | Difficult | Easy to unit test |

## Testing the New Structure

### Quick Test (10 papers)
```bash
python scripts/download_full_texts.py --max-results 10 --batch-size 5
```

### Check Output
```bash
ls -lh data/paper_full_texts/
cat data/paper_full_texts/documents_final.pkl  # Binary file
```

### Compare with Old Script
```bash
# Old script
python download_papers_full_texts.py

# New script
python scripts/download_full_texts.py
```

Both should produce similar results, but the new script is more maintainable.

## What's Next?

1. **Test the new script** with a small dataset
2. **Migrate other scripts** to use new modules
3. **Add unit tests** for each module
4. **Remove old files** once migration is complete

## Need Help?

- See `PROJECT_STRUCTURE.md` for detailed documentation
- See `MIGRATION_GUIDE.md` for migration instructions
- Check `config/settings.py` for all configuration options
