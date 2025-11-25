import { useState, useRef, useEffect } from 'react';
import styles from './ChatWidget.module.css';

export default function ChatWidget() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { type: 'bot', text: 'Olá! Sou a IA de atendimento. Posso consultar o status do seu chamado. Qual o número do protocolo?' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

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

        // Check if input is a number (ticket ID)
        const ticketId = parseInt(userMessage);
        if (isNaN(ticketId)) {
            setMessages(prev => [...prev, { type: 'bot', text: 'Por favor, digite apenas o número do protocolo (ex: 123).' }]);
            setLoading(false);
            return;
        }

        try {
            const response = await fetch(`/api/chamados/public/${ticketId}`);
            if (!response.ok) {
                throw new Error('Chamado não encontrado');
            }
            const data = await response.json();

            let statusText = '';
            if (data.status === 'resolvido') statusText = '✅ Seu chamado foi resolvido automaticamente.';
            else if (data.status === 'encaminhado') statusText = '⚠️ Seu chamado foi encaminhado para um especialista e está em análise.';
            else statusText = `ℹ️ Seu chamado está com status: ${data.status}`;

            setMessages(prev => [...prev, {
                type: 'bot',
                text: `${statusText}\n\nÚltima resposta: "${data.resposta_automatica}"`
            }]);

        } catch (err) {
            setMessages(prev => [...prev, { type: 'bot', text: 'Não encontrei nenhum chamado com esse número. Verifique e tente novamente.' }]);
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
