"""
Description: testing module for load_testing __init__ file
"""
from load_testing import __version__


def test_version():
    """test version of application"""
    assert __version__ == "0.1.0"
