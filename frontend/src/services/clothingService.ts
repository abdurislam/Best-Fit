import {
  collection,
  doc,
  addDoc,
  updateDoc,
  deleteDoc,
  getDocs,
  getDoc,
  query,
  where,
} from 'firebase/firestore';
import { db } from '@/lib/firebase';
import { ClothingItem, ClothingCategory, ClothingStyle, ColorInfo } from '@/types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const COLLECTION_NAME = 'clothing';

export const clothingService = {
  // Get all clothing items for a user
  async getAll(userId: string): Promise<ClothingItem[]> {
    const q = query(
      collection(db, COLLECTION_NAME),
      where('userId', '==', userId)
    );
    
    const snapshot = await getDocs(q);
    const items = snapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data(),
    })) as ClothingItem[];
    
    // Sort client-side to avoid needing a composite index
    return items.sort((a, b) => 
      new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
  },

  // Get clothing by category
  async getByCategory(userId: string, category: ClothingCategory): Promise<ClothingItem[]> {
    const q = query(
      collection(db, COLLECTION_NAME),
      where('userId', '==', userId),
      where('category', '==', category)
    );
    
    const snapshot = await getDocs(q);
    const items = snapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data(),
    })) as ClothingItem[];
    
    return items.sort((a, b) => 
      new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
  },

  // Get single item
  async getById(id: string): Promise<ClothingItem | null> {
    const docRef = doc(db, COLLECTION_NAME, id);
    const docSnap = await getDoc(docRef);
    
    if (!docSnap.exists()) {
      return null;
    }
    
    return { id: docSnap.id, ...docSnap.data() } as ClothingItem;
  },

  // Upload image to backend server (instead of Firebase Storage)
  async uploadImage(userId: string, file: File): Promise<string> {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('user_id', userId);

    const response = await fetch(`${API_URL}/api/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload image');
    }

    const data = await response.json();
    return data.image_url;
  },

  // Add new clothing item
  async add(
    userId: string,
    data: {
      name: string;
      category: ClothingCategory;
      style: ClothingStyle;
      imageUrl: string;
      dominantColors: ColorInfo[];
      tags: string[];
    }
  ): Promise<ClothingItem> {
    const docRef = await addDoc(collection(db, COLLECTION_NAME), {
      ...data,
      userId,
      createdAt: new Date().toISOString(),
    });
    
    return {
      id: docRef.id,
      userId,
      ...data,
      createdAt: new Date().toISOString(),
    };
  },

  // Update clothing item
  async update(id: string, updates: Partial<ClothingItem>): Promise<void> {
    const docRef = doc(db, COLLECTION_NAME, id);
    await updateDoc(docRef, updates);
  },

  // Delete clothing item (image deleted via backend)
  async delete(id: string, imageUrl: string): Promise<void> {
    // Delete image from backend storage
    try {
      await fetch(`${API_URL}/api/upload`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_url: imageUrl }),
      });
    } catch (error) {
      console.error('Error deleting image:', error);
    }
    
    // Delete document from Firestore
    const docRef = doc(db, COLLECTION_NAME, id);
    await deleteDoc(docRef);
  },
};
