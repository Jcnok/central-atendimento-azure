import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export default function LoginForm() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const { login, loading, error } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        await login(username, password);
    };

    return (
        <div className="glass-panel" style={{ padding: '2rem', maxWidth: '400px', margin: '2rem auto' }}>
            <h2 style={{ textAlign: 'center', marginBottom: '1.5rem' }}>Login</h2>

            {error && (
                <div style={{
                    background: 'rgba(255, 0, 0, 0.1)',
                    border: '1px solid rgba(255, 0, 0, 0.2)',
                    color: '#ff6b6b',
                    padding: '0.75rem',
                    borderRadius: '8px',
                    marginBottom: '1rem',
                    fontSize: '0.9rem'
                }}>
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                        Usuário
                    </label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                        style={{
                            width: '100%',
                            padding: '10px',
                            borderRadius: '8px',
                            border: '1px solid var(--glass-border)',
                            background: 'rgba(255, 255, 255, 0.05)',
                            color: 'white',
                            outline: 'none',
                            boxSizing: 'border-box'
                        }}
                    />
                </div>

                <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                        Senha
                    </label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        style={{
                            width: '100%',
                            padding: '10px',
                            borderRadius: '8px',
                            border: '1px solid var(--glass-border)',
                            background: 'rgba(255, 255, 255, 0.05)',
                            color: 'white',
                            outline: 'none',
                            boxSizing: 'border-box'
                        }}
                    />
                </div>

                <button
                    type="submit"
                    className="btn-primary"
                    disabled={loading}
                    style={{ marginTop: '1rem', opacity: loading ? 0.7 : 1 }}
                >
                    {loading ? 'Entrando...' : 'Entrar'}
                </button>
            </form>

            <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                Não tem conta? <a href="/signup" style={{ color: '#4facfe', textDecoration: 'none' }}>Cadastre-se</a>
            </p>

            <div style={{ marginTop: '2rem', paddingTop: '1rem', borderTop: '1px solid var(--glass-border)', textAlign: 'center' }}>
                <a href="/support" style={{ color: 'white', textDecoration: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                    <span>🎧</span> Precisa de ajuda? Fale com a IA
                </a>
            </div>
        </div>
    );
}

