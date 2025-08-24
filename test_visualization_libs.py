#!/usr/bin/env python3
"""
Test script to check what visualization libraries are available
"""
import sys

print(f"Python version: {sys.version}")
print("\nTesting visualization libraries:")
print("-" * 40)

# Test matplotlib
try:
    import matplotlib
    print("✅ matplotlib: Available")
    import matplotlib.pyplot as plt
    print("✅ matplotlib.pyplot: Available")
except ImportError as e:
    print(f"❌ matplotlib: Not available ({e})")

# Test pandas
try:
    import pandas
    print("✅ pandas: Available")
except ImportError as e:
    print(f"❌ pandas: Not available ({e})")

# Test numpy
try:
    import numpy
    print("✅ numpy: Available")
except ImportError as e:
    print(f"❌ numpy: Not available ({e})")

# Test seaborn
try:
    import seaborn
    print("✅ seaborn: Available")
except ImportError as e:
    print(f"❌ seaborn: Not available ({e})")

print("\nNote: If libraries are missing, you can install them with:")
print("pip install matplotlib pandas numpy seaborn")
