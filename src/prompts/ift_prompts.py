"""
Information Flow Tracking (IFT) Prompt Templates

This module contains all the prompt templates used for hardware security analysis
using Information Flow Tracking techniques with LLMs.

Author: IFT-LLM Project
"""

from langchain_core.prompts import ChatPromptTemplate


# IFT Techniques Documentation
IFT_TECHNIQUES = {
    "gate-level IFT": (
        "In gate-level IFT, each logic gate in the hardware design is augmented or paired with additional tracking "
        "logic that propagates 'taint' or 'tags' representing sensitive data. This allows fine-grained visibility "
        "into exactly how each gate transforms or propagates the data."
    ),
    "net-level IFT": (
        "Net-level IFT focuses on tagging and tracking data at the signal or net boundaries instead of at every gate. "
        "Because nets often group multiple gates or logic elements together, this approach reduces the instrumentation "
        "overhead."
    ),
}

TECHNIQUES_EXPLANATION = "\n".join([
    f"- **{tech}**: {desc}" for tech, desc in IFT_TECHNIQUES.items()
])

IFT_TECHNIQUES_LIST = list(IFT_TECHNIQUES.keys())


# Initial graph context prompt
INITIAL_GRAPH_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert in hardware security. You will use advanced hardware Information Flow Tracking (IFT) methods.\n\n"
        "IFT is a technique used to track data propagation within a hardware design to ensure that sensitive information "
        "does not flow to unauthorized or unintended parts of the system. Here are some common IFT methods and their details:\n\n"
        f"{TECHNIQUES_EXPLANATION}\n\n"
        "Your goal is to detect any definite information leakage in the provided design."
    ),
    (
        "user",
        "I will provide the full structure of a Verilog design, including the topological order of modules and the "
        "module dependency graph. Analyze and store this context for subsequent prompts. You will use these hardware "
        "IFT methods to trace how sensitive data flows through the design.\n\n"
        "Focus on detecting **definite information leakage** caused by unauthorized access or unintended data flows.\n"
        "Be strict in your analysis and only return a positive result if you confirm actual leakage with certainty.\n\n"
        "Topologically Sorted Modules:\n{sorted_modules}\n\n"
        "Adjacency List of Module Dependencies:\n{adjacency_list}\n\n"
        "Store this context but do not provide any output yet. I will provide further prompts."
    )
])


# Module analysis prompt with ancestor context tracking
MODULE_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        f"You are analyzing modules using advanced hardware IFT methods (e.g., {', '.join(IFT_TECHNIQUES_LIST)}) based on previously stored context."
    ),
    (
        "user",
        "Analyze the following Verilog module to find **definite information leakage**.\n\n"
        "Use ONLY the specified IFT techniques to track how sensitive or critical signals identified so far flow into or out of this module.\n"
        "Report **only confirmed leakage**, where data flows to unintended or unauthorized points.\n\n"
        "**Ancestor Path** (modules above in the hierarchy):\n{ancestor_path}\n\n"
        "**Ancestor Context** (findings from each ancestor):\n{ancestor_context}\n\n"
        "----\n"
        "**Module Name**: {module_name}\n"
        "**Dependencies**: {dependencies}\n"
        "**Verilog Code**:\n{verilog_code}\n\n"
        "Instructions:\n"
        "1. Integrate relevant details from the ancestor modules to see if sensitive data enters this module.\n"
        "2. Check if any signals here propagate that data to an unauthorized output.\n"
        "3. Provide a strict analysis focusing on whether there is confirmed leakage, referencing signals and logic within this module.\n\n"
        "Provide the context and analysis for this module that can be used for the next module's analysis."
    )
])


