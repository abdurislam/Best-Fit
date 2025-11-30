import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { clothingService } from '@/services/clothingService';
import { ClothingItem } from '@/types';
import { ArrowLeft, Trash2, Sparkles, AlertTriangle, Loader2 } from 'lucide-react';
import Modal from '@/components/Modal';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const getImageUrl = (imageUrl: string) => {
  if (imageUrl.startsWith('http')) return imageUrl;
  return `${API_URL}${imageUrl}`;
};

export default function ItemDetail() {
  const { id } = useParams<{ id: string }>();
  useAuth(); // Ensure user is authenticated
  const navigate = useNavigate();
  const [item, setItem] = useState<ClothingItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  useEffect(() => {
    loadItem();
  }, [id]);

  const loadItem = async () => {
    if (!id) return;
    try {
      const data = await clothingService.getById(id);
      setItem(data);
    } catch (error) {
      console.error('Error loading item:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!item) return;

    setDeleting(true);
    try {
      await clothingService.delete(item.id, item.imageUrl);
      navigate('/closet');
    } catch (error) {
      console.error('Error deleting item:', error);
      setDeleting(false);
      setShowDeleteModal(false);
    }
  };

  const handleGetSuggestions = () => {
    navigate(`/suggestions?baseItem=${id}`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (!item) {
    return (
      <div className="text-center py-16">
        <h2 className="text-2xl font-semibold text-gray-700">Item not found</h2>
        <button onClick={() => navigate('/closet')} className="btn-primary mt-4">
          Back to Closet
        </button>
      </div>
    );
  }

  return (
    <div>
      <button
        onClick={() => navigate('/closet')}
        className="flex items-center gap-2 text-gray-600 hover:text-gray-800 mb-6"
      >
        <ArrowLeft size={20} />
        Back to Closet
      </button>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="grid md:grid-cols-2 gap-8">
          <div className="p-6">
            <img
              src={getImageUrl(item.imageUrl)}
              alt={item.name}
              className="w-full rounded-lg"
            />
          </div>

          <div className="p-6">
            <h1 className="text-3xl font-bold text-gray-800 mb-4">{item.name}</h1>

            <div className="space-y-4 mb-8">
              <div>
                <span className="text-sm text-gray-500">Category</span>
                <p className="font-medium capitalize">{item.category}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Style</span>
                <p className="font-medium capitalize">{item.style}</p>
              </div>
              {item.tags.length > 0 && (
                <div>
                  <span className="text-sm text-gray-500">Tags</span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {item.tags.map((tag, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-gray-100 rounded-full text-sm"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="mb-8">
              <h3 className="text-lg font-semibold mb-4">Detected Colors</h3>
              <div className="space-y-3">
                {item.dominantColors.map((color, idx) => (
                  <div key={idx} className="flex items-center gap-4">
                    <div
                      className="w-10 h-10 rounded-lg border border-gray-200"
                      style={{ backgroundColor: color.hex }}
                    />
                    <div className="flex-1">
                      <span className="font-medium capitalize">{color.name}</span>
                      <span className="text-gray-400 ml-2">{color.hex}</span>
                    </div>
                    <span className="text-sm text-gray-500">
                      {color.percentage.toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={handleGetSuggestions}
                className="btn-primary flex items-center gap-2"
              >
                <Sparkles size={20} />
                Get Outfit Ideas
              </button>
              <button
                onClick={() => setShowDeleteModal(true)}
                disabled={deleting}
                className="btn-danger flex items-center gap-2"
              >
                <Trash2 size={20} />
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Delete Item"
      >
        <div className="text-center mb-6">
          <AlertTriangle className="mx-auto h-16 w-16 text-red-500 mb-4" />
          <h3 className="text-lg font-semibold text-gray-800 mb-2">
            Are you sure you want to delete this item?
          </h3>
          <p className="text-gray-500">
            This action cannot be undone. "{item.name}" will be permanently removed from your closet.
          </p>
        </div>

        <div className="flex gap-3">
          <button
            onClick={() => setShowDeleteModal(false)}
            className="btn-secondary flex-1"
          >
            Cancel
          </button>
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="btn-danger flex-1 flex items-center justify-center gap-2"
          >
            {deleting ? (
              <>
                <Loader2 className="animate-spin" size={18} />
                Deleting...
              </>
            ) : (
              <>
                <Trash2 size={18} />
                Delete
              </>
            )}
          </button>
        </div>
      </Modal>
    </div>
  );
}
