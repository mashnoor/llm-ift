# Hardware Trojan Benchmarks

This directory contains hardware Trojan benchmarks used for evaluating the IFT-LLM framework.

## Benchmark Structure

Each benchmark typically contains two versions:
- **TjFree**: Clean version without Trojans (labeled as `false`)
- **TjIn**: Trojan-infected version (labeled as `true`)

## Available Benchmarks

### AES Implementations

The AES benchmarks are from various trust-HUB challenges with different types of hardware Trojans:

- **AES-T100**: Basic hardware Trojan in AES encryption
- **AES-T200**: Information leakage via side channel
- **AES-T300**: Key leakage through unauthorized outputs
- **AES-T600**: Trigger-based Trojan activation
- **AES-T700**: Sequential trigger with payload
- **AES-T800**: Rare event trigger
- **AES-T900**: Chaining attack
- **AES-T1000**: State-based activation
- **AES-T1200**: Time-based trigger
- **AES-T1300**: Conditional payload execution
- **AES-T1400**: Hybrid trigger mechanism
- **AES-T1500**: Advanced obfuscation

### Other Benchmarks

- **BasicRSA-T100**: RSA implementation with basic Trojan
- **BasicRSA-T400**: RSA with advanced Trojan
- **debug_module**: Debug module with potential vulnerabilities
- **sequential**: Simple sequential circuits for testing

## Benchmark Source

The benchmarks are sourced from:
- **Trust-HUB**: Repository of hardware Trojan benchmarks
- **Custom designs**: Specifically designed test cases

## Usage

To analyze a benchmark:

```bash
python examples/analyze_design.py benchmarks/AES-T100/TjIn top --label true
```

For batch analysis of multiple benchmarks, see the example configuration in `configs/batch_config_example.json`.

## Benchmark Metadata

Each benchmark folder may contain:
- `*.v` or `*.vhd`: Verilog/VHDL source files
- `Readme.txt`: Description of the Trojan (if applicable)
- `*.pdf`: Detailed documentation
- `*.do`: Simulation scripts (for ModelSim/Questasim)

## Notes

- The benchmarks are organized by their Trust-HUB identifiers
- Test benches (files starting with `test_`, `tb_`, `tbTOP`) are automatically excluded from analysis
- Make sure to specify the correct top module for each design

