"""Shared pytest fixtures for all tests"""
import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope='session')
def test_data_dir():
    """Directory for test fixtures"""
    return os.path.join(os.path.dirname(__file__), 'fixtures')
