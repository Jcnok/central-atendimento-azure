import { useState } from 'react';

export default function ChatWidget() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { type: 'bot', text: 'Olá! Sou a IA de atendimento. Posso consultar o status do seu chamado. Qual o número do protocolo?' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

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
        <div style={{ position: 'fixed', bottom: '20px', right: '20px', zIndex: 1000 }}>
            {/* Chat Window */}
            {isOpen && (
                <div className="glass-panel" style={{
                    width: '300px',
                    height: '400px',
                    marginBottom: '1rem',
                    display: 'flex',
                    flexDirection: 'column',
                    boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)'
                }}>
                    <div style={{
                        padding: '1rem',
                        borderBottom: '1px solid var(--glass-border)',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        background: 'rgba(255,255,255,0.05)'
                    }}>
                        <span style={{ fontWeight: 'bold' }}>Assistente Virtual</span>
                        <button
                            onClick={() => setIsOpen(false)}
                            style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', fontSize: '1.2rem' }}
                        >
                            ×
                        </button>
                    </div>

                    <div style={{ flex: 1, padding: '1rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        {messages.map((msg, idx) => (
                            <div key={idx} style={{
                                alignSelf: msg.type === 'user' ? 'flex-end' : 'flex-start',
                                background: msg.type === 'user' ? '#3b82f6' : 'rgba(255,255,255,0.1)',
                                padding: '8px 12px',
                                borderRadius: '12px',
                                maxWidth: '85%',
                                fontSize: '0.9rem',
                                whiteSpace: 'pre-wrap'
                            }}>
                                {msg.text}
                            </div>
                        ))}
                        {loading && <div style={{ alignSelf: 'flex-start', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>Digitando...</div>}
                    </div>

                    <form onSubmit={handleSend} style={{ padding: '1rem', borderTop: '1px solid var(--glass-border)' }}>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                            <input
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Digite o protocolo..."
                                style={{
                                    flex: 1,
                                    padding: '8px',
                                    borderRadius: '6px',
                                    border: '1px solid var(--glass-border)',
                                    background: 'rgba(255,255,255,0.05)',
                                    color: 'white',
                                    fontSize: '0.9rem'
                                }}
                            />
                            <button
                                type="submit"
                                disabled={loading}
                                style={{
                                    background: '#3b82f6',
                                    border: 'none',
                                    borderRadius: '6px',
                                    color: 'white',
                                    padding: '0 12px',
                                    cursor: 'pointer'
                                }}
                            >
                                ➤
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Floating Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                style={{
                    width: '60px',
                    height: '60px',
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                    border: 'none',
                    boxShadow: '0 4px 12px rgba(37, 99, 235, 0.4)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '1.5rem',
                    color: 'white',
                    transition: 'transform 0.2s'
                }}
                onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.1)'}
                onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
            >
                {isOpen ? '💬' : '🤖'}
            </button>
        </div>
    );
}
