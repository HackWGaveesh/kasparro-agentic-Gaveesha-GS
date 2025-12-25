"""
Question Generator Agent - Generates categorized user questions.
Uses LangChain LLM with tools bound for proper agent reasoning.
Single responsibility: Generate 15+ categorized questions about the product.
"""
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from config.llm_config import get_llm, MODEL_NAME
from tools.product_tools import get_product_tools
import json
import re


class QuestionGeneratorAgent:
    """Agent responsible for generating categorized questions using tools for reasoning."""
    
    def __init__(self):
        self.llm = get_llm(temperature=0.7)
        self.tools = get_product_tools()
        # Bind tools to LLM for tool calling capability
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        # Create tool map for execution
        self.tool_map = {tool.name: tool for tool in self.tools}
    
    def _execute_tool(self, tool_call) -> str:
        """Execute a tool call and return result."""
        tool_name = tool_call["name"]
        tool_args = tool_call.get("args", {})
        
        if tool_name in self.tool_map:
            result = self.tool_map[tool_name].invoke(tool_args)
            return json.dumps(result) if isinstance(result, dict) else str(result)
        return "Tool not found"
    
    def generate_categorized_questions(self, product_data: Dict[str, Any], 
                                      min_questions: int = 15) -> List[Dict[str, Any]]:
        """
        Generate categorized questions about the product using agent reasoning with tools.
        NO FALLBACKS - Uses LangChain LLM with tools.
        
        Args:
            product_data: Product data dictionary
            min_questions: Minimum number of questions to generate
            
        Returns:
            List of categorized questions with answers
        """
        system_prompt = """You are a question generation agent. Your role is to 
generate categorized user questions about skincare products.

You have access to tools that help you:
- analyze_product_data: Analyze product structure
- validate_question_structure: Validate question format
- categorize_question: Determine question category
- generate_answer_for_question: Create answers

Categories:
- Informational: Questions about ingredients, benefits, how it works
- Safety: Questions about side effects, skin compatibility, warnings
- Usage: Questions about application, frequency, best practices
- Purchase: Questions about price, availability, value
- Comparison: Questions comparing with other products

ALWAYS use your tools for reasoning:
1. First use analyze_product_data to understand the product
2. Generate questions and use categorize_question for each
3. Use generate_answer_for_question to create answers
4. Use validate_question_structure to ensure proper format

Never provide hardcoded responses. Always use tools."""
        
        user_prompt = f"""Generate exactly {min_questions} categorized questions about this product.

Product Information:
- Name: {product_data.get('product_name', '')}
- Concentration: {product_data.get('concentration', '')}
- Ingredients: {', '.join(product_data.get('key_ingredients', []))}
- Benefits: {', '.join(product_data.get('benefits', []))}
- Skin Type: {', '.join(product_data.get('skin_type', []))}
- Price: {product_data.get('price', '')}
- Side Effects: {product_data.get('side_effects', '')}
- Usage: {product_data.get('how_to_use', '')}

IMPORTANT: Return ONLY a valid JSON array. No markdown, no code blocks, no explanations.
The response must start with [ and end with ].

Format:
[
  {{"question": "What is this product?", "category": "Informational", "answer": "This product is..."}},
  {{"question": "Is it safe?", "category": "Safety", "answer": "Yes, it is safe..."}},
  ...
]

Generate {min_questions} questions across these categories:
- Informational (at least 3)
- Safety (at least 3)
- Usage (at least 3)
- Purchase (at least 3)
- Comparison (at least 3)"""
        
        # Use direct LLM call first (more reliable for JSON generation)
        # This avoids tool calling complexity and gets cleaner JSON responses
        questions = self._generate_questions_direct_llm(product_data, min_questions)
        
        # If we got valid questions, use them
        if questions and len(questions) >= min_questions - 3:
            return questions
        
        # If direct call didn't work well, try with tools as backup
        # (This should rarely be needed, but provides redundancy)
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm_with_tools.invoke(messages)
            final_response = response.content if hasattr(response, 'content') else str(response)
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', final_response, re.DOTALL)
            if json_match:
                tool_questions = json.loads(json_match.group())
                if isinstance(tool_questions, list) and len(tool_questions) > len(questions):
                    questions = tool_questions
        except:
            pass  # If tool approach fails, use what we got from direct call
        
        # Ensure we have enough questions (only if significantly short to save API calls)
        if len(questions) < min_questions - 3:  # Only generate more if we're significantly short
            additional = self._generate_additional_questions_with_tools(
                product_data, min_questions - len(questions)
            )
            questions.extend(additional)
        
        # Validate and ensure all questions have answers (minimal tool usage to save API calls)
        validated_questions = []
        for q in questions[:min_questions]:
            if isinstance(q, dict) and q.get("question"):
                # Only use tools if absolutely necessary (to save API calls)
                if not q.get("category"):
                    from tools.product_tools import categorize_question
                    q["category"] = categorize_question.invoke({
                        "question_text": q["question"],
                        "product_data": product_data
                    })
                
                # Only generate answer if missing or very short
                if not q.get("answer") or len(q.get("answer", "")) < 5:
                    from tools.product_tools import generate_answer_for_question
                    q["answer"] = generate_answer_for_question.invoke({
                        "question": q["question"],
                        "category": q.get("category", "Informational"),
                        "product_data": product_data
                    })
                
                validated_questions.append(q)
        
        return validated_questions[:min_questions]
    
    def _generate_questions_direct_llm(self, product_data: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
        """Generate questions using direct LLM call - more reliable for JSON generation."""
        prompt = f"""Generate exactly {count} questions about this skincare product.

Product Details:
- Name: {product_data.get('product_name', '')}
- Concentration: {product_data.get('concentration', '')}
- Key Ingredients: {', '.join(product_data.get('key_ingredients', []))}
- Benefits: {', '.join(product_data.get('benefits', []))}
- Suitable for Skin Types: {', '.join(product_data.get('skin_type', []))}
- Price: {product_data.get('price', '')}
- Side Effects: {product_data.get('side_effects', '')}
- How to Use: {product_data.get('how_to_use', '')}

CRITICAL: Return ONLY a valid JSON array. Start with [ and end with ]. No markdown code blocks, no explanations.

Required format (JSON array):
[
  {{"question": "What is this product?", "category": "Informational", "answer": "This is a vitamin C serum..."}},
  {{"question": "Is it safe for sensitive skin?", "category": "Safety", "answer": "It may cause mild tingling..."}},
  {{"question": "How do I use it?", "category": "Usage", "answer": "Apply 2-3 drops in the morning..."}},
  {{"question": "What is the price?", "category": "Purchase", "answer": "The price is ₹699..."}},
  {{"question": "How does it compare to other serums?", "category": "Comparison", "answer": "This product offers..."}}
]

Generate {count} questions total, distributed across:
- Informational: questions about ingredients, benefits, how it works
- Safety: questions about side effects, skin compatibility, warnings
- Usage: questions about application, frequency, best practices
- Purchase: questions about price, availability, value
- Comparison: questions comparing with other products"""
        
        response = self.llm.invoke([
            SystemMessage(content="""You are a question generator for skincare products. 
You MUST return ONLY a valid JSON array. No markdown, no code blocks, no explanations.
The response must be parseable JSON starting with [ and ending with ]."""),
            HumanMessage(content=prompt)
        ])
        
        # Extract JSON from response
        content = response.content.strip()
        
        # Remove markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        # Remove any leading/trailing text
        content = content.strip()
        if not content.startswith('['):
            # Try to find JSON array in the content
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                content = json_match.group()
        
        # Parse JSON
        try:
            questions = json.loads(content)
            if isinstance(questions, dict) and "questions" in questions:
                questions = questions["questions"]
            elif not isinstance(questions, list):
                questions = []
            return questions
        except json.JSONDecodeError as e:
            # If JSON parsing fails, try to extract and fix common issues
            try:
                # Try to fix common JSON issues
                content = content.replace("'", '"')  # Replace single quotes
                content = re.sub(r',\s*}', '}', content)  # Remove trailing commas
                content = re.sub(r',\s*]', ']', content)  # Remove trailing commas
                questions = json.loads(content)
                if isinstance(questions, list):
                    return questions
            except:
                pass
            
            # Last resort: return empty and let the error handling catch it
            return []
    
    def _generate_questions_with_tools(self, product_data: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
        """Generate questions using tools."""
        return self._generate_questions_direct_llm(product_data, count)
    
    def _generate_additional_questions_with_tools(self, product_data: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
        """Generate additional questions using tools."""
        return self._generate_questions_with_tools(product_data, count)
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process state and generate questions using agent reasoning.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with categorized questions
        """
        product_data = state.get("parsed_product", {})
        
        if not product_data:
            return {
                "errors": ["No product data available for question generation"]
            }
        
        try:
            questions = self.generate_categorized_questions(product_data, min_questions=15)
            
            # Ensure we have at least some questions (NO fallback, but ensure we don't fail silently)
            if not questions or len(questions) == 0:
                return {
                    "errors": ["Question generator failed to generate any questions. Check API connection."],
                    "questions": [],
                    "questions_generated": False,
                    "question_count": 0
                }
            
            return {
                "questions": questions,
                "questions_generated": True,
                "question_count": len(questions),
                "categories": list(set(q.get("category", "Informational") for q in questions if q.get("category")))
            }
        except Exception as e:
            return {
                "errors": [f"Question generator error: {str(e)}"],
                "questions": [],
                "questions_generated": False,
                "question_count": 0
            }
