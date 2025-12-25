"""
Main entry point for Product Content Generation System.
Runs the complete workflow to generate FAQ, Product, and Comparison pages.
"""
import os
import json
import sys
import io
from dotenv import load_dotenv
from workflow.product_workflow import ProductContentWorkflow

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Load product data
PRODUCT_DATA = {
    "product_name": "GlowBoost Vitamin C Serum",
    "concentration": "10% Vitamin C",
    "skin_type": ["Oily", "Combination"],
    "key_ingredients": ["Vitamin C", "Hyaluronic Acid"],
    "benefits": ["Brightening", "Fades dark spots"],
    "how_to_use": "Apply 2–3 drops in the morning before sunscreen",
    "side_effects": "Mild tingling for sensitive skin",
    "price": "₹699"
}


def main():
    """Main function to run the product content generation system."""
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("\n" + "="*70)
        print("ERROR: OPENROUTER_API_KEY not found")
        print("="*70)
        print("\nPlease create a .env file in the project root with:")
        print("OPENROUTER_API_KEY=your-api-key-here")
        print("\nOr set it as an environment variable:")
        print("export OPENROUTER_API_KEY=your-api-key-here")
        print("\nSee README.md for setup instructions.")
        print("="*70)
        return
    
    print("\n" + "="*70)
    print("PRODUCT CONTENT GENERATION SYSTEM")
    print("="*70)
    print(f"\nProduct: {PRODUCT_DATA['product_name']}")
    # Handle Unicode characters for Windows console
    try:
        print(f"Price: {PRODUCT_DATA['price']}")
    except UnicodeEncodeError:
        price_safe = PRODUCT_DATA['price'].encode('ascii', 'replace').decode('ascii')
        print(f"Price: {price_safe}")
    print("\nGenerating content pages...")
    print("-" * 70)
    
    try:
        # Initialize workflow
        workflow = ProductContentWorkflow()
        
        # Run the workflow
        final_state = workflow.run(PRODUCT_DATA)
        
        # Display results
        print("\n" + "="*70)
        print("CONTENT GENERATION COMPLETE")
        print("="*70)
        
        if final_state.get("errors"):
            print(f"\n⚠️  Errors: {final_state['errors']}")
        
        if final_state.get("faq_generated"):
            print(f"\n✅ FAQ Page Generated")
            print(f"   Questions: {final_state.get('question_count', 0)}")
            print(f"   Categories: {', '.join(final_state.get('categories', []))}")
        
        if final_state.get("product_page_generated"):
            print(f"\n✅ Product Description Page Generated")
        
        if final_state.get("comparison_generated"):
            print(f"\n✅ Comparison Page Generated")
            if final_state.get("product_b_data"):
                print(f"   Compared with: {final_state['product_b_data'].get('product_name', 'N/A')}")
        
        if final_state.get("json_output_complete"):
            print(f"\n✅ JSON Files Created")
            files = final_state.get("files_created", {})
            for page_type, file_path in files.items():
                print(f"   {page_type}: {file_path}")
            
            # Display sample content
            print("\n" + "="*70)
            print("SAMPLE OUTPUT")
            print("="*70)
            
            if final_state.get("faq_page"):
                print("\n📋 FAQ Page Sample:")
                faq = final_state["faq_page"]
                print(f"   Total Q&As: {faq.get('total_questions', 0)}")
                if faq.get("faq_items"):
                    print(f"   First Question: {faq['faq_items'][0].get('question', 'N/A')[:60]}...")
            
            if final_state.get("product_page"):
                print("\n📄 Product Page Sample:")
                product = final_state["product_page"]
                print(f"   Product: {product.get('product_name', 'N/A')}")
                print(f"   Price: {product.get('price', 'N/A')}")
                print(f"   Sections: {len(product.get('sections', {}))}")
            
            if final_state.get("comparison_page"):
                print("\n⚖️  Comparison Page Sample:")
                comparison = final_state["comparison_page"]
                products = comparison.get("products", {})
                if products.get("product1") and products.get("product2"):
                    print(f"   {products['product1'].get('name', 'N/A')} vs {products['product2'].get('name', 'N/A')}")
        
        print("\n" + "="*70)
        print("Workflow completed successfully!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error during workflow execution: {str(e)}")
        
        # Check for OpenRouter privacy settings error
        error_str = str(e)
        if "404" in error_str and "data policy" in error_str.lower():
            print("\n" + "="*70)
            print("⚠️  OPENROUTER PRIVACY SETTINGS REQUIRED")
            print("="*70)
            print("\nYou need to enable 'Free model publication' in OpenRouter settings.")
            print("Visit: https://openrouter.ai/settings/privacy")
            print("\nSteps:")
            print("1. Log in to OpenRouter")
            print("2. Go to Settings > Privacy")
            print("3. Enable 'Free model publication'")
            print("4. Save settings")
            print("5. Try running again")
            print("\nSee OPENROUTER_PRIVACY_FIX.md for detailed instructions.")
            print("="*70)
        
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

