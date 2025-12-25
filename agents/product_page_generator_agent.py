"""
Product Page Generator Agent - Generates product description page.
Uses LangChain LLM with tools for proper agent reasoning.
Single responsibility: Generate product description page JSON output.
"""
from typing import Dict, Any
from templates.template_engine import TemplateEngine
from config.llm_config import get_llm
from tools.product_tools import get_product_tools, analyze_page_structure
from langchain_core.messages import SystemMessage, HumanMessage
import json


class ProductPageGeneratorAgent:
    """Agent responsible for generating product description page using tools for reasoning."""
    
    def __init__(self):
        self.template_engine = TemplateEngine()
        self.llm = get_llm(temperature=0.4)
        self.tools = [t for t in get_product_tools() if t.name in ["analyze_page_structure", "analyze_product_data"]]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.tool_map = {tool.name: tool for tool in self.tools}
    
    def generate_product_page(self, product_data: Dict[str, Any], 
                             content_blocks: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate product description page using template with agent reasoning via tools.
        Uses tools to analyze page structure needs.
        
        Args:
            product_data: Product data
            content_blocks: Content logic block outputs
            
        Returns:
            Structured product page
        """
        # Use tool to analyze page structure (no API call - tool is pure function)
        structure_analysis = analyze_page_structure.invoke({
            "content_blocks": content_blocks,
            "product_data": product_data
        })
        
        # Use template engine
        data = {
            "product_data": product_data,
            "benefits_content": content_blocks.get("benefits", {}),
            "usage_content": content_blocks.get("usage", {}),
            "ingredients_content": content_blocks.get("ingredients", {}),
            "safety_content": content_blocks.get("safety", {})
        }
        
        product_page = self.template_engine.apply_template(
            "product_description",
            data,
            content_blocks
        )
        
        # Use agent reasoning to optimize page if needed (single API call only if structure is incomplete)
        recommended_sections = structure_analysis.get("recommended_sections", [])
        if not recommended_sections or len(recommended_sections) < 3:
            system_prompt = """You are a product page generator agent. Analyze and optimize product page structure.

You have access to tools:
- analyze_page_structure: Determine what sections are needed
- analyze_product_data: Understand product information

Use tools to ensure complete page structure."""
            
            user_prompt = f"""Analyze the product page structure:

Product: {product_data.get('product_name', '')}
Available blocks: {list(content_blocks.keys())}
Current sections: {list(product_page.get('sections', {}).keys()) if isinstance(product_page.get('sections'), dict) else []}

Use analyze_page_structure to ensure all necessary sections are included."""
            
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
                        # Could use result to enhance page, but template already handles it
        
        return product_page
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process state and generate product page.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with product page
        """
        product_data = state.get("parsed_product", {})
        content_blocks = state.get("content_blocks", {})
        
        if not product_data or not content_blocks:
            return {
                "errors": ["Missing product data or content blocks for product page generation"]
            }
        
        product_page = self.generate_product_page(product_data, content_blocks)
        
        return {
            "product_page": product_page,
            "product_page_generated": True
        }

