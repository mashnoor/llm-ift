# IFT-LLM: LLM-based Hardware Information Flow Tracking

> **📄 Paper**: [LLM-IFT: LLM-Powered Information Flow Tracking for Secure Hardware](https://ieeexplore.ieee.org/abstract/document/11022949)  
> *IEEE 43rd VLSI Test Symposium (VTS), 2025*  
> **Authors**: Nowfel Mashnoor, Mohammad Akyash, Hadi Kamali, Kimia Azar

A framework for detecting information leakage and hardware Trojans in Verilog designs using Large Language Models (LLMs) and Information Flow Tracking (IFT) techniques.

## Overview

IFT-LLM leverages the power of large language models to analyze hardware designs for potential security vulnerabilities. The framework uses advanced IFT techniques including:

- **Gate-level IFT**: Fine-grained tracking at the logic gate level
- **Net-level IFT**: Efficient tracking at signal/net boundaries

The analyzer processes hardware designs hierarchically, building context across module dependencies to detect unauthorized information flow paths.

## Features

- 🔍 **Automated Hardware Trojan Detection**: Identifies malicious modifications in hardware designs
- 🌳 **Hierarchical Analysis**: Analyzes designs bottom-up following module dependencies
- 🧠 **Context-Aware**: Maintains context across modules for comprehensive analysis
- 📊 **Detailed Reporting**: Provides step-by-step leakage paths and explanations
- 🔧 **Flexible Configuration**: Supports multiple LLM providers (Azure OpenAI, OpenRouter)
- 📦 **Batch Processing**: Analyze multiple designs efficiently

## Architecture

```
ift_llm_final/
├── src/
│   ├── core/           # Core analysis engine
│   ├── prompts/        # LLM prompt templates
│   └── utils/          # Utility functions (graph extraction, module parsing)
├── examples/           # Usage examples
├── benchmarks/         # Hardware Trojan benchmarks
├── configs/            # Configuration templates
├── docs/               # Additional documentation
└── tests/              # Test suites
```

## Installation

### Prerequisites

1. **Python 3.8+**
2. **Yosys** - Open-source Verilog synthesis tool
   ```bash
   # Ubuntu/Debian
   sudo apt install yosys
   
   # macOS
   brew install yosys
   ```

### Setup

1. Clone the repository or navigate to the project directory:
   ```bash
   cd ift_llm_final
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure API credentials:
   
   For **Azure OpenAI**:
   ```bash
   cp configs/azure_config_template.env .env
   # Edit .env and add your credentials
   ```
   
   For **OpenRouter**:
   ```bash
   cp configs/openrouter_config_template.env .env
   # Edit .env and add your credentials
   ```

5. Load environment variables:
   ```bash
   export $(cat .env | xargs)
   ```

## Quick Start

### Analyze a Single Design

```bash
python examples/analyze_design.py \
    benchmarks/AES-T100/TjIn \
    top \
    --label true \
    --output results/aes_t100_analysis.json
```

**Parameters:**
- First argument: Path to folder containing Verilog files
- Second argument: Top module name
- `--label`: Ground truth label (true = vulnerable, false = safe)
- `--output`: Path to save results JSON

### Batch Analysis

1. Create a configuration file (see `configs/batch_config_example.json`):
   ```json
   {
     "llm": {
       "provider": "azure",
       "model": "gpt-4o",
       "temperature": 0
     },
     "designs": [
       {
         "folder": "benchmarks/AES-T100/TjFree",
         "top_module": "aes_128",
         "label": false
       },
       {
         "folder": "benchmarks/AES-T100/TjIn",
         "top_module": "top",
         "label": true
       }
     ]
   }
   ```

2. Run batch analysis:
   ```bash
   python examples/batch_analysis.py \
       --config configs/my_batch_config.json \
       --output batch_results
   ```

## Usage as a Library

```python
from src.core.analyzer import HardwareIFTAnalyzer
from src.utils.extract_graph import get_modules_and_dependencies
from src.utils.extract_module import get_module

# Initialize analyzer
analyzer = HardwareIFTAnalyzer(
    llm_provider="azure",
    model="gpt-4o",
    temperature=0
)

# Load and parse Verilog
with open("design.v", "r") as f:
    verilog_code = f.read()

# Extract module hierarchy
sorted_modules, dependency_dict = get_modules_and_dependencies(
    "design.v", 
    "top_module"
)

# Prepare module data
module_data = []
for module in sorted_modules:
    module_code = get_module(verilog_code, module)
    module_data.append({
        "name": module,
        "dependencies": dependency_dict.get(module, []),
        "verilog_code": module_code
    })

# Run analysis
results = analyzer.analyze_design(
    sorted_modules,
    dependency_dict,
    module_data,
    save_contexts=True,
    context_folder="analysis_contexts"
)

# Parse results
results_json = analyzer.extract_json_result(results)
print(f"Vulnerable: {results_json['is_vulnerable']}")
```

## Configuration

### LLM Providers

#### Azure OpenAI
```python
analyzer = HardwareIFTAnalyzer(
    llm_provider="azure",
    model="gpt-4o",
    temperature=0
)
```

Required environment variables:
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `OPENAI_API_VERSION`

#### OpenRouter
```python
analyzer = HardwareIFTAnalyzer(
    llm_provider="openrouter",
    model="meta-llama/llama-3.3-70b-instruct",
    temperature=0
)
```

Required environment variables:
- `OPENROUTER_API_KEY`
- `OPENROUTER_API_BASE`

## Output Format

The analysis produces a JSON report with the following structure:

```json
{
  "is_vulnerable": true,
  "vulnerable_modules": ["module1", "module2"],
  "leakage_path": [
    "Step 1: top.key[127:0] -> XOR with counter -> trojan_module.xor_out",
    "Step 2: trojan_module.xor_out -> SHIFT by trigger -> leakage_signal",
    "Step 3: leakage_signal -> top.output_port (externally visible)"
  ],
  "leakage_type": "key_extraction",
  "explanation": "The design leaks encryption key bits through..."
}
```

## Benchmarks

The framework includes several hardware Trojan benchmarks from Trust-HUB:

- **AES-T100 to AES-T1500**: Various AES implementations with different Trojans
- **BasicRSA**: RSA implementations with Trojans
- **Custom designs**: Additional test cases

See `benchmarks/README.md` for detailed information.

## Project Structure

```
src/
├── core/
│   └── analyzer.py         # Main analysis engine
├── prompts/
│   └── ift_prompts.py      # LLM prompt templates
└── utils/
    ├── extract_graph.py    # Module dependency extraction
    └── extract_module.py   # Module code extraction

examples/
├── analyze_design.py       # Single design analysis
└── batch_analysis.py       # Batch processing

configs/
├── azure_config_template.env
├── openrouter_config_template.env
└── batch_config_example.json

benchmarks/
└── [Various hardware designs]

docs/
├── IFT_TECHNIQUES.md       # IFT methodology details
├── API_REFERENCE.md        # API documentation
└── TROUBLESHOOTING.md      # Common issues and solutions
```

## How It Works

1. **Module Extraction**: Uses Yosys to extract the module hierarchy and dependencies
2. **Topological Sort**: Analyzes modules in dependency order (bottom-up)
3. **Context Building**: Maintains context from parent modules during analysis
4. **IFT Analysis**: Applies gate-level and net-level IFT techniques via LLM
5. **Path Tracing**: Identifies and reports complete leakage paths
6. **Report Generation**: Produces detailed JSON reports with explanations


## Citation

If you use this framework in your research, please cite:

**Mashnoor, N., Akyash, M., Kamali, H., & Azar, K.** (2025). LLM-IFT: LLM-Powered Information Flow Tracking for Secure Hardware. *2025 IEEE 43rd VLSI Test Symposium (VTS)*, 1-5. https://doi.org/10.1109/VTS65138.2025.11022949

```bibtex
@INPROCEEDINGS{11022949,
  author={Mashnoor, Nowfel and Akyash, Mohammad and Kamali, Hadi and Azar, Kimia},
  booktitle={2025 IEEE 43rd VLSI Test Symposium (VTS)}, 
  title={LLM-IFT: LLM-Powered Information Flow Tracking for Secure Hardware}, 
  year={2025},
  volume={},
  number={},
  pages={1-5},
  keywords={Scalability;Large language models;Integrated circuit interconnections;Focusing;Very large scale integration;Transformers;Hardware;Security;IP networks;Integrated circuit modeling;Information Flow Tracking;LLM;Security},
  doi={10.1109/VTS65138.2025.11022949}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Hardware Trojan benchmarks from Trust-HUB
- Yosys open-source synthesis suite
- LangChain framework for LLM integration

## Contact

For questions, issues, or collaborations, please open an issue on the project repository.

---

**Note**: This tool is for research and educational purposes. Always verify results independently for production systems.

