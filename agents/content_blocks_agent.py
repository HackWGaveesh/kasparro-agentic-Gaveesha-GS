"""
Content Blocks Agent - Applies reusable content logic blocks.
Uses LangChain LLM with tools for proper agent reasoning.
Single responsibility: Generate all content blocks from product data.
"""
from typing import Dict, Any
from content_blocks.benefits_block import generate_benefits_content
from content_blocks.usage_block import generate_usage_content
from content_blocks.ingredients_block import generate_ingredients_content
from content_blocks.safety_block import generate_safety_content
from config.llm_config import get_llm
from tools.product_tools import get_product_tools, analyze_content_needs
from langchain_core.messages import SystemMessage, HumanMessage
import json


class ContentBlocksAgent:
    """Agent responsible for generating content blocks using tools for reasoning."""
    
    def __init__(self):
        self.llm = get_llm(temperature=0.3)  # Low temperature for logic
        self.tools = [t for t in get_product_tools() if t.name in ["analyze_content_needs", "analyze_product_data"]]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.tool_map = {tool.name: tool for tool in self.tools}
    
    def generate_all_blocks(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate all content blocks from product data using agent reasoning with tools.
        Uses tools to analyze content needs, then generates blocks.
        
        Args:
            product_data: Product data dictionary
            
        Returns:
            Dictionary of all content blocks
        """
        # Use tool to analyze content needs (no API call - tool is pure function)
        content_needs = analyze_content_needs.invoke({"product_data": product_data})
        
        # Generate blocks based on analysis
        blocks = {}
        
        if content_needs.get("needs_benefits"):
            blocks["benefits"] = generate_benefits_content(product_data)
        if content_needs.get("needs_usage"):
            blocks["usage"] = generate_usage_content(product_data)
        if content_needs.get("needs_ingredients"):
            blocks["ingredients"] = generate_ingredients_content(product_data)
        if content_needs.get("needs_safety"):
            blocks["safety"] = generate_safety_content(product_data)
        
        # Use agent reasoning to validate and optimize blocks (single API call if needed)
        if not blocks:
            # If no blocks generated, use agent to reason about what's needed
            system_prompt = """You are a content blocks agent. Analyze product data and determine 
which content blocks should be generated.

You have access to tools:
- analyze_content_needs: Determine what blocks are needed
- analyze_product_data: Understand product structure

Use tools to reason about content needs."""
            
            user_prompt = f"""Analyze this product data and determine which content blocks to generate:

{product_data}

Use analyze_content_needs tool to understand what's needed."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm_with_tools.invoke(messages)
            
            # Execute tool if called
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call.get("args", {})
                    if tool_name in self.tool_map:
                        result = self.tool_map[tool_name].invoke(tool_args)
                        # Use result to generate blocks
                        if tool_name == "analyze_content_needs":
                            needs = result
                            if needs.get("needs_benefits"):
                                blocks["benefits"] = generate_benefits_content(product_data)
                            if needs.get("needs_usage"):
                                blocks["usage"] = generate_usage_content(product_data)
                            if needs.get("needs_ingredients"):
                                blocks["ingredients"] = generate_ingredients_content(product_data)
                            if needs.get("needs_safety"):
                                blocks["safety"] = generate_safety_content(product_data)
        
        # Ensure we always generate all blocks (fallback to generate all if empty)
        if not blocks:
            blocks = {
                "benefits": generate_benefits_content(product_data),
                "usage": generate_usage_content(product_data),
                "ingredients": generate_ingredients_content(product_data),
                "safety": generate_safety_content(product_data)
            }
        
        return blocks
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process state and generate content blocks.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with content blocks
        """
        product_data = state.get("parsed_product", {})
        
        if not product_data:
            return {
                "errors": ["No product data available for content block generation"]
            }
        
        content_blocks = self.generate_all_blocks(product_data)
        
        return {
            "content_blocks": content_blocks,
            "content_blocks_generated": True
        }

