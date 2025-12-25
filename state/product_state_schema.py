"""
State schema for the product content generation workflow.
"""
from typing import TypedDict, List, Optional, Dict, Any, Annotated
from langgraph.graph.message import add_messages
from models.product_model import Product


class ProductState(TypedDict):
    """
    State schema for the product content generation workflow.
    All agents read from and write to this shared state.
    """
    # Input
    raw_product_data: Dict[str, Any]
    
    # Data parsing phase
    parsed_product: Optional[Dict[str, Any]]
    product: Optional[Product]  # Model instance
    data_parsed: bool
    
    # Content blocks phase
    content_blocks: Optional[Dict[str, Any]]
    content_blocks_generated: bool
    
    # Question generation phase
    questions: Optional[List[Dict[str, Any]]]
    questions_generated: bool
    question_count: int
    categories: Optional[List[str]]
    
    # FAQ generation phase
    faq_page: Optional[Dict[str, Any]]
    faq_generated: bool
    
    # Product page generation phase
    product_page: Optional[Dict[str, Any]]
    product_page_generated: bool
    
    # Comparison generation phase
    comparison_page: Optional[Dict[str, Any]]
    product_b_data: Optional[Dict[str, Any]]
    comparison_generated: bool
    
    # JSON output phase
    files_created: Optional[Dict[str, str]]
    output_directory: Optional[str]
    json_output_complete: bool
    
    # Error handling
    errors: List[str]

