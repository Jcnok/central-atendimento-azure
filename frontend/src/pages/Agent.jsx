import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import styles from './Dashboard.module.css';
import ReactMarkdown from 'react-markdown';

export default function Agent() {
    const { token } = useAuth();
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'Olá! Sou o Agente Admin. Posso analisar dados e gerar relatórios para você. Como posso ajudar?' }
    ]);
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const res = await fetch('/api/agent/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    query: input,
                    agent_type: 'crm'
                })
            });

            const data = await res.json();
            setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
        } catch (error) {
            console.error("Error calling agent:", error);
            setMessages(prev => [...prev, { role: 'assistant', content: "Desculpe, tive um erro ao processar sua solicitação." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
            <h2 style={{ marginBottom: '1.5rem' }}>Agente IA - CRM</h2>

            <div className="glass-panel" style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden',
                padding: 0
            }}>
                {/* Chat History */}
                <div style={{
                    flex: 1,
                    overflowY: 'auto',
                    padding: '2rem',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '1.5rem'
                }}>
                    {messages.length <= 1 && (
                        <div style={{
                            textAlign: 'center',
                            color: 'var(--text-secondary)',
                            marginTop: '2rem'
                        }}>
                            <h3>Olá! Como posso ajudar com os dados hoje?</h3>
                            <p>Exemplos de perguntas:</p>
                            <div style={{
                                display: 'flex',
                                gap: '1rem',
                                justifyContent: 'center',
                                flexWrap: 'wrap',
                                marginTop: '1rem'
                            }}>
                                {['Qual a economia total com IA?', 'Gere um relatório gerencial', 'Qual a taxa de churn atual?', 'Compare o custo IA vs Humano'].map((ex, i) => (
                                    <button
                                        key={i}
                                        onClick={() => setInput(ex)}
                                        style={{
                                            background: 'rgba(255,255,255,0.05)',
                                            border: '1px solid var(--glass-border)',
                                            padding: '8px 16px',
                                            borderRadius: '20px',
                                            color: 'var(--text-primary)',
                                            cursor: 'pointer',
                                            fontSize: '0.9rem'
                                        }}
                                    >
                                        {ex}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {messages.map((msg, index) => (
                        <div key={index} style={{
                            alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                            maxWidth: '80%',
                            background: msg.role === 'user'
                                ? 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)'
                                : 'rgba(30, 41, 59, 0.8)',
                            padding: '1rem 1.5rem',
                            borderRadius: '12px',
                            borderTopRightRadius: msg.role === 'user' ? '2px' : '12px',
                            borderTopLeftRadius: msg.role === 'assistant' ? '2px' : '12px',
                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                            border: msg.role === 'assistant' ? '1px solid var(--glass-border)' : 'none'
                        }}>
                            <div style={{
                                fontWeight: 'bold',
                                marginBottom: '0.5rem',
                                fontSize: '0.8rem',
                                opacity: 0.8
                            }}>
                                {msg.role === 'user' ? 'Você' : 'Agente CRM'}
                            </div>
                            <div style={{ lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>
                                {msg.role === 'assistant' ? (
                                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                                ) : (
                                    msg.content
                                )}
                            </div>
                        </div>
                    ))}

                    {loading && (
                        <div style={{ alignSelf: 'flex-start', padding: '1rem', color: 'var(--text-secondary)' }}>
                            Digitando...
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div style={{
                    padding: '1.5rem',
                    background: 'rgba(0, 0, 0, 0.2)',
                    borderTop: '1px solid var(--glass-border)'
                }}>
                    <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '1rem' }}>
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Digite sua pergunta sobre os dados..."
                            style={{
                                flex: 1,
                                padding: '12px 16px',
                                borderRadius: '8px',
                                border: '1px solid var(--glass-border)',
                                background: 'rgba(255, 255, 255, 0.05)',
                                color: 'white',
                                fontSize: '1rem'
                            }}
                            disabled={loading}
                        />
                        <button
                            type="submit"
                            disabled={loading || !input.trim()}
                            className="btn-primary"
                            style={{ padding: '0 24px' }}
                        >
                            {loading ? '...' : 'Enviar'}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}
