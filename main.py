"""
CalderR AI Internship 2026 - Main Application
Location: Desktop/calderr-ai-2026
"""

import sys
import os
from datetime import datetime

def main():
    print("=" * 60)
    print("🚀 Welcome to CalderR AI Internship 2026!")
    print("=" * 60)
    print(f"📅 Date: {datetime.now().strftime('%A, %B %d, %Y')}")
    print(f"🐍 Python Version: {sys.version.split()[0]}")
    print(f"📁 Project Location: {os.getcwd()}")
    print(f"🔧 Virtual Environment: {os.environ.get('VIRTUAL_ENV', 'Not Set')}")
    print("\n✨ Environment ready for Day 2!")
    print("=" * 60)

if __name__ == "__main__":
    main()
