# Usage Guide

This guide provides detailed examples and best practices for using the IFT-LLM framework.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Single Design Analysis](#single-design-analysis)
3. [Batch Analysis](#batch-analysis)
4. [Programmatic Usage](#programmatic-usage)
5. [Advanced Features](#advanced-features)
6. [Interpreting Results](#interpreting-results)

## Basic Usage

### Command-Line Interface

The simplest way to analyze a design:

```bash
python examples/analyze_design.py <folder> <top_module> [options]
```

**Arguments**:
- `folder`: Path to directory containing Verilog files
- `top_module`: Name of the top-level module

**Options**:
- `--label <true|false>`: Ground truth label for evaluation
- `--output <file>`: Save results to JSON file

### Example

```bash
python examples/analyze_design.py \
    ../automate/sequential \
    counter_module \
    --label true \
    --output results/sequential_analysis.json
```

## Single Design Analysis

### Step 1: Prepare Your Design

Organize your Verilog files in a directory:

```
my_design/
├── top.v
├── submodule1.v
├── submodule2.v
└── utils.v
```

**Note**: Test benches (files starting with `test_`, `tb_`, or `tbTOP`) are automatically excluded.

### Step 2: Identify the Top Module

Find the top-level module in your design hierarchy. For example, if `top.v` contains:

```verilog
module chip_top(
    input clk,
    input [127:0] key,
    output [127:0] result
);
    // ...
endmodule
```

The top module is `chip_top`.

### Step 3: Run Analysis

```bash
python examples/analyze_design.py my_design chip_top --output my_results.json
```

### Step 4: Review Results

The analysis will:
1. Extract module dependencies
2. Analyze each module in topological order
3. Generate a final report

Check the console output for progress and `my_results.json` for detailed results.

## Batch Analysis

Batch mode allows analyzing multiple designs efficiently.

### Step 1: Create Configuration File

Create `my_batch_config.json`:

```json
{
  "llm": {
    "provider": "azure",
    "model": "gpt-4o",
    "temperature": 0
  },
  "designs": [
    {
      "folder": "designs/aes_clean",
      "top_module": "aes_128",
      "label": false
    },
    {
      "folder": "designs/aes_trojan",
      "top_module": "aes_128",
      "label": true
    },
    {
      "folder": "designs/rsa_clean",
      "top_module": "rsa_core",
      "label": false
    }
  ]
}
```

### Step 2: Run Batch Analysis

```bash
python examples/batch_analysis.py \
    --config my_batch_config.json \
    --output batch_results
```

### Step 3: Review Summary

After completion, check:
- `batch_results/summary.json`: Overall statistics
- `batch_results/<design_name>.json`: Individual results
- `batch_results/contexts/`: Intermediate analysis contexts

**Example Summary**:
```json
{
  "total_designs": 3,
  "successful": 3,
  "failed": 0,
  "correct_predictions": 3,
  "accuracy": "100.00%"
}
```

## Programmatic Usage

### Basic Example

```python
import os
from src.core.analyzer import HardwareIFTAnalyzer
from src.utils.extract_graph import get_modules_and_dependencies
from src.utils.extract_module import get_module

# Load Verilog code
with open("design.v", "r") as f:
    verilog_code = f.read()

# Initialize analyzer
analyzer = HardwareIFTAnalyzer(
    llm_provider="azure",
    model="gpt-4o"
)

# Extract module hierarchy
sorted_modules, dependency_dict = get_modules_and_dependencies(
    "design.v",
    "top_module"
)

# Prepare module data
module_data = []
for module in sorted_modules:
    code = get_module(verilog_code, module)
    if code:
        module_data.append({
            "name": module,
            "dependencies": dependency_dict.get(module, []),
            "verilog_code": code
        })

# Run analysis
results = analyzer.analyze_design(
    sorted_modules,
    dependency_dict,
    module_data
)

# Parse and use results
results_json = analyzer.extract_json_result(results)
if results_json["is_vulnerable"]:
    print("Warning: Design is vulnerable!")
    print(f"Leakage path: {results_json['leakage_path']}")
```

### Custom Analysis Pipeline

```python
class CustomAnalyzer:
    def __init__(self):
        self.analyzer = HardwareIFTAnalyzer()
        
    def analyze_with_preprocessing(self, verilog_file, top_module):
        # Step 1: Preprocess (e.g., remove comments)
        preprocessed = self.preprocess(verilog_file)
        
        # Step 2: Extract hierarchy
        modules, deps = get_modules_and_dependencies(
            preprocessed,
            top_module
        )
        
        # Step 3: Filter modules (e.g., only analyze security-critical)
        filtered = self.filter_security_critical(modules)
        
        # Step 4: Analyze
        results = self.analyzer.analyze_design(filtered, deps, ...)
        
        return results
    
    def preprocess(self, verilog_file):
        # Custom preprocessing logic
        pass
    
    def filter_security_critical(self, modules):
        # Custom filtering logic
        pass
```

## Advanced Features

### Context Saving

Save intermediate analysis contexts for debugging:

```python
results = analyzer.analyze_design(
    sorted_modules,
    dependency_dict,
    module_data,
    save_contexts=True,
    context_folder="debug_contexts"
)
```

Check `debug_contexts/<module_name>.txt` to see what the LLM learned about each module.

### Custom Prompts

Modify prompts for specific analysis needs:

```python
from src.prompts.ift_prompts import MODULE_ANALYSIS_PROMPT

# Create custom prompt
custom_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a hardware security expert with focus on cryptographic implementations."),
    ("user", "Analyze this module for timing side channels...\n{verilog_code}")
])

# Use in analysis (requires modifying analyzer code)
```

### Multiple Providers

Compare results across different LLMs:

```python
providers = [
    ("azure", "gpt-4o"),
    ("azure", "gpt-4"),
    ("openrouter", "meta-llama/llama-3.3-70b-instruct")
]

for provider, model in providers:
    analyzer = HardwareIFTAnalyzer(provider, model)
    results = analyzer.analyze_design(...)
    # Compare results
```

## Interpreting Results

### Understanding the Output

A typical result looks like:

```json
{
  "is_vulnerable": true,
  "vulnerable_modules": ["trojan_module", "top"],
  "leakage_path": [
    "Step 1: top.secret_key[127:0] -> passed to trojan_module.key_input",
    "Step 2: trojan_module XORs key_input with trigger_state",
    "Step 3: XOR result assigned to leak_wire",
    "Step 4: leak_wire connected to top.debug_output",
    "Step 5: top.debug_output is externally observable"
  ],
  "leakage_type": "key_extraction_via_debug_port",
  "explanation": "The design contains a hardware Trojan that..."
}
```

### Key Fields

- **is_vulnerable**: Boolean indicating if leakage detected
- **vulnerable_modules**: List of modules involved in leakage
- **leakage_path**: Step-by-step trace from source to sink
- **leakage_type**: Category of leakage (e.g., key_extraction, state_leakage)
- **explanation**: Human-readable description

### Validation Steps

1. **Review Leakage Path**: Verify each step makes sense
2. **Check Source Code**: Manually inspect identified modules
3. **Test Exploitability**: Can the leak actually be exploited?
4. **Consider Context**: Is this intentional (e.g., debug mode)?

### False Positives

The analysis may report false positives when:
- Legitimate debug features are present
- Encrypted/hashed data flows to outputs
- Design uses unconventional patterns

Always manually verify findings.

### False Negatives

The analysis may miss vulnerabilities that:
- Use very sophisticated obfuscation
- Depend on analog/mixed-signal effects
- Require multi-cycle analysis
- Exploit implementation-specific features

## Tips and Best Practices

### For Accurate Analysis

1. **Clean Designs**: Remove unnecessary comments and test code
2. **Clear Naming**: Use descriptive signal names
3. **Modular Structure**: Well-organized hierarchies work best
4. **Complete Code**: Ensure all dependencies are included

### For Performance

1. **Start Small**: Test on small modules first
2. **Batch Similar Designs**: Group related analyses
3. **Cache Results**: Save contexts for reuse
4. **Optimize Prompts**: Shorter prompts = faster analysis

### For Debugging

1. **Enable Context Saving**: Always save contexts initially
2. **Check Dependencies**: Verify module hierarchy is correct
3. **Review Intermediate Steps**: Look at per-module analysis
4. **Compare with Ground Truth**: Use labeled datasets

## Common Workflows

### Workflow 1: Design Verification

```bash
# Analyze your new design
python examples/analyze_design.py my_new_chip top_module

# Review results
cat results.json

# If vulnerable, inspect leakage path
# Fix design
# Re-analyze
```

### Workflow 2: Trojan Benchmark Evaluation

```bash
# Create batch config for all benchmarks
# Run batch analysis
python examples/batch_analysis.py --config benchmarks.json

# Analyze accuracy
python scripts/evaluate_results.py batch_results/summary.json
```

### Workflow 3: Comparative Analysis

```bash
# Analyze clean version
python examples/analyze_design.py design_v1 top --output v1.json

# Analyze modified version
python examples/analyze_design.py design_v2 top --output v2.json

# Compare results
diff v1.json v2.json
```

## Next Steps

- Read [IFT Techniques](IFT_TECHNIQUES.md) for methodology details
- Check [API Reference](API_REFERENCE.md) for full API documentation
- Explore [Benchmarks](../benchmarks/README.md) for test cases
- Review [Troubleshooting](TROUBLESHOOTING.md) for common issues

