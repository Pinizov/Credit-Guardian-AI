import React, { useState } from 'react';
import { analyzeContract } from '../api/client';

export default function ContractAnalyzer() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const analyze = async () => {
    if (!file) {
      setError('Моля изберете файл');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const { data } = await analyzeContract(file);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Грешка при анализ на договора');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level) => {
    const colors = {
      low: 'success',
      medium: 'warning',
      high: 'danger',
      critical: 'danger'
    };
    return colors[level] || 'info';
  };

  return (
    <div className="card">
      <h2>Анализ на договор</h2>
      
      <div className="upload-zone" onClick={() => document.getElementById('fileInput').click()}>
        <input
          id="fileInput"
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={handleFileChange}
        />
        <p>{file ? `Избран: ${file.name}` : 'Кликнете за избор на файл (PDF, DOCX, TXT)'}</p>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <button
        onClick={analyze}
        className="btn"
        disabled={loading || !file}
        style={{ marginTop: '20px' }}
      >
        {loading ? 'Анализиране...' : 'Анализирай'}
      </button>

      {result && (
        <div style={{ marginTop: '30px' }}>
          <div className={`alert alert-${getRiskColor(result.risk_level)}`}>
            <h3>Анализ завършен</h3>
            <p><strong>Кредитор:</strong> {result.creditor}</p>
            <p><strong>Размер:</strong> {result.amount.toFixed(2)} лв</p>
            <p><strong>ГПР (декларирано):</strong> {result.declared_gpr.toFixed(2)}%</p>
            <p><strong>Ниво на риск:</strong> <span className={`risk-badge risk-${result.risk_level}`}>{result.risk_level.toUpperCase()}</span></p>
          </div>

          {result.gpr_verification && !result.gpr_verification.is_correct && (
            <div className="alert alert-danger">
              ⚠️ <strong>НЕСЪОТВЕТСТВИЕ В ГПР!</strong>
              <p>Декларирано: {result.gpr_verification.declared_gpr.toFixed(2)}%</p>
              <p>Изчислено: {result.gpr_verification.calculated_gpr.toFixed(2)}%</p>
              <p>Разлика: {result.gpr_verification.difference.toFixed(3)}%</p>
            </div>
          )}

          {result.illegal_fees && result.illegal_fees.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <h4>⚠️ Незаконни такси</h4>
              <ul className="violation-list">
                {result.illegal_fees.map((fee, i) => (
                  <li key={i} className="violation-item">
                    <h4>{fee.name}</h4>
                    <p><strong>Сума:</strong> {fee.amount.toFixed(2)} лв</p>
                    <p><strong>Основание:</strong> {fee.legal_basis}</p>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.unfair_clauses && result.unfair_clauses.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <h4>📋 Неравноправни клаузи ({result.unfair_clauses.length})</h4>
              <ul className="violation-list">
                {result.unfair_clauses.slice(0, 5).map((clause, i) => (
                  <li key={i} className="violation-item">
                    <h4>{clause.type}</h4>
                    <p><em>"{clause.text.substring(0, 150)}..."</em></p>
                    <p><strong>Основание:</strong> {clause.legal_basis}</p>
                    <span className={`risk-badge risk-${clause.severity}`}>{clause.severity.toUpperCase()}</span>
                  </li>
                ))}
              </ul>
              {result.unfair_clauses.length > 5 && (
                <p style={{ color: '#657786', marginTop: '10px' }}>
                  + още {result.unfair_clauses.length - 5} клаузи
                </p>
              )}
            </div>
          )}

          {result.clause_risk && (
            <div className="alert alert-info" style={{ marginTop: '20px' }}>
              <h4>Препоръка</h4>
              <p>{result.clause_risk.recommendation}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
