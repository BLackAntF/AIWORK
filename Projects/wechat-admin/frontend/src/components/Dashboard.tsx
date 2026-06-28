import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
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
  const { theme, toggleTheme } = useTheme();
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
        setError('获取项目列表失败');
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
      setError(editingItem ? '更新项目失败' : '创建项目失败');
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
        setError('删除项目失败');
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
    return <div className="loading">加载中...</div>;
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>欢迎，{user?.email}</h1>
        <div className="header-actions">
          <button onClick={toggleTheme} className="theme-toggle">
            {theme === 'light' ? '🌙 暗色模式' : '☀️ 亮色模式'}
          </button>
          <button onClick={handleLogout} className="logout-btn">退出登录</button>
        </div>
      </header>

      {error && <div className="error-message">{error}</div>}

      <div className="dashboard-content">
        <div className="items-header">
          <h2>项目列表</h2>
          <button onClick={() => handleOpenModal()} className="add-btn">添加项目</button>
        </div>

        <div className="items-list">
          {items.length === 0 ? (
            <p>暂无项目，点击"添加项目"创建一个。</p>
          ) : (
            items.map((item) => (
              <div key={item.id} className="item-card">
                <h3>{item.name}</h3>
                {item.description && <p>{item.description}</p>}
                {item.created_at && (
                  <span className="item-date">{new Date(item.created_at).toLocaleDateString()}</span>
                )}
                <div className="item-actions">
                  <button onClick={() => handleOpenModal(item)}>编辑</button>
                  <button onClick={() => handleDeleteClick(item.id)} className="delete-btn">删除</button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>{editingItem ? '编辑项目' : '添加项目'}</h3>
            {error && <div className="error-message">{error}</div>}
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>名称</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  placeholder="请输入项目名称"
                />
              </div>
              <div className="form-group">
                <label>描述</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="请输入项目描述"
                />
              </div>
              <div className="modal-actions">
                <button type="button" onClick={handleCloseModal}>取消</button>
                <button type="submit">{editingItem ? '更新' : '创建'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showDeleteConfirm && (
        <div className="modal-overlay" onClick={handleCancelDelete}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>确认删除</h3>
            <p>确定要删除这个项目吗？</p>
            <div className="modal-actions">
              <button type="button" onClick={handleCancelDelete}>取消</button>
              <button type="button" onClick={handleConfirmDelete} className="delete-btn">删除</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};