"""
Outfits Router - Manage outfits and get suggestions
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional

from app.models.outfit import Outfit, OutfitCreate, OutfitItem, OutfitSuggestionRequest
from app.models.clothing import ClothingStyle
from app.services.storage_service import storage_service
from app.services.outfit_service import outfit_generator_service


router = APIRouter()


@router.get("/", response_model=List[Outfit])
async def get_all_outfits():
    """Get all saved outfits"""
    return storage_service.get_all_outfits()


@router.get("/{outfit_id}", response_model=Outfit)
async def get_outfit(outfit_id: str):
    """Get a specific outfit by ID"""
    outfit = storage_service.get_outfit_by_id(outfit_id)
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    return outfit


@router.post("/", response_model=Outfit)
async def create_outfit(outfit_data: OutfitCreate):
    """Create a new outfit from clothing items"""
    # Validate that all clothing items exist
    items = []
    for i, clothing_id in enumerate(outfit_data.clothing_ids):
        item = storage_service.get_clothing_by_id(clothing_id)
        if not item:
            raise HTTPException(
                status_code=404, 
                detail=f"Clothing item {clothing_id} not found"
            )
        items.append(item)
    
    # Calculate color harmony score
    harmony_score = outfit_generator_service.calculate_outfit_harmony(items)
    
    # Create outfit items with positions
    outfit_items = [
        OutfitItem(clothing_id=cid, position=i)
        for i, cid in enumerate(outfit_data.clothing_ids)
    ]
    
    outfit = Outfit(
        name=outfit_data.name,
        items=outfit_items,
        style=outfit_data.style,
        occasion=outfit_data.occasion,
        color_harmony_score=harmony_score
    )
    
    return storage_service.add_outfit(outfit)


@router.delete("/{outfit_id}")
async def delete_outfit(outfit_id: str):
    """Delete an outfit"""
    if not storage_service.delete_outfit(outfit_id):
        raise HTTPException(status_code=404, detail="Outfit not found")
    return {"message": "Outfit deleted successfully"}


@router.post("/suggest")
async def get_outfit_suggestions(request: OutfitSuggestionRequest):
    """
    Get outfit suggestions based on criteria
    
    - items: List of clothing items from frontend (used when data is in Firestore)
    - base_item_id: Build outfit around a specific item
    - style: Filter by clothing style
    - color_scheme: Use specific color harmony (complementary, analogous, triadic, monochromatic)
    - max_suggestions: Maximum number of suggestions to return
    """
    try:
        suggestions = outfit_generator_service.generate_outfit_suggestions(
            items=request.items,
            base_item_id=request.base_item_id,
            style=request.style,
            color_scheme=request.color_scheme,
            max_suggestions=request.max_suggestions
        )
        
        return {
            "count": len(suggestions),
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate suggestions: {str(e)}")


@router.get("/suggest/for/{item_id}")
async def get_suggestions_for_item(
    item_id: str,
    style: Optional[ClothingStyle] = None,
    color_scheme: Optional[str] = None,
    max_suggestions: int = 5
):
    """Get outfit suggestions that include a specific clothing item"""
    item = storage_service.get_clothing_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Clothing item not found")
    
    suggestions = outfit_generator_service.generate_outfit_suggestions(
        base_item_id=item_id,
        style=style,
        color_scheme=color_scheme,
        max_suggestions=max_suggestions
    )
    
    return {
        "base_item": item.model_dump(),
        "count": len(suggestions),
        "suggestions": suggestions
    }
