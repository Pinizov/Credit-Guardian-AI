import React, { useState } from 'react';
import { calculateGPR, verifyGPR } from '../api/client';

export default function GPRCalculator() {
  const [showHelp, setShowHelp] = useState(true);
  const [formData, setFormData] = useState({
    amount: '',
    total_repayment: '',
    term_months: '',
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const calculate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const payload = {
        amount: parseFloat(formData.amount),
        total_repayment: parseFloat(formData.total_repayment),
        term_months: parseInt(formData.term_months),
        fees: []
      };
      const { data } = await calculateGPR(payload);
      setResult(data);
    } catch (error) {
      console.error('GPR calc error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Калкулатор на ГПР</h2>
      <form onSubmit={calculate}>
        <div className="form-group">
          <label>Размер на кредита (лв)</label>
          <input
            type="number"
            name="amount"
            value={formData.amount}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label>Обща сума за връщане (лв)</label>
          <input
            type="number"
            name="total_repayment"
            value={formData.total_repayment}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label>Срок (месеци)</label>
          <input
            type="number"
            name="term_months"
            value={formData.term_months}
            onChange={handleChange}
            required
          />
        </div>
        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Изчисляване...' : 'Изчисли ГПР'}
        </button>
      </form>

      {result && (
        <div style={{ marginTop: '30px' }}>
          <div className="alert alert-info">
            <h3>Резултати</h3>
            <p><strong>ГПР (опростен):</strong> {result.gpr_simple.toFixed(2)}%</p>
            <p><strong>ГПР (точен):</strong> {result.gpr_exact.toFixed(2)}%</p>
            <p><strong>Общо оскъпяване:</strong> {result.overpayment.toFixed(2)} лв ({result.overpayment_percent.toFixed(2)}%)</p>
            <p><strong>Месечна вноска:</strong> {result.breakdown.monthly_payment.toFixed(2)} лв</p>
          </div>
        </div>
      )}
    </div>
  );
}
