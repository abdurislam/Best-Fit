import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { clothingService } from '@/services/clothingService';
import { ClothingItem, ClothingCategory, ClothingStyle } from '@/types';
import { Package } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Helper to get full image URL
const getImageUrl = (imageUrl: string) => {
  if (imageUrl.startsWith('http')) return imageUrl;
  return `${API_URL}${imageUrl}`;
};

export default function Closet() {
  const { user } = useAuth();
  const [items, setItems] = useState<ClothingItem[]>([]);
  const [filteredItems, setFilteredItems] = useState<ClothingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [styleFilter, setStyleFilter] = useState<string>('');

  useEffect(() => {
    loadItems();
  }, [user]);

  useEffect(() => {
    filterItems();
  }, [items, categoryFilter, styleFilter]);

  const loadItems = async () => {
    if (!user) return;
    try {
      const data = await clothingService.getAll(user.uid);
      setItems(data);
    } catch (error) {
      console.error('Error loading items:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterItems = () => {
    let filtered = [...items];
    if (categoryFilter) {
      filtered = filtered.filter(item => item.category === categoryFilter);
    }
    if (styleFilter) {
      filtered = filtered.filter(item => item.style === styleFilter);
    }
    setFilteredItems(filtered);
  };

  const categories: ClothingCategory[] = ['top', 'bottom', 'dress', 'outerwear', 'shoes', 'accessory'];
  const styles: ClothingStyle[] = ['casual', 'formal', 'sporty', 'business', 'evening', 'bohemian', 'streetwear', 'vintage'];

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
        <h1 className="text-3xl font-bold text-gray-800">My Closet</h1>
        <div className="flex gap-4">
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">All Categories</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</option>
            ))}
          </select>
          <select
            value={styleFilter}
            onChange={(e) => setStyleFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">All Styles</option>
            {styles.map(style => (
              <option key={style} value={style}>{style.charAt(0).toUpperCase() + style.slice(1)}</option>
            ))}
          </select>
        </div>
      </div>

      {filteredItems.length === 0 ? (
        <div className="text-center py-16">
          <Package className="mx-auto h-16 w-16 text-gray-300 mb-4" />
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">
            {items.length === 0 ? 'Your closet is empty' : 'No items match your filters'}
          </h2>
          <p className="text-gray-500 mb-6">
            {items.length === 0 ? 'Add some clothing items to get started!' : 'Try adjusting your filters'}
          </p>
          {items.length === 0 && (
            <Link to="/add-item" className="btn-primary inline-block">
              Add First Item
            </Link>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredItems.map(item => (
            <Link
              key={item.id}
              to={`/closet/${item.id}`}
              className="card hover:shadow-lg transition-shadow cursor-pointer"
            >
              <img
                src={getImageUrl(item.imageUrl)}
                alt={item.name}
                className="w-full h-48 object-contain bg-gray-50"
              />
              <div className="p-4">
                <h3 className="font-semibold text-gray-800 mb-2">{item.name}</h3>
                <div className="flex justify-between text-sm text-gray-500 mb-3">
                  <span>{item.category}</span>
                  <span>{item.style}</span>
                </div>
                <div className="flex gap-1">
                  {item.dominantColors.slice(0, 5).map((color, idx) => (
                    <div
                      key={idx}
                      className="w-5 h-5 rounded-full border-2 border-white shadow-sm"
                      style={{ backgroundColor: color.hex }}
                      title={color.name}
                    />
                  ))}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
