"""
Colors Router - Color analysis and harmony utilities
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Tuple
import tempfile
import os

from app.models.clothing import ColorInfo
from app.services.color_service import color_extraction_service, color_harmony_service


router = APIRouter()


@router.post("/extract", response_model=List[ColorInfo])
async def extract_colors_from_image(
    image: UploadFile = File(...),
    num_colors: int = 5
):
    """
    Extract dominant colors from an uploaded image
    
    Uses K-means clustering ML algorithm for accurate color detection
    """
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        content = await image.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        colors = color_extraction_service.extract_colors(tmp_path, num_colors)
        return colors
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract colors: {str(e)}")
    finally:
        os.unlink(tmp_path)


@router.get("/harmony/{scheme}")
async def get_color_harmony(hex_color: str, scheme: str):
    """
    Get harmonious colors based on a color scheme
    
    Schemes:
    - complementary: Opposite on color wheel
    - analogous: Adjacent colors
    - triadic: Evenly spaced colors
    """
    # Parse hex color
    hex_color = hex_color.lstrip('#')
    try:
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid hex color")
    
    result = {
        "input_color": {
            "hex": f"#{hex_color}",
            "rgb": rgb
        },
        "scheme": scheme,
        "harmonious_colors": []
    }
    
    if scheme == "complementary":
        comp = color_harmony_service.get_complementary(rgb)
        result["harmonious_colors"] = [{
            "hex": color_extraction_service.rgb_to_hex(comp),
            "rgb": comp,
            "name": color_extraction_service.get_color_name(comp)
        }]
    elif scheme == "analogous":
        colors = color_harmony_service.get_analogous(rgb)
        result["harmonious_colors"] = [{
            "hex": color_extraction_service.rgb_to_hex(c),
            "rgb": c,
            "name": color_extraction_service.get_color_name(c)
        } for c in colors]
    elif scheme == "triadic":
        colors = color_harmony_service.get_triadic(rgb)
        result["harmonious_colors"] = [{
            "hex": color_extraction_service.rgb_to_hex(c),
            "rgb": c,
            "name": color_extraction_service.get_color_name(c)
        } for c in colors]
    else:
        raise HTTPException(
            status_code=400, 
            detail="Invalid scheme. Use: complementary, analogous, or triadic"
        )
    
    return result


@router.post("/harmony/score")
async def calculate_harmony_score(colors: List[str]):
    """
    Calculate color harmony score for a set of hex colors
    
    Returns a score from 0-100 indicating how well the colors work together
    """
    if len(colors) < 2:
        raise HTTPException(status_code=400, detail="At least 2 colors required")
    
    rgb_colors = []
    for hex_color in colors:
        hex_color = hex_color.lstrip('#')
        try:
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            rgb_colors.append(rgb)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid hex color: {hex_color}")
    
    score = color_harmony_service.calculate_harmony_score(rgb_colors)
    
    return {
        "colors": colors,
        "harmony_score": round(score, 2),
        "rating": (
            "Excellent" if score >= 80 else
            "Good" if score >= 60 else
            "Fair" if score >= 40 else
            "Poor"
        )
    }


@router.get("/schemes")
async def get_available_schemes():
    """Get all available color harmony schemes"""
    return {
        "schemes": [
            {
                "name": "complementary",
                "description": "Colors opposite on the color wheel. High contrast, vibrant look."
            },
            {
                "name": "analogous",
                "description": "Colors adjacent on the color wheel. Harmonious, cohesive look."
            },
            {
                "name": "triadic",
                "description": "Three colors evenly spaced on the color wheel. Balanced, colorful look."
            },
            {
                "name": "monochromatic",
                "description": "Different shades and tints of one color. Elegant, unified look."
            }
        ]
    }
