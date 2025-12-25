"""
Product data model - Internal representation of product information.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class Product(BaseModel):
    """Internal product model."""
    product_name: str
    concentration: str
    skin_type: List[str]
    key_ingredients: List[str]
    benefits: List[str]
    how_to_use: str
    side_effects: str
    price: str
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "product_name": "GlowBoost Vitamin C Serum",
                "concentration": "10% Vitamin C",
                "skin_type": ["Oily", "Combination"],
                "key_ingredients": ["Vitamin C", "Hyaluronic Acid"],
                "benefits": ["Brightening", "Fades dark spots"],
                "how_to_use": "Apply 2–3 drops in the morning before sunscreen",
                "side_effects": "Mild tingling for sensitive skin",
                "price": "₹699"
            }
        }


class ComparisonProduct(BaseModel):
    """Model for comparison product (can be fictional)."""
    product_name: str
    concentration: Optional[str] = None
    skin_type: List[str]
    key_ingredients: List[str]
    benefits: List[str]
    how_to_use: str
    side_effects: Optional[str] = None
    price: str

