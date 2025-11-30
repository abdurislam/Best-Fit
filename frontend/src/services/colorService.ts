import axios from 'axios';
import { ColorInfo } from '@/types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const colorService = {
  // Extract colors from image using backend ML service
  async extractColors(imageFile: File): Promise<ColorInfo[]> {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('num_colors', '5');
    
    const response = await axios.post(`${API_URL}/api/colors/extract`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // Get color harmony suggestions
  async getHarmony(hexColor: string, scheme: string): Promise<any> {
    const response = await axios.get(
      `${API_URL}/api/colors/harmony/${scheme}?hex_color=${encodeURIComponent(hexColor)}`
    );
    return response.data;
  },

  // Calculate harmony score for multiple colors
  async calculateHarmonyScore(colors: string[]): Promise<{ harmony_score: number; rating: string }> {
    const response = await axios.post(`${API_URL}/api/colors/harmony/score`, colors);
    return response.data;
  },
};
