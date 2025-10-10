# Root Directory Cleanup Summary

## 📊 Analysis Complete

All root directory files have been analyzed and categorized.

---

## ✅ Files to KEEP in Root (7 files)

### Configuration & Environment
```
✅ .env                    (179 bytes)  - API keys and credentials
✅ .env.template           (57 bytes)   - Environment template
✅ .gitignore              (54 bytes)   - Git ignore patterns
✅ requirements.txt        (187 bytes)  - Python dependencies
```

### User-Facing Data Files
```
✅ doi_list.py             (886 bytes)  - Positive examples (golden set)
✅ dois_minus_list.py      (1 KB)       - Negative examples
✅ README.md               (if exists)  - Main documentation
```

**Reason**: These are frequently edited, user-facing configuration files that should remain easily accessible in the root.

---

## 🔄 Files to MIGRATE (6 files → 13 new files)

### 1. LLM System (High Priority)
```
📄 aging_theory_prompt.py (8.8 KB)
   └─→ src/llm/prompts.py

📄 paper_llm_system.py (18.6 KB)
   ├─→ src/llm/system.py
   └─→ scripts/run_llm_analysis.py
```

### 2. Data Collection (High Priority)
```
📄 paper_data_collector.py (18.3 KB)
   ├─→ src/collectors/paper_collector.py
   └─→ scripts/collect_papers.py

📄 process_negative_examples.py (18.2 KB)
   └─→ scripts/collect_negative_examples.py
```

### 3. Analysis (High Priority)
```
📄 paper_data_analyzer.py (17 KB)
   ├─→ src/analyzers/paper_analyzer.py
   └─→ scripts/analyze_papers.py
```

### 4. Already Replaced
```
⚠️ download_papers_full_texts.py (12.5 KB)
   └─→ REPLACED by scripts/download_full_texts.py
   └─→ Add deprecation notice, then remove
```

---

## 📦 Test Data
```
🔄 test_data.json (12 KB)
   └─→ tests/fixtures/test_data.json
   └─→ ✅ MOVED
```

---

## 📁 Data Directories (Auto-handled)

These directories are already configured in `config/settings.py`:
```
✅ paper_data/          → data/paper_data/
✅ negative_examples/   → data/negative_examples/
✅ final_query_results/ → data/final_query_results/
✅ llm_analysis_resutlts/ → data/llm_analysis_results/ (typo fixed)
```

---

## 📈 Migration Impact

### Before Cleanup
```
Root Directory: 13 Python files + 4 config files + 4 data dirs = 21 items
```

### After Cleanup
```
Root Directory: 2 Python files (DOI lists) + 4 config files = 6 items
Organized Structure: 
  - src/: 13 modular files
  - scripts/: 6 executable scripts
  - tests/: fixtures + tests
  - data/: all data organized
```

**Reduction**: 21 → 6 items in root (71% cleaner!)

---

## 🎯 Next Steps

### ✅ Completed
- [x] Analyzed all root files
- [x] Created new modular structure
- [x] Moved test data to tests/fixtures/
- [x] Created comprehensive documentation

### 🔄 Recommended Next Actions

#### Immediate (5 minutes)
```bash
# 1. Add deprecation notice to old download script
# (Manual edit needed - see below)

# 2. Verify test data moved
ls -la tests/fixtures/test_data.json
```

#### Short-term (1-2 hours each)
1. **Migrate LLM System**
   - Move `aging_theory_prompt.py` → `src/llm/prompts.py`
   - Refactor `paper_llm_system.py` → `src/llm/system.py`
   - Create `scripts/run_llm_analysis.py`

2. **Migrate Collectors**
   - Refactor `paper_data_collector.py` → `src/collectors/paper_collector.py`
   - Create `scripts/collect_papers.py`
   - Refactor `process_negative_examples.py` → `scripts/collect_negative_examples.py`

3. **Migrate Analyzers**
   - Refactor `paper_data_analyzer.py` → `src/analyzers/paper_analyzer.py`
   - Create `scripts/analyze_papers.py`

#### Long-term (After migration)
- Add unit tests for all modules
- Remove deprecated files
- Update all documentation
- Add CI/CD pipeline

---

## 📝 Deprecation Notice Template

Add this to the top of `download_papers_full_texts.py`:

```python
#!/usr/bin/env python3
"""
⚠️ DEPRECATED - This script has been replaced by a modular version.

Please use instead:
    python scripts/download_full_texts.py

The new version offers:
- Modular, testable code
- Command-line arguments
- Better error handling
- Improved documentation

This file will be removed in a future version.
"""
import warnings
warnings.warn(
    "download_papers_full_texts.py is deprecated. "
    "Use scripts/download_full_texts.py instead.",
    DeprecationWarning,
    stacklevel=2
)

# Original code follows...
```

---

## 🎨 Visual Before/After

### BEFORE (Cluttered Root)
```
paper_patterns/
├── .env
├── .gitignore
├── requirements.txt
├── doi_list.py
├── dois_minus_list.py
├── aging_theory_prompt.py          ❌ Should be in src/llm/
├── download_papers_full_texts.py   ❌ Replaced
├── paper_data_analyzer.py          ❌ Should be in src/analyzers/
├── paper_data_collector.py         ❌ Should be in src/collectors/
├── paper_llm_system.py             ❌ Should be in src/llm/
├── process_negative_examples.py    ❌ Should be in scripts/
├── test_data.json                  ❌ Should be in tests/
├── paper_data/                     ❌ Should be in data/
├── negative_examples/              ❌ Should be in data/
├── final_query_results/            ❌ Should be in data/
└── llm_analysis_resutlts/          ❌ Should be in data/
```

### AFTER (Clean Root)
```
paper_patterns/
├── .env                    ✅ Config
├── .env.template           ✅ Config
├── .gitignore              ✅ Config
├── requirements.txt        ✅ Config
├── doi_list.py             ✅ User data
├── dois_minus_list.py      ✅ User data
├── README.md               ✅ Docs
│
├── config/                 ✅ All settings
├── src/                    ✅ All modules
├── scripts/                ✅ All executables
├── tests/                  ✅ All tests
├── data/                   ✅ All data
└── documentation/          ✅ All docs
```

---

## 💡 Key Decisions Made

### Why Keep DOI Lists in Root?
1. **Frequently edited** by researchers
2. **Easy to find** - no need to navigate directories
3. **User-facing data** - not code
4. **Similar to requirements.txt** - configuration data
5. **Referenced by multiple scripts**

### Why Move Everything Else?
1. **Separation of concerns** - code vs data vs config
2. **Modularity** - reusable components
3. **Testability** - easier to test isolated modules
4. **Maintainability** - clear organization
5. **Scalability** - easy to extend

---

## 📚 Documentation Created

All analysis and migration guides are now available:

1. **ROOT_FILES_ANALYSIS.md** (this file) - Detailed analysis
2. **PROJECT_STRUCTURE.md** - Architecture documentation
3. **MIGRATION_GUIDE.md** - Step-by-step migration
4. **QUICK_START.md** - Quick reference
5. **REFACTORING_SUMMARY.md** - What changed and why
6. **README_NEW_STRUCTURE.md** - Visual overview

---

## ✅ Summary

**Analysis Complete!** 

- ✅ 7 files should stay in root
- 🔄 6 files need migration → 13 new organized files
- ✅ Test data moved to proper location
- ✅ Comprehensive documentation created
- 🎯 Clear migration path defined

**Root directory will be 71% cleaner after migration!**

Next: Choose which module to migrate first (recommend starting with LLM system).
