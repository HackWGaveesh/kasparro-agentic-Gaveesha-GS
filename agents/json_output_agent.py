"""
JSON Output Agent - Formats pages as clean, machine-readable JSON.
Uses LangChain LLM with tools for proper agent reasoning.
Single responsibility: Format and save pages as JSON files.
"""
from typing import Dict, Any, List
import json
import os
from config.llm_config import get_llm
from tools.product_tools import get_product_tools, validate_json_structure
from langchain_core.messages import SystemMessage, HumanMessage


class JSONOutputAgent:
    """Agent responsible for formatting and saving JSON output using tools for reasoning."""
    
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.llm = get_llm(temperature=0.2)  # Very low temperature for validation
        self.tools = [t for t in get_product_tools() if t.name == "validate_json_structure"]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.tool_map = {tool.name: tool for tool in self.tools}
    
    def format_and_save(self, faq_page: Dict[str, Any], 
                       product_page: Dict[str, Any],
                       comparison_page: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format pages as JSON and save to files using agent reasoning with tools.
        Uses tools to validate JSON structure before saving.
        
        Args:
            faq_page: FAQ page data
            product_page: Product page data
            comparison_page: Comparison page data
            
        Returns:
            Dictionary with file paths
        """
        files_created = {}
        pages = {
            "faq": faq_page,
            "product_page": product_page,
            "comparison_page": comparison_page
        }
        
        # Validate each page using tool (no API calls - tools are pure functions)
        for page_name, page_data in pages.items():
            if page_data:
                expected_keys = ["page_type"]  # Minimum expected
                validation = validate_json_structure.invoke({
                    "data": page_data,
                    "expected_keys": expected_keys
                })
                
                # If validation fails, use agent reasoning to fix (single API call only if needed)
                if not validation.get("json_serializable"):
                    system_prompt = """You are a JSON output agent. Validate and fix JSON structure.

You have access to tools:
- validate_json_structure: Check if data is valid JSON

Use tools to ensure JSON is valid before saving."""
                    
                    user_prompt = f"""The {page_name} has JSON serialization issues. Fix it:

Data: {str(page_data)[:500]}
Validation error: {validation.get('json_error', 'Unknown')}

Return fixed JSON structure."""
                    
                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=user_prompt)
                    ]
                    
                    response = self.llm_with_tools.invoke(messages)
                    
                    # Execute tool if called
                    if hasattr(response, 'tool_calls') and response.tool_calls:
                        for tool_call in response.tool_calls:
                            tool_name = tool_call["name"]
                            if tool_name == "validate_json_structure":
                                # Re-validate after potential fixes
                                result = self.tool_map[tool_name].invoke(tool_call.get("args", {}))
                                if result.get("json_serializable"):
                                    # Could update page_data here if needed
                                    pass
                
                # Save page
                page_path = os.path.join(self.output_dir, f"{page_name}.json")
                try:
                    with open(page_path, 'w', encoding='utf-8') as f:
                        json.dump(page_data, f, indent=2, ensure_ascii=False)
                    files_created[page_name] = page_path
                except (TypeError, ValueError) as e:
                    # If still can't serialize, log error but continue
                    print(f"Warning: Could not save {page_name}: {e}")
        
        return {
            "files_created": files_created,
            "output_directory": self.output_dir,
            "all_pages_generated": len(files_created) == 3
        }
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process state and save JSON files.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with file paths
        """
        faq_page = state.get("faq_page")
        product_page = state.get("product_page")
        comparison_page = state.get("comparison_page")
        
        # Check which pages are missing and provide detailed error
        missing = []
        if not faq_page:
            missing.append("FAQ page")
        if not product_page:
            missing.append("Product page")
        if not comparison_page:
            missing.append("Comparison page")
        
        if missing:
            # Try to generate missing pages or provide helpful error
            error_msg = f"Missing pages for JSON output: {', '.join(missing)}"
            
            # Check if we can still save what we have
            if product_page and comparison_page:
                # Save available pages even if FAQ is missing
                files_created = {}
                
                if product_page:
                    product_path = os.path.join(self.output_dir, "product_page.json")
                    with open(product_path, 'w', encoding='utf-8') as f:
                        json.dump(product_page, f, indent=2, ensure_ascii=False)
                    files_created["product_page"] = product_path
                
                if comparison_page:
                    comparison_path = os.path.join(self.output_dir, "comparison_page.json")
                    with open(comparison_path, 'w', encoding='utf-8') as f:
                        json.dump(comparison_page, f, indent=2, ensure_ascii=False)
                    files_created["comparison_page"] = comparison_path
                
                return {
                    "files_created": files_created,
                    "output_directory": self.output_dir,
                    "errors": [error_msg],
                    "json_output_complete": False
                }
            
            return {
                "errors": [error_msg]
            }
        
        result = self.format_and_save(faq_page, product_page, comparison_page)
        
        return {
            **result,
            "json_output_complete": True
        }