# Final design summary prompt with detailed leakage path
FINAL_DESIGN_SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert in hardware security using advanced IFT methods. "
        "You have completed analyzing all modules in this design. "
        f"You are generating a final report on information leakage based on hardware IFT methods (e.g., {', '.join(IFT_TECHNIQUES_LIST)})."
    ),
    (
        "user",
        "Provide a comprehensive, **final** analysis of the entire hardware design using all previous context. "
        "Focus on whether there is **definite information leakage** across modules.\n\n"
        "Here is the overall context collected from all modules:\n\n{accumulated_context}\n\n"
        "Here is the topologically sorted list of modules:\n{sorted_modules}\n\n"
        "Here is the adjacency list of dependencies:\n{adjacency_list}\n\n"
        "Instructions:\n"
        "1. Use the complete context and your prior analyses to determine if any end-to-end leakage path exists.\n"
        "2. If leakage is found, produce a **detailed** path from the sensitive source in the top module all the way "
        "   to the unauthorized sink/output.\n"
        "3. The `leakage_path` must be an ordered sequence of steps with arrow marks (`-->`). Each step should mention:\n"
        "   - Module name\n"
        "   - Signal name\n"
        "   - Operation performed (e.g., XOR, SHIFT, register assignment)\n"
        "   - Resulting signal or net\n"
        "   - Next module (if applicable)\n"
        "4. In the **final step**, explicitly show how the submodule's output is mapped to the top module's output signal, "
        "   i.e., how the internal leakage becomes externally visible.\n\n"
        "Output must be in **strict JSON format** (no extra keys or text) as follows:\n"
        "{{\n"
        '  "is_vulnerable": true/false,\n'
        '  "vulnerable_modules": ["module1", "module2", ...],\n'
        '  "leakage_path": [\n'
        '    "Step 1: <Detailed explanation of module.signal, operation, next signal> --> <module.signal>",\n'
        '    "Step 2: ...",\n'
        '    "..."\n'
        '  ],\n'
        '  "leakage_type": "type_of_leakage",\n'
        '  "explanation": "A detailed explanation of how the leak actually occurs."\n'
        "}}"
    )
])


# Simple asset identification prompt
ASSET_IDENTIFICATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are an expert in hardware security and Verilog code analysis."),
    ("user", 
     "Analyze the given Verilog code to identify the critical security assets within the design. "
     "Focus on signals, inputs, outputs, and intermediate variables that play a sensitive role in the operation of the module. "
     "For example, these could include encryption keys, input states, or output signals that are essential to the functionality or security of the design. "
     "Provide a detailed explanation of why these assets are critical and describe their purpose in the overall system. "
     "Additionally, indicate where these assets appear in the Verilog code, including the specific modules or components they are tied to.\n\n"
     "Analyze the following Verilog code to identify:\n"
     "1. Assets: Critical variables, signals, or modules that handle sensitive information.\n\n"
     "Provide the results strictly in the following JSON format without any additional text:\n"
     "{{{{\n"
     '  "assets": ["asset1", "asset2", ...]\n'
     "}}}}\n\n"
     "Verilog Code:\n{verilog_code}")
])


# Vulnerability analysis prompt
VULNERABILITY_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are an expert in hardware security and Verilog code analysis."),
    ("user", 
     "Analyze the following Verilog code to determine if it is vulnerable to information leakage. "
     "Consider the provided assets in your analysis. "
     "If a Yosys DOT file and/or a Trojan description are provided, include them as well. "
     "Identify any leakage modules and trace the leakage paths.\n\n"
     "Provide the results strictly in the following JSON format without any additional text:\n"
     "{{{{\n"
     '  "is_vulnerable": true/false,\n'
     '  "leakage_module": "module_name",\n'
     '  "leakage_path": ["signal1", "signal2", ...],\n'
     '  "explanation": "Explanation why it can be considered vulnerability or why its not a vulnerability"\n'
     "}}}}\n\n"
     "Assets:\n{assets}\n\n"
     "Verilog Code:\n{verilog_code}\n\n"
     "Yosys DOT File (optional):\n{yosys_dot}\n\n"
     "Trojan Description (optional):\n{trojan_description}")
])

