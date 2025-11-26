import React, { useState, useEffect } from 'react';
import { getRootStats, getLegalStats } from '../api/client';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [legalStats, setLegalStats] = useState(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const root = await getRootStats();
      setStats(root);
      const { data: legal } = await getLegalStats();
      setLegalStats(legal);
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
      {legalStats && (
        <div style={{ marginTop: '30px' }}>
          <h3>Правна база</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="number">{legalStats.total_documents}</div>
              <div className="label">Правни документи</div>
            </div>
            <div className="stat-card">
              <div className="number">{legalStats.total_articles}</div>
              <div className="label">Членове</div>
            </div>
            <div className="stat-card">
              <div className="number">{legalStats.total_tags}</div>
              <div className="label">Тагове</div>
            </div>
            <div className="stat-card">
              <div className="number">{legalStats.total_embeddings}</div>
              <div className="label">Семантични embedding-и</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
