import {
  collection,
  doc,
  addDoc,
  deleteDoc,
  getDocs,
  getDoc,
  query,
  where,
} from 'firebase/firestore';
import { db } from '@/lib/firebase';
import { Outfit, OutfitItem, ClothingStyle } from '@/types';

const COLLECTION_NAME = 'outfits';

export const outfitService = {
  // Get all outfits for a user
  async getAll(userId: string): Promise<Outfit[]> {
    const q = query(
      collection(db, COLLECTION_NAME),
      where('userId', '==', userId)
    );
    
    const snapshot = await getDocs(q);
    const outfits = snapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data(),
    })) as Outfit[];
    
    // Sort client-side to avoid needing a composite index
    return outfits.sort((a, b) => 
      new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
  },

  // Get single outfit
  async getById(id: string): Promise<Outfit | null> {
    const docRef = doc(db, COLLECTION_NAME, id);
    const docSnap = await getDoc(docRef);
    
    if (!docSnap.exists()) {
      return null;
    }
    
    return { id: docSnap.id, ...docSnap.data() } as Outfit;
  },

  // Create new outfit
  async create(
    userId: string,
    data: {
      name: string;
      items: OutfitItem[];
      style: ClothingStyle;
      occasion?: string;
      colorHarmonyScore: number;
    }
  ): Promise<Outfit> {
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

  // Delete outfit
  async delete(id: string): Promise<void> {
    const docRef = doc(db, COLLECTION_NAME, id);
    await deleteDoc(docRef);
  },
};
