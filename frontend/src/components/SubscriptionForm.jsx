import React, { useState } from 'react';
import { subscribeNewsletter } from '../api/client';
import Button from './ui/Button';
import Input from './ui/Input';
import Alert from './ui/Alert';

/**
 * Subscription form component with validation
 */
export default function SubscriptionForm() {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null); // 'success' | 'error' | null
  const [message, setMessage] = useState('');

  const validateEmail = (email) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!email.trim()) {
      setStatus('error');
      setMessage('Моля, въведете имейл адрес');
      return;
    }

    if (!validateEmail(email)) {
      setStatus('error');
      setMessage('Моля, въведете валиден имейл адрес');
      return;
    }

    setLoading(true);
    setStatus(null);
    setMessage('');

    try {
      await subscribeNewsletter({ email, name: name || undefined });
      setStatus('success');
      setMessage('Успешно се абонирахте! Проверете имейла си за потвърждение.');
      setEmail('');
      setName('');
    } catch (error) {
      setStatus('error');
      setMessage(
        error.response?.data?.detail || 
        'Възникна грешка. Моля, опитайте отново по-късно.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <Input
            type="text"
            placeholder="Вашето име (по избор)"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="flex-1 bg-white/10 border-white/30 text-white placeholder:text-white/70 focus:bg-white/20"
          />
          <Input
            type="email"
            placeholder="Вашият имейл адрес"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="flex-1 bg-white/10 border-white/30 text-white placeholder:text-white/70 focus:bg-white/20"
          />
        </div>
        
        <Button
          type="submit"
          disabled={loading}
          className="w-full bg-white text-blue-700 hover:bg-blue-50 font-semibold py-3 shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
        >
          {loading ? (
            <>
              <span className="inline-block animate-spin mr-2">⏳</span>
              Изпращане...
            </>
          ) : (
            <>
              <span className="mr-2">📧</span>
              Абонирайте се
            </>
          )}
        </Button>
      </form>

      {status && (
        <div className="mt-4">
          <Alert
            type={status === 'success' ? 'success' : 'error'}
            message={message}
            onClose={() => setStatus(null)}
          />
        </div>
      )}

      <p className="mt-4 text-sm text-blue-100 text-center">
        🔒 Вашите данни са защитени. Няма да споделяме вашия имейл с трети страни.
      </p>
    </div>
  );
}

