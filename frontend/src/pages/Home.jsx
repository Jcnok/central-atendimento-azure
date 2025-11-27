import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styles from './Home.module.css';

export default function Home() {
    const navigate = useNavigate();
    const [showChatBalloon, setShowChatBalloon] = useState(true);
    const [planos, setPlanos] = useState([]);
    const [showChatWidget, setShowChatWidget] = useState(false);
    const [chatInput, setChatInput] = useState('');
    const [chatMessages, setChatMessages] = useState([
        { type: 'bot', text: 'Olá! Sou a assistente virtual da Central Inteligente. Como posso te ajudar hoje?' }
    ]);
    const [loadingChat, setLoadingChat] = useState(false);

    useEffect(() => {
        fetchPlanos();
    }, []);

    const fetchPlanos = async () => {
        try {
            const response = await fetch('/api/planos/');
            if (response.ok) {
                const data = await response.json();
                setPlanos(data);
            }
        } catch (error) {
            console.error("Erro ao buscar planos:", error);
        }
    };

    const handleChatSubmit = async (e) => {
        e.preventDefault();
        if (!chatInput.trim()) return;

        const userMsg = chatInput;
        setChatMessages(prev => [...prev, { type: 'user', text: userMsg }]);
        setChatInput('');
        setLoadingChat(true);

        try {
            // Use public endpoint if available or standard chat endpoint without auth?
            // Since we implemented optional auth in /api/chat, we can use it.
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMsg })
            });

            const data = await response.json();
            setChatMessages(prev => [...prev, { type: 'bot', text: data.response }]);
        } catch (error) {
            setChatMessages(prev => [...prev, { type: 'bot', text: "Erro de conexão. Tente novamente." }]);
        } finally {
            setLoadingChat(false);
        }
    };

    return (
        <div className={styles.container}>
            {/* Header */}
            <header className={styles.header}>
                <div className={styles.logo}>Central<span className={styles.logoHighlight}>Inteligente</span></div>
                <nav className={styles.nav}>
                    <a href="#planos">Planos</a>
                    <a href="#" onClick={() => setShowChatWidget(true)}>Ajuda</a>
                </nav>
                <div className={styles.authButtons}>
                    <Link to="/login" className={styles.loginButton}>Minha Conta</Link>
                </div>
            </header>

            {/* Hero Section */}
            <section className={styles.hero}>
                <div className={styles.heroContent}>
                    <h1>O futuro da conexão chegou.</h1>
                    <p>Internet Fibra, 5G e TV 4K com a melhor experiência de atendimento do Brasil.</p>
                    <button className={styles.ctaButton} onClick={() => document.getElementById('planos').scrollIntoView({ behavior: 'smooth' })}>
                        Conheça os Planos
                    </button>
                </div>
            </section>

            {/* Plans Section */}
            <section id="planos" className={styles.plansSection}>
                <h2>Escolha o plano ideal para você</h2>
                <div className={styles.plansGrid}>
                    {planos.length > 0 ? planos.map(plano => (
                        <div key={plano.plano_id} className={`${styles.planCard} ${plano.velocidade.includes('1GB') ? styles.featured : ''}`}>
                            {plano.velocidade.includes('1GB') && <div className={styles.badge}>MAIS VENDIDO</div>}
                            <h3>{plano.nome}</h3>
                            <div className={styles.speed}>{plano.velocidade}</div>
                            <div className={styles.price}>R$ {plano.preco}<span>/mês</span></div>
                            <ul>
                                <li>{plano.descricao}</li>
                                <li>Instalação Grátis</li>
                            </ul>
                            <button className={styles.planButton}>Assinar</button>
                        </div>
                    )) : (
                        <p>Carregando planos...</p>
                    )}
                </div>
            </section>

            {/* Chat Balloon */}
            {showChatBalloon && !showChatWidget && (
                <div className={styles.chatBalloon}>
                    <div className={styles.balloonHeader}>
                        <button onClick={() => setShowChatBalloon(false)}>×</button>
                    </div>
                    <div className={styles.balloonContent}>
                        <p><strong>Oi! Precisa de ajuda?</strong></p>
                        <p>Posso te ajudar a consultar faturas, tirar dúvidas e muito mais.</p>
                        <button onClick={() => setShowChatWidget(true)} className={styles.balloonLink}>
                            Acessar Atendimento
                        </button>
                    </div>
                </div>
            )}

            {/* Public Chat Widget Modal */}
            {showChatWidget && (
                <div className={styles.chatWidgetOverlay}>
                    <div className={styles.chatWidget}>
                        <div className={styles.chatWidgetHeader}>
                            <h3>Atendimento Online</h3>
                            <button onClick={() => setShowChatWidget(false)}>×</button>
                        </div>
                        <div className={styles.chatWidgetMessages}>
                            {chatMessages.map((msg, idx) => (
                                <div key={idx} className={`${styles.chatMsg} ${msg.type === 'user' ? styles.userMsg : styles.botMsg}`}>
                                    {msg.text}
                                </div>
                            ))}
                            {loadingChat && <div className={styles.loading}>Digitando...</div>}
                        </div>
                        <form onSubmit={handleChatSubmit} className={styles.chatWidgetInput}>
                            <input
                                value={chatInput}
                                onChange={e => setChatInput(e.target.value)}
                                placeholder="Digite sua dúvida..."
                            />
                            <button type="submit">➤</button>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
