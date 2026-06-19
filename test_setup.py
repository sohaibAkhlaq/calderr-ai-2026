print("=" * 50)
print("🔍 CalderR AI - Setup Verification")
print("=" * 50)

print(f"\n📌 Python Version: {__import__('sys').version}")
print(f"📌 Python Location: {__import__('sys').executable}")

print("\n📦 Checking installed packages...")
packages = [
    'langchain',
    'langchain_groq',
    'langchain_community',
    'langgraph',
    'groq',
    'openai',
    'pydantic',
    'dotenv',
    'fastapi',
    'uvicorn',
    'chromadb',
    'sentence_transformers',
    'httpx',
    'rich',
    'typer',
    'pytest',
    'jupyter',
    'streamlit'
]

success = 0
failed = 0

for package in packages:
    try:
        __import__(package.replace('-', '_'))
        print(f"✅ {package} - OK")
        success += 1
    except ImportError:
        print(f"❌ {package} - NOT FOUND")
        failed += 1

print(f"\n📊 Summary: {success} packages installed, {failed} missing")
print("=" * 50)

if failed == 0:
    print("✅ All packages installed successfully!")
else:
    print("⚠️  Some packages are missing. Please check installation.")
print("=" * 50)
