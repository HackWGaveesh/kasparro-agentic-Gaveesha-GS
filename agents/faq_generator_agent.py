"""
FAQ Generator Agent - Generates FAQ page using FAQ template.
Uses LangChain LLM with tools for proper agent reasoning.
Single responsibility: Generate FAQ page JSON output.
"""
from typing import Dict, Any, List
from templates.template_engine import TemplateEngine
from config.llm_config import get_llm
from tools.product_tools import get_product_tools, select_best_questions, validate_faq_structure
from langchain_core.messages import SystemMessage, HumanMessage
import json


class FAQGeneratorAgent:
    """Agent responsible for generating FAQ page using tools for reasoning."""
    
    def __init__(self):
        self.template_engine = TemplateEngine()
        self.llm = get_llm(temperature=0.5)
        self.tools = [t for t in get_product_tools() if t.name in ["select_best_questions", "validate_faq_structure", "validate_question_structure"]]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.tool_map = {tool.name: tool for tool in self.tools}
    
    def generate_faq_page(self, product_data: Dict[str, Any], 
                          questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate FAQ page using template with agent reasoning via tools.
        Uses tools to select best questions and validate structure.
        
        Args:
            product_data: Product data
            questions: Categorized questions with answers
            
        Returns:
            Structured FAQ page
        """
        # Use tool to select best questions (no API call - tool is pure function)
        selected_questions = select_best_questions.invoke({"questions": questions, "count": 5})
        
        # Use template engine
        data = {
            "questions": selected_questions,
            "product_data": product_data
        }
        
        faq_page = self.template_engine.apply_template(
            "faq",
            data,
            {}  # No additional content blocks needed for FAQ
        )
        
        # Use tool to validate FAQ structure (no API call)
        validation = validate_faq_structure.invoke({"faq_page": faq_page})
        
        # If validation fails, use agent reasoning to fix (single API call only if needed)
        if not validation.get("valid"):
            system_prompt = """You are an FAQ generator agent. Generate and validate FAQ pages.

You have access to tools:
- select_best_questions: Choose best questions for FAQ
- validate_faq_structure: Check FAQ page structure

Use tools to ensure FAQ quality."""
            
            user_prompt = f"""The FAQ page validation failed. Fix the FAQ structure:

Current FAQ: {faq_page}
Validation issues: {validation.get('missing_fields', [])}

Ensure FAQ has at least 5 Q&As and all required fields."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm_with_tools.invoke(messages)
            
            # If tool calls, execute them
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call.get("args", {})
                    if tool_name in self.tool_map:
                        result = self.tool_map[tool_name].invoke(tool_args)
                        # Use result to fix FAQ if needed
                        if tool_name == "select_best_questions" and "questions" in tool_args:
                            # Re-generate with better questions
                            data["questions"] = result
                            faq_page = self.template_engine.apply_template("faq", data, {})
        
        return faq_page
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process state and generate FAQ page.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with FAQ page
        """
        product_data = state.get("parsed_product")
        questions = state.get("questions")
        
        # Check what's missing and provide detailed error
        if not product_data:
            return {
                "errors": ["Missing product data for FAQ generation. Data parser may have failed."]
            }
        
        if not questions:
            return {
                "errors": ["Missing questions for FAQ generation. Question generator may have failed."]
            }
        
        if not isinstance(questions, list) or len(questions) == 0:
            return {
                "errors": [f"Questions list is empty or invalid. Got: {type(questions)}. Question generator may have failed."],
                "faq_page": None,
                "faq_generated": False
            }
        
        try:
            faq_page = self.generate_faq_page(product_data, questions)
            
            if not faq_page:
                return {
                    "errors": ["FAQ page generation returned empty result"],
                    "faq_page": None,
                    "faq_generated": False
                }
            
            return {
                "faq_page": faq_page,
                "faq_generated": True
            }
        except Exception as e:
            return {
                "errors": [f"FAQ generation error: {str(e)}"],
                "faq_page": None,
                "faq_generated": False
            }

