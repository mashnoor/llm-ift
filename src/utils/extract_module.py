"""
Verilog Module Extractor

This module provides utilities to extract individual module definitions 
from Verilog source code files.

Author: IFT-LLM Project
"""

import re


def get_module(verilog_code: str, module_name: str) -> str:
    """
    Extract a specific module definition from Verilog code.
    
    Args:
        verilog_code: Complete Verilog source code as string
        module_name: Name of the module to extract
        
    Returns:
        Module definition as string, or None if not found
        
    Example:
        >>> verilog = "module test(input a); endmodule"
        >>> get_module(verilog, "test")
        'module test(input a); endmodule'
    """
    # Regex pattern to capture the full module definition
    module_pattern = re.compile(
        rf"module\s+{module_name}\b.*?endmodule",  # Match module declaration and contents
        re.DOTALL  # Allow matching across multiple lines
    )

    # Search for the module in the Verilog code
    match = module_pattern.search(verilog_code)

    if match:
        return match.group(0)  # Return the full module definition
    else:
        return None  # Return None if the module is not found


def extract_all_modules(verilog_code: str) -> dict:
    """
    Extract all modules from Verilog code.
    
    Args:
        verilog_code: Complete Verilog source code as string
        
    Returns:
        Dictionary mapping module names to their definitions
    """
    module_pattern = re.compile(
        r"module\s+(\w+)\b.*?endmodule",
        re.DOTALL
    )
    
    modules = {}
    for match in module_pattern.finditer(verilog_code):
        module_name = match.group(1)
        module_code = match.group(0)
        modules[module_name] = module_code
    
    return modules

