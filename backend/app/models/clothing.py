from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime
import uuid


class ClothingCategory(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"
    DRESS = "dress"
    OUTERWEAR = "outerwear"
    SHOES = "shoes"
    ACCESSORY = "accessory"


class ClothingStyle(str, Enum):
    CASUAL = "casual"
    FORMAL = "formal"
    SPORTY = "sporty"
    BUSINESS = "business"
    EVENING = "evening"
    BOHEMIAN = "bohemian"
    STREETWEAR = "streetwear"
    VINTAGE = "vintage"


class ColorInfo(BaseModel):
    hex: str = Field(..., description="Hex color code")
    rgb: tuple[int, int, int] = Field(..., description="RGB values")
    name: str = Field(..., description="Human-readable color name")
    percentage: float = Field(..., description="Percentage of this color in the image")


class ClothingItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Name of the clothing item")
    category: ClothingCategory
    style: ClothingStyle
    image_path: str = Field(..., description="Path to the uploaded image")
    dominant_colors: List[ColorInfo] = Field(default=[], description="Extracted dominant colors")
    tags: List[str] = Field(default=[], description="Custom tags for the item")
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ClothingItemCreate(BaseModel):
    name: str
    category: ClothingCategory
    style: ClothingStyle
    tags: List[str] = []


class ClothingItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[ClothingCategory] = None
    style: Optional[ClothingStyle] = None
    tags: Optional[List[str]] = None
