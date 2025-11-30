"""
Storage Service for managing clothing items and outfits

Using a simple JSON-based storage for simplicity.
Can be easily replaced with a database like SQLite, PostgreSQL, or MongoDB.
"""

import json
import os
from typing import List, Optional, Dict
from datetime import datetime

from app.models.clothing import ClothingItem, ClothingCategory, ClothingStyle
from app.models.outfit import Outfit


class StorageService:
    """JSON-based storage service for clothing items and outfits"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.clothing_file = os.path.join(data_dir, "clothing.json")
        self.outfits_file = os.path.join(data_dir, "outfits.json")
        
        # Initialize files if they don't exist
        if not os.path.exists(self.clothing_file):
            self._save_json(self.clothing_file, [])
        if not os.path.exists(self.outfits_file):
            self._save_json(self.outfits_file, [])
    
    def _load_json(self, filepath: str) -> List[Dict]:
        """Load data from JSON file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_json(self, filepath: str, data: List[Dict]):
        """Save data to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    # Clothing Item Operations
    def get_all_clothing(self) -> List[ClothingItem]:
        """Get all clothing items"""
        data = self._load_json(self.clothing_file)
        return [ClothingItem(**item) for item in data]
    
    def get_clothing_by_id(self, item_id: str) -> Optional[ClothingItem]:
        """Get a specific clothing item by ID"""
        data = self._load_json(self.clothing_file)
        for item in data:
            if item['id'] == item_id:
                return ClothingItem(**item)
        return None
    
    def get_clothing_by_category(self, category: ClothingCategory) -> List[ClothingItem]:
        """Get clothing items by category"""
        all_items = self.get_all_clothing()
        return [item for item in all_items if item.category == category]
    
    def get_clothing_by_style(self, style: ClothingStyle) -> List[ClothingItem]:
        """Get clothing items by style"""
        all_items = self.get_all_clothing()
        return [item for item in all_items if item.style == style]
    
    def add_clothing(self, item: ClothingItem) -> ClothingItem:
        """Add a new clothing item"""
        data = self._load_json(self.clothing_file)
        item_dict = item.model_dump()
        item_dict['created_at'] = item.created_at.isoformat()
        data.append(item_dict)
        self._save_json(self.clothing_file, data)
        return item
    
    def update_clothing(self, item_id: str, updates: Dict) -> Optional[ClothingItem]:
        """Update a clothing item"""
        data = self._load_json(self.clothing_file)
        for i, item in enumerate(data):
            if item['id'] == item_id:
                for key, value in updates.items():
                    if value is not None:
                        if hasattr(value, 'value'):
                            data[i][key] = value.value
                        else:
                            data[i][key] = value
                self._save_json(self.clothing_file, data)
                return ClothingItem(**data[i])
        return None
    
    def delete_clothing(self, item_id: str) -> bool:
        """Delete a clothing item"""
        data = self._load_json(self.clothing_file)
        original_len = len(data)
        data = [item for item in data if item['id'] != item_id]
        if len(data) < original_len:
            self._save_json(self.clothing_file, data)
            return True
        return False
    
    # Outfit Operations
    def get_all_outfits(self) -> List[Outfit]:
        """Get all outfits"""
        data = self._load_json(self.outfits_file)
        return [Outfit(**outfit) for outfit in data]
    
    def get_outfit_by_id(self, outfit_id: str) -> Optional[Outfit]:
        """Get a specific outfit by ID"""
        data = self._load_json(self.outfits_file)
        for outfit in data:
            if outfit['id'] == outfit_id:
                return Outfit(**outfit)
        return None
    
    def add_outfit(self, outfit: Outfit) -> Outfit:
        """Add a new outfit"""
        data = self._load_json(self.outfits_file)
        outfit_dict = outfit.model_dump()
        outfit_dict['created_at'] = outfit.created_at.isoformat()
        data.append(outfit_dict)
        self._save_json(self.outfits_file, data)
        return outfit
    
    def delete_outfit(self, outfit_id: str) -> bool:
        """Delete an outfit"""
        data = self._load_json(self.outfits_file)
        original_len = len(data)
        data = [outfit for outfit in data if outfit['id'] != outfit_id]
        if len(data) < original_len:
            self._save_json(self.outfits_file, data)
            return True
        return False


# Singleton instance
storage_service = StorageService()
