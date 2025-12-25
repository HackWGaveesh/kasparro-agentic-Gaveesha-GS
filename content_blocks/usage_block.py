"""
Usage Content Block - Reusable logic for generating usage instructions.
"""
from typing import Dict, Any, List


def generate_usage_content(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate usage content from product data.
    Reusable content logic block.
    
    Args:
        product_data: Product data dictionary
        
    Returns:
        Structured usage content
    """
    how_to_use = product_data.get("how_to_use", "")
    skin_type = product_data.get("skin_type", [])
    concentration = product_data.get("concentration", "")
    
    # Content logic: Structure usage information
    usage_content = {
        "instructions": how_to_use,
        "steps": _extract_steps(how_to_use),
        "frequency": _determine_frequency(how_to_use),
        "best_for_skin_types": skin_type,
        "application_tips": _generate_tips(concentration, skin_type),
        "precautions": _generate_precautions(product_data.get("side_effects", ""))
    }
    
    return usage_content


def _extract_steps(instructions: str) -> List[str]:
    """Extract step-by-step instructions from the provided instructions text."""
    # Parse instructions dynamically - no hardcoded steps
    steps = []
    
    # Split by common separators (periods, commas, "and", "then")
    import re
    # Split by sentence boundaries or common connectors
    parts = re.split(r'[.,;]\s+|and\s+|then\s+', instructions)
    
    for part in parts:
        part = part.strip()
        if part and len(part) > 5:  # Only meaningful steps
            # Capitalize first letter
            if part[0].islower():
                part = part[0].upper() + part[1:]
            steps.append(part)
    
    # If no steps extracted, use the full instruction as a single step
    return steps if steps else [instructions]


def _determine_frequency(instructions: str) -> str:
    """Determine usage frequency from instructions dynamically."""
    instructions_lower = instructions.lower()
    
    # Extract frequency information from instructions
    if "morning" in instructions_lower:
        return "Daily (morning)"
    elif "night" in instructions_lower or "evening" in instructions_lower:
        return "Daily (night)"
    elif "twice" in instructions_lower or "2 times" in instructions_lower:
        return "Twice daily"
    elif "once" in instructions_lower or "daily" in instructions_lower:
        return "Daily"
    else:
        # Extract from instructions - use the actual instruction text
        return instructions if len(instructions) < 50 else "As directed"


def _generate_tips(concentration: str, skin_types: List[str]) -> List[str]:
    """Generate application tips based on product properties dynamically."""
    tips = []
    
    # Generate tips based on concentration level (if numeric)
    import re
    conc_match = re.search(r'(\d+)%', concentration)
    if conc_match:
        conc_value = int(conc_match.group(1))
        if conc_value >= 10:
            tips.append(f"Start with a patch test due to {conc_value}% concentration")
            tips.append("Begin with every other day, then increase frequency gradually")
        elif conc_value >= 5:
            tips.append("Suitable for regular use")
    
    # Generate tips based on skin types
    if skin_types:
        skin_types_str = ", ".join(skin_types)
        if "Oily" in skin_types or "Combination" in skin_types:
            tips.append(f"Apply to clean, dry skin for best absorption ({skin_types_str} skin)")
        if "Sensitive" in skin_types:
            tips.append("Perform patch test before first use (sensitive skin)")
    
    # General tip based on product type (serum, cream, etc.)
    if "serum" in concentration.lower() or "serum" in str(skin_types).lower():
        tips.append("Allow product to absorb before applying other products")
    
    return tips


def _generate_precautions(side_effects: str) -> List[str]:
    """Generate precautions from side effects dynamically."""
    precautions = []
    
    side_effects_lower = side_effects.lower() if side_effects else ""
    
    # Generate precautions based on actual side effects mentioned
    if "tingling" in side_effects_lower:
        precautions.append("Mild tingling may occur, especially for sensitive skin")
        precautions.append("Discontinue use if irritation persists or worsens")
    
    if "irritat" in side_effects_lower or "sensitive" in side_effects_lower:
        precautions.append("Perform patch test before first use")
        precautions.append("Reduce frequency if irritation occurs")
    
    if "dry" in side_effects_lower:
        precautions.append("May cause dryness - use moisturizer as needed")
    
    # General safety precautions (based on product type, not hardcoded)
    if side_effects:
        precautions.append("Follow usage instructions carefully")
        precautions.append("Discontinue if adverse reactions occur")
    
    return precautions


def format_usage_for_display(usage_content: Dict[str, Any]) -> str:
    """
    Format usage content for display.
    
    Args:
        usage_content: Usage content dictionary
        
    Returns:
        Formatted usage text
    """
    formatted = []
    formatted.append(f"How to Use: {usage_content['instructions']}")
    formatted.append(f"Frequency: {usage_content['frequency']}")
    
    if usage_content.get("steps"):
        formatted.append("\nSteps:")
        for i, step in enumerate(usage_content["steps"], 1):
            formatted.append(f"{i}. {step}")
    
    if usage_content.get("application_tips"):
        formatted.append("\nTips:")
        for tip in usage_content["application_tips"]:
            formatted.append(f"• {tip}")
    
    return "\n".join(formatted)

