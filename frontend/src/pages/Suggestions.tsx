import { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { clothingService } from '@/services/clothingService';
import { outfitService } from '@/services/outfitService';
import { suggestionService } from '@/services/suggestionService';
import { ClothingItem, ClothingStyle, OutfitSuggestion } from '@/types';
import { Sparkles, Save, Loader2, CheckCircle, ChevronDown, X } from 'lucide-react';
import Modal from '@/components/Modal';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const getImageUrl = (imageUrl: string) => {
  if (imageUrl.startsWith('http')) return imageUrl;
  return `${API_URL}${imageUrl}`;
};

export default function Suggestions() {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const baseItemId = searchParams.get('baseItem');

  const [clothingItems, setClothingItems] = useState<ClothingItem[]>([]);
  const [suggestions, setSuggestions] = useState<OutfitSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [savingIndex, setSavingIndex] = useState<number | null>(null);

  // Modal state
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [outfitName, setOutfitName] = useState('');
  const [selectedSuggestion, setSelectedSuggestion] = useState<{ suggestion: OutfitSuggestion; index: number } | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const [selectedBaseItem, setSelectedBaseItem] = useState<string>(baseItemId || '');
  const [selectedStyle, setSelectedStyle] = useState<string>('');
  const [colorScheme, setColorScheme] = useState<string>('');
  const [isItemDropdownOpen, setIsItemDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const styles: ClothingStyle[] = ['casual', 'formal', 'sporty', 'business', 'evening', 'bohemian', 'streetwear', 'vintage'];
  const colorSchemes = [
    { value: 'complementary', label: 'Complementary' },
    { value: 'analogous', label: 'Analogous' },
    { value: 'triadic', label: 'Triadic' },
    { value: 'monochromatic', label: 'Monochromatic' },
  ];

  useEffect(() => {
    loadClothingItems();
  }, [user]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsItemDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const loadClothingItems = async () => {
    if (!user) return;
    try {
      const data = await clothingService.getAll(user.uid);
      setClothingItems(data);
    } catch (error) {
      console.error('Error loading items:', error);
    } finally {
      setInitialLoading(false);
    }
  };

  const [error, setError] = useState<string>('');

  const handleGenerateSuggestions = async () => {
    if (clothingItems.length < 2) {
      setError('You need at least 2 items in your closet to generate suggestions');
      return;
    }

    setLoading(true);
    setSuggestions([]);
    setError('');

    try {
      const results = await suggestionService.getSuggestions(clothingItems, {
        baseItemId: selectedBaseItem || undefined,
        style: (selectedStyle as ClothingStyle) || undefined,
        colorScheme: colorScheme || undefined,
        maxSuggestions: 5,
      });
      setSuggestions(results);
      if (results.length === 0) {
        setError('No outfit combinations found. Try adding more items to your closet or adjusting filters.');
      }
    } catch (err: any) {
      console.error('Error generating suggestions:', err);
      setError(err.message || 'Failed to generate suggestions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const openSaveModal = (suggestion: OutfitSuggestion, index: number) => {
    setSelectedSuggestion({ suggestion, index });
    setOutfitName('New Outfit');
    setSaveSuccess(false);
    setShowSaveModal(true);
  };

  const closeSaveModal = () => {
    setShowSaveModal(false);
    setSelectedSuggestion(null);
    setOutfitName('');
    setSaveSuccess(false);
  };

  const handleSaveOutfit = async () => {
    if (!user || !selectedSuggestion || !outfitName.trim()) return;

    const { suggestion, index } = selectedSuggestion;
    setSavingIndex(index);

    try {
      await outfitService.create(user.uid, {
        name: outfitName.trim(),
        items: suggestion.items.map((item, idx) => ({
          clothingId: item.id,
          position: idx,
        })),
        style: suggestion.items[0]?.style || 'casual',
        colorHarmonyScore: suggestion.colorHarmonyScore,
      });
      setSaveSuccess(true);
      setTimeout(() => {
        closeSaveModal();
      }, 1500);
    } catch (error) {
      console.error('Error saving outfit:', error);
      setError('Failed to save outfit. Please try again.');
    } finally {
      setSavingIndex(null);
    }
  };

  if (initialLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-800 mb-8">Outfit Suggestions</h1>

      {/* Controls */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              Build around item
            </label>
            <div className="relative" ref={dropdownRef}>
              <button
                type="button"
                onClick={() => setIsItemDropdownOpen(!isItemDropdownOpen)}
                className="input w-full flex items-center justify-between gap-2 text-left min-h-[52px]"
              >
                {selectedBaseItem ? (
                  <div className="flex items-center gap-3 min-w-0">
                    <img
                      src={getImageUrl(clothingItems.find(i => i.id === selectedBaseItem)?.imageUrl || '')}
                      alt=""
                      className="w-10 h-10 object-cover rounded flex-shrink-0"
                    />
                    <span className="truncate">
                      {clothingItems.find(i => i.id === selectedBaseItem)?.name}
                    </span>
                  </div>
                ) : (
                  <span className="text-gray-500">Any item...</span>
                )}
                <ChevronDown 
                  size={18} 
                  className={`flex-shrink-0 text-gray-400 transition-transform ${isItemDropdownOpen ? 'rotate-180' : ''}`} 
                />
              </button>

              {isItemDropdownOpen && (
                <div className="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-72 overflow-y-auto">
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedBaseItem('');
                      setIsItemDropdownOpen(false);
                    }}
                    className="w-full px-3 py-2.5 text-left hover:bg-gray-50 flex items-center gap-3 text-gray-500"
                  >
                    <div className="w-10 h-10 bg-gray-100 rounded flex items-center justify-center flex-shrink-0">
                      <X size={18} className="text-gray-400" />
                    </div>
                    <span>Any item...</span>
                  </button>
                  {clothingItems.map(item => (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => {
                        setSelectedBaseItem(item.id);
                        setIsItemDropdownOpen(false);
                      }}
                      className={`w-full px-3 py-2.5 text-left hover:bg-primary-50 flex items-center gap-3 ${
                        selectedBaseItem === item.id ? 'bg-primary-50' : ''
                      }`}
                    >
                      <img
                        src={getImageUrl(item.imageUrl)}
                        alt={item.name}
                        className="w-10 h-10 object-cover rounded flex-shrink-0"
                      />
                      <div className="min-w-0">
                        <p className="font-medium text-gray-800 truncate">{item.name}</p>
                        <p className="text-xs text-gray-500 capitalize">{item.category}</p>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              Preferred style
            </label>
            <select
              value={selectedStyle}
              onChange={(e) => setSelectedStyle(e.target.value)}
              className="input"
            >
              <option value="">Any style...</option>
              {styles.map(style => (
                <option key={style} value={style}>
                  {style.charAt(0).toUpperCase() + style.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              Color harmony
            </label>
            <select
              value={colorScheme}
              onChange={(e) => setColorScheme(e.target.value)}
              className="input"
            >
              <option value="">Any colors...</option>
              {colorSchemes.map(scheme => (
                <option key={scheme.value} value={scheme.value}>
                  {scheme.label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={handleGenerateSuggestions}
              disabled={loading || clothingItems.length < 2}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles size={20} />
                  Generate
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {/* Suggestions */}
      {suggestions.length === 0 && !loading && !error ? (
        <div className="text-center py-16 bg-white rounded-xl shadow-sm border border-gray-100">
          <Sparkles className="mx-auto h-16 w-16 text-gray-300 mb-4" />
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">
            Ready to find your perfect outfit?
          </h2>
          <p className="text-gray-500">
            {clothingItems.length < 2 
              ? `Add at least 2 items to your closet (you have ${clothingItems.length})`
              : 'Set your preferences above and click "Generate"'
            }
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {suggestions.map((suggestion, index) => (
            <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="bg-gradient-to-r from-primary-500 to-purple-500 text-white p-4 flex justify-between items-center">
                <div>
                  <span className="font-medium">Suggestion {index + 1}</span>
                  <span className="ml-3 text-white/80">
                    {suggestion.pattern.join(' + ')}
                  </span>
                </div>
                <div className="text-2xl font-bold">
                  {suggestion.totalScore.toFixed(0)}
                </div>
              </div>

              <div className="p-6">
                <div className="flex gap-4 overflow-x-auto pb-4">
                  {suggestion.items.map((item, idx) => (
                    <div key={idx} className="flex-shrink-0 text-center">
                      <img
                        src={getImageUrl(item.imageUrl)}
                        alt={item.name}
                        className="w-32 h-32 object-cover rounded-lg mb-2"
                      />
                      <p className="text-sm font-medium truncate w-32">{item.name}</p>
                      <div className="flex justify-center gap-1 mt-1">
                        {item.dominantColors.slice(0, 3).map((color, colorIdx) => (
                          <div
                            key={colorIdx}
                            className="w-4 h-4 rounded-full border border-white shadow-sm"
                            style={{ backgroundColor: color.hex }}
                          />
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-gray-50 p-4 flex justify-between items-center">
                <div className="text-sm text-gray-500">
                  Color Harmony: {suggestion.colorHarmonyScore.toFixed(0)} |
                  Style Match: {suggestion.styleCompatibilityScore.toFixed(0)}
                </div>
                <button
                  onClick={() => openSaveModal(suggestion, index)}
                  disabled={savingIndex === index}
                  className="btn-primary flex items-center gap-2"
                >
                  {savingIndex === index ? (
                    <Loader2 className="animate-spin" size={18} />
                  ) : (
                    <Save size={18} />
                  )}
                  Save Outfit
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Save Outfit Modal */}
      <Modal
        isOpen={showSaveModal}
        onClose={closeSaveModal}
        title="Save Outfit"
      >
        {saveSuccess ? (
          <div className="text-center py-4">
            <CheckCircle className="mx-auto h-16 w-16 text-green-500 mb-4" />
            <h3 className="text-xl font-semibold text-gray-800 mb-2">Outfit Saved!</h3>
            <p className="text-gray-500">Your outfit has been added to your collection.</p>
          </div>
        ) : (
          <div>
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Outfit Name
              </label>
              <input
                type="text"
                value={outfitName}
                onChange={(e) => setOutfitName(e.target.value)}
                className="input"
                placeholder="Enter a name for your outfit"
                autoFocus
              />
            </div>

            {selectedSuggestion && (
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Items in this outfit
                </label>
                <div className="flex gap-2 overflow-x-auto pb-2">
                  {selectedSuggestion.suggestion.items.map((item, idx) => (
                    <img
                      key={idx}
                      src={getImageUrl(item.imageUrl)}
                      alt={item.name}
                      className="w-16 h-16 object-contain bg-gray-50 rounded-lg flex-shrink-0"
                    />
                  ))}
                </div>
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={closeSaveModal}
                className="btn-secondary flex-1"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveOutfit}
                disabled={!outfitName.trim() || savingIndex !== null}
                className="btn-primary flex-1 flex items-center justify-center gap-2"
              >
                {savingIndex !== null ? (
                  <>
                    <Loader2 className="animate-spin" size={18} />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save size={18} />
                    Save Outfit
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
