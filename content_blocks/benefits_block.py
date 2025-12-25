"""
Benefits Content Block - Reusable logic for generating benefits content.
"""
from typing import List, Dict, Any


def generate_benefits_content(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate benefits content from product data.
    Reusable content logic block.
    
    Args:
        product_data: Product data dictionary
        
    Returns:
        Structured benefits content
    """
    benefits = product_data.get("benefits", [])
    ingredients = product_data.get("key_ingredients", [])
    
    # Content logic: Transform data into structured benefits
    benefits_content = {
        "primary_benefits": benefits,
        "benefit_count": len(benefits),
        "ingredient_benefits": {},
        "formatted_benefits": []
    }
    
    # Map ingredients to benefits based on product data (no hardcoded mappings)
    # Ingredients support benefits that are listed in the product benefits
    for ingredient in ingredients:
        # Match ingredient to benefits that mention related keywords
        ingredient_lower = ingredient.lower()
        related_benefits = []
        for benefit in benefits:
            benefit_lower = benefit.lower()
            # Check if ingredient name appears in benefit or vice versa
            if ingredient_lower in benefit_lower or any(word in benefit_lower for word in ingredient_lower.split()):
                related_benefits.append(benefit)
        if related_benefits:
            benefits_content["ingredient_benefits"][ingredient] = ", ".join(related_benefits)
    
    # Format benefits for display (no hardcoded descriptions)
    for benefit in benefits:
        # Find which ingredients might support this benefit
        supported_by = []
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            benefit_lower = benefit.lower()
            # If ingredient name appears in benefit or benefit keywords match ingredient
            if ingredient_lower in benefit_lower or any(word in benefit_lower for word in ingredient_lower.split()):
                supported_by.append(ingredient)
        
        benefits_content["formatted_benefits"].append({
            "benefit": benefit,
            "description": f"Provides {benefit.lower()} benefits",
            "supported_by": supported_by if supported_by else ingredients  # Use all ingredients if no match
        })
    
    return benefits_content


def format_benefits_for_display(benefits_content: Dict[str, Any]) -> str:
    """
    Format benefits content for display.
    
    Args:
        benefits_content: Benefits content dictionary
        
    Returns:
        Formatted benefits text
    """
    formatted = []
    for benefit_item in benefits_content.get("formatted_benefits", []):
        formatted.append(f"• {benefit_item['benefit']}: {benefit_item['description']}")
    
    return "\n".join(formatted)

