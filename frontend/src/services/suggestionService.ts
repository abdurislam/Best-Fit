import { ClothingItem, ClothingStyle, OutfitSuggestion } from '@/types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const suggestionService = {
  // Get outfit suggestions
  async getSuggestions(
    items: ClothingItem[],
    options: {
      baseItemId?: string;
      style?: ClothingStyle;
      colorScheme?: string;
      maxSuggestions?: number;
    } = {}
  ): Promise<OutfitSuggestion[]> {
    // Send items to backend for analysis
    const response = await fetch(`${API_URL}/api/outfits/suggest`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        items: items.map(item => ({
          id: item.id,
          name: item.name,
          category: item.category,
          style: item.style,
          imageUrl: item.imageUrl,
          dominant_colors: item.dominantColors.map(c => ({
            hex: c.hex,
            rgb: c.rgb,
            name: c.name,
            percentage: c.percentage,
          })),
          tags: item.tags || [],
        })),
        base_item_id: options.baseItemId || null,
        style: options.style || null,
        color_scheme: options.colorScheme || null,
        max_suggestions: options.maxSuggestions || 5,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(error || 'Failed to generate suggestions');
    }

    const data = await response.json();
    
    // Map response back to our types
    return data.suggestions.map((suggestion: any) => ({
      items: suggestion.items.map((item: any) => {
        const originalItem = items.find(i => i.id === item.id);
        return originalItem || item;
      }),
      colorHarmonyScore: suggestion.color_harmony_score,
      styleCompatibilityScore: suggestion.style_compatibility_score,
      totalScore: suggestion.total_score,
      pattern: suggestion.pattern,
    }));
  },
};
