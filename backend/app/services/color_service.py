"""
Color Extraction Service using ML-based approach

This service uses a combination of:
1. rembg for AI-based background removal
2. ColorThief library for dominant color extraction (K-means clustering)
3. Custom color naming using webcolors and color distance algorithms
4. Color harmony analysis for outfit matching

Why ML Model over Local LLM:
- Color extraction is a well-defined computer vision task
- K-means clustering is efficient, fast, and lightweight
- No need for GPU or significant RAM
- More accurate for specific color values than LLM descriptions
- Works offline without Ollama dependency
"""

from PIL import Image
from colorthief import ColorThief
import webcolors
import numpy as np
from typing import List, Tuple, Optional
from io import BytesIO
import math
import colorsys
import tempfile
import os

# Try to import rembg for background removal (optional - can be slow)
# Set to False to disable AI background removal and use simpler filtering
USE_REMBG = False  # Disabled by default for faster processing

try:
    if USE_REMBG:
        from rembg import remove as remove_background
        REMBG_AVAILABLE = True
    else:
        REMBG_AVAILABLE = False
except ImportError:
    REMBG_AVAILABLE = False

from app.models.clothing import ColorInfo


class ColorExtractionService:
    """ML-based color extraction service using K-means clustering"""
    
    # Extended color name mapping for better accuracy
    EXTENDED_COLORS = {
        (0, 0, 0): "black",
        (255, 255, 255): "white",
        (128, 128, 128): "gray",
        (192, 192, 192): "silver",
        (255, 0, 0): "red",
        (128, 0, 0): "maroon",
        (255, 165, 0): "orange",
        (255, 215, 0): "gold",
        (255, 255, 0): "yellow",
        (128, 128, 0): "olive",
        (0, 255, 0): "lime",
        (0, 128, 0): "green",
        (0, 255, 255): "cyan",
        (0, 128, 128): "teal",
        (0, 0, 255): "blue",
        (0, 0, 128): "navy",
        (255, 0, 255): "magenta",
        (128, 0, 128): "purple",
        (255, 192, 203): "pink",
        (165, 42, 42): "brown",
        (245, 245, 220): "beige",
        (210, 180, 140): "tan",
        (255, 127, 80): "coral",
        (75, 0, 130): "indigo",
        (230, 230, 250): "lavender",
        (245, 245, 245): "off-white",
        (47, 79, 79): "dark slate",
        (70, 130, 180): "steel blue",
        (178, 34, 34): "firebrick",
        (220, 20, 60): "crimson",
        (255, 99, 71): "tomato",
        (250, 128, 114): "salmon",
        (255, 218, 185): "peach",
        (240, 230, 140): "khaki",
        (189, 183, 107): "dark khaki",
        (144, 238, 144): "light green",
        (34, 139, 34): "forest green",
        (0, 100, 0): "dark green",
        (143, 188, 143): "dark sea green",
        (135, 206, 235): "sky blue",
        (173, 216, 230): "light blue",
        (100, 149, 237): "cornflower blue",
        (65, 105, 225): "royal blue",
        (25, 25, 112): "midnight blue",
        (138, 43, 226): "blue violet",
        (148, 0, 211): "dark violet",
        (218, 112, 214): "orchid",
        (255, 20, 147): "deep pink",
        (199, 21, 133): "medium violet red",
        (139, 69, 19): "saddle brown",
        (160, 82, 45): "sienna",
        (210, 105, 30): "chocolate",
        (205, 133, 63): "peru",
        (244, 164, 96): "sandy brown",
        (222, 184, 135): "burlywood",
        (112, 128, 144): "slate gray",
        (119, 136, 153): "light slate gray",
        (105, 105, 105): "dim gray",
        (169, 169, 169): "dark gray",
        (211, 211, 211): "light gray",
    }
    
    def __init__(self):
        self.color_cache = {}
    
    def rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex string"""
        return "#{:02x}{:02x}{:02x}".format(*rgb)
    
    def color_distance(self, c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> float:
        """
        Calculate color distance using weighted Euclidean distance in RGB space
        Weights account for human perception of color differences
        """
        r1, g1, b1 = c1
        r2, g2, b2 = c2
        
        # Weighted RGB distance (human eye is more sensitive to green)
        rmean = (r1 + r2) / 2
        dr = r1 - r2
        dg = g1 - g2
        db = b1 - b2
        
        return math.sqrt(
            (2 + rmean / 256) * dr ** 2 +
            4 * dg ** 2 +
            (2 + (255 - rmean) / 256) * db ** 2
        )
    
    def get_color_name(self, rgb: Tuple[int, int, int]) -> str:
        """Get the closest color name for an RGB value"""
        # Check cache first
        if rgb in self.color_cache:
            return self.color_cache[rgb]
        
        # Try exact match with webcolors
        try:
            name = webcolors.rgb_to_name(rgb)
            self.color_cache[rgb] = name
            return name
        except ValueError:
            pass
        
        # Find closest color in extended colors
        min_distance = float('inf')
        closest_name = "unknown"
        
        for color_rgb, name in self.EXTENDED_COLORS.items():
            distance = self.color_distance(rgb, color_rgb)
            if distance < min_distance:
                min_distance = distance
                closest_name = name
        
        self.color_cache[rgb] = closest_name
        return closest_name
    
    def _is_background_color(self, rgb: Tuple[int, int, int], threshold: int = 240) -> bool:
        """Check if a color is likely a background color (white, near-white, or very light)"""
        r, g, b = rgb
        # Check for white/near-white
        if r > threshold and g > threshold and b > threshold:
            return True
        # Check for pure black (sometimes used as background)
        if r < 15 and g < 15 and b < 15:
            return True
        # Check for very light gray
        if r > 230 and g > 230 and b > 230:
            return True
        return False

    def _remove_background(self, image_path: str) -> Optional[Image.Image]:
        """Remove background from image using rembg AI model"""
        if not REMBG_AVAILABLE:
            return None
            
        try:
            img = Image.open(image_path)
            # Use AI-based background removal
            img_no_bg = remove_background(img)
            return img_no_bg
        except Exception as e:
            print(f"Warning: Background removal failed: {e}")
            return None

    def _get_non_transparent_pixels(self, img: Image.Image) -> List[Tuple[int, int, int]]:
        """Get only non-transparent and non-background pixels from an RGBA image"""
        img = img.convert('RGBA')
        pixels = list(img.getdata())
        
        valid_pixels = []
        for pixel in pixels:
            r, g, b, a = pixel
            # Skip transparent pixels
            if a < 128:
                continue
            # Skip background colors
            if self._is_background_color((r, g, b)):
                continue
            valid_pixels.append((r, g, b))
        
        return valid_pixels
    
    def _filter_background_from_image(self, image_path: str) -> List[Tuple[int, int, int]]:
        """Filter out background colors from image without AI removal"""
        img = Image.open(image_path)
        img = img.convert('RGBA')
        img = img.resize((150, 150))  # Resize for faster processing
        
        pixels = list(img.getdata())
        valid_pixels = []
        
        for pixel in pixels:
            if len(pixel) == 4:
                r, g, b, a = pixel
                if a < 128:  # Skip transparent
                    continue
            else:
                r, g, b = pixel
            
            # Skip background colors
            if not self._is_background_color((r, g, b)):
                valid_pixels.append((r, g, b))
        
        return valid_pixels

    def extract_colors(self, image_path: str, num_colors: int = 5) -> List[ColorInfo]:
        """
        Extract dominant colors from an image using K-means clustering
        
        Args:
            image_path: Path to the image file
            num_colors: Number of dominant colors to extract
            
        Returns:
            List of ColorInfo objects with color details
        """
        try:
            valid_pixels = []
            
            # Step 1: Try AI background removal if available
            if REMBG_AVAILABLE:
                img_no_bg = self._remove_background(image_path)
                if img_no_bg:
                    valid_pixels = self._get_non_transparent_pixels(img_no_bg)
            
            # Step 2: Fallback - just filter background colors without AI
            if len(valid_pixels) < 100:
                valid_pixels = self._filter_background_from_image(image_path)
            
            # Step 3: If still not enough pixels, use original image
            if len(valid_pixels) < 100:
                color_thief = ColorThief(image_path)
                palette = color_thief.get_palette(color_count=num_colors, quality=1)
            else:
                # Create a new image from valid pixels for ColorThief
                size = int(math.sqrt(len(valid_pixels)))
                if size < 10:
                    size = 10
                
                # Pad or truncate pixels to fit
                needed_pixels = size * size
                if len(valid_pixels) > needed_pixels:
                    valid_pixels = valid_pixels[:needed_pixels]
                else:
                    # Repeat pixels to fill
                    while len(valid_pixels) < needed_pixels:
                        valid_pixels.extend(valid_pixels[:needed_pixels - len(valid_pixels)])
                
                # Create image from valid pixels
                temp_img = Image.new('RGB', (size, size))
                temp_img.putdata(valid_pixels[:size*size])
                
                # Save to temp file for ColorThief
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    temp_img.save(tmp.name)
                    color_thief = ColorThief(tmp.name)
                    palette = color_thief.get_palette(color_count=num_colors, quality=1)
                    os.unlink(tmp.name)
            
            # Filter out any remaining background colors from palette
            filtered_palette = [c for c in palette if not self._is_background_color(c)]
            if not filtered_palette:
                filtered_palette = palette  # Fallback if all filtered out
            
            # Calculate color percentages
            total_pixels = len(valid_pixels) if valid_pixels else 1
            color_counts = {i: 0 for i in range(len(filtered_palette))}
            
            for pixel in valid_pixels:
                min_dist = float('inf')
                closest_idx = 0
                for idx, p_color in enumerate(filtered_palette):
                    dist = self.color_distance(pixel, p_color)
                    if dist < min_dist:
                        min_dist = dist
                        closest_idx = idx
                color_counts[closest_idx] += 1
            
            # Create ColorInfo objects
            colors = []
            for idx, rgb in enumerate(filtered_palette):
                percentage = (color_counts.get(idx, 0) / total_pixels) * 100
                colors.append(ColorInfo(
                    hex=self.rgb_to_hex(rgb),
                    rgb=rgb,
                    name=self.get_color_name(rgb),
                    percentage=round(percentage, 2)
                ))
            
            # Sort by percentage (most dominant first)
            colors.sort(key=lambda x: x.percentage, reverse=True)
            
            return colors[:num_colors]
            
        except Exception as e:
            raise ValueError(f"Failed to extract colors: {str(e)}")
    
    def extract_colors_from_bytes(self, image_bytes: bytes, num_colors: int = 5) -> List[ColorInfo]:
        """Extract colors from image bytes"""
        # Save to temporary BytesIO and use ColorThief
        img = Image.open(BytesIO(image_bytes))
        img = img.convert('RGB')
        
        # Save to temp file for ColorThief (it requires file path)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            img.save(tmp.name)
            colors = self.extract_colors(tmp.name, num_colors)
        
        import os
        os.unlink(tmp.name)
        return colors


class ColorHarmonyService:
    """Service for analyzing color harmony and suggesting matching colors"""
    
    @staticmethod
    def rgb_to_hsl(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """Convert RGB to HSL"""
        r, g, b = rgb[0] / 255, rgb[1] / 255, rgb[2] / 255
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return (h * 360, s * 100, l * 100)
    
    @staticmethod
    def hsl_to_rgb(hsl: Tuple[float, float, float]) -> Tuple[int, int, int]:
        """Convert HSL to RGB"""
        h, s, l = hsl[0] / 360, hsl[1] / 100, hsl[2] / 100
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return (int(r * 255), int(g * 255), int(b * 255))
    
    @classmethod
    def get_complementary(cls, rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Get complementary color (opposite on color wheel)"""
        h, s, l = cls.rgb_to_hsl(rgb)
        new_h = (h + 180) % 360
        return cls.hsl_to_rgb((new_h, s, l))
    
    @classmethod
    def get_analogous(cls, rgb: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        """Get analogous colors (adjacent on color wheel)"""
        h, s, l = cls.rgb_to_hsl(rgb)
        colors = []
        for offset in [-30, 30]:
            new_h = (h + offset) % 360
            colors.append(cls.hsl_to_rgb((new_h, s, l)))
        return colors
    
    @classmethod
    def get_triadic(cls, rgb: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        """Get triadic colors (evenly spaced on color wheel)"""
        h, s, l = cls.rgb_to_hsl(rgb)
        colors = []
        for offset in [120, 240]:
            new_h = (h + offset) % 360
            colors.append(cls.hsl_to_rgb((new_h, s, l)))
        return colors
    
    @classmethod
    def calculate_harmony_score(cls, colors: List[Tuple[int, int, int]]) -> float:
        """
        Calculate a color harmony score for a set of colors
        Returns a score from 0-100
        """
        if len(colors) < 2:
            return 100.0
        
        # Convert to HSL for analysis
        hsl_colors = [cls.rgb_to_hsl(c) for c in colors]
        
        score = 100.0
        
        # Check for complementary relationships
        for i, c1 in enumerate(hsl_colors):
            for c2 in hsl_colors[i+1:]:
                h_diff = abs(c1[0] - c2[0])
                if h_diff > 180:
                    h_diff = 360 - h_diff
                
                # Perfect complementary (180°)
                if 165 <= h_diff <= 195:
                    score += 10
                # Analogous (30°)
                elif h_diff <= 45:
                    score += 5
                # Triadic (120°)
                elif 105 <= h_diff <= 135:
                    score += 8
                # Clashing colors
                elif 60 <= h_diff <= 90:
                    score -= 15
        
        # Normalize score to 0-100
        return max(0, min(100, score))
    
    @classmethod
    def colors_match(cls, rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int], 
                     scheme: str = "complementary", tolerance: float = 30) -> bool:
        """Check if two colors match according to a color scheme"""
        h1, s1, l1 = cls.rgb_to_hsl(rgb1)
        h2, s2, l2 = cls.rgb_to_hsl(rgb2)
        
        h_diff = abs(h1 - h2)
        if h_diff > 180:
            h_diff = 360 - h_diff
        
        if scheme == "complementary":
            target = 180
        elif scheme == "analogous":
            return h_diff <= tolerance
        elif scheme == "triadic":
            return abs(h_diff - 120) <= tolerance or abs(h_diff - 240) <= tolerance
        elif scheme == "monochromatic":
            return h_diff <= 15  # Same hue, different saturation/lightness
        else:
            return True
        
        return abs(h_diff - target) <= tolerance


# Singleton instance
color_extraction_service = ColorExtractionService()
color_harmony_service = ColorHarmonyService()
