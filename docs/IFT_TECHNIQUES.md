# Information Flow Tracking (IFT) Techniques

This document describes the Information Flow Tracking (IFT) methodologies used in the IFT-LLM framework for detecting hardware Trojans and information leakage.

## Overview

Information Flow Tracking (IFT) is a security analysis technique that tracks how sensitive data propagates through a system. In hardware security, IFT helps identify unauthorized information flows that could indicate the presence of hardware Trojans or design vulnerabilities.

## IFT Techniques Implemented

### 1. Gate-Level IFT

**Description**: Gate-level IFT operates at the finest granularity, tracking information flow through individual logic gates in the hardware design.

**How it works**:
- Each logic gate is analyzed for how it transforms input signals to output signals
- Taint tags are propagated through gates based on their logic function
- If any input to a gate is tainted (sensitive), the output is also considered tainted
- Provides precise tracking but requires detailed analysis

**Example**:
```verilog
// If 'key' is sensitive data
wire intermediate = key[0] ^ plaintext[0];  // intermediate becomes tainted
wire output = intermediate & enable;         // output is tainted if intermediate is used
```

**Advantages**:
- High precision
- Detailed leakage paths
- Can identify subtle information flows

**Limitations**:
- Computationally intensive
- May produce false positives in complex designs

### 2. Net-Level IFT

**Description**: Net-level IFT tracks information at signal/net boundaries, grouping related logic together for more efficient analysis.

**How it works**:
- Tracks data flow between major signal nets rather than individual gates
- Focuses on module boundaries and significant data paths
- More efficient than gate-level with acceptable precision loss

**Example**:
```verilog
module data_processor(
    input [127:0] secret_key,    // Tainted net
    input [127:0] data,
    output [127:0] result,       // Check if tainted
    output leak                  // Check if tainted
);
    // Analysis focuses on net-level connections
endmodule
```

**Advantages**:
- Better performance/scalability
- Clearer high-level information flows
- Suitable for large designs

**Limitations**:
- May miss fine-grained leakage patterns
- Less precise than gate-level

## IFT Analysis Process

### Phase 1: Asset Identification

Identify sensitive data sources (assets):
- Encryption keys
- Secret states
- Authentication data
- Proprietary algorithms

### Phase 2: Taint Propagation

Track how tainted (sensitive) data flows:
1. Mark all assets as tainted
2. Propagate taint through operations:
   - Arithmetic: `taint(a op b) = taint(a) | taint(b)`
   - Logical: `taint(a & b) = taint(a) | taint(b)`
   - Assignment: `taint(dest) = taint(source)`
3. Track taint across module boundaries

### Phase 3: Sink Detection

Identify unauthorized observable points:
- Debug outputs
- Unused outputs
- Timing-dependent signals
- Power/EM side channels

### Phase 4: Path Construction

If taint reaches an unauthorized sink:
1. Trace back from sink to source
2. Document each transformation
3. Verify the path is exploitable

## LLM-Enhanced IFT

The IFT-LLM framework enhances traditional IFT with LLM capabilities:

### Context-Aware Analysis

- **Hierarchical Context**: Maintains analysis context across module hierarchy
- **Semantic Understanding**: LLM understands design intent and typical patterns
- **Anomaly Detection**: Identifies unusual or suspicious logic patterns

### Ancestor-Based Tracking

```
Top Module (key input)
  ├─> SubModule A (processes key)
  │     ├─> SubModule B (uses key data)
  │     └─> SubModule C (should not access key)
  └─> SubModule D (outputs data)
```

The framework:
1. Analyzes SubModule B with knowledge that parent A has key
2. Detects if SubModule C inappropriately accesses key data
3. Traces if key data flows to SubModule D's outputs

### Multi-Level Analysis

Combines both IFT techniques:
1. **Coarse Analysis**: Net-level IFT for overall flow
2. **Detailed Analysis**: Gate-level IFT for suspicious paths
3. **Verification**: LLM validates findings with design semantics

## Trojan Detection Scenarios

### Scenario 1: Key Leakage

**Trojan Behavior**: Leaks encryption key through unused output

```verilog
// Trojan in AES module
module aes_128(clk, key, plaintext, ciphertext, unused_out);
    // ...
    assign unused_out[0] = key[127];  // LEAK!
endmodule
```

**IFT Detection**:
1. Mark `key` as sensitive (asset)
2. Track taint to `unused_out`
3. Flag as unauthorized information flow

### Scenario 2: Trigger-Based Leakage

**Trojan Behavior**: Activates on rare condition

```verilog
// Conditional leakage
if (rare_trigger) begin
    debug_out <= secret_state;  // LEAK on trigger
end
```

**IFT Detection**:
1. Analyze all paths (including conditional)
2. Detect sensitive data flow to debug_out
3. Report conditional leakage vulnerability

### Scenario 3: Obfuscated Leakage

**Trojan Behavior**: XORs key with counter before leaking

```verilog
wire [7:0] obfuscated = key[7:0] ^ counter;
assign output = obfuscated;  // Disguised leak
```

**IFT Detection**:
1. Taint propagates through XOR operation
2. Tainted data reaches output
3. Report leakage despite obfuscation

## Best Practices

### For Analysis

1. **Start Simple**: Test on known-vulnerable designs first
2. **Verify Assets**: Ensure all sensitive data is identified
3. **Check Boundaries**: Pay special attention to module interfaces
4. **Review Context**: Examine saved contexts for each module
5. **Validate Results**: Cross-reference with design specifications

### For Design Review

1. **Minimize Sensitive Paths**: Limit where sensitive data flows
2. **Explicit Isolation**: Clearly separate trusted and untrusted components
3. **Output Validation**: Justify all outputs, especially unused ones
4. **Conditional Logic**: Review all conditional paths for data leakage

## Limitations and Future Work

### Current Limitations

- Timing-based side channels not fully addressed
- Power/EM analysis requires additional modeling
- Large designs may be computationally expensive
- LLM interpretation can vary

### Future Enhancements

- Integration with formal verification tools
- Side-channel analysis capabilities
- Hardware model checking integration
- Automated repair suggestions

## References

1. Tiwari, M., et al. "Complete information flow tracking from the gates up." ASPLOS 2009.
2. Hu, W., et al. "Detecting hardware Trojans with gate-level information-flow tracking." IEEE Computer 2016.
3. Ardeshiricham, A., et al. "Information flow tracking in analog/mixed-signal designs." DATE 2017.

## See Also

- [Usage Guide](USAGE.md) - How to use the framework
- [API Reference](API_REFERENCE.md) - Programmatic interface
- [Benchmarks](../benchmarks/README.md) - Test cases and examples

