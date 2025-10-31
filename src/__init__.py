"""
IFT-LLM: LLM-based Hardware Information Flow Tracking

A framework for detecting information leakage in hardware designs using
Large Language Models and Information Flow Tracking techniques.

Paper: "LLM-IFT: LLM-Powered Information Flow Tracking for Secure Hardware"
       IEEE 43rd VLSI Test Symposium (VTS), 2025
       DOI: 10.1109/VTS65138.2025.11022949
"""

__version__ = "1.0.0"
__author__ = "Nowfel Mashnoor, Mohammad Akyash, Hadi Kamali, Kimia Azar"
__paper__ = "LLM-IFT: LLM-Powered Information Flow Tracking for Secure Hardware"
__doi__ = "10.1109/VTS65138.2025.11022949"

from .core.analyzer import HardwareIFTAnalyzer
from .utils.extract_graph import get_modules_and_dependencies
from .utils.extract_module import get_module, extract_all_modules

__all__ = [
    'HardwareIFTAnalyzer',
    'get_modules_and_dependencies',
    'get_module',
    'extract_all_modules'
]

