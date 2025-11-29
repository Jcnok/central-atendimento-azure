import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import styles from './Support.module.css';

export default function Support() {
    const { user, token, logout } = useAuth();
    const navigate = useNavigate();
    const userName = localStorage.getItem('user_name') || user?.sub?.split('@')[0] || 'Cliente';

    const [messages, setMessages] = useState([
        { type: 'bot', text: `Olá, ${userName}! Sou sua assistente virtual. Como posso ajudar com seus planos hoje?` }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [sessionId] = useState(() => 'session-' + Math.random().toString(36).substr(2, 9));

    const [contracts, setContracts] = useState([]);
    const [invoices, setInvoices] = useState([]);
    const [tickets, setTickets] = useState([]);

    const messagesEndRef = useRef(null);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            const headers = { 'Authorization': `Bearer ${token}` };
            console.log("Fetching dashboard summary...");

            const response = await fetch('/api/clientes/me/resumo', { headers });

            if (response.status === 401) {
                console.warn("Session expired or unauthorized. Redirecting to login.");
                logout();
                navigate('/login');
                return;
            }

            if (response.ok) {
                const data = await response.json();
                console.log("Summary Data:", data);

                // Map Plan to Contracts format
                if (data.plano_ativo) {
                    setContracts([{
                        id: data.plano_ativo.plano_id,
                        plan: data.plano_ativo.nome,
                        velocidade: data.plano_ativo.velocidade,
                        preco: data.plano_ativo.preco,
                        status: 'ativo'
                    }]);
                } else {
                    setContracts([]);
                }

                // Map Invoices
                if (data.faturas_pendentes) {
                    setInvoices(data.faturas_pendentes.map(f => ({
                        id: f.fatura_id,
                        valor: f.valor,
                        vencimento: f.data_vencimento,
                        status: f.status
                    })));
                }

                // Map Tickets
                if (data.ultimos_chamados) {
                    setTickets(data.ultimos_chamados.map(t => ({
                        id: t.id,
                        assunto: t.mensagem ? (t.mensagem.substring(0, 30) + '...') : 'Sem assunto',
                        status: t.status,
                        data: t.data_criacao
                    })));
                }
            }
        } catch (error) {
            console.error("Erro ao buscar dados do dashboard:", error);
        }
    };

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

            // Check for success keywords to trigger data refresh
            const lowerResponse = data.response.toLowerCase();
            if (lowerResponse.includes('sucesso') ||
                lowerResponse.includes('atualizado') ||
                lowerResponse.includes('realizado') ||
                lowerResponse.includes('protocolo')) {
                console.log("Action detected, refreshing dashboard data...");
                fetchDashboardData();
            }

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
        alert(`Obrigado pela avaliação: ${npsScore}`);
        setShowNPS(false);
        navigate('/'); // Redirect to Home after finishing
    };

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className={styles.container}>
            {/* Sidebar */}
            <aside className={styles.sidebar}>
                <div className={styles.logo}>Central<span className={styles.highlight}>Inteligente</span></div>

                <div className={styles.userInfo}>
                    <div className={styles.avatar}>{userName.charAt(0).toUpperCase()}</div>
                    <div className={styles.userDetails}>
                        <span className={styles.userName}>{userName}</span>
                        <span className={styles.userRole}>Cliente</span>
                    </div>
                </div>

                <div className={styles.sidebarContent}>
                    {/* Card: Meus Serviços */}
                    <div className={styles.card}>
                        <h3>Meus Serviços</h3>
                        <div className={styles.cardList}>
                            {contracts.length > 0 ? contracts.map(c => (
                                <div key={c.id} className={styles.cardItem}>
                                    <div className={styles.cardHeader}>
                                        <span className={styles.planName}>{c.plan}</span>
                                        <span className={`${styles.statusDot} ${styles[c.status]}`}></span>
                                    </div>
                                    <div className={styles.planDetail}>{c.velocidade} - R$ {c.preco}</div>
                                </div>
                            )) : (
                                <div className={styles.emptyState}>Nenhum serviço ativo</div>
                            )}
                        </div>
                    </div>

                    {/* Card: Faturas */}
                    <div className={styles.card}>
                        <h3>Faturas em Aberto</h3>
                        <div className={styles.cardList}>
                            {invoices.filter(i => i.status === 'pendente').length > 0 ?
                                invoices.filter(i => i.status === 'pendente').map(f => (
                                    <div key={f.id} className={styles.cardItem}>
                                        <div className={styles.cardHeader}>
                                            <span className={styles.invoiceIcon}>📄</span>
                                            <span className={styles.planName}>Vence {f.vencimento}</span>
                                        </div>
                                        <div className={styles.planDetail}>R$ {f.valor.toFixed(2)}</div>
                                    </div>
                                )) : (
                                    <div className={styles.emptyState}>Nenhuma fatura pendente</div>
                                )}
                        </div>
                    </div>

                    {/* Card: Chamados */}
                    <div className={styles.card}>
                        <h3>Últimos Chamados</h3>
                        <div className={styles.cardList}>
                            {tickets.length > 0 ? tickets.map(t => (
                                <div key={t.id} className={styles.cardItem}>
                                    <div className={styles.cardHeader}>
                                        <span className={styles.planName}>{t.assunto}</span>
                                        <span className={`${styles.statusDot} ${t.status === 'aberto' ? styles.pendente : styles.pago}`}></span>
                                    </div>
                                    <div className={styles.planDetail}>{t.data} - {t.status}</div>
                                </div>
                            )) : (
                                <div className={styles.emptyState}>Nenhum chamado recente</div>
                            )}
                        </div>
                    </div>
                </div>

                <button onClick={handleLogout} className={styles.logoutButton}>Sair</button>
            </aside>

            {/* Main Chat Area */}
            <main className={styles.main}>
                <div className={styles.chatHeader}>
                    <div>
                        <h2>Atendimento Virtual</h2>
                        <div className={styles.platformFlags}>
                            <span className={styles.flag} title="Você está no Site">🌐 Site</span>
                        </div>
                    </div>
                    <button onClick={handleFinish} className={styles.finishButton}>Finalizar Atendimento</button>
                </div>

                <div className={styles.messagesArea}>
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`${styles.messageRow} ${msg.type === 'user' ? styles.userRow : styles.botRow}`}>
                            <div className={`${styles.message} ${msg.type === 'user' ? styles.userMessage : styles.botMessage}`}>
                                {msg.type === 'bot' ? (
                                    <ReactMarkdown>{msg.text}</ReactMarkdown>
                                ) : (
                                    msg.text
                                )}
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
