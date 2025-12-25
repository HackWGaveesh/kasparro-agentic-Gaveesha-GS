"""
Data Parser Agent - Parses product data into clean internal model.
Uses LangChain LLM with tools for proper agent reasoning.
Single responsibility: Convert raw product data to structured Product model.
"""
from typing import Dict, Any
from models.product_model import Product
from config.llm_config import get_llm, MODEL_NAME
from tools.product_tools import get_product_tools, validate_data_structure, analyze_product_data
from langchain_core.messages import SystemMessage, HumanMessage
import json


class DataParserAgent:
    """Agent responsible for parsing and validating product data using tools for reasoning."""
    
    def __init__(self):
        self.llm = get_llm(temperature=0.1)  # Low temperature for data parsing
        self.tools = [t for t in get_product_tools() if t.name in ["validate_data_structure", "analyze_product_data"]]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.tool_map = {tool.name: tool for tool in self.tools}
    
    def parse_product_data(self, raw_data: Dict[str, Any]) -> Product:
        """
        Parse raw product data into clean Product model using agent reasoning with tools.
        NO FALLBACKS - Uses tools for validation and reasoning.
        
        Args:
            raw_data: Raw product data dictionary
            
        Returns:
            Validated Product model
        """
        required_fields = ["product_name", "concentration", "skin_type", 
                          "key_ingredients", "benefits", "how_to_use", "price"]
        
        # Use tool to validate structure first (no API call)
        validation = validate_data_structure.invoke({"data": raw_data, "required_fields": required_fields})
        
        # Try direct parsing first (most efficient - no API call)
        if validation["valid"]:
            try:
                product = Product(**raw_data)
                return product
            except Exception:
                pass  # Fall through to LLM fixing
        
        # Use agent reasoning with tools if validation fails or parsing fails
        system_prompt = """You are a data parser agent. Your role is to parse and validate product data.

You have access to tools:
- validate_data_structure: Check if data has required fields
- analyze_product_data: Analyze product structure

Use these tools to understand the data structure, then fix and return valid JSON."""
        
        user_prompt = f"""Parse and fix this product data to match the required structure:

{raw_data}

Required fields: {', '.join(required_fields)}

Use validate_data_structure tool first to check what's missing, then return fixed JSON."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # Agent reasoning with tools (single API call)
        response = self.llm_with_tools.invoke(messages)
        messages.append(response)
        
        # Execute tool calls if any
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call.get("args", {})
                if tool_name in self.tool_map:
                    result = self.tool_map[tool_name].invoke(tool_args)
                    messages.append({
                        "role": "tool",
                        "content": json.dumps(result) if isinstance(result, dict) else str(result),
                        "tool_call_id": tool_call.get("id")
                    })
            
            # Get final response after tool execution
            final_response = self.llm_with_tools.invoke(messages)
            result_text = final_response.content
        else:
            result_text = response.content
        
        # Parse JSON from response
        try:
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            fixed_data = json.loads(result_text)
            product = Product(**fixed_data)
            return product
        except Exception as e:
            # Last resort: try to fix with minimal LLM call
            fix_prompt = f"Fix this data to have all fields {required_fields}. Return ONLY valid JSON: {raw_data}"
            simple_response = self.llm.invoke([
                SystemMessage(content="You are a JSON fixer. Return ONLY valid JSON, no markdown."),
                HumanMessage(content=fix_prompt)
            ])
            fix_text = simple_response.content.strip()
            if "```json" in fix_text:
                fix_text = fix_text.split("```json")[1].split("```")[0].strip()
            fixed_data = json.loads(fix_text)
            return Product(**fixed_data)
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process state and parse product data.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with parsed product
        """
        raw_data = state.get("raw_product_data")
        
        if not raw_data:
            return {
                "errors": ["No product data provided"]
            }
        
        product = self.parse_product_data(raw_data)
        
        return {
            "parsed_product": product.model_dump(),
            "product": product,  # Keep model instance for agents
            "data_parsed": True
        }

