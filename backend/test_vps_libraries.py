#!/usr/bin/env python3
"""Test script to verify all required libraries are installed on VPS"""

import sys

def test_library(name, import_func):
    """Test if a library can be imported and get its version"""
    try:
        module = import_func()
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {name:25s} {version}")
        return True
    except ImportError as e:
        print(f"❌ {name:25s} NOT INSTALLED - {e}")
        return False
    except Exception as e:
        print(f"⚠️  {name:25s} ERROR - {e}")
        return False

print("=" * 60)
print("  PYTHON ENVIRONMENT VERIFICATION")
print("=" * 60)
print(f"\nPython Version: {sys.version}")
print(f"Python Path: {sys.executable}\n")
print("=" * 60)
print("  CORE LIBRARIES")
print("=" * 60)

results = []

# Core Data Processing
results.append(test_library("pandas", lambda: __import__('pandas')))
results.append(test_library("numpy", lambda: __import__('numpy')))
results.append(test_library("pytz", lambda: __import__('pytz')))

# Technical Analysis
results.append(test_library("pandas_ta", lambda: __import__('pandas_ta')))

# Oanda API
results.append(test_library("oandapyV20", lambda: __import__('oandapyV20')))

# Web Framework
results.append(test_library("fastapi", lambda: __import__('fastapi')))
results.append(test_library("uvicorn", lambda: __import__('uvicorn')))
results.append(test_library("sqlalchemy", lambda: __import__('sqlalchemy')))

# Utilities
results.append(test_library("dotenv", lambda: __import__('dotenv')))

# Visualization
results.append(test_library("matplotlib", lambda: __import__('matplotlib')))
results.append(test_library("seaborn", lambda: __import__('seaborn')))
results.append(test_library("plotly", lambda: __import__('plotly')))

# AI
results.append(test_library("google.generativeai", lambda: __import__('google.generativeai')))

# Additional common libraries
results.append(test_library("requests", lambda: __import__('requests')))
results.append(test_library("json", lambda: __import__('json')))
results.append(test_library("datetime", lambda: __import__('datetime')))

print("=" * 60)
print(f"  RESULTS: {sum(results)}/{len(results)} libraries OK")
print("=" * 60)

if all(results):
    print("\n✅ ALL REQUIRED LIBRARIES ARE INSTALLED!")
    sys.exit(0)
else:
    print(f"\n⚠️  {len(results) - sum(results)} LIBRARIES MISSING OR HAVE ISSUES")
    sys.exit(1)
