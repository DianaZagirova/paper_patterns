# Root Directory Files Analysis

## Overview
This document analyzes all files currently in the root directory, determines if they're needed, and recommends their proper location in the new structure.

---

## 📋 File-by-File Analysis

### ✅ **Keep in Root (Essential)**

#### 1. `.env` & `.env.template`
- **Purpose**: Environment variables (API keys, credentials)
- **Status**: ✅ Keep in root
- **Reason**: Standard convention for environment configuration
- **Action**: None needed

#### 2. `.gitignore`
- **Purpose**: Git ignore patterns
- **Status**: ✅ Keep in root
- **Reason**: Required by Git in root directory
- **Action**: None needed

#### 3. `requirements.txt`
- **Purpose**: Python dependencies
- **Status**: ✅ Keep in root
- **Reason**: Standard Python convention
- **Action**: None needed

#### 4. `README.md`
- **Purpose**: Main project documentation
- **Status**: ✅ Keep in root (if exists)
- **Reason**: Standard convention for project entry point
- **Action**: Update to reflect new structure

---

### 📊 **Data Files - Keep in Root**

#### 5. `doi_list.py`
- **Purpose**: List of positive example DOIs (golden set - aging theory papers)
- **Current Size**: 20 DOIs
- **Status**: ✅ Keep in root
- **Reason**: 
  - User-facing data file that's frequently edited
  - Easy to find and modify
  - Referenced by multiple scripts
- **Alternative**: Could move to `data/doi_lists/` but root is more convenient
- **Action**: Keep in root for easy access

