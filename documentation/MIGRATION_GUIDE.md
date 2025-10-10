# Migration Guide

## Quick Reference: Old vs New Structure

### File Locations

| Old Location | New Location | Status |
|-------------|--------------|--------|
| `download_papers_full_texts.py` | `scripts/download_full_texts.py` | ✅ Refactored |
| N/A | `src/api/ncbi_client.py` | ✅ New module |
| N/A | `src/api/rate_limiter.py` | ✅ New module |
| N/A | `src/parsers/xml_parser.py` | ✅ New module |
| N/A | `src/collectors/pmc_downloader.py` | ✅ New module |
| N/A | `src/collectors/checkpoint_manager.py` | ✅ New module |
| N/A | `config/settings.py` | ✅ New module |
| `paper_data_collector.py` | `src/collectors/paper_collector.py` | 🔄 To migrate |
| `paper_data_analyzer.py` | `src/analyzers/paper_analyzer.py` | 🔄 To migrate |
| `paper_llm_system.py` | `src/llm/system.py` | 🔄 To migrate |
| `aging_theory_prompt.py` | `src/llm/prompts.py` | 🔄 To migrate |

### Running Scripts

**Old way:**
```bash
python download_papers_full_texts.py
```

**New way:**
```bash
python scripts/download_full_texts.py

# Or with custom settings:
python scripts/download_full_texts.py --batch-size 50 --threads 4
```

### Importing Modules

**Old way:**
```python
# Everything was in one file
from download_papers_full_texts import collect_pmc_doc, fetch_pmcids_batch
```

**New way:**
```python
# Import from organized modules
from src.api.ncbi_client import NCBIClient
from src.collectors.pmc_downloader import PMCDownloader
from src.parsers.xml_parser import parse_pmc_xml
from config.settings import NCBIConfig, DownloadConfig
```

### Configuration

**Old way:**
```python
# Hardcoded in file
SAVE_DIR = './paper_full_texts'
MAX_REQUESTS_PER_SEC = 9
BATCH_SIZE = 20
```

**New way:**
```python
# Centralized configuration
from config.settings import FULL_TEXTS_DIR, NCBIConfig, DownloadConfig

save_dir = FULL_TEXTS_DIR
rate_limit = NCBIConfig.MAX_REQUESTS_PER_SEC
batch_size = DownloadConfig.BATCH_SIZE
```

## Key Benefits of New Structure

### 1. **Modularity**
- Each component has a single responsibility
- Easy to test individual parts
- Reusable across different scripts

### 2. **Maintainability**
- Changes to API logic only affect `src/api/`
- Parsing changes isolated to `src/parsers/`
- Configuration in one place

### 3. **Clarity**
- Clear separation between API, parsing, and business logic
- Type hints throughout
- Comprehensive docstrings

### 4. **Extensibility**
- Easy to add new data sources
- Simple to add new parsers
- Straightforward to extend functionality

## Testing the New Structure

### 1. Test the new download script:
```bash
# Small test run
python scripts/download_full_texts.py --max-results 10 --batch-size 5
```

### 2. Verify output:
```bash
ls -la data/paper_full_texts/
```

### 3. Check for errors:
Look for any import errors or configuration issues.

## Backward Compatibility

The old `download_papers_full_texts.py` file is still present and functional. You can:

1. **Continue using the old script** while migrating
2. **Test the new script** with small datasets
3. **Gradually migrate** other scripts to use new modules
4. **Remove old files** once migration is complete

## Common Issues and Solutions

### Issue: Import errors
```
ModuleNotFoundError: No module named 'src'
```

**Solution**: Run scripts from project root or add to PYTHONPATH:
```bash
cd /Users/diana/Documents/projects/paper_patterns
python scripts/download_full_texts.py
```

### Issue: Configuration not found
```
FileNotFoundError: [Errno 2] No such file or directory: 'config/settings.py'
```

**Solution**: Ensure you're in the project root directory.

### Issue: Data directories not created
**Solution**: The new structure auto-creates directories. Check `config/settings.py` for paths.

## Next Steps

1. ✅ Test the new download script
2. ⏳ Migrate `paper_data_collector.py`
3. ⏳ Migrate `paper_data_analyzer.py`
4. ⏳ Migrate `paper_llm_system.py`
5. ⏳ Update all scripts to use new modules
6. ⏳ Add unit tests
7. ⏳ Remove old files after verification
