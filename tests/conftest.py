"""
Pytest configuration and fixtures for ResearchOps tests
"""
import os
import sys

# Add src directory to Python path for imports
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)
