# 🧹 Project Cleanup Recommendations

## Files to DELETE (Safe to Remove)

### 🔴 **Temporary/Debug Scripts** (Can Delete)
These were created for debugging/testing and are no longer needed:

1. `diagnose_backend.py` - Diagnostic script for backend issues
2. `test_improved_intent.py` - Test script for intent classification
3. `check_qdrant.py` - Debug script to check Qdrant contents
4. `inspect_knowledge_base.py` - Debug script to inspect knowledge base
5. `show_data.py` - Debug script to show data
6. `draft_generator.py` - Old/unused draft generator
7. `enhanced_answer_email.py` - Was for notebook enhancement (can remove if not using)
8. `fix_answer_email.py` - Temporary fix file
9. `evaluation_semantic_search.py` - Evaluation script
10. `notebook_cells_evaluation.py` - Evaluation script
11. `validator.py` - Validation script
12. `compile_pipeline.py` - Old/unused pipeline compiler
13. `graphrag.py` - Old/unused graph RAG script
14. `pipeline_def.py` - Old/unused pipeline definition
15. `rag.py` - Old/unused RAG script

### 🔴 **Old/Backup Data** (Can Delete)
16. `qdrant_data_old/` - Old backup of Qdrant data (if you have current `qdrant_data/`)
17. `sample_email.txt` - Sample file (unless needed for testing)
18. `sample_emails.csv` - Sample file (unless needed for testing)

### 🔴 **Redundant Documentation** (Can Delete)
19. `PROJECT_COMPLETE.txt` - Completion message (informational only)
20. `requirements_l.txt` - Only contains Google Cloud dependencies (not needed)
21. `SETUP.md` - Different project setup (mentions Neo4j/Docker, not your current setup)

### 🔴 **Redundant Test Files** (Keep one, delete others)
21. `test_backend_api.py` - Redundant if `test_backend.py` covers everything

---

## ⚠️ **Large Directory to Consider Removing**

### 🟡 **llama_index/** (HUGE - ~4000+ files) ✅ **SAFE TO DELETE**
This appears to be a cloned repository that's **NOT used** in your project.

**Size:** Probably 100-500 MB

**Verification:** ✅ Checked - `llama_index` is NOT imported in:
- `backend/` directory
- `chrome-extension/` directory
- Only found in old unused files (`graphrag.py`, etc.)

**Decision:** ✅ **DELETE** - Not used anywhere in active code

---

## 📋 **Files to KEEP** (Important)

### ✅ **Core Backend Files**
- `backend/` - All files (keep)
- `backend/requirements.txt` - Keep

### ✅ **Chrome Extension Files**
- `chrome-extension/` - All files (keep)

### ✅ **Core Documentation**
- `README_START_HERE.md` - Main README
- `SETUP_INSTRUCTIONS.md` - Setup guide
- `QUICK_START.md` - Quick start
- `README_CHROME_EXTENSION.md` - Extension guide
- `TROUBLESHOOTING.md` - Troubleshooting guide
- `PROJECT_SUMMARY.md` - Project summary
- `COMPARISON_ZUBAIR_VS_CHROME_EXTENSION.md` - Comparison doc
- `PERSONAL_DATA_INTEGRATION.md` - Integration guide
- `GMAIL_API_ALTERNATIVES.md` - API alternatives
- `RETRIEVAL_ENHANCEMENT.md` - Enhancement docs

### ✅ **Data Files** (Keep - needed for system)
- `graph_data.gpickle` - Graph data
- `student_email_pairs.labels.jsonl` - Training data
- `student_email_pairs_refined.csv` - Refined data
- `faq.csv` - FAQ data
- `qdrant_data/` - Current Qdrant database

### ✅ **Notebooks** (Keep)
- `graph_rag_updated.ipynb` - Main notebook

### ✅ **Scripts** (Keep)
- `start_backend.sh` - Start script
- `restart_backend.sh` - Restart script
- `test_backend.py` - Main test file

### ✅ **Other**
- `zubair_approach/` - Reference implementation (keep for comparison)
- `.gitignore` - Git ignore file
- `requirements.txt` - Main requirements

---

## 🚀 **Quick Cleanup Commands**

### **Safe to Delete (Debug Scripts)**
```bash
cd /Users/iramkamdar/RAG

# Delete debug/test scripts
rm diagnose_backend.py
rm test_improved_intent.py
rm check_qdrant.py
rm inspect_knowledge_base.py
rm show_data.py
rm draft_generator.py
rm enhanced_answer_email.py
rm fix_answer_email.py
rm evaluation_semantic_search.py
rm notebook_cells_evaluation.py
rm validator.py
rm compile_pipeline.py
rm graphrag.py
rm pipeline_def.py
rm rag.py
rm test_backend_api.py
```

### **Safe to Delete (Sample/Backup Data)**
```bash
# Delete old backup (if you have current qdrant_data/)
rm -rf qdrant_data_old/

# Delete sample files (if not needed)
rm sample_email.txt
rm sample_emails.csv
```

### **Safe to Delete (Redundant Docs)**
```bash
rm PROJECT_COMPLETE.txt
rm requirements_l.txt
rm SETUP.md  # Different project setup
```

### **Delete Large Directory (Verified Safe)**
```bash
# Already verified - llama_index is NOT used in active code
rm -rf llama_index/
```

---

## 📊 **Estimated Space Savings**

- Debug scripts: ~50 KB
- Sample files: ~10 KB
- Old backup: ~10-50 MB (depends on size)
- **llama_index/**: ~100-500 MB (HUGE!)

**Total potential savings: ~100-550 MB**

---

## ✅ **Recommended Action Plan**

1. **Delete debug scripts** (safe, immediate)
2. **Delete sample/backup files** (safe, immediate)
3. **Check llama_index usage** (check first, then delete if unused)
4. **Keep all documentation** (useful for reference)
5. **Keep test_backend.py** (useful for testing)

---

## 🎯 **After Cleanup**

Your project structure should be:
```
RAG/
├── backend/              # Backend code
├── chrome-extension/     # Extension code
├── zubair_approach/      # Reference implementation
├── qdrant_data/         # Vector database
├── graph_data.gpickle    # Graph data
├── *.jsonl              # Training data
├── *.csv                # Data files
├── *.md                 # Documentation
├── *.sh                 # Scripts
├── *.ipynb              # Notebooks
└── .gitignore           # Git config
```

Much cleaner! 🎉

