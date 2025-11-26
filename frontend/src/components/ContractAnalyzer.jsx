import React, { useState } from 'react';
import { analyzeContractFull, analyzeContractSimple, exportComplaintPdf } from '../api/client';

export default function ContractAnalyzer() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [complaintId, setComplaintId] = useState(null);
  const [useFull, setUseFull] = useState(true);
  const [userFields, setUserFields] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    egn: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleFieldChange = (e) => {
    const { name, value } = e.target;
    setUserFields(f => ({ ...f, [name]: value }));
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
      let data;
      if (useFull) {
        const response = await analyzeContractFull(file, userFields);
        data = response.data;
        setComplaintId(data.complaint_id || null);
        setResult(data.analysis || data); // store full analysis portion
      } else {
        const response = await analyzeContractSimple(file);
        data = response.data;
        setResult(data);
      }
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
      <h2>📄 Анализ на кредитен договор</h2>
      
      <div className="welcome-message" style={{backgroundColor: '#e3f2fd', padding: '20px', borderRadius: '8px', marginBottom: '20px'}}>
        <h3 style={{margin: '0 0 10px 0', color: '#1976d2'}}>👋 Добре дошли в Credit Guardian!</h3>
        <p style={{margin: '5px 0', lineHeight: '1.6'}}>
          Качете вашия кредитен договор и нашият AI агент ще анализира:
        </p>
        <ul style={{marginLeft: '20px', lineHeight: '1.8'}}>
          <li>✅ Правилност на ГПР (Годишен процент на разходите)</li>
          <li>⚠️ Неравноправни клаузи и забранени условия</li>
          <li>💰 Незаконни такси и скрити разходи</li>
          <li>🔍 История на нарушения от кредитора</li>
          <li>📋 Съответствие със Закона за потребителския кредит</li>
        </ul>
        <p style={{margin: '10px 0 0 0', fontSize: '14px', color: '#666'}}>
          💡 <strong>Съвет:</strong> Подгответе договора в PDF, DOCX или TXT формат за най-добри резултати.
        </p>
      </div>
      
      <div className="upload-zone" onClick={() => document.getElementById('fileInput').click()}>
        <input
          id="fileInput"
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={handleFileChange}
        />
        <p>{file ? `✅ Избран: ${file.name}` : '📎 Кликнете за избор на файл (PDF, DOCX, TXT)'}</p>
        {!file && <p style={{fontSize: '14px', color: '#888', marginTop: '10px'}}>или плъзнете файл тук</p>}
      </div>

      <div style={{ marginTop: '20px' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <input type="checkbox" checked={useFull} onChange={() => setUseFull(v => !v)} /> Пълен AI анализ (запис в база + жалба)
        </label>
      </div>

      {useFull && (
        <div className="form-grid" style={{ marginTop: '15px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(220px,1fr))', gap: '12px' }}>
          <div>
            <label>Име</label>
            <input name="name" value={userFields.name} onChange={handleFieldChange} placeholder="Вашето име" />
          </div>
          <div>
            <label>Email</label>
            <input name="email" value={userFields.email} onChange={handleFieldChange} placeholder="email@пример.bg" />
          </div>
          <div>
            <label>Телефон</label>
            <input name="phone" value={userFields.phone} onChange={handleFieldChange} placeholder="08xx..." />
          </div>
            <div>
            <label>Адрес</label>
            <input name="address" value={userFields.address} onChange={handleFieldChange} placeholder="гр. София..." />
          </div>
          <div>
            <label>ЕГН</label>
            <input name="egn" value={userFields.egn} onChange={handleFieldChange} placeholder="**********" />
          </div>
        </div>
      )}

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
          <div className={`alert alert-${getRiskColor(result.risk_level || result.risk_level_estimate || 'medium')}`}>
            <h3>Анализ завършен</h3>
            <p><strong>Кредитор:</strong> {result.creditor || result.creditor_name || 'Неизвестен'}</p>
            {result.amount && <p><strong>Размер:</strong> {Number(result.amount).toFixed(2)} лв</p>}
            {(result.declared_gpr || result.stated_apr) && <p><strong>ГПР (декларирано):</strong> {(result.declared_gpr || result.stated_apr).toFixed(2)}%</p>}
            {(result.calculated_real_apr || result.calculated_apr) && <p><strong>ГПР (изчислено):</strong> {(result.calculated_real_apr || result.calculated_apr).toFixed(2)}%</p>}
            {(result.risk_level || result.risk_level_estimate) && (
              <p><strong>Ниво на риск:</strong> <span className={`risk-badge risk-${(result.risk_level || result.risk_level_estimate)}`}>{(result.risk_level || result.risk_level_estimate).toUpperCase()}</span></p>
            )}
          </div>

          {complaintId && (
            <div style={{ marginTop: '15px' }}>
              <button className="btn" onClick={() => exportComplaintPdf(complaintId)}>⬇️ Изтегли жалбата (PDF)</button>
            </div>
          )}

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
