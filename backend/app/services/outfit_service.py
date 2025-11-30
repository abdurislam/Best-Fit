"""
Outfit Generation Service

Uses color harmony analysis and style matching to suggest outfits
"""

from typing import List, Optional, Tuple
from itertools import combinations

from app.models.clothing import ClothingItem, ClothingCategory, ClothingStyle, ColorInfo
from app.models.outfit import Outfit, OutfitItem
from app.services.color_service import color_harmony_service, ColorHarmonyService
from app.services.storage_service import storage_service


class OutfitGeneratorService:
    """Service for generating outfit suggestions based on color and style matching"""
    
    # Define which categories can be combined
    OUTFIT_COMBINATIONS = [
        [ClothingCategory.TOP, ClothingCategory.BOTTOM],
        [ClothingCategory.TOP, ClothingCategory.BOTTOM, ClothingCategory.SHOES],
        [ClothingCategory.TOP, ClothingCategory.BOTTOM, ClothingCategory.OUTERWEAR],
        [ClothingCategory.TOP, ClothingCategory.BOTTOM, ClothingCategory.OUTERWEAR, ClothingCategory.SHOES],
        [ClothingCategory.DRESS],
        [ClothingCategory.DRESS, ClothingCategory.SHOES],
        [ClothingCategory.DRESS, ClothingCategory.OUTERWEAR],
        [ClothingCategory.DRESS, ClothingCategory.OUTERWEAR, ClothingCategory.SHOES],
    ]
    
    def __init__(self):
        self.storage = storage_service
        self.color_harmony = color_harmony_service
    
    def get_dominant_rgb(self, item: ClothingItem) -> Optional[Tuple[int, int, int]]:
        """Get the most dominant color RGB from a clothing item"""
        if not item.dominant_colors:
            return None
        return item.dominant_colors[0].rgb
    
    def calculate_outfit_harmony(self, items: List[ClothingItem]) -> float:
        """Calculate the color harmony score for a set of items"""
        colors = []
        for item in items:
            rgb = self.get_dominant_rgb(item)
            if rgb:
                colors.append(rgb)
        
        if len(colors) < 2:
            return 100.0
        
        return self.color_harmony.calculate_harmony_score(colors)
    
    def check_style_compatibility(self, items: List[ClothingItem]) -> float:
        """Check if items have compatible styles (returns score 0-100)"""
        if not items:
            return 0.0
        
        styles = [item.style for item in items]
        
        # All same style = perfect score
        if len(set(styles)) == 1:
            return 100.0
        
        # Compatible style pairs
        compatible_pairs = [
            (ClothingStyle.CASUAL, ClothingStyle.STREETWEAR),
            (ClothingStyle.FORMAL, ClothingStyle.BUSINESS),
            (ClothingStyle.EVENING, ClothingStyle.FORMAL),
            (ClothingStyle.BOHEMIAN, ClothingStyle.CASUAL),
            (ClothingStyle.SPORTY, ClothingStyle.CASUAL),
            (ClothingStyle.VINTAGE, ClothingStyle.BOHEMIAN),
        ]
        
        score = 50.0  # Base score for mixed styles
        
        for s1, s2 in zip(styles, styles[1:]):
            if s1 == s2:
                score += 10
            elif (s1, s2) in compatible_pairs or (s2, s1) in compatible_pairs:
                score += 5
            else:
                score -= 10
        
        return max(0, min(100, score))
    
    def _convert_items_from_request(self, items_data: List[dict]) -> List[ClothingItem]:
        """Convert items from frontend request format to ClothingItem objects"""
        converted_items = []
        for item in items_data:
            colors = []
            for c in item.get('dominant_colors', []):
                colors.append(ColorInfo(
                    hex=c.get('hex', '#000000'),
                    rgb=tuple(c.get('rgb', [0, 0, 0])),
                    name=c.get('name', 'unknown'),
                    percentage=c.get('percentage', 0)
                ))
            
            converted_items.append(ClothingItem(
                id=item.get('id', ''),
                name=item.get('name', ''),
                category=ClothingCategory(item.get('category', 'top')),
                style=ClothingStyle(item.get('style', 'casual')),
                image_path=item.get('image_path', item.get('imageUrl', '')),
                dominant_colors=colors,
                tags=item.get('tags', [])
            ))
        return converted_items
    
    def generate_outfit_suggestions(
        self,
        items: Optional[List[dict]] = None,
        base_item_id: Optional[str] = None,
        style: Optional[ClothingStyle] = None,
        color_scheme: Optional[str] = None,
        max_suggestions: int = 5
    ) -> List[dict]:
        """
        Generate outfit suggestions based on criteria
        
        Args:
            items: List of clothing items from frontend (Firestore data)
            base_item_id: ID of item to build outfit around
            style: Preferred style filter
            color_scheme: Color harmony scheme (complementary, analogous, triadic, monochromatic)
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of outfit suggestions with scores
        """
        # Use items from request if provided, otherwise fall back to local storage
        if items:
            all_items = self._convert_items_from_request(items)
        else:
            all_items = self.storage.get_all_clothing()
        
        if not all_items:
            return []
        
        # Filter by style if specified
        if style:
            filtered_items = [item for item in all_items if item.style == style]
            if filtered_items:
                all_items = filtered_items
        
        # Group items by category
        items_by_category = {}
        for item in all_items:
            if item.category not in items_by_category:
                items_by_category[item.category] = []
            items_by_category[item.category].append(item)
        
        suggestions = []
        
        # If we have a base item, build around it
        if base_item_id:
            base_item = next((item for item in all_items if item.id == base_item_id), None)
            if base_item:
                suggestions = self._generate_from_base(
                    base_item, items_by_category, color_scheme
                )
        else:
            # Generate all valid combinations
            suggestions = self._generate_all_combinations(
                items_by_category, color_scheme
            )
        
        # Sort by combined score (color harmony + style compatibility)
        suggestions.sort(key=lambda x: x['total_score'], reverse=True)
        
        return suggestions[:max_suggestions]
    
    def _generate_from_base(
        self,
        base_item: ClothingItem,
        items_by_category: dict,
        color_scheme: Optional[str]
    ) -> List[dict]:
        """Generate outfits starting from a base item"""
        suggestions = []
        base_rgb = self.get_dominant_rgb(base_item)
        
        # Find valid outfit patterns that include this category
        valid_patterns = [
            pattern for pattern in self.OUTFIT_COMBINATIONS
            if base_item.category in pattern
        ]
        
        for pattern in valid_patterns:
            other_categories = [c for c in pattern if c != base_item.category]
            
            # Generate combinations for other categories
            category_options = []
            for cat in other_categories:
                if cat in items_by_category:
                    options = items_by_category[cat]
                    
                    # Filter by color scheme if specified
                    if color_scheme and base_rgb:
                        filtered = []
                        for item in options:
                            item_rgb = self.get_dominant_rgb(item)
                            if item_rgb and self.color_harmony.colors_match(
                                base_rgb, item_rgb, color_scheme
                            ):
                                filtered.append(item)
                        if filtered:
                            options = filtered
                    
                    category_options.append(options)
            
            if len(category_options) == len(other_categories):
                # Generate all combinations
                from itertools import product
                for combo in product(*category_options):
                    outfit_items = [base_item] + list(combo)
                    
                    harmony_score = self.calculate_outfit_harmony(outfit_items)
                    style_score = self.check_style_compatibility(outfit_items)
                    total_score = (harmony_score * 0.6) + (style_score * 0.4)
                    
                    suggestions.append({
                        'items': [item.model_dump() for item in outfit_items],
                        'color_harmony_score': round(harmony_score, 2),
                        'style_compatibility_score': round(style_score, 2),
                        'total_score': round(total_score, 2),
                        'pattern': [cat.value for cat in pattern]
                    })
        
        return suggestions
    
    def _generate_all_combinations(
        self,
        items_by_category: dict,
        color_scheme: Optional[str]
    ) -> List[dict]:
        """Generate all valid outfit combinations"""
        suggestions = []
        
        for pattern in self.OUTFIT_COMBINATIONS:
            # Check if we have items for all categories in this pattern
            if all(cat in items_by_category for cat in pattern):
                category_options = [items_by_category[cat] for cat in pattern]
                
                from itertools import product
                for combo in product(*category_options):
                    outfit_items = list(combo)
                    
                    # Apply color scheme filter if specified
                    if color_scheme:
                        colors = [self.get_dominant_rgb(item) for item in outfit_items]
                        colors = [c for c in colors if c]
                        
                        if len(colors) >= 2:
                            # Check if first two colors match the scheme
                            if not self.color_harmony.colors_match(
                                colors[0], colors[1], color_scheme
                            ):
                                continue
                    
                    harmony_score = self.calculate_outfit_harmony(outfit_items)
                    style_score = self.check_style_compatibility(outfit_items)
                    total_score = (harmony_score * 0.6) + (style_score * 0.4)
                    
                    suggestions.append({
                        'items': [item.model_dump() for item in outfit_items],
                        'color_harmony_score': round(harmony_score, 2),
                        'style_compatibility_score': round(style_score, 2),
                        'total_score': round(total_score, 2),
                        'pattern': [cat.value for cat in pattern]
                    })
        
        return suggestions


# Singleton instance
outfit_generator_service = OutfitGeneratorService()
