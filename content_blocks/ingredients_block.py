"""
Ingredients Content Block - Reusable logic for generating ingredients content.
"""
from typing import Dict, Any, List


def generate_ingredients_content(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate ingredients content from product data.
    Reusable content logic block.
    
    Args:
        product_data: Product data dictionary
        
    Returns:
        Structured ingredients content
    """
    ingredients = product_data.get("key_ingredients", [])
    concentration = product_data.get("concentration", "")
    
    # Content logic: Structure ingredients information
    ingredients_content = {
        "key_ingredients": ingredients,
        "concentration": concentration,
        "ingredient_details": {},
        "ingredient_count": len(ingredients),
        "active_ingredients": [],
        "supporting_ingredients": []
    }
    
    # Add ingredient details based on product data (no hardcoded ingredient info)
    # Extract concentration from product concentration field if it mentions the ingredient
    concentration_text = concentration.lower() if concentration else ""
    
    # Get benefits from product data to associate with ingredients
    product_benefits = product_data.get("benefits", [])
    
    for ingredient in ingredients:
        ingredient_lower = ingredient.lower()
        
        # Determine if ingredient concentration is mentioned
        ingredient_concentration = ""
        if ingredient_lower in concentration_text:
            # Extract concentration value if mentioned
            import re
            conc_match = re.search(r'(\d+%)', concentration)
            if conc_match:
                ingredient_concentration = conc_match.group(1)
            else:
                ingredient_concentration = concentration
        else:
            ingredient_concentration = "As listed"  # Not specifically mentioned
        
        # Find related benefits from product benefits list
        related_benefits = []
        for benefit in product_benefits:
            benefit_lower = benefit.lower()
            if ingredient_lower in benefit_lower or any(word in benefit_lower for word in ingredient_lower.split()):
                related_benefits.append(benefit)
        
        # All key ingredients are considered active
        ingredient_type = "active"
        
        ingredients_content["ingredient_details"][ingredient] = {
            "type": ingredient_type,
            "benefits": related_benefits if related_benefits else product_benefits[:2],  # Use product benefits if no match
            "concentration": ingredient_concentration,
            "description": f"{ingredient} - Key active ingredient in this product"
        }
        
        if ingredient_type == "active":
            ingredients_content["active_ingredients"].append(ingredient)
        else:
            ingredients_content["supporting_ingredients"].append(ingredient)
    
    return ingredients_content


def format_ingredients_for_display(ingredients_content: Dict[str, Any]) -> str:
    """
    Format ingredients content for display.
    
    Args:
        ingredients_content: Ingredients content dictionary
        
    Returns:
        Formatted ingredients text
    """
    formatted = []
    
    for ingredient, details in ingredients_content.get("ingredient_details", {}).items():
        concentration = details.get('concentration', '')
        if concentration:
            formatted.append(f"{ingredient} ({concentration})")
        else:
            formatted.append(f"{ingredient}")
        formatted.append(f"  {details.get('description', '')}")
        benefits = details.get('benefits', [])
        if benefits:
            formatted.append(f"  Benefits: {', '.join(benefits)}")
        formatted.append("")
    
    return "\n".join(formatted)


def compare_ingredients(product1_ingredients: List[str], 
                       product2_ingredients: List[str]) -> Dict[str, Any]:
    """
    Compare ingredients between two products.
    Reusable comparison logic block.
    
    Args:
        product1_ingredients: First product's ingredients
        product2_ingredients: Second product's ingredients
        
    Returns:
        Comparison results
    """
    common = list(set(product1_ingredients) & set(product2_ingredients))
    unique_to_1 = list(set(product1_ingredients) - set(product2_ingredients))
    unique_to_2 = list(set(product2_ingredients) - set(product1_ingredients))
    
    return {
        "common_ingredients": common,
        "unique_to_product1": unique_to_1,
        "unique_to_product2": unique_to_2,
        "similarity_score": len(common) / max(len(product1_ingredients), len(product2_ingredients), 1) * 100
    }

