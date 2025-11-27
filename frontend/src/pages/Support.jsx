import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import styles from './Support.module.css';

export default function Support() {
    const { user, token, logout } = useAuth();
    const [messages, setMessages] = useState([
        { type: 'bot', text: `Olá, ${user?.sub?.split('@')[0] || 'Cliente'}! Sou sua assistente virtual. Como posso ajudar com seus planos hoje?` }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [sessionId] = useState(() => 'session-' + Math.random().toString(36).substr(2, 9));
    const messagesEndRef = useRef(null);

    // Mock Data for Sidebar (In a real app, fetch from API)
    const contracts = [
        { id: 1, plan: 'Internet Fibra 500MB', status: 'Ativo' },
        { id: 2, plan: 'Móvel 5G', status: 'Ativo' }
    ];

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = input;
        setMessages(prev => [...prev, { type: 'user', text: userMessage }]);
        setInput('');
        setLoading(true);

        try {
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    message: userMessage,
                    session_id: sessionId
                })
            });

            if (!response.ok) {
                throw new Error('Erro na comunicação com o servidor');
            }

            const data = await response.json();

            setMessages(prev => [...prev, {
                type: 'bot',
                text: data.response
            }]);

        } catch (err) {
            console.error(err);
            setMessages(prev => [...prev, { type: 'bot', text: 'Desculpe, tive um problema técnico. Tente novamente em instantes.' }]);
        } finally {
            setLoading(false);
        }
    };

    const [showNPS, setShowNPS] = useState(false);
    const [npsScore, setNpsScore] = useState(0);

    const handleFinish = () => {
        setShowNPS(true);
    };

    const submitNPS = () => {
        // In a real app, send to backend
        alert(`Obrigado pela avaliação: ${npsScore}`);
        setShowNPS(false);
        setMessages(prev => [...prev, { type: 'bot', text: 'Atendimento finalizado. Obrigado!' }]);
    };

    return (
        <div className={styles.container}>
            {/* Sidebar */}
            <aside className={styles.sidebar}>
                <div className={styles.logo}>Central<span className={styles.highlight}>Inteligente</span></div>

                <div className={styles.userInfo}>
                    <div className={styles.avatar}>{user?.sub?.charAt(0).toUpperCase()}</div>
                    <div className={styles.userDetails}>
                        <span className={styles.userName}>{user?.sub}</span>
                        <span className={styles.userRole}>Cliente</span>
                    </div>
                </div>

                <nav className={styles.nav}>
                    <h3>Meus Serviços</h3>
                    <ul>
                        {contracts.map(c => (
                            <li key={c.id} className={styles.navItem}>
                                <span className={styles.statusDot}></span>
                                {c.plan}
                            </li>
                        ))}
                    </ul>

                    <h3>Atalhos</h3>
                    <ul>
                        <li>📄 Segunda via de Fatura</li>
                        <li>🔧 Suporte Técnico</li>
                        <li>💳 Alterar Forma de Pagamento</li>
                    </ul>
                </nav>

                <button onClick={logout} className={styles.logoutButton}>Sair</button>
            </aside>

            {/* Main Chat Area */}
            <main className={styles.main}>
                <div className={styles.chatHeader}>
                    <div>
                        <h2>Atendimento Virtual</h2>
                        <div className={styles.platformFlags}>
                            <span className={styles.flag} title="Você está no Site">🌐 Site</span>
                            {/* Mock flags for other channels */}
                            {/* <span className={styles.flag}>📱 WhatsApp</span> */}
                        </div>
                    </div>
                    <button onClick={handleFinish} className={styles.finishButton}>Finalizar Atendimento</button>
                </div>

                <div className={styles.messagesArea}>
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`${styles.messageRow} ${msg.type === 'user' ? styles.userRow : styles.botRow}`}>
                            <div className={`${styles.message} ${msg.type === 'user' ? styles.userMessage : styles.botMessage}`}>
                                {msg.text}
                            </div>
                        </div>
                    ))}
                    {loading && <div className={styles.loading}>Digitando...</div>}
                    <div ref={messagesEndRef} />
                </div>

                <form onSubmit={handleSend} className={styles.inputArea}>
                    <div className={styles.inputWrapper}>
                        <input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Digite sua mensagem..."
                            disabled={loading}
                        />
                        <button type="submit" disabled={loading || !input.trim()}>
                            ➤
                        </button>
                    </div>
                </form>

                {/* NPS Modal */}
                {showNPS && (
                    <div className={styles.modalOverlay}>
                        <div className={styles.modal}>
                            <h3>Como foi seu atendimento?</h3>
                            <p>De 0 a 10, qual a probabilidade de você recomendar nossa empresa?</p>
                            <div className={styles.npsGrid}>
                                {[...Array(11).keys()].map(num => (
                                    <button
                                        key={num}
                                        className={`${styles.npsButton} ${npsScore === num ? styles.selected : ''}`}
                                        onClick={() => setNpsScore(num)}
                                    >
                                        {num}
                                    </button>
                                ))}
                            </div>
                            <div className={styles.modalActions}>
                                <button onClick={() => setShowNPS(false)} className={styles.cancelButton}>Cancelar</button>
                                <button onClick={submitNPS} className={styles.submitButton}>Enviar Avaliação</button>
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
