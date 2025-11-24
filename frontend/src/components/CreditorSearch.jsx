import React, { useState } from 'react';
import { getCreditor } from '../api/client';

export default function CreditorSearch() {
  const [query, setQuery] = useState('');
  const [creditor, setCreditor] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const search = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setCreditor(null);

    try {
      const { data } = await getCreditor(query);
      setCreditor(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Кредиторът не е намерен');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Проверка на кредитор</h2>
      <form onSubmit={search}>
        <div className="form-group">
          <label>Име на кредитор</label>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Въведете име..."
          />
        </div>
        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Търсене...' : 'Провери'}
        </button>
      </form>

      {error && <div className="alert alert-danger">{error}</div>}

      {creditor && (
        <div style={{ marginTop: '30px' }}>
          <h3>{creditor.name}</h3>
          <p><strong>Тип:</strong> {creditor.type}</p>
          <p><strong>Нарушения:</strong> {creditor.violations_count}</p>
          <p><strong>Риск скор:</strong> {creditor.risk_score.toFixed(1)}/10</p>
          {creditor.blacklisted && (
            <div className="alert alert-danger">
              🚨 ВНИМАНИЕ: Този кредитор е в черния списък!
            </div>
          )}

          {creditor.violations.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <h4>Нарушения</h4>
              <ul className="violation-list">
                {creditor.violations.map((v, i) => (
                  <li key={i} className="violation-item">
                    <h4>{v.type}</h4>
                    <p><strong>Орган:</strong> {v.authority}</p>
                    <p><strong>Санкция:</strong> {v.penalty ? `${v.penalty.toFixed(2)} лв` : 'N/A'}</p>
                    <span className={`risk-badge risk-${v.severity}`}>{v.severity.toUpperCase()}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {creditor.unfair_clauses.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <h4>Неравноправни клаузи</h4>
              <ul className="violation-list">
                {creditor.unfair_clauses.map((c, i) => (
                  <li key={i} className="violation-item">
                    <h4>{c.type}</h4>
                    <p><strong>Основание:</strong> {c.legal_basis}</p>
                    {c.confirmed && <span className="risk-badge risk-critical">Потвърдена</span>}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
