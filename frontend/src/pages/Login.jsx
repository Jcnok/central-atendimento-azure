import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import styles from './Login.module.css';

export default function Login() {
    const [activeTab, setActiveTab] = useState('client'); // 'client' or 'admin'
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            // Determine endpoint based on tab
            const endpoint = activeTab === 'client' ? '/api/auth/login/client' : '/api/auth/login';

            // For admin, username field is expected, for client it's email (but form_data uses username key)
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Credenciais inválidas');
            }

            const data = await response.json();
            login(data.access_token);

            // Save user name for display
            if (data.user_name) {
                localStorage.setItem('user_name', data.user_name);
            }

            // Redirect based on role
            if (activeTab === 'client') {
                navigate('/support');
            } else {
                navigate('/dashboard');
            }

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.card}>
                <div className={styles.header}>
                    <h2>Bem-vindo de volta</h2>
                    <p>Acesse sua conta para continuar</p>
                </div>

                <div className={styles.tabs}>
                    <button
                        className={`${styles.tab} ${activeTab === 'client' ? styles.active : ''}`}
                        onClick={() => setActiveTab('client')}
                    >
                        Sou Cliente
                    </button>
                    <button
                        className={`${styles.tab} ${activeTab === 'admin' ? styles.active : ''}`}
                        onClick={() => setActiveTab('admin')}
                    >
                        Sou Colaborador
                    </button>
                </div>

                <form onSubmit={handleSubmit} className={styles.form}>
                    {error && <div className={styles.error}>{error}</div>}

                    <div className={styles.inputGroup}>
                        <label>{activeTab === 'client' ? 'E-mail ou CPF' : 'Usuário Corporativo'}</label>
                        <input
                            type="text"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            placeholder={activeTab === 'client' ? 'seu@email.com' : 'usuario.admin'}
                        />
                    </div>

                    <div className={styles.inputGroup}>
                        <label>Senha</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            placeholder="••••••••"
                        />
                    </div>

                    <button type="submit" className={styles.submitButton} disabled={loading}>
                        {loading ? 'Entrando...' : 'Entrar'}
                    </button>
                </form>

                {activeTab === 'client' && (
                    <div className={styles.footer}>
                        Ainda não é cliente? <a href="/">Conheça nossos planos</a>
                    </div>
                )}
            </div>
        </div>
    );
}