#### 6. `dois_minus_list.py`
- **Purpose**: List of negative example DOIs (papers that mimic but aren't aging theory)
- **Current Size**: 22 DOIs
- **Status**: ✅ Keep in root
- **Reason**: Same as doi_list.py - frequently edited, user-facing
- **Action**: Keep in root for easy access

#### 7. `test_data.json`
- **Purpose**: Test/sample data for development
- **Current Size**: 12KB
- **Status**: 🔄 Move to `tests/fixtures/`
- **Reason**: Test data should be with tests
- **Action**: 
  ```bash
  mkdir -p tests/fixtures
  mv test_data.json tests/fixtures/
  ```

---

### 🔧 **Scripts to Migrate**

#### 8. `download_papers_full_texts.py` (12.5KB, 321 lines)
- **Purpose**: Original monolithic download script
- **Status**: ⚠️ Can be deprecated after testing
- **New Location**: Replaced by `scripts/download_full_texts.py`
- **Action**: 
  - Keep temporarily for backward compatibility
  - Add deprecation notice at top
  - Remove after verifying new script works
  ```python
  # DEPRECATED: Use scripts/download_full_texts.py instead
  ```

#### 9. `paper_data_collector.py` (18.3KB, 557 lines)
- **Purpose**: Collects paper data from DOIs
- **Status**: 🔄 Migrate to `src/collectors/paper_collector.py`
- **Contains**:
  - DOI-based paper collection
  - PubMed metadata extraction
  - Full text retrieval
  - Incremental processing
- **Action**: Refactor into modular components
  ```
  src/collectors/paper_collector.py    # Main collector class
  scripts/collect_papers.py            # Executable script
  ```

#### 10. `paper_data_analyzer.py` (17KB, 459 lines)
- **Purpose**: Analyzes collected paper data
- **Status**: 🔄 Migrate to `src/analyzers/paper_analyzer.py`
- **Contains**:
  - Statistical analysis
  - Clustering
  - Visualization
  - TF-IDF analysis
- **Action**: Refactor and move
  ```
  src/analyzers/paper_analyzer.py      # Analysis class
  scripts/analyze_papers.py            # Executable script
  ```

#### 11. `paper_llm_system.py` (18.6KB, 456 lines)
- **Purpose**: LLM-based paper analysis system
- **Status**: 🔄 Migrate to `src/llm/system.py`
- **Contains**:
  - OpenAI GPT integration
  - Paper data loading
  - Query processing
  - Results management
- **Action**: Refactor and move
  ```
  src/llm/system.py                    # LLM system class
  scripts/run_llm_analysis.py          # Executable script
  ```

#### 12. `process_negative_examples.py` (18.2KB, 549 lines)
- **Purpose**: Collects negative example papers
- **Status**: 🔄 Migrate to `scripts/collect_negative_examples.py`
- **Contains**: Similar to paper_data_collector.py but for negative examples
- **Action**: 
  - Can reuse `src/collectors/paper_collector.py` with different config
  - Create simple wrapper script
  ```
  scripts/collect_negative_examples.py  # Uses paper_collector with negative config
  ```

#### 13. `aging_theory_prompt.py` (8.8KB, 159 lines)
- **Purpose**: LLM prompt templates for aging theory analysis
- **Status**: 🔄 Migrate to `src/llm/prompts.py`
- **Contains**:
  - System prompts
  - Query templates
  - Prompt variations
- **Action**: Move to LLM module
  ```
  src/llm/prompts.py                   # All prompt templates
  ```

---

### 📁 **Directories to Reorganize**

#### 14. `paper_data/` directory
- **Purpose**: Stores collected paper data
- **Status**: 🔄 Move to `data/paper_data/`
- **Action**: Already handled by new config
  ```bash
  # Already configured in config/settings.py
  PAPER_DATA_DIR = DATA_DIR / 'paper_data'
  ```

#### 15. `negative_examples/` directory
- **Purpose**: Stores negative example papers
- **Status**: 🔄 Move to `data/negative_examples/`
- **Action**: Already handled by new config

#### 16. `final_query_results/` directory
- **Purpose**: Stores final query results
- **Status**: 🔄 Move to `data/final_query_results/`
- **Action**: Already handled by new config

#### 17. `llm_analysis_resutlts/` directory (note: typo in name)
- **Purpose**: Stores LLM analysis results
- **Status**: 🔄 Move to `data/llm_analysis_results/` (fix typo)
- **Action**: Already handled by new config

---

## 📊 Summary Table

| File | Size | Keep/Move/Delete | New Location | Priority |
|------|------|------------------|--------------|----------|
| `.env` | 179B | ✅ Keep | Root | - |
| `.env.template` | 57B | ✅ Keep | Root | - |
| `.gitignore` | 54B | ✅ Keep | Root | - |
| `requirements.txt` | 187B | ✅ Keep | Root | - |
| `doi_list.py` | 886B | ✅ Keep | Root | - |
| `dois_minus_list.py` | 1KB | ✅ Keep | Root | - |
| `test_data.json` | 12KB | 🔄 Move | `tests/fixtures/` | Low |
| `download_papers_full_texts.py` | 12.5KB | ⚠️ Deprecate | (replaced) | Medium |
| `paper_data_collector.py` | 18.3KB | 🔄 Migrate | `src/collectors/` | High |
| `paper_data_analyzer.py` | 17KB | 🔄 Migrate | `src/analyzers/` | High |
| `paper_llm_system.py` | 18.6KB | 🔄 Migrate | `src/llm/` | High |
| `process_negative_examples.py` | 18.2KB | 🔄 Migrate | `scripts/` | Medium |
| `aging_theory_prompt.py` | 8.8KB | 🔄 Migrate | `src/llm/` | High |

---

## 🎯 Recommended Actions

### Immediate (Do Now)
1. ✅ Keep essential files in root (`.env`, `.gitignore`, `requirements.txt`, DOI lists)
2. 🔄 Move `test_data.json` to `tests/fixtures/`
3. ⚠️ Add deprecation notice to `download_papers_full_texts.py`

### Short-term (Next Steps)
4. 🔄 Migrate `aging_theory_prompt.py` → `src/llm/prompts.py`
5. 🔄 Migrate `paper_llm_system.py` → `src/llm/system.py` + `scripts/run_llm_analysis.py`
6. 🔄 Migrate `paper_data_collector.py` → `src/collectors/paper_collector.py` + `scripts/collect_papers.py`
7. 🔄 Migrate `paper_data_analyzer.py` → `src/analyzers/paper_analyzer.py` + `scripts/analyze_papers.py`
8. 🔄 Refactor `process_negative_examples.py` → `scripts/collect_negative_examples.py`

### Long-term (After Migration)
9. 🗑️ Remove old script files after verification
10. 📝 Update all documentation
11. ✅ Add unit tests for all modules

---

## 🏗️ Proposed Final Structure

```
paper_patterns/
├── .env                              ✅ Keep
├── .env.template                     ✅ Keep
├── .gitignore                        ✅ Keep
├── requirements.txt                  ✅ Keep
├── doi_list.py                       ✅ Keep (user-facing data)
├── dois_minus_list.py                ✅ Keep (user-facing data)
├── README.md                         ✅ Keep/Update
│
├── config/
│   └── settings.py                   ✅ Done
│
├── src/
│   ├── api/
│   │   ├── ncbi_client.py           ✅ Done
│   │   └── rate_limiter.py          ✅ Done
│   ├── parsers/
│   │   └── xml_parser.py            ✅ Done
│   ├── collectors/
│   │   ├── pmc_downloader.py        ✅ Done
│   │   ├── checkpoint_manager.py    ✅ Done
│   │   └── paper_collector.py       🔄 To migrate
│   ├── analyzers/
│   │   └── paper_analyzer.py        🔄 To migrate
│   └── llm/
│       ├── system.py                🔄 To migrate
│       └── prompts.py               🔄 To migrate
│
├── scripts/
│   ├── download_full_texts.py       ✅ Done
│   ├── collect_papers.py            🔄 To create
│   ├── collect_negative_examples.py 🔄 To create
│   ├── analyze_papers.py            🔄 To create
│   └── run_llm_analysis.py          🔄 To create
│
├── tests/
│   ├── fixtures/
│   │   └── test_data.json           🔄 Move here
│   └── (unit tests)                 🔄 To create
│
├── data/                             ✅ Auto-created
│   ├── paper_data/
│   ├── negative_examples/
│   ├── paper_full_texts/
│   ├── final_query_results/
│   └── llm_analysis_results/
│
└── documentation/                    ✅ Done
    ├── PROJECT_STRUCTURE.md
    ├── MIGRATION_GUIDE.md
    ├── QUICK_START.md
    └── REFACTORING_SUMMARY.md
```

---

## 🔍 Special Considerations

### DOI Lists (`doi_list.py` & `dois_minus_list.py`)
**Why keep in root?**
- Frequently edited by users
- Easy to find and modify
- Not code, but data configuration
- Referenced by multiple scripts
- Similar to `requirements.txt` - configuration data

**Alternative approach** (if you prefer):
```
data/
├── doi_lists/
│   ├── positive_examples.py  # doi_list.py
│   └── negative_examples.py  # dois_minus_list.py
```
But root is more convenient for frequent editing.

### Test Data
`test_data.json` should move to `tests/fixtures/` because:
- It's test data, not production data
- Should be with test suite
- Standard testing convention

### Old Scripts
Keep temporarily with deprecation notices:
```python
#!/usr/bin/env python3
"""
DEPRECATED: This script has been replaced by the modular version.

Please use: python scripts/download_full_texts.py

This file will be removed in a future version.
"""
import warnings
warnings.warn(
    "download_papers_full_texts.py is deprecated. "
    "Use scripts/download_full_texts.py instead.",
    DeprecationWarning
)
```

---

## 📝 Migration Checklist

### Phase 1: Immediate Cleanup
- [ ] Move `test_data.json` to `tests/fixtures/`
- [ ] Add deprecation notice to `download_papers_full_texts.py`
- [ ] Update main `README.md` with new structure

### Phase 2: LLM Module Migration
- [ ] Migrate `aging_theory_prompt.py` → `src/llm/prompts.py`
- [ ] Migrate `paper_llm_system.py` → `src/llm/system.py`
- [ ] Create `scripts/run_llm_analysis.py`
- [ ] Test LLM functionality

### Phase 3: Collectors Migration
- [ ] Migrate `paper_data_collector.py` → `src/collectors/paper_collector.py`
- [ ] Create `scripts/collect_papers.py`
- [ ] Refactor `process_negative_examples.py` → `scripts/collect_negative_examples.py`
- [ ] Test collection functionality

### Phase 4: Analyzers Migration
- [ ] Migrate `paper_data_analyzer.py` → `src/analyzers/paper_analyzer.py`
- [ ] Create `scripts/analyze_papers.py`
- [ ] Test analysis functionality

### Phase 5: Cleanup
- [ ] Verify all new scripts work
- [ ] Remove old deprecated files
- [ ] Update all documentation
- [ ] Add unit tests

---

## 🎯 Conclusion

**Keep in Root:**
- Configuration files (`.env`, `.gitignore`, `requirements.txt`)
- User-facing data files (`doi_list.py`, `dois_minus_list.py`)
- Main documentation (`README.md`)

**Migrate to New Structure:**
- All Python scripts → `src/` modules + `scripts/` executables
- Test data → `tests/fixtures/`
- Data directories → `data/` (already configured)

**Priority Order:**
1. High: LLM and collector modules (most used)
2. Medium: Analyzer and negative examples
3. Low: Test data and cleanup

This organization will result in a clean, professional, and maintainable codebase.
