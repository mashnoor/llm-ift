"""
Example: Batch Analysis of Multiple Hardware Designs

This example demonstrates how to run IFT analysis on multiple designs
in batch mode for evaluation purposes.

Usage:
    python batch_analysis.py --config batch_config.json
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.analyzer import HardwareIFTAnalyzer
from src.utils.extract_graph import get_modules_and_dependencies
from src.utils.extract_module import get_module


def load_verilog_files(folder_path: str) -> str:
    """Load all Verilog files from a folder."""
    verilog_code = ""
    
    for file in os.listdir(folder_path):
        if file.startswith(("test_", "tb_", "tbTOP")):
            continue
        if file.endswith((".v", ".vhd")):
            with open(os.path.join(folder_path, file), "r") as f:
                verilog_code += f.read() + "\n"
    
    return verilog_code


def analyze_single_design(analyzer: HardwareIFTAnalyzer, folder: str, 
                         top_module: str, label: bool, results_dir: str) -> Dict:
    """Analyze a single design and return results."""
    print(f"\n{'='*80}")
    print(f"Analyzing: {folder}")
    print(f"Top module: {top_module}, Label: {label}")
    print('='*80)
    
    # Load Verilog code
    verilog_code = load_verilog_files(folder)
    
    # Write to temporary file
    tmp_file = "tmp_batch.v"
    with open(tmp_file, "w") as f:
        f.write(verilog_code)
    
    try:
        # Extract dependencies
        sorted_modules, dependency_dict = get_modules_and_dependencies(tmp_file, top_module)
        
        if not sorted_modules:
            return {
                "folder": folder,
                "error": "Could not extract module hierarchy",
                "success": False
            }
        
        # Prepare module data
        module_data = []
        for module in sorted_modules:
            module_code = get_module(verilog_code, module)
            if module_code:
                module_data.append({
                    "name": module,
                    "dependencies": dependency_dict.get(module, []),
                    "verilog_code": module_code
                })
        
        # Run analysis
        folder_name = folder.replace("/", "_")
        context_dir = os.path.join(results_dir, "contexts", folder_name)
        
        results = analyzer.analyze_design(
            sorted_modules, 
            dependency_dict, 
            module_data,
            save_contexts=True,
            context_folder=context_dir
        )
        
        # Parse results
        results_json = analyzer.extract_json_result(results)
        
        if results_json is None:
            return {
                "folder": folder,
                "error": "Could not parse results",
                "success": False,
                "raw_output": results
            }
        
        # Compile summary
        predicted = results_json.get('is_vulnerable', None)
        correct = predicted == label
        
        result_summary = {
            "folder": folder,
            "top_module": top_module,
            "actual_label": label,
            "predicted_label": predicted,
            "correct": correct,
            "modules": sorted_modules,
            "vulnerable_modules": results_json.get('vulnerable_modules', []),
            "leakage_type": results_json.get('leakage_type', None),
            "success": True
        }
        
        # Save individual result
        output_file = os.path.join(results_dir, f"{folder_name}.json")
        with open(output_file, "w") as f:
            json.dump({
                **result_summary,
                "full_analysis": results_json
            }, f, indent=2)
        
        return result_summary
        
    finally:
        if os.path.exists(tmp_file):
            os.remove(tmp_file)


def run_batch_analysis(config_file: str, results_dir: str = "batch_results"):
    """Run batch analysis based on configuration file."""
    # Load configuration
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    llm_config = config.get("llm", {})
    designs = config.get("designs", [])
    
    print(f"Loaded configuration with {len(designs)} designs")
    print(f"LLM Provider: {llm_config.get('provider', 'azure')}")
    print(f"Model: {llm_config.get('model', 'gpt-4o')}")
    
    # Create results directory
    os.makedirs(results_dir, exist_ok=True)
    
    # Initialize analyzer
    analyzer = HardwareIFTAnalyzer(
        llm_provider=llm_config.get("provider", "azure"),
        model=llm_config.get("model", "gpt-4o"),
        temperature=llm_config.get("temperature", 0)
    )
    
    # Run analysis on each design
    all_results = []
    
    for i, design in enumerate(designs, 1):
        print(f"\n[{i}/{len(designs)}]")
        
        result = analyze_single_design(
            analyzer,
            design["folder"],
            design["top_module"],
            design["label"],
            results_dir
        )
        
        all_results.append(result)
        
        # Print summary
        if result.get("success"):
            status = "✓ CORRECT" if result["correct"] else "✗ INCORRECT"
            print(f"Result: {status} (Actual: {result['actual_label']}, Predicted: {result['predicted_label']})")
        else:
            print(f"Result: ERROR - {result.get('error', 'Unknown error')}")
    
    # Calculate statistics
    successful = [r for r in all_results if r.get("success")]
    correct = [r for r in successful if r.get("correct")]
    
    total = len(all_results)
    success_count = len(successful)
    correct_count = len(correct)
    
    accuracy = (correct_count / success_count * 100) if success_count > 0 else 0
    
    # Save summary
    summary = {
        "total_designs": total,
        "successful": success_count,
        "failed": total - success_count,
        "correct_predictions": correct_count,
        "accuracy": f"{accuracy:.2f}%",
        "results": all_results
    }
    
    summary_file = os.path.join(results_dir, "summary.json")
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    # Print final summary
    print(f"\n{'='*80}")
    print("BATCH ANALYSIS SUMMARY")
    print('='*80)
    print(f"Total Designs: {total}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total - success_count}")
    print(f"Correct Predictions: {correct_count}/{success_count}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"\nResults saved to: {results_dir}/")
    print('='*80)


def main():
    parser = argparse.ArgumentParser(
        description="Run batch IFT analysis on multiple hardware designs"
    )
    parser.add_argument("--config", "-c", required=True,
                       help="Path to batch configuration JSON file")
    parser.add_argument("--output", "-o", default="batch_results",
                       help="Output directory for results (default: batch_results)")
    
    args = parser.parse_args()
    
    run_batch_analysis(args.config, args.output)


if __name__ == "__main__":
    main()

