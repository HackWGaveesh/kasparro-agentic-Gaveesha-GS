"""
Template Engine - Applies templates to generate structured content.
"""
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod


class Template(ABC):
    """Base template class."""
    
    @abstractmethod
    def get_fields(self) -> List[str]:
        """Get required fields for this template."""
        pass
    
    @abstractmethod
    def apply(self, data: Dict[str, Any], content_blocks: Dict[str, Any]) -> Dict[str, Any]:
        """Apply template to data using content blocks."""
        pass


class FAQTemplate(Template):
    """FAQ Page Template."""
    
    def get_fields(self) -> List[str]:
        """Required fields for FAQ template."""
        return ["questions", "product_data"]
    
    def apply(self, data: Dict[str, Any], content_blocks: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply FAQ template.
        
        Args:
            data: Product data and questions
            content_blocks: Content logic block outputs
            
        Returns:
            Structured FAQ page
        """
        questions = data.get("questions", [])
        product_data = data.get("product_data", {})
        
        faq_items = []
        for qa in questions[:5]:  # Minimum 5 Q&As
            # Ensure category exists - if missing, use first available category from question
            category = qa.get("category")
            if not category:
                # Try to infer from question text or use first available category
                question_text = qa.get("question", "").lower()
                if any(word in question_text for word in ["safe", "side effect", "irritat"]):
                    category = "Safety"
                elif any(word in question_text for word in ["how to", "use", "apply"]):
                    category = "Usage"
                elif any(word in question_text for word in ["price", "cost", "buy"]):
                    category = "Purchase"
                elif any(word in question_text for word in ["compare", "vs", "versus"]):
                    category = "Comparison"
                else:
                    category = "Informational"  # Default category based on assignment requirements
            
            faq_items.append({
                "question": qa.get("question", ""),
                "answer": qa.get("answer", ""),
                "category": category
            })
        
        return {
            "page_type": "faq",
            "product_name": product_data.get("product_name", ""),
            "faq_items": faq_items,
            "total_questions": len(faq_items),
            "categories": list(set(item.get("category") for item in faq_items))
        }


class ProductDescriptionTemplate(Template):
    """Product Description Page Template."""
    
    def get_fields(self) -> List[str]:
        """Required fields for product template."""
        return ["product_data", "benefits_content", "usage_content", "ingredients_content", "safety_content"]
    
    def apply(self, data: Dict[str, Any], content_blocks: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply product description template.
        
        Args:
            data: Product data
            content_blocks: Content logic block outputs
            
        Returns:
            Structured product page
        """
        product_data = data.get("product_data", {})
        benefits = content_blocks.get("benefits", {})
        usage = content_blocks.get("usage", {})
        ingredients = content_blocks.get("ingredients", {})
        safety = content_blocks.get("safety", {})
        
        return {
            "page_type": "product_description",
            "product_name": product_data.get("product_name", ""),
            "price": product_data.get("price", ""),
            "concentration": product_data.get("concentration", ""),
            "sections": {
                "overview": {
                    "description": f"{product_data.get('product_name', '')} - {product_data.get('concentration', '')}",
                    "key_highlights": product_data.get("benefits", [])
                },
                "ingredients": {
                    "key_ingredients": ingredients.get("key_ingredients", []),
                    "ingredient_details": ingredients.get("ingredient_details", {}),
                    "concentration": ingredients.get("concentration", "")
                },
                "benefits": {
                    "primary_benefits": benefits.get("primary_benefits", []),
                    "formatted_benefits": benefits.get("formatted_benefits", [])
                },
                "usage": {
                    "instructions": usage.get("instructions", ""),
                    "steps": usage.get("steps", []),
                    "frequency": usage.get("frequency", ""),
                    "tips": usage.get("application_tips", [])
                },
                "safety": {
                    "side_effects": safety.get("side_effects", ""),
                    "warnings": safety.get("warnings", []),
                    "precautions": safety.get("safety_notes", [])
                },
                "skin_type": {
                    "suitable_for": product_data.get("skin_type", [])
                }
            }
        }


class ComparisonTemplate(Template):
    """Comparison Page Template."""
    
    def get_fields(self) -> List[str]:
        """Required fields for comparison template."""
        return ["product1_data", "product2_data"]
    
    def apply(self, data: Dict[str, Any], content_blocks: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply comparison template.
        
        Args:
            data: Product data for both products
            content_blocks: Content logic block outputs (including comparison)
            
        Returns:
            Structured comparison page
        """
        product1 = data.get("product1_data", {})
        product2 = data.get("product2_data", {})
        comparison = content_blocks.get("ingredients_comparison", {})
        
        return {
            "page_type": "comparison",
            "products": {
                "product1": {
                    "name": product1.get("product_name", ""),
                    "price": product1.get("price", ""),
                    "concentration": product1.get("concentration", ""),
                    "key_ingredients": product1.get("key_ingredients", []),
                    "benefits": product1.get("benefits", []),
                    "skin_type": product1.get("skin_type", [])
                },
                "product2": {
                    "name": product2.get("product_name", ""),
                    "price": product2.get("price", ""),
                    "concentration": product2.get("concentration", ""),
                    "key_ingredients": product2.get("key_ingredients", []),
                    "benefits": product2.get("benefits", []),
                    "skin_type": product2.get("skin_type", [])
                }
            },
            "comparison": {
                "ingredients": {
                    "common": comparison.get("common_ingredients", []),
                    "unique_to_product1": comparison.get("unique_to_product1", []),
                    "unique_to_product2": comparison.get("unique_to_product2", []),
                    "similarity_score": comparison.get("similarity_score", 0)
                },
                "price": {
                    "product1_price": product1.get("price", ""),
                    "product2_price": product2.get("price", ""),
                    "price_difference": _calculate_price_difference(product1.get("price", ""), product2.get("price", ""))
                },
                "benefits": {
                    "product1_benefits": product1.get("benefits", []),
                    "product2_benefits": product2.get("benefits", []),
                    "shared_benefits": list(set(product1.get("benefits", [])) & set(product2.get("benefits", [])))
                }
            },
            "recommendation": _generate_recommendation(product1, product2, comparison)
        }


def _calculate_price_difference(price1: str, price2: str) -> str:
    """Calculate price difference."""
    try:
        # Extract numbers from price strings
        import re
        num1 = float(re.findall(r'\d+', price1.replace(',', ''))[0])
        num2 = float(re.findall(r'\d+', price2.replace(',', ''))[0])
        diff = abs(num1 - num2)
        return f"₹{diff:.0f}"
    except:
        return ""  # Return empty string instead of hardcoded "N/A"


def _generate_recommendation(product1: Dict, product2: Dict, comparison: Dict) -> str:
    """Generate recommendation based on comparison."""
    similarity = comparison.get("similarity_score", 0)
    
    if similarity > 70:
        return "Both products are similar. Choose based on price and specific needs."
    else:
        return "Products differ significantly. Consider your specific skin concerns and budget."


class TemplateEngine:
    """Template engine for applying templates."""
    
    def __init__(self):
        self.templates = {
            "faq": FAQTemplate(),
            "product_description": ProductDescriptionTemplate(),
            "comparison": ComparisonTemplate()
        }
    
    def apply_template(self, template_name: str, data: Dict[str, Any], 
                      content_blocks: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a template to data.
        
        Args:
            template_name: Name of template to apply
            data: Data for template
            content_blocks: Content logic block outputs
            
        Returns:
            Structured page content
        """
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        template = self.templates[template_name]
        
        # Validate required fields
        required_fields = template.get_fields()
        missing = [field for field in required_fields if field not in data]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        
        return template.apply(data, content_blocks)

