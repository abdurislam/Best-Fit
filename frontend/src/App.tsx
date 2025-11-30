import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Closet from './pages/Closet';
import AddItem from './pages/AddItem';
import Outfits from './pages/Outfits';
import Suggestions from './pages/Suggestions';
import ItemDetail from './pages/ItemDetail';

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return user ? <>{children}</> : <Navigate to="/login" />;
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Navigate to="/closet" replace />} />
        <Route path="closet" element={<Closet />} />
        <Route path="closet/:id" element={<ItemDetail />} />
        <Route path="add-item" element={<AddItem />} />
        <Route path="outfits" element={<Outfits />} />
        <Route path="suggestions" element={<Suggestions />} />
      </Route>
    </Routes>
  );
}

export default App;
