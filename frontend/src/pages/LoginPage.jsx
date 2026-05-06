import { useState } from 'react';
import { login } from '../api/client.js';

export function LoginPage({ onLogin }) {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  async function submit(event) {
    event.preventDefault();
    setError('');
    try {
      await login(password);
      onLogin();
    } catch (err) {
      setError(err.message);
    }
  }
  return (
    <section className="login-page">
      <form onSubmit={submit} className="login-card">
        <p className="eyebrow">Private market replay</p>
        <h1>Tang Strategy Console</h1>
        <p>Enter the readonly or admin password to access charts, strategies, review, and statistics.</p>
        <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Access password" autoFocus />
        {error && <div className="error">{error}</div>}
        <button type="submit">Enter workspace</button>
      </form>
    </section>
  );
}
