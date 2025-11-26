import React, { useEffect, useState, useCallback } from 'react';
import { getCreditors, syncCreditors } from '../api/client';

export default function CreditorList() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [syncing, setSyncing] = useState(false);
  const pageSize = 50;

  const loadCreditors = useCallback(async (pageNum = 1, searchTerm = '', type = '') => {
    setLoading(true);
    setError(null);
    try {
      const offset = (pageNum - 1) * pageSize;
      const { data } = await getCreditors({
        limit: pageSize,
        offset,
        search: searchTerm,
        creditor_type: type || undefined,
        sort_by: 'risk_score'
      });
      setItems(data.creditors || []);
      setTotal(data.total || 0);
    } catch (e) {
      setError('Неуспешно зареждане на кредитори');
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [pageSize]);

  useEffect(() => {
    loadCreditors(page, search, filterType);
  }, [page, loadCreditors]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    loadCreditors(1, search, filterType);
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      await syncCreditors();
      await loadCreditors(page, search, filterType);
      alert('Синхронизацията завърши успешно!');
    } catch (e) {
      alert('Грешка при синхронизация: ' + (e.response?.data?.detail || e.message));
    } finally {
      setSyncing(false);
    }
  };

  const totalPages = Math.ceil(total / pageSize);

  if (loading && items.length === 0) {
    return <div className="loading">Зареждане на кредитори...</div>;
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Кредитори ({total})</h2>
        <button 
          onClick={handleSync} 
          disabled={syncing}
          style={{ padding: '8px 16px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
        >
          {syncing ? 'Синхронизиране...' : '🔄 Синхронизирай от API'}
        </button>
      </div>

      {/* Search and Filters */}
      <form onSubmit={handleSearch} style={{ marginBottom: '20px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Търси по име или БУЛСТАТ..."
          style={{ flex: 1, minWidth: '200px', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
        />
        <select
          value={filterType}
          onChange={(e) => {
            setFilterType(e.target.value);
            setPage(1);
            loadCreditors(1, search, e.target.value);
          }}
          style={{ padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
        >
          <option value="">Всички типове</option>
          <option value="bank">Банки</option>
          <option value="non-bank">Небанкови</option>
          <option value="unknown">Неизвестни</option>
        </select>
        <button type="submit" style={{ padding: '8px 16px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          Търси
        </button>
      </form>

      {error && <div className="alert alert-danger">{error}</div>}

      {loading && items.length > 0 && (
        <div style={{ textAlign: 'center', padding: '10px' }}>Зареждане...</div>
      )}

      <div style={{ overflowX: 'auto' }}>
        <table className="table" style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ textAlign: 'left', padding: '10px', borderBottom: '2px solid #ddd' }}>Име</th>
              <th style={{ textAlign: 'left', padding: '10px', borderBottom: '2px solid #ddd' }}>БУЛСТАТ</th>
              <th style={{ textAlign: 'left', padding: '10px', borderBottom: '2px solid #ddd' }}>Тип</th>
              <th style={{ textAlign: 'right', padding: '10px', borderBottom: '2px solid #ddd' }}>Риск скор</th>
              <th style={{ textAlign: 'right', padding: '10px', borderBottom: '2px solid #ddd' }}>Нарушения</th>
              <th style={{ textAlign: 'center', padding: '10px', borderBottom: '2px solid #ddd' }}>Статус</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 && !loading ? (
              <tr>
                <td colSpan="6" style={{ textAlign: 'center', padding: '20px' }}>
                  Няма намерени кредитори
                </td>
              </tr>
            ) : (
              items.map(c => (
                <tr key={c.id} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '10px' }}>{c.name}</td>
                  <td style={{ padding: '10px', fontFamily: 'monospace' }}>{c.bulstat || '-'}</td>
                  <td style={{ padding: '10px' }}>{c.type || 'unknown'}</td>
                  <td style={{ textAlign: 'right', padding: '10px' }}>
                    <span style={{ 
                      color: c.risk_score >= 7 ? '#dc3545' : c.risk_score >= 4 ? '#ffc107' : '#28a745',
                      fontWeight: 'bold'
                    }}>
                      {c.risk_score?.toFixed(1) || '0.0'}
                    </span>
                  </td>
                  <td style={{ textAlign: 'right', padding: '10px' }}>{c.violations_count || 0}</td>
                  <td style={{ textAlign: 'center', padding: '10px' }}>
                    {c.blacklisted ? (
                      <span className="risk-badge risk-critical" style={{ 
                        backgroundColor: '#dc3545', 
                        color: 'white', 
                        padding: '4px 8px', 
                        borderRadius: '4px',
                        fontSize: '12px'
                      }}>
                        Черен списък
                      </span>
                    ) : (
                      <span style={{ color: '#28a745' }}>✓ OK</span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'center', gap: '10px', alignItems: 'center' }}>
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1 || loading}
            style={{ padding: '8px 16px', border: '1px solid #ddd', borderRadius: '4px', cursor: 'pointer', backgroundColor: 'white' }}
          >
            ← Предишна
          </button>
          <span style={{ padding: '8px 16px' }}>
            Страница {page} от {totalPages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages || loading}
            style={{ padding: '8px 16px', border: '1px solid #ddd', borderRadius: '4px', cursor: 'pointer', backgroundColor: 'white' }}
          >
            Следваща →
          </button>
        </div>
      )}
    </div>
  );
}
