export interface ColorInfo {
  hex: string;
  rgb: [number, number, number];
  name: string;
  percentage: number;
}

export type ClothingCategory = 'top' | 'bottom' | 'dress' | 'outerwear' | 'shoes' | 'accessory';
export type ClothingStyle = 'casual' | 'formal' | 'sporty' | 'business' | 'evening' | 'bohemian' | 'streetwear' | 'vintage';

export interface ClothingItem {
  id: string;
  userId: string;
  name: string;
  category: ClothingCategory;
  style: ClothingStyle;
  imageUrl: string;
  dominantColors: ColorInfo[];
  tags: string[];
  createdAt: string;
}

export interface OutfitItem {
  clothingId: string;
  position: number;
}

export interface Outfit {
  id: string;
  userId: string;
  name: string;
  items: OutfitItem[];
  style: ClothingStyle;
  occasion?: string;
  colorHarmonyScore: number;
  createdAt: string;
}

export interface OutfitSuggestion {
  items: ClothingItem[];
  colorHarmonyScore: number;
  styleCompatibilityScore: number;
  totalScore: number;
  pattern: string[];
}
