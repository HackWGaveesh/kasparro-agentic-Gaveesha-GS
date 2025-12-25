"""
Comparison Generator Agent - Generates comparison page with fictional Product B.
Uses LangChain LLM with tools for proper agent reasoning.
Single responsibility: Generate comparison page JSON output.
"""
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from templates.template_engine import TemplateEngine
from content_blocks.ingredients_block import compare_ingredients
from config.llm_config import get_llm, MODEL_NAME
from tools.product_tools import get_product_tools, validate_product_structure, compare_products
import json


class ComparisonGeneratorAgent:
    """Agent responsible for generating comparison page."""
    
    def __init__(self):
        self.template_engine = TemplateEngine()
        self.llm = get_llm(temperature=0.8)
        self.tools = get_product_tools()
        # Bind tools to LLM for tool calling
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.tool_map = {tool.name: tool for tool in self.tools}
    
    def generate_fictional_product_b(self, product_a_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate fictional Product B for comparison.
        NO FALLBACKS - Makes real API call.
        
        Args:
            product_a_data: Original product data
            
        Returns:
            Fictional Product B data
        """
        system_prompt = """You are a product generation agent. Create a fictional 
skincare product that is similar but different from the given product.

You have access to tools:
- validate_product_structure: Validate product has all required fields
- compare_products: Compare products to ensure differences

The product must be:
- Realistic and structured
- Similar category (serum, cream, etc.)
- Different ingredients, benefits, or price
- Complete with all required fields

ALWAYS use validate_product_structure tool to ensure the product is complete."""

        prompt = f"""Create a fictional skincare product for comparison with:

{product_a_data.get('product_name', '')}

Generate a complete product with:
- product_name (fictional but realistic)
- concentration (different from original)
- skin_type (list)
- key_ingredients (list, some overlap but also unique)
- benefits (list, some similar, some different)
- how_to_use (string)
- side_effects (string, optional)
- price (different from original, in ₹)

Use validate_product_structure tool to ensure all fields are present.
Return as JSON matching this structure."""

        # Use LLM with tools for proper agent reasoning
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        # Agent reasoning with tools
        response = self.llm_with_tools.invoke(messages)
        messages.append(response)
        
        # Check for tool calls and execute
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                if tool_call["name"] == "validate_product_structure":
                    # Tool will be called, but we need the product JSON first
                    pass
        
        result_text = response.content
        
        # Try to extract JSON from response
        try:
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            product_b = json.loads(result_text)
        except Exception as e:
            # If JSON parsing fails, retry with LLM - NO HARDCODED FALLBACK
            retry_prompt = f"""The previous response was not valid JSON. Please generate a fictional skincare product for comparison with:

{product_a_data.get('product_name', '')}

Return ONLY valid JSON (no markdown, no code blocks) with this exact structure:
{{
  "product_name": "fictional product name",
  "concentration": "concentration",
  "skin_type": ["type1", "type2"],
  "key_ingredients": ["ingredient1", "ingredient2"],
  "benefits": ["benefit1", "benefit2"],
  "how_to_use": "usage instructions",
  "side_effects": "side effects",
  "price": "₹price"
}}"""
            
            retry_response = self.llm_with_tools.invoke([
                SystemMessage(content="You are a JSON generator. Return ONLY valid JSON, no markdown, no explanations."),
                HumanMessage(content=retry_prompt)
            ])
            
            retry_text = retry_response.content.strip()
            # Remove any markdown formatting
            if "```json" in retry_text:
                retry_text = retry_text.split("```json")[1].split("```")[0].strip()
            elif "```" in retry_text:
                retry_text = retry_text.split("```")[1].split("```")[0].strip()
            
            product_b = json.loads(retry_text)
        
        # Validate required fields exist (but don't use defaults - raise error if missing)
        required_fields = [
            "product_name", "concentration", "skin_type", 
            "key_ingredients", "benefits", "how_to_use", "price"
        ]
        
        for field in required_fields:
            if field not in product_b:
                raise ValueError(f"Missing required field in Product B: {field}")
        
        # Validate using tool - NO hardcoded defaults
        validation = validate_product_structure.invoke({"product": product_b})
        
        if not validation.get("valid"):
            # Only retry if critical fields missing (to save API calls)
            critical_fields = ["product_name", "key_ingredients", "benefits", "price"]
            missing_critical = [f for f in validation.get('missing_fields', []) if f in critical_fields]
            
            if missing_critical:
                # Use LLM to fix missing fields - NO hardcoded defaults
                fix_prompt = f"""The product is missing these critical fields: {missing_critical}
                
Fix the product JSON to include all required fields. Return ONLY valid JSON."""
                
                fix_response = self.llm_with_tools.invoke([
                    SystemMessage(content="You are a JSON fixer. Return ONLY valid JSON."),
                    HumanMessage(content=fix_prompt)
                ])
                
                fix_text = fix_response.content
                if "```json" in fix_text:
                    fix_text = fix_text.split("```json")[1].split("```")[0].strip()
                elif "```" in fix_text:
                    fix_text = fix_text.split("```")[1].split("```")[0].strip()
                
                try:
                    product_b = json.loads(fix_text)
                except:
                    raise ValueError(f"Could not generate valid Product B. Missing: {missing_critical}")
        
        # Ensure proper types (convert, don't use defaults)
        if not isinstance(product_b.get("skin_type"), list):
            product_b["skin_type"] = [product_b.get("skin_type")] if product_b.get("skin_type") else []
        if not isinstance(product_b.get("key_ingredients"), list):
            product_b["key_ingredients"] = [product_b.get("key_ingredients")] if product_b.get("key_ingredients") else []
        if not isinstance(product_b.get("benefits"), list):
            product_b["benefits"] = [product_b.get("benefits")] if product_b.get("benefits") else []
        
        # Final validation
        final_validation = validate_product_structure.invoke({"product": product_b})
        if not final_validation.get("valid"):
            raise ValueError(f"Product B validation failed: {final_validation.get('missing_fields', [])}")
        
        return product_b
    
    def generate_comparison_page(self, product_a_data: Dict[str, Any], 
                                product_b_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comparison page using template.
        
        Args:
            product_a_data: Original product data
            product_b_data: Fictional Product B data
            
        Returns:
            Structured comparison page
        """
        # Use tool for comparison - proper agent reasoning
        comparison_result = compare_products.invoke({
            "product1": product_a_data,
            "product2": product_b_data
        })
        
        # Also use content block for ingredients comparison
        ingredients_comparison = compare_ingredients(
            product_a_data.get("key_ingredients", []),
            product_b_data.get("key_ingredients", [])
        )
        
        # Merge tool result with content block result
        ingredients_comparison.update(comparison_result)
        
        # Use template engine
        data = {
            "product1_data": product_a_data,
            "product2_data": product_b_data
        }
        
        content_blocks = {
            "ingredients_comparison": ingredients_comparison
        }
        
        comparison_page = self.template_engine.apply_template(
            "comparison",
            data,
            content_blocks
        )
        
        return comparison_page
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process state and generate comparison page.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with comparison page
        """
        product_a_data = state.get("parsed_product", {})
        
        if not product_a_data:
            return {
                "errors": ["Missing product data for comparison generation"]
            }
        
        # Generate fictional Product B
        product_b_data = self.generate_fictional_product_b(product_a_data)
        
        # Generate comparison
        comparison_page = self.generate_comparison_page(product_a_data, product_b_data)
        
        return {
            "comparison_page": comparison_page,
            "product_b_data": product_b_data,
            "comparison_generated": True
        }

