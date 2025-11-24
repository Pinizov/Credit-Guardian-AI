import React, { useEffect, useState } from 'react';
import { getCreditors } from '../api/client';

export default function CreditorList() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await getCreditors();
        setItems(data.creditors || []);
      } catch (e) {
        setError('Неуспешно зареждане на кредитори');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <div className="loading">Зареждане на кредитори...</div>;
  if (error) return <div className="alert alert-danger">{error}</div>;

  return (
    <div className="card">
      <h2>Кредитори</h2>
      <table className="table" style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ textAlign: 'left' }}>Име</th>
            <th style={{ textAlign: 'left' }}>Тип</th>
            <th style={{ textAlign: 'right' }}>Риск скор</th>
            <th style={{ textAlign: 'right' }}>Нарушения</th>
            <th style={{ textAlign: 'center' }}>Статус</th>
          </tr>
        </thead>
        <tbody>
          {items.map(c => (
            <tr key={c.id} style={{ borderBottom: '1px solid #eee' }}>
              <td>{c.name}</td>
              <td>{c.type}</td>
              <td style={{ textAlign: 'right' }}>{c.risk_score?.toFixed(1)}</td>
              <td style={{ textAlign: 'right' }}>{c.violations_count}</td>
              <td style={{ textAlign: 'center' }}>{c.blacklisted ? <span className="risk-badge risk-critical">Черeн списък</span> : 'OK'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
