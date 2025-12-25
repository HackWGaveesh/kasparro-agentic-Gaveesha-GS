"""
Tools for product content generation agents.
These tools enable agents to reason and make decisions.
"""
from typing import List, Dict, Any
from langchain.tools import tool
from langchain_core.tools import ToolException


@tool
def analyze_product_data(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze product data structure and extract key information.
    Helps agents understand product data better.
    
    Args:
        product_data: Product data dictionary
        
    Returns:
        Analysis results with key insights
    """
    analysis = {
        "has_all_fields": all(key in product_data for key in [
            "product_name", "concentration", "skin_type", 
            "key_ingredients", "benefits", "how_to_use", "price"
        ]),
        "ingredient_count": len(product_data.get("key_ingredients", [])),
        "benefit_count": len(product_data.get("benefits", [])),
        "skin_types": product_data.get("skin_type", []),
        "price": product_data.get("price", ""),
        "notes": "Product data analyzed successfully"
    }
    return analysis


@tool
def validate_question_structure(question: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that a question has the required structure.
    
    Args:
        question: Question dictionary
        
    Returns:
        Validation results
    """
    required_fields = ["question", "category", "answer"]
    has_all = all(field in question for field in required_fields)
    
    return {
        "valid": has_all,
        "missing_fields": [f for f in required_fields if f not in question],
        "has_question": "question" in question and "?" in question.get("question", ""),
        "has_category": "category" in question,
        "has_answer": "answer" in question and len(question.get("answer", "")) > 0
    }


@tool
def categorize_question(question_text: str, product_data: Dict[str, Any]) -> str:
    """
    Categorize a question based on its content and product data.
    
    Args:
        question_text: The question text
        product_data: Product data for context
        
    Returns:
        Category name (Informational, Safety, Usage, Purchase, Comparison)
    """
    question_lower = question_text.lower()
    
    # Safety-related keywords
    if any(word in question_lower for word in ["side effect", "safe", "irritat", "sensitive", "warning", "risk"]):
        return "Safety"
    
    # Usage-related keywords
    if any(word in question_lower for word in ["how to use", "apply", "frequency", "when", "how often", "steps"]):
        return "Usage"
    
    # Purchase-related keywords
    if any(word in question_lower for word in ["price", "cost", "buy", "purchase", "where to buy", "available"]):
        return "Purchase"
    
    # Comparison-related keywords
    if any(word in question_lower for word in ["compare", "vs", "versus", "better than", "difference", "alternative"]):
        return "Comparison"
    
    # Default to Informational
    return "Informational"


@tool
def generate_answer_for_question(question: str, category: str, product_data: Dict[str, Any]) -> str:
    """
    Generate an answer for a question based on product data using LLM.
    NO HARDCODED FALLBACKS - Uses LLM to generate answers.
    
    Args:
        question: The question text
        category: Question category
        product_data: Product data to use for answer
        
    Returns:
        Generated answer text from LLM
    """
    # Use LLM to generate answer - NO hardcoded responses
    from config.llm_config import get_llm
    from langchain_core.messages import SystemMessage, HumanMessage
    
    llm = get_llm(temperature=0.7)
    
    system_prompt = """You are an answer generation tool. Generate detailed, accurate answers 
to questions about skincare products based on the provided product data.

Your answers must:
- Be specific and informative
- Use only the provided product data
- Be appropriate for the question category
- Not include any hardcoded or generic responses"""
    
    user_prompt = f"""Generate a detailed answer for this question:

Question: {question}
Category: {category}

Product Information:
- Name: {product_data.get('product_name', '')}
- Concentration: {product_data.get('concentration', '')}
- Key Ingredients: {', '.join(product_data.get('key_ingredients', []))}
- Benefits: {', '.join(product_data.get('benefits', []))}
- Skin Type: {', '.join(product_data.get('skin_type', []))}
- Price: {product_data.get('price', '')}
- Side Effects: {product_data.get('side_effects', '')}
- How to Use: {product_data.get('how_to_use', '')}

Generate a comprehensive answer based on this product data. Do not use generic or hardcoded responses."""
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    
    return response.content


@tool
def validate_product_structure(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that a product has all required fields for comparison.
    
    Args:
        product: Product dictionary
        
    Returns:
        Validation results
    """
    required_fields = [
        "product_name", "concentration", "skin_type",
        "key_ingredients", "benefits", "how_to_use", "price"
    ]
    
    missing = [f for f in required_fields if f not in product]
    has_all = len(missing) == 0
    
    return {
        "valid": has_all,
        "missing_fields": missing,
        "field_count": len([f for f in required_fields if f in product]),
        "total_required": len(required_fields)
    }


@tool
def compare_products(product1: Dict[str, Any], product2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare two products and identify differences.
    
    Args:
        product1: First product data
        product2: Second product data
        
    Returns:
        Comparison results
    """
    comparison = {
        "price_difference": product1.get("price", "") != product2.get("price", ""),
        "ingredient_overlap": list(set(product1.get("key_ingredients", [])) & set(product2.get("key_ingredients", []))),
        "ingredient_unique_1": list(set(product1.get("key_ingredients", [])) - set(product2.get("key_ingredients", []))),
        "ingredient_unique_2": list(set(product2.get("key_ingredients", [])) - set(product1.get("key_ingredients", []))),
        "benefit_overlap": list(set(product1.get("benefits", [])) & set(product2.get("benefits", []))),
        "skin_type_overlap": list(set(product1.get("skin_type", [])) & set(product2.get("skin_type", [])))
    }
    return comparison


@tool
def validate_data_structure(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    """
    Validate that data has all required fields.
    Helps DataParserAgent reason about data structure.
    
    Args:
        data: Data dictionary to validate
        required_fields: List of required field names
        
    Returns:
        Validation results with missing fields
    """
    missing = [f for f in required_fields if f not in data or data.get(f) is None]
    return {
        "valid": len(missing) == 0,
        "missing_fields": missing,
        "present_fields": [f for f in required_fields if f in data and data.get(f) is not None],
        "field_count": len([f for f in required_fields if f in data])
    }


@tool
def analyze_content_needs(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze what content blocks are needed based on product data.
    Helps ContentBlocksAgent reason about which blocks to generate.
    
    Args:
        product_data: Product data dictionary
        
    Returns:
        Analysis of content needs
    """
    needs = {
        "needs_benefits": bool(product_data.get("benefits")),
        "needs_usage": bool(product_data.get("how_to_use")),
        "needs_ingredients": bool(product_data.get("key_ingredients")),
        "needs_safety": bool(product_data.get("side_effects")),
        "recommended_blocks": []
    }
    
    if needs["needs_benefits"]:
        needs["recommended_blocks"].append("benefits")
    if needs["needs_usage"]:
        needs["recommended_blocks"].append("usage")
    if needs["needs_ingredients"]:
        needs["recommended_blocks"].append("ingredients")
    if needs["needs_safety"]:
        needs["recommended_blocks"].append("safety")
    
    return needs


@tool
def select_best_questions(questions: List[Dict[str, Any]], count: int = 5) -> List[Dict[str, Any]]:
    """
    Select the best questions for FAQ page.
    Helps FAQGeneratorAgent reason about question selection.
    
    Args:
        questions: List of all questions
        count: Number of questions to select (default 5)
        
    Returns:
        Selected questions with reasoning
    """
    if len(questions) <= count:
        return questions
    
    # Prioritize: diverse categories, complete answers, clear questions
    categorized = {}
    for q in questions:
        cat = q.get("category", "Informational")
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(q)
    
    selected = []
    # Try to get at least one from each category
    for cat, qs in categorized.items():
        if qs and len(selected) < count:
            # Select question with longest answer (most informative)
            best = max(qs, key=lambda x: len(x.get("answer", "")))
            selected.append(best)
    
    # Fill remaining slots
    remaining = [q for q in questions if q not in selected]
    remaining.sort(key=lambda x: len(x.get("answer", "")), reverse=True)
    selected.extend(remaining[:count - len(selected)])
    
    return selected[:count]


@tool
def validate_faq_structure(faq_page: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate FAQ page structure.
    Helps FAQGeneratorAgent ensure quality.
    
    Args:
        faq_page: FAQ page dictionary
        
    Returns:
        Validation results
    """
    required = ["page_type", "product_name", "faq_items"]
    missing = [f for f in required if f not in faq_page]
    
    faq_items = faq_page.get("faq_items", [])
    item_count = len(faq_items)
    
    return {
        "valid": len(missing) == 0 and item_count >= 5,
        "missing_fields": missing,
        "item_count": item_count,
        "meets_minimum": item_count >= 5,
        "all_items_valid": all("question" in item and "answer" in item for item in faq_items)
    }


@tool
def analyze_page_structure(content_blocks: Dict[str, Any], product_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze what sections should be in product page.
    Helps ProductPageGeneratorAgent reason about page structure.
    
    Args:
        content_blocks: Available content blocks
        product_data: Product data
        
    Returns:
        Analysis of page structure needs
    """
    sections = {
        "overview": True,  # Always needed
        "ingredients": "ingredients" in content_blocks,
        "benefits": "benefits" in content_blocks,
        "usage": "usage" in content_blocks,
        "safety": "safety" in content_blocks,
        "skin_type": bool(product_data.get("skin_type"))
    }
    
    return {
        "recommended_sections": [k for k, v in sections.items() if v],
        "section_count": sum(1 for v in sections.values() if v),
        "has_all_blocks": all(k in content_blocks for k in ["benefits", "usage", "ingredients", "safety"])
    }


@tool
def validate_json_structure(data: Dict[str, Any], expected_keys: List[str]) -> Dict[str, Any]:
    """
    Validate JSON structure before saving.
    Helps JSONOutputAgent ensure valid JSON.
    
    Args:
        data: Data dictionary to validate
        expected_keys: List of expected top-level keys
        
    Returns:
        Validation results
    """
    import json
    
    # Check if it's JSON serializable
    try:
        json.dumps(data)
        json_serializable = True
    except (TypeError, ValueError) as e:
        json_serializable = False
        json_error = str(e)
    
    # Check expected keys
    missing_keys = [k for k in expected_keys if k not in data]
    
    result = {
        "json_serializable": json_serializable,
        "has_expected_keys": len(missing_keys) == 0,
        "missing_keys": missing_keys,
        "present_keys": list(data.keys())
    }
    
    if not json_serializable:
        result["json_error"] = json_error
    
    return result


def get_product_tools():
    """Return all tools available for product agents."""
    return [
        analyze_product_data,
        validate_question_structure,
        categorize_question,
        generate_answer_for_question,
        validate_product_structure,
        compare_products,
        validate_data_structure,
        analyze_content_needs,
        select_best_questions,
        validate_faq_structure,
        analyze_page_structure,
        validate_json_structure
    ]

