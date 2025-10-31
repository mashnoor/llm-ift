"""
Module Dependency Graph Extractor

This module uses Yosys to extract module hierarchy and dependencies from Verilog designs.
It performs topological sorting to determine the order in which modules should be analyzed.

Author: IFT-LLM Project
"""

import subprocess
import re
import networkx as nx


def run_yosys(verilog_file: str, top_module: str) -> str:
    """
    Run Yosys to extract hierarchy information from a Verilog file.
    
    Args:
        verilog_file: Path to the Verilog file
        top_module: Name of the top module
        
    Returns:
        Yosys output as string
        
    Raises:
        subprocess.CalledProcessError: If Yosys execution fails
    """
    try:
        yosys_command = f'yosys -p "read_verilog {verilog_file}; hierarchy -top {top_module} -auto-top"'
        result = subprocess.run(
            yosys_command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running Yosys: {e.stderr}")
        return None


def number_of_spaces(line: str) -> int:
    """
    Count leading spaces in a line.
    
    Args:
        line: Input string
        
    Returns:
        Number of leading spaces
    """
    count = 0
    for char in line:
        if char == " ":
            count += 1
        else:
            break
    return count


def parse_hierarchy(output: str) -> tuple:
    """
    Parse Yosys hierarchy output to extract dependency edges.
    
    Args:
        output: Yosys command output
        
    Returns:
        Tuple of (dependency_edges, all_modules)
        - dependency_edges: List of (parent, child) tuples
        - all_modules: List of all module names found
    """
    lines = output.splitlines()
    hierarchy_stack = []
    dependency_edges = []
    all_modules = []
    
    hierarchy_started = False
    last_spaces = 0
    current_spaces = 0
    
    for line in lines:
        if "Top module:" in line:
            current_line = line.replace("Top module:", "").replace("\\", "")
            current_module = current_line.strip()
            all_modules.append(current_module)
            current_spaces = number_of_spaces(current_line)
            last_spaces = current_spaces
            
            hierarchy_started = True
            hierarchy_stack.append(current_line)
  
        elif hierarchy_started and "Used module" in line:
            current_line = line.replace("Used module:", "").replace("\\", "")
            current_module = current_line.strip()
            all_modules.append(current_module)
            current_spaces = number_of_spaces(current_line)

            if current_spaces > last_spaces:
                dependency_edges.append((hierarchy_stack[-1].strip(), current_module))
                hierarchy_stack.append(current_line)
            elif current_spaces == last_spaces:
                hierarchy_stack.pop()
                if len(hierarchy_stack) > 0:
                    dependency_edges.append((hierarchy_stack[-1].strip(), current_module))
                hierarchy_stack.append(current_module)
            else:
                while number_of_spaces(hierarchy_stack[-1]) >= current_spaces:
                    hierarchy_stack.pop()
                dependency_edges.append((hierarchy_stack[-1].strip(), current_module))
                hierarchy_stack.append(current_module)
        
        last_spaces = current_spaces
        
        # Check if hierarchy section ended
        if hierarchy_started and len(line.strip()) == 0:
            hierarchy_stack.pop()
            hierarchy_started = False
            break
            
    # Return unique edges
    return list(set(dependency_edges)), all_modules


def topological_sort(edges: list) -> list:
    """
    Perform topological sort on the module dependency graph.
    
    Args:
        edges: List of (parent, child) dependency tuples
        
    Returns:
        List of modules in topological order, or None if cycle detected
    """
    graph = nx.DiGraph(edges)
    
    # Check for cycles
    if not nx.is_directed_acyclic_graph(graph):
        print("The module hierarchy contains a cycle. Topological sort is not possible.")
        return None

    # Perform topological sort
    return list(nx.topological_sort(graph))


def get_modules_and_dependencies(verilog_file: str, top_module: str) -> tuple:
    """
    Extract modules and their dependencies from a Verilog file.
    
    Args:
        verilog_file: Path to the Verilog file
        top_module: Name of the top module
        
    Returns:
        Tuple of (sorted_modules, dependency_dict)
        - sorted_modules: Topologically sorted list of module names
        - dependency_dict: Dictionary mapping module names to their dependencies
    """
    # Step 1: Run Yosys and get the hierarchy output
    yosys_output = run_yosys(verilog_file, top_module)
    if yosys_output is None:
        print("Failed to extract hierarchy from Yosys.")
        return None, None

    # Step 2: Parse the hierarchy output
    dependency_edges, all_modules = parse_hierarchy(yosys_output)

    # Convert dependency_edges to a dictionary
    dependency_dict = {}
    for module in all_modules:
        if module not in dependency_dict:
            dependency_dict[module] = []
    
    for edge in dependency_edges:
        src, dst = edge
        if src not in dependency_dict:
            dependency_dict[src] = []
        dependency_dict[src].append(dst)

    # Step 3: Perform topological sort
    sorted_modules = topological_sort(dependency_edges)
    
    # Add any modules that weren't in the sorted list
    if sorted_modules:
        for module in all_modules:
            if module not in sorted_modules:
                sorted_modules.append(module)
    else:
        sorted_modules = all_modules

    return sorted_modules, dependency_dict

