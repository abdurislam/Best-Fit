"""
Closet Router - Manage clothing items
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
import os
import uuid
import aiofiles

from app.models.clothing import (
    ClothingItem, 
    ClothingItemCreate, 
    ClothingItemUpdate,
    ClothingCategory,
    ClothingStyle
)
from app.services.storage_service import storage_service
from app.services.color_service import color_extraction_service


router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")


@router.get("/", response_model=List[ClothingItem])
async def get_all_clothing():
    """Get all clothing items in the closet"""
    return storage_service.get_all_clothing()


@router.get("/categories")
async def get_categories():
    """Get all available clothing categories"""
    return [{"value": cat.value, "label": cat.value.title()} for cat in ClothingCategory]


@router.get("/styles")
async def get_styles():
    """Get all available clothing styles"""
    return [{"value": style.value, "label": style.value.title()} for style in ClothingStyle]


@router.get("/category/{category}", response_model=List[ClothingItem])
async def get_clothing_by_category(category: ClothingCategory):
    """Get clothing items by category"""
    return storage_service.get_clothing_by_category(category)


@router.get("/style/{style}", response_model=List[ClothingItem])
async def get_clothing_by_style(style: ClothingStyle):
    """Get clothing items by style"""
    return storage_service.get_clothing_by_style(style)


@router.get("/{item_id}", response_model=ClothingItem)
async def get_clothing_item(item_id: str):
    """Get a specific clothing item by ID"""
    item = storage_service.get_clothing_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Clothing item not found")
    return item


@router.post("/", response_model=ClothingItem)
async def add_clothing_item(
    name: str = Form(...),
    category: ClothingCategory = Form(...),
    style: ClothingStyle = Form(...),
    tags: str = Form(""),
    image: UploadFile = File(...)
):
    """
    Add a new clothing item with image upload
    
    The image will be analyzed to extract dominant colors using ML-based color detection.
    """
    # Validate file type
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate unique filename
    file_extension = os.path.splitext(image.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save uploaded file
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    async with aiofiles.open(file_path, 'wb') as f:
        content = await image.read()
        await f.write(content)
    
    # Extract colors from the image
    try:
        dominant_colors = color_extraction_service.extract_colors(file_path, num_colors=5)
    except Exception as e:
        # Clean up file if color extraction fails
        os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to analyze image: {str(e)}")
    
    # Parse tags
    tag_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else []
    
    # Create clothing item
    item = ClothingItem(
        name=name,
        category=category,
        style=style,
        image_path=f"/uploads/{unique_filename}",
        dominant_colors=dominant_colors,
        tags=tag_list
    )
    
    return storage_service.add_clothing(item)


@router.put("/{item_id}", response_model=ClothingItem)
async def update_clothing_item(item_id: str, updates: ClothingItemUpdate):
    """Update a clothing item's metadata"""
    item = storage_service.update_clothing(item_id, updates.model_dump(exclude_unset=True))
    if not item:
        raise HTTPException(status_code=404, detail="Clothing item not found")
    return item


@router.delete("/{item_id}")
async def delete_clothing_item(item_id: str):
    """Delete a clothing item and its image"""
    item = storage_service.get_clothing_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Clothing item not found")
    
    # Delete the image file
    image_path = os.path.join(UPLOAD_DIR, os.path.basename(item.image_path))
    if os.path.exists(image_path):
        os.remove(image_path)
    
    storage_service.delete_clothing(item_id)
    return {"message": "Clothing item deleted successfully"}


@router.post("/{item_id}/reanalyze")
async def reanalyze_colors(item_id: str):
    """Re-analyze colors for an existing clothing item"""
    item = storage_service.get_clothing_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Clothing item not found")
    
    image_path = os.path.join(UPLOAD_DIR, os.path.basename(item.image_path))
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    
    try:
        dominant_colors = color_extraction_service.extract_colors(image_path, num_colors=5)
        updated_item = storage_service.update_clothing(
            item_id, 
            {"dominant_colors": [c.model_dump() for c in dominant_colors]}
        )
        return updated_item
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze image: {str(e)}")
