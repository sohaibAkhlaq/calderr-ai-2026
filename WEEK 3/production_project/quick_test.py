"""
quick_test.py -- Lightweight Pre-Flight Check (No PyTorch required)
===================================================================
Tests Steps 1-3 of the pipeline (Download, Load, Split) without
importing torch or sentence-transformers.

Usage:
    python quick_test.py
"""

import os
import sys
import ssl
import urllib.request

# Force UTF-8 output on Windows (prevents charmap codec errors with special chars)
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ssl._create_default_https_context = ssl._create_unverified_context

GREEN = "\033[92m"
RED   = "\033[91m"
BLUE  = "\033[94m"
BOLD  = "\033[1m"
RESET = "\033[0m"

PASS_LABEL = f"{GREEN}{BOLD}[PASS]{RESET}"
FAIL_LABEL = f"{RED}{BOLD}[FAIL]{RESET}"
INFO_LABEL = f"{BLUE}{BOLD}[INFO]{RESET}"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")

PDF_SOURCES = [
    {
        "name": "Attention Is All You Need",
        "url":  "https://arxiv.org/pdf/1706.03762.pdf",
        "file": "attention_is_all_you_need.pdf",
    },
    {
        "name": "BERT Pre-training",
        "url":  "https://arxiv.org/pdf/1810.04805.pdf",
        "file": "bert_pretraining.pdf",
    },
]

passed = 0
failed = 0

print(f"\n{BOLD}{'='*60}{RESET}")
print(f"{BOLD}  QUICK PRE-FLIGHT CHECK (Steps 1-3, No PyTorch){RESET}")
print(f"{BOLD}{'='*60}{RESET}\n")

# -- Test 1: docs directory -------------------------------------------
os.makedirs(DOCS_DIR, exist_ok=True)
print(f"  {PASS_LABEL} docs/ directory exists or was created\n")
passed += 1

# -- Test 2: PDF Download ---------------------------------------------
print(f"{BOLD}[ Phase 1: PDF Download ]{RESET}")
for src in PDF_SOURCES:
    dest = os.path.join(DOCS_DIR, src["file"])
    if os.path.exists(dest):
        size_kb = os.path.getsize(dest) // 1024
        print(f"  {PASS_LABEL} Already downloaded: {src['name']} ({size_kb} KB)")
        passed += 1
    else:
        print(f"  {INFO_LABEL} Downloading: {src['name']}...")
        try:
            urllib.request.urlretrieve(src["url"], dest)
            size_kb = os.path.getsize(dest) // 1024
            print(f"  {PASS_LABEL} Downloaded: {src['name']} ({size_kb} KB)")
            passed += 1
        except Exception as e:
            print(f"  {FAIL_LABEL} Download FAILED for {src['name']}: {e}")
            failed += 1

# -- Test 3: PDF Loading ----------------------------------------------
print(f"\n{BOLD}[ Phase 2: PDF Loading ]{RESET}")
try:
    from langchain_community.document_loaders import PyPDFLoader
    total_pages = 0
    all_docs = []
    for src in PDF_SOURCES:
        dest = os.path.join(DOCS_DIR, src["file"])
        if not os.path.exists(dest):
            print(f"  {FAIL_LABEL} Skipping load -- file missing: {src['file']}")
            failed += 1
            continue
        try:
            loader = PyPDFLoader(dest)
            docs = loader.load()
            total_pages += len(docs)
            all_docs.extend(docs)
            print(f"  {PASS_LABEL} Loaded: {src['name']} -> {len(docs)} pages")
            passed += 1
        except Exception as e:
            print(f"  {FAIL_LABEL} Load FAILED for {src['name']}: {e}")
            failed += 1
    print(f"\n  {INFO_LABEL} Total pages loaded: {total_pages}")
except ImportError as e:
    print(f"  {FAIL_LABEL} langchain_community not installed: {e}")
    failed += 1
    all_docs = []

# -- Test 4: Text Splitting -------------------------------------------
print(f"\n{BOLD}[ Phase 3: Text Splitting ]{RESET}")
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
    splits = splitter.split_documents(all_docs)

    if len(splits) >= 50:
        print(f"  {PASS_LABEL} Created {len(splits)} chunks from {len(all_docs)} pages (threshold: >=50)")
        passed += 1
    else:
        print(f"  {FAIL_LABEL} Only {len(splits)} chunks created -- too few")
        failed += 1
except Exception as e:
    print(f"  {FAIL_LABEL} Splitting FAILED: {e}")
    failed += 1

# -- Summary ----------------------------------------------------------
print(f"\n{BOLD}{'='*60}{RESET}")
print(f"  Total : {passed + failed}  |  {GREEN}Passed: {passed}{RESET}  |  {RED}Failed: {failed}{RESET}")
print(f"{BOLD}{'='*60}{RESET}")

if failed == 0:
    print(f"\n  {GREEN}{BOLD}Pre-flight passed! Run the full test in your terminal:{RESET}")
    print(f"  {BOLD}  python test_suite.py{RESET}")
    print(f"\n  Or launch Streamlit directly:")
    print(f"  {BOLD}  streamlit run app.py{RESET}\n")
    sys.exit(0)
else:
    print(f"\n  {RED}{BOLD}{failed} check(s) failed. Fix before launching the app.{RESET}\n")
    sys.exit(1)
