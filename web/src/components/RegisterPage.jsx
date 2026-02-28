import React, { useState } from 'react';
import { useAuth } from '../contexts/useAuth';

export default function RegisterPage({ onSwitchToLogin }) {
  const { register } = useAuth();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (password.length < 6) {
      setError('Sifre en az 6 karakter olmalidir');
      return;
    }
    setLoading(true);
    try {
      await register(email, fullName, password);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-logo">
          <div className="app-logo-icon">DV</div>
          <h1>DROV Engineering</h1>
          <p>Yeni hesap olusturun</p>
        </div>
        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="auth-error">{error}</div>}
          <div className="auth-field">
            <label>Ad Soyad</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Ad Soyad"
              required
            />
          </div>
          <div className="auth-field">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="ornek@firma.com"
              required
            />
          </div>
          <div className="auth-field">
            <label>Sifre</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="En az 6 karakter"
              required
              minLength={6}
            />
          </div>
          <button type="submit" className="auth-submit" disabled={loading}>
            {loading ? 'Kayit yapiliyor...' : 'Kayit Ol'}
          </button>
        </form>
        <div className="auth-switch">
          Zaten hesabiniz var mi?{' '}
          <button onClick={onSwitchToLogin}>Giris Yap</button>
        </div>
      </div>
    </div>
  );
}
