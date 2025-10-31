"""
Example: Analyze a Hardware Design for Information Leakage

This example demonstrates how to use the IFT-LLM framework to analyze
a Verilog hardware design for potential information leakage.

Usage:
    python analyze_design.py <verilog_folder> <top_module> [--label <true/false>]
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.analyzer import HardwareIFTAnalyzer
from src.utils.extract_graph import get_modules_and_dependencies
from src.utils.extract_module import get_module


def load_verilog_files(folder_path: str) -> str:
    """
    Load all Verilog files from a folder.
    
    Args:
        folder_path: Path to folder containing Verilog files
        
    Returns:
        Combined Verilog code as string
    """
    verilog_code = ""
    
    for file in os.listdir(folder_path):
        # Skip test files
        if file.startswith(("test_", "tb_", "tbTOP")):
            continue
            
        if file.endswith((".v", ".vhd")):
            file_path = os.path.join(folder_path, file)
            with open(file_path, "r") as f:
                verilog_code += f.read() + "\n"
    
    return verilog_code


def analyze_hardware_design(folder_path: str, top_module: str, 
                            actual_label: bool = None, output_file: str = None):
    """
    Analyze a hardware design for information leakage.
    
    Args:
        folder_path: Path to folder containing Verilog files
        top_module: Name of the top module
        actual_label: Actual vulnerability label (True if vulnerable, False if safe)
        output_file: Path to save results (optional)
    """
    print(f"Analyzing design in folder: {folder_path}")
    print(f"Top module: {top_module}")
    print("-" * 80)
    
    # Load Verilog files
    verilog_code = load_verilog_files(folder_path)
    
    # Write to temporary file for Yosys analysis
    tmp_file = "tmp_analysis.v"
    with open(tmp_file, "w") as f:
        f.write(verilog_code)
    
    try:
        # Extract module dependencies
        print("Extracting module dependencies...")
        sorted_modules, dependency_dict = get_modules_and_dependencies(tmp_file, top_module)
        
        if not sorted_modules:
            print("Error: Could not extract module hierarchy.")
            return
        
        print(f"Found {len(sorted_modules)} modules:")
        for i, mod in enumerate(sorted_modules, 1):
            deps = dependency_dict.get(mod, [])
            deps_str = f" -> {deps}" if deps else ""
            print(f"  {i}. {mod}{deps_str}")
        print()
        
        # Prepare module data
        module_data = []
        for module in sorted_modules:
            module_code = get_module(verilog_code, module)
            if module_code is None:
                print(f"Warning: Could not extract code for module '{module}'")
                continue
            
            dependencies = dependency_dict.get(module, [])
            module_data.append({
                "name": module,
                "dependencies": dependencies,
                "verilog_code": module_code
            })
        
        # Initialize analyzer
        print("Initializing IFT analyzer...")
        analyzer = HardwareIFTAnalyzer(llm_provider="azure", model="gpt-4o")
        
        # Run analysis
        print("Running IFT analysis (this may take a few minutes)...")
        print()
        results = analyzer.analyze_design(
            sorted_modules, 
            dependency_dict, 
            module_data,
            save_contexts=True,
            context_folder="analysis_contexts"
        )
        
        # Parse results
        results_json = analyzer.extract_json_result(results)
        
        if results_json is None:
            print("Error: Could not parse analysis results")
            print("Raw output:")
            print(results)
            return
        
        # Display results
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS")
        print("=" * 80)
        print(f"Vulnerable: {results_json.get('is_vulnerable', 'Unknown')}")
        
        if actual_label is not None:
            predicted = results_json.get('is_vulnerable', None)
            match = "✓" if predicted == actual_label else "✗"
            print(f"Actual Label: {actual_label}")
            print(f"Prediction Match: {match}")
        
        if results_json.get('vulnerable_modules'):
            print(f"\nVulnerable Modules: {', '.join(results_json['vulnerable_modules'])}")
        
        if results_json.get('leakage_type'):
            print(f"Leakage Type: {results_json['leakage_type']}")
        
        if results_json.get('leakage_path'):
            print("\nLeakage Path:")
            for step in results_json['leakage_path']:
                print(f"  {step}")
        
        if results_json.get('explanation'):
            print(f"\nExplanation:\n{results_json['explanation']}")
        
        print("=" * 80)
        
        # Save results if output file specified
        if output_file:
            output_data = {
                "folder": folder_path,
                "top_module": top_module,
                "actual_label": actual_label,
                "modules": sorted_modules,
                "dependencies": dependency_dict,
                "analysis_results": results_json
            }
            
            os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
            with open(output_file, "w") as f:
                json.dump(output_data, f, indent=2)
            
            print(f"\nResults saved to: {output_file}")
        
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_file):
            os.remove(tmp_file)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a hardware design for information leakage using IFT-LLM"
    )
    parser.add_argument("folder", help="Path to folder containing Verilog files")
    parser.add_argument("top_module", help="Name of the top module")
    parser.add_argument("--label", type=lambda x: x.lower() == 'true', 
                       help="Actual vulnerability label (true/false)")
    parser.add_argument("--output", "-o", help="Path to save results JSON file")
    
    args = parser.parse_args()
    
    analyze_hardware_design(
        args.folder, 
        args.top_module, 
        args.label,
        args.output
    )


if __name__ == "__main__":
    main()

