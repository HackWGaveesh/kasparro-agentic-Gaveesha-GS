"""
Safety Content Block - Reusable logic for generating safety information.
"""
from typing import Dict, Any, List


def generate_safety_content(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate safety content from product data.
    Reusable content logic block.
    
    Args:
        product_data: Product data dictionary
        
    Returns:
        Structured safety content
    """
    side_effects = product_data.get("side_effects", "")
    skin_type = product_data.get("skin_type", [])
    concentration = product_data.get("concentration", "")
    
    # Content logic: Structure safety information
    safety_content = {
        "side_effects": side_effects,
        "safety_notes": [],
        "warnings": [],
        "contraindications": [],
        "patch_test_recommended": True
    }
    
    # Generate safety notes based on actual data (no hardcoded values)
    side_effects_lower = side_effects.lower() if side_effects else ""
    concentration_lower = concentration.lower() if concentration else ""
    
    # Safety notes from side effects
    if "tingling" in side_effects_lower:
        safety_content["safety_notes"].append(
            f"Mild tingling may occur as mentioned: {side_effects}"
        )
        safety_content["warnings"].append(
            "Discontinue use if severe irritation or persistent discomfort occurs"
        )
    
    if "irritat" in side_effects_lower:
        safety_content["warnings"].append(
            "May cause irritation - use with caution"
        )
    
    # Safety notes from concentration
    import re
    conc_match = re.search(r'(\d+)%', concentration)
    if conc_match:
        conc_value = int(conc_match.group(1))
        if conc_value >= 10:
            safety_content["safety_notes"].append(
                f"{conc_value}% concentration - start with patch test"
            )
            safety_content["warnings"].append(
                "Begin with lower frequency if you have sensitive skin"
            )
        elif conc_value >= 5:
            safety_content["safety_notes"].append(
                f"{conc_value}% concentration is generally well-tolerated"
            )
    
    # Warnings based on product data
    if side_effects:
        safety_content["warnings"].append("Follow product instructions and discontinue if adverse reactions occur")
    
    # Contraindications based on skin type data
    skin_type_str = str(skin_type).lower()
    if "sensitive" not in skin_type_str:
        safety_content["contraindications"].append(
            "May cause irritation for very sensitive skin types not listed in product specifications"
        )
    
    return safety_content


def format_safety_for_display(safety_content: Dict[str, Any]) -> str:
    """
    Format safety content for display.
    
    Args:
        safety_content: Safety content dictionary
        
    Returns:
        Formatted safety text
    """
    formatted = []
    
    if safety_content.get("side_effects"):
        formatted.append(f"Side Effects: {safety_content['side_effects']}")
    
    if safety_content.get("safety_notes"):
        formatted.append("\nSafety Notes:")
        for note in safety_content["safety_notes"]:
            formatted.append(f"• {note}")
    
    if safety_content.get("warnings"):
        formatted.append("\nWarnings:")
        for warning in safety_content["warnings"]:
            formatted.append(f"⚠ {warning}")
    
    return "\n".join(formatted)

