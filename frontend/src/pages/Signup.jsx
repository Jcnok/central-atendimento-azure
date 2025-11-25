import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

export default function Signup() {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { signup, loading, error } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        await signup(username, email, password);
    };

    return (
        <div className="glass-panel" style={{ padding: '2rem', maxWidth: '400px', margin: '4rem auto' }}>
            <h2 style={{ textAlign: 'center', marginBottom: '1.5rem' }}>Criar Conta</h2>

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
                        Email
                    </label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
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
                    {loading ? 'Criando conta...' : 'Cadastrar'}
                </button>
            </form>

            <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                Já tem uma conta? <Link to="/login" style={{ color: '#4facfe', textDecoration: 'none' }}>Entrar</Link>
            </p>
        </div>
    );
}
