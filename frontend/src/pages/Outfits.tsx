import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { outfitService } from '@/services/outfitService';
import { clothingService } from '@/services/clothingService';
import { Outfit, ClothingItem } from '@/types';
import { Shirt, Trash2, Star } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const getImageUrl = (imageUrl: string) => {
  if (imageUrl.startsWith('http')) return imageUrl;
  return `${API_URL}${imageUrl}`;
};

export default function Outfits() {
  const { user } = useAuth();
  const [outfits, setOutfits] = useState<Outfit[]>([]);
  const [clothingItems, setClothingItems] = useState<ClothingItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [user]);

  const loadData = async () => {
    if (!user) return;
    try {
      const [outfitsData, clothingData] = await Promise.all([
        outfitService.getAll(user.uid),
        clothingService.getAll(user.uid),
      ]);
      setOutfits(outfitsData);
      setClothingItems(clothingData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (outfitId: string) => {
    if (!confirm('Are you sure you want to delete this outfit?')) return;

    try {
      await outfitService.delete(outfitId);
      setOutfits(outfits.filter(o => o.id !== outfitId));
    } catch (error) {
      console.error('Error deleting outfit:', error);
    }
  };

  const getClothingItem = (clothingId: string) => {
    return clothingItems.find(item => item.id === clothingId);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800">My Outfits</h1>
      </div>

      {outfits.length === 0 ? (
        <div className="text-center py-16">
          <Shirt className="mx-auto h-16 w-16 text-gray-300 mb-4" />
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">No outfits yet</h2>
          <p className="text-gray-500">
            Get outfit suggestions and save your favorites!
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {outfits.map(outfit => (
            <div key={outfit.id} className="card">
              <div className="p-4 border-b border-gray-100 flex justify-between items-center">
                <h3 className="font-semibold text-gray-800">{outfit.name}</h3>
                <div className="flex items-center gap-2 text-amber-500">
                  <Star size={16} fill="currentColor" />
                  <span className="font-medium">{outfit.colorHarmonyScore.toFixed(0)}</span>
                </div>
              </div>

              <div className="p-4 flex gap-3 overflow-x-auto">
                {outfit.items.map((outfitItem, idx) => {
                  const clothing = getClothingItem(outfitItem.clothingId);
                  return clothing ? (
                    <img
                      key={idx}
                      src={getImageUrl(clothing.imageUrl)}
                      alt={clothing.name}
                      className="w-20 h-20 object-cover rounded-lg flex-shrink-0"
                    />
                  ) : null;
                })}
              </div>

              <div className="p-4 bg-gray-50 flex justify-between items-center">
                <div className="text-sm text-gray-500">
                  <span className="capitalize">{outfit.style}</span>
                  {outfit.occasion && <span> • {outfit.occasion}</span>}
                </div>
                <button
                  onClick={() => handleDelete(outfit.id)}
                  className="text-red-500 hover:text-red-600 p-2"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
