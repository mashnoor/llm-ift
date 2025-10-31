"""
Hardware IFT Analyzer

Main analysis engine for detecting information leakage in hardware designs
using Information Flow Tracking (IFT) techniques with LLMs.

Author: IFT-LLM Project
"""

import os
import json
from typing import Dict, List, Tuple, Optional

from langchain_openai import AzureChatOpenAI, ChatOpenAI

from ..prompts.ift_prompts import (
    INITIAL_GRAPH_PROMPT,
    MODULE_ANALYSIS_PROMPT,
    FINAL_DESIGN_SUMMARY_PROMPT
)


class HardwareIFTAnalyzer:
    """
    Analyzer for detecting information leakage in hardware designs using IFT.
    
    This analyzer uses LLM-based analysis with context tracking across modules
    to detect information leakage paths in Verilog designs.
    """
    
    def __init__(self, llm_provider: str = "azure", model: str = "gpt-4o", temperature: float = 0):
        """
        Initialize the analyzer with specified LLM configuration.
        
        Args:
            llm_provider: LLM provider ("azure" or "openrouter")
            model: Model name
            temperature: Sampling temperature for LLM
        """
        self.llm_provider = llm_provider
        self.model = model
        self.temperature = temperature
        self.llm = self._initialize_llm()
        self.context_db = {}
        
    def _initialize_llm(self):
        """Initialize the LLM based on provider configuration."""
        if self.llm_provider == "azure":
            return AzureChatOpenAI(
                deployment_name=self.model,
                temperature=self.temperature
            )
        elif self.llm_provider == "openrouter":
            api_key = os.getenv("OPENROUTER_API_KEY")
            api_base = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
            return ChatOpenAI(
                base_url=api_base,
                api_key=api_key,
                model=self.model,
                temperature=self.temperature
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def get_module_ancestors(self, module: str, adjacency_list: Dict[str, List[str]], 
                            path: Optional[List[str]] = None) -> List[str]:
        """
        Get the ancestor path for a given module in the dependency hierarchy.
        
        Args:
            module: Module name
            adjacency_list: Dictionary mapping modules to their children
            path: Current path (used for recursion)
            
        Returns:
            List of ancestor modules in hierarchical order
        """
        if path is None:
            path = []
        
        path = [module] + path
        
        for mod in adjacency_list:
            children = adjacency_list[mod]
            if module in children:
                path = self.get_module_ancestors(mod, adjacency_list, path)
        
        return path
    
    def analyze_design(self, sorted_modules: List[str], adjacency_list: Dict[str, List[str]], 
                      module_data: List[Dict], save_contexts: bool = False,
                      context_folder: str = "contexts") -> str:
        """
        Analyze a complete hardware design for information leakage.
        
        Args:
            sorted_modules: List of modules in topological order
            adjacency_list: Module dependency graph
            module_data: List of dicts containing module info (name, dependencies, verilog_code)
            save_contexts: Whether to save intermediate contexts to files
            context_folder: Folder to save contexts (if save_contexts is True)
            
        Returns:
            JSON string with analysis results
        """
        # Step 1: Send the initial design structure to the LLM
        chain = INITIAL_GRAPH_PROMPT | self.llm
        chain.invoke({
            "sorted_modules": sorted_modules, 
            "adjacency_list": adjacency_list
        })
        
        # Reset context database
        self.context_db = {}
        
        # Step 2: Process each module and accumulate context
        accumulated_context = ""
        
        for i, module_info in enumerate(module_data):
            module_name = module_info["name"]
            dependencies = module_info["dependencies"]
            verilog_code = module_info["verilog_code"]

            print(f"Analyzing module {i+1}/{len(module_data)}: {module_name}")

            # Gather ancestor info
            ancestor_modules = self.get_module_ancestors(module_name, adjacency_list)
            ancestor_modules = [mod for mod in ancestor_modules if mod != module_name]

            # Build ancestor context string
            ancestor_contexts = "".join(
                self.context_db.get(ancestor, "") for ancestor in ancestor_modules
            )
            if not ancestor_contexts:
                ancestor_contexts = "This module has no parent modules.\n"

            # Analyze the module
            response = (MODULE_ANALYSIS_PROMPT | self.llm).invoke({
                "module_name": module_name,
                "dependencies": dependencies,
                "verilog_code": verilog_code,
                "ancestor_path": ancestor_modules,
                "ancestor_context": ancestor_contexts
            })

            # Update accumulated context
            module_context = f"\nModule: {module_name}\nResponse:\n{response.content}\n"
            accumulated_context += module_context
            self.context_db[module_name] = f"Context of module {module_name}:\n{response.content}\n"

            # Save context if requested
            if save_contexts:
                os.makedirs(context_folder, exist_ok=True)
                context_file = os.path.join(context_folder, f"{module_name}.txt")
                with open(context_file, "w") as f:
                    f.write(self.context_db[module_name])

        # Step 3: Generate final summary
        print("Generating final analysis summary...")
        summary_response = (FINAL_DESIGN_SUMMARY_PROMPT | self.llm).invoke({
            "accumulated_context": accumulated_context,
            "sorted_modules": sorted_modules,
            "adjacency_list": adjacency_list
        })

        return summary_response.content
    
    def extract_json_result(self, response: str) -> Dict:
        """
        Extract JSON result from LLM response.
        
        Args:
            response: Raw LLM response string
            
        Returns:
            Parsed JSON dictionary
        """
        # Try to find JSON between braces
        start = response.find('{')
        end = response.rfind('}')
        
        if start != -1 and end != -1:
            json_str = response[start:end+1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                return None
        
        return None

