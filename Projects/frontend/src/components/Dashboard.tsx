import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { getItems, createItem, updateItem, deleteItem } from '../api/items';
import type { Item } from '../api/types';

interface DashboardProps {
  onNavigate: (path: string) => void;
}

export const Dashboard = ({ onNavigate }: DashboardProps) => {
  const [items, setItems] = useState<Item[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingItem, setEditingItem] = useState<Item | null>(null);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<string | null>(null);
  const { user, logout } = useAuth();
  const abortControllerRef = useRef<AbortController | null>(null);

  const fetchItems = useCallback(async () => {
    abortControllerRef.current?.abort();
    abortControllerRef.current = new AbortController();

    setIsLoading(true);
    try {
      const response = await getItems();
      if (response.success) {
        setItems(response.data);
      }
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        setError('Failed to fetch items');
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchItems();
    return () => {
      abortControllerRef.current?.abort();
    };
  }, [fetchItems]);

  const handleOpenModal = (item?: Item) => {
    if (item) {
      setEditingItem(item);
      setName(item.name);
      setDescription(item.description || '');
    } else {
      setEditingItem(null);
      setName('');
      setDescription('');
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingItem(null);
    setName('');
    setDescription('');
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      if (editingItem) {
        await updateItem(editingItem.id, name, description);
      } else {
        await createItem(name, description);
      }
      handleCloseModal();
      fetchItems();
    } catch (err) {
      setError(editingItem ? 'Failed to update item' : 'Failed to create item');
    }
  };

  const handleDeleteClick = (id: string) => {
    setItemToDelete(id);
    setShowDeleteConfirm(true);
  };

  const handleConfirmDelete = async () => {
    if (itemToDelete) {
      try {
        await deleteItem(itemToDelete);
        fetchItems();
      } catch (err) {
        setError('Failed to delete item');
      }
    }
    setShowDeleteConfirm(false);
    setItemToDelete(null);
  };

  const handleCancelDelete = () => {
    setShowDeleteConfirm(false);
    setItemToDelete(null);
  };

  const handleLogout = () => {
    logout();
    onNavigate('/login');
  };

  if (isLoading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Welcome, {user?.email}</h1>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </header>

      {error && <div className="error-message">{error}</div>}

      <div className="dashboard-content">
        <div className="items-header">
          <h2>Items</h2>
          <button onClick={() => handleOpenModal()} className="add-btn">Add Item</button>
        </div>

        <div className="items-list">
          {items.length === 0 ? (
            <p>No items found. Click "Add Item" to create one.</p>
          ) : (
            items.map((item) => (
              <div key={item.id} className="item-card">
                <h3>{item.name}</h3>
                {item.description && <p>{item.description}</p>}
                {item.created_at && (
                  <span className="item-date">{new Date(item.created_at).toLocaleDateString()}</span>
                )}
                <div className="item-actions">
                  <button onClick={() => handleOpenModal(item)}>Edit</button>
                  <button onClick={() => handleDeleteClick(item.id)} className="delete-btn">Delete</button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>{editingItem ? 'Edit Item' : 'Add Item'}</h3>
            {error && <div className="error-message">{error}</div>}
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  placeholder="Enter item name"
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Enter item description"
                />
              </div>
              <div className="modal-actions">
                <button type="button" onClick={handleCloseModal}>Cancel</button>
                <button type="submit">{editingItem ? 'Update' : 'Create'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showDeleteConfirm && (
        <div className="modal-overlay" onClick={handleCancelDelete}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Confirm Delete</h3>
            <p>Are you sure you want to delete this item?</p>
            <div className="modal-actions">
              <button type="button" onClick={handleCancelDelete}>Cancel</button>
              <button type="button" onClick={handleConfirmDelete} className="delete-btn">Delete</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};