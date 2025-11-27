import { useState, useRef, useEffect } from 'react';
import styles from './ChatWidget.module.css';

export default function ChatWidget() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { type: 'bot', text: 'Olá! Sou a IA da Central de Atendimento. Posso ajudar com boletos, suporte técnico, vendas ou dúvidas gerais. Como posso ajudar hoje?' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    // Generate session ID on mount
    const [sessionId] = useState(() => 'session-' + Math.random().toString(36).substr(2, 9));

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isOpen]);

    useEffect(() => {
        if (isOpen && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isOpen]);

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

    return (
        <div className={styles.chatContainer}>
            {/* Chat Window */}
            {isOpen && (
                <div className={styles.glassPanel} role="dialog" aria-label="Assistente Virtual">
                    <div className={styles.header}>
                        <span className={styles.headerTitle}>Assistente Virtual</span>
                        <button
                            onClick={() => setIsOpen(false)}
                            className={styles.closeButton}
                            aria-label="Fechar chat"
                        >
                            ×
                        </button>
                    </div>

                    <div className={styles.messagesArea} role="log" aria-live="polite">
                        {messages.map((msg, idx) => (
                            <div
                                key={idx}
                                className={`${styles.message} ${msg.type === 'user' ? styles.userMessage : styles.botMessage}`}
                            >
                                {msg.text}
                            </div>
                        ))}
                        {loading && <div className={styles.loading}>Digitando...</div>}
                        <div ref={messagesEndRef} />
                    </div>

                    <form onSubmit={handleSend} className={styles.inputForm}>
                        <input
                            ref={inputRef}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Digite o protocolo..."
                            className={styles.input}
                            aria-label="Digite sua mensagem"
                            disabled={loading}
                        />
                        <button
                            type="submit"
                            disabled={loading || !input.trim()}
                            className={styles.sendButton}
                            aria-label="Enviar mensagem"
                        >
                            ➤
                        </button>
                    </form>
                </div>
            )}

            {/* Floating Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={styles.toggleButton}
                aria-label={isOpen ? "Fechar chat" : "Abrir chat de suporte"}
                aria-expanded={isOpen}
            >
                {isOpen ? '💬' : '🤖'}
            </button>
        </div>
    );
}
