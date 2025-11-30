import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { clothingService } from '@/services/clothingService';
import { colorService } from '@/services/colorService';
import { ClothingCategory, ClothingStyle, ColorInfo } from '@/types';
import { Upload, Camera, Loader2, Check } from 'lucide-react';

export default function AddItem() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [name, setName] = useState('');
  const [category, setCategory] = useState<ClothingCategory>('top');
  const [style, setStyle] = useState<ClothingStyle>('casual');
  const [tags, setTags] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>('');
  const [extractedColors, setExtractedColors] = useState<ColorInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [extractingColors, setExtractingColors] = useState(false);
  const [error, setError] = useState('');

  const categories: ClothingCategory[] = ['top', 'bottom', 'dress', 'outerwear', 'shoes', 'accessory'];
  const styles: ClothingStyle[] = ['casual', 'formal', 'sporty', 'business', 'evening', 'bohemian', 'streetwear', 'vintage'];

  const handleImageChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setImageFile(file);
    setExtractedColors([]);

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);

    // Extract colors
    setExtractingColors(true);
    try {
      const colors = await colorService.extractColors(file);
      setExtractedColors(colors);
    } catch (err) {
      console.error('Error extracting colors:', err);
      setError('Failed to extract colors from image. Please try again.');
    } finally {
      setExtractingColors(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || !imageFile) return;

    setLoading(true);
    setError('');

    try {
      // Upload image to Firebase Storage
      const imageUrl = await clothingService.uploadImage(user.uid, imageFile);

      // Add clothing item to Firestore
      await clothingService.add(user.uid, {
        name,
        category,
        style,
        imageUrl,
        dominantColors: extractedColors,
        tags: tags.split(',').map(t => t.trim()).filter(Boolean),
      });

      navigate('/closet');
    } catch (err: any) {
      setError(err.message || 'Failed to add item');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-800 mb-8">Add New Item</h1>

      <form onSubmit={handleSubmit} className="max-w-2xl bg-white rounded-xl shadow-sm border border-gray-100 p-8">
        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Item Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="input"
            placeholder="e.g., Blue Denim Jacket"
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value as ClothingCategory)}
              className="input"
              required
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>
                  {cat.charAt(0).toUpperCase() + cat.slice(1)}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Style
            </label>
            <select
              value={style}
              onChange={(e) => setStyle(e.target.value as ClothingStyle)}
              className="input"
              required
            >
              {styles.map(s => (
                <option key={s} value={s}>
                  {s.charAt(0).toUpperCase() + s.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tags (comma-separated)
          </label>
          <input
            type="text"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            className="input"
            placeholder="e.g., summer, favorite, gift"
          />
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Image
          </label>
          <div
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
              imagePreview ? 'border-primary-300 bg-primary-50' : 'border-gray-300 hover:border-primary-400'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              className="hidden"
              required
            />
            {imagePreview ? (
              <div className="space-y-4">
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="max-h-64 mx-auto rounded-lg"
                />
                <p className="text-sm text-gray-500">Click to change image</p>
              </div>
            ) : (
              <div>
                <Camera className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <p className="text-gray-600">Click or drag to upload image</p>
                <p className="text-sm text-gray-400 mt-2">PNG, JPG up to 10MB</p>
              </div>
            )}
          </div>
        </div>

        {/* Extracted Colors */}
        {extractingColors && (
          <div className="mb-6 flex items-center gap-3 text-primary-600">
            <Loader2 className="animate-spin" size={20} />
            <span>Analyzing colors...</span>
          </div>
        )}

        {extractedColors.length > 0 && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              <Check className="inline-block mr-2 text-green-500" size={16} />
              Detected Colors
            </label>
            <div className="flex flex-wrap gap-3">
              {extractedColors.map((color, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-2 bg-gray-50 px-3 py-2 rounded-lg"
                >
                  <div
                    className="w-6 h-6 rounded-full border border-gray-200"
                    style={{ backgroundColor: color.hex }}
                  />
                  <div>
                    <span className="text-sm font-medium capitalize">{color.name}</span>
                    <span className="text-xs text-gray-400 ml-2">{color.percentage.toFixed(1)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !imageFile || extractingColors}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="animate-spin" size={20} />
              Adding to Closet...
            </>
          ) : (
            <>
              <Upload size={20} />
              Add to Closet
            </>
          )}
        </button>
      </form>
    </div>
  );
}
