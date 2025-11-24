import React, { useState, useEffect } from 'react';
import { getStats } from '../api/client';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const { data } = await getStats();
      setStats(data);
    } catch (error) {
      console.error('Stats error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Зареждане...</div>;
  if (!stats) return <div className="alert alert-danger">Грешка при зареждане на данни</div>;

  return (
    <div>
      <h2>Статистика</h2>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="number">{stats.creditors}</div>
          <div className="label">Кредитори в базата</div>
        </div>
        <div className="stat-card">
          <div className="number">{stats.violations}</div>
          <div className="label">Регистрирани нарушения</div>
        </div>
        <div className="stat-card">
          <div className="number">{stats.critical_violations}</div>
          <div className="label">Критични нарушения</div>
        </div>
        <div className="stat-card">
          <div className="number">{stats.court_cases}</div>
          <div className="label">Съдебни дела</div>
        </div>
        <div className="stat-card">
          <div className="number">{stats.unfair_clauses}</div>
          <div className="label">Неравноправни клаузи</div>
        </div>
      </div>
    </div>
  );
}
