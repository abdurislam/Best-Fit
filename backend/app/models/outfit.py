from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

from app.models.clothing import ClothingStyle


class OutfitItem(BaseModel):
    clothing_id: str
    position: int = Field(..., description="Order in the outfit display")


class Outfit(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Name of the outfit")
    items: List[OutfitItem] = Field(default=[], description="Clothing items in this outfit")
    style: ClothingStyle
    occasion: Optional[str] = None
    color_harmony_score: float = Field(default=0.0, description="Color harmony score 0-100")
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OutfitCreate(BaseModel):
    name: str
    clothing_ids: List[str]
    style: ClothingStyle
    occasion: Optional[str] = None


class OutfitSuggestionRequest(BaseModel):
    items: Optional[List[dict]] = Field(None, description="Clothing items to use for suggestions")
    base_item_id: Optional[str] = None
    style: Optional[ClothingStyle] = None
    color_scheme: Optional[str] = Field(None, description="complementary, analogous, triadic, monochromatic")
    max_suggestions: int = Field(default=5, ge=1, le=20)
