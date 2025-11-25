import { useState } from 'react';
import { Link } from 'react-router-dom';
import ChatWidget from '../components/ChatWidget';

export default function Support() {
    const [step, setStep] = useState(1);
    const [email, setEmail] = useState('');
    const [client, setClient] = useState(null);
    const [message, setMessage] = useState('');
    const [ticket, setTicket] = useState(null);
    const [boleto, setBoleto] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [mode, setMode] = useState('support'); // 'support' or 'boleto'

    const handleCheckEmail = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`/api/clientes/buscar?email=${email}`);
            if (!response.ok) {
                if (response.status === 404) {
                    // Show 0800 card instead of throwing error
                    setStep('non-client');
                    return;
                }
                throw new Error('Erro ao buscar cliente.');
            }
            const data = await response.json();
            setClient(data);
            setStep(2);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateTicket = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            const response = await fetch('/api/chamados/public', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    cliente_id: client.id,
                    canal: 'site',
                    mensagem: message
                })
            });

            if (!response.ok) {
                throw new Error('Erro ao processar sua solicitação.');
            }

            const data = await response.json();
            setTicket(data);
            setStep(3);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleGerarBoleto = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            const response = await fetch('/api/boletos/gerar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });

            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('Nenhum boleto pendente encontrado para este e-mail.');
                }
                throw new Error('Erro ao gerar boleto.');
            }

            const data = await response.json();
            setBoleto(data);
            setStep('boleto-result');
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
            color: 'white'
        }}>
            <div className="glass-panel" style={{ width: '100%', maxWidth: '600px', padding: '3rem', margin: '1rem' }}>
                <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                    <h1 className="hero-title" style={{ fontSize: '2rem' }}>Central de Ajuda</h1>
                    <p style={{ color: 'var(--text-secondary)' }}>Atendimento Inteligente 24h</p>
                </div>

                {/* Mode Selection */}
                {step === 1 && !mode.startsWith('selected') && (
                    <div style={{ display: 'grid', gap: '1rem' }}>
                        <button
                            onClick={() => { setMode('support'); setStep('email-input'); }}
                            className="glass-panel"
                            style={{
                                padding: '1.5rem',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '1rem',
                                cursor: 'pointer',
                                border: '1px solid var(--glass-border)',
                                background: 'rgba(255,255,255,0.05)',
                                transition: 'transform 0.2s',
                                textAlign: 'left'
                            }}
                            onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                            onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                        >
                            <div style={{ fontSize: '2rem' }}>💬</div>
                            <div>
                                <div style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>Falar com Suporte</div>
                                <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Tire dúvidas ou relate problemas</div>
                            </div>
                        </button>

                        <button
                            onClick={() => { setMode('boleto'); setStep('email-input'); }}
                            className="glass-panel"
                            style={{
                                padding: '1.5rem',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '1rem',
                                cursor: 'pointer',
                                border: '1px solid var(--glass-border)',
                                background: 'rgba(255,255,255,0.05)',
                                transition: 'transform 0.2s',
                                textAlign: 'left'
                            }}
                            onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                            onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                        >
                            <div style={{ fontSize: '2rem' }}>📄</div>
                            <div>
                                <div style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>2ª Via de Boleto</div>
                                <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Gere seu boleto atualizado</div>
                            </div>
                        </button>
                    </div>
                )}

                {/* STEP: Email Input (Shared) */}
                {step === 'email-input' && (
                    <form onSubmit={mode === 'support' ? handleCheckEmail : handleGerarBoleto}>
                        <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <button
                                type="button"
                                onClick={() => setStep(1)}
                                style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '1.2rem' }}
                            >
                                ←
                            </button>
                            <h2 style={{ fontSize: '1.2rem', margin: 0 }}>
                                {mode === 'support' ? 'Identificação' : 'Gerar Boleto'}
                            </h2>
                        </div>

                        <p style={{ marginBottom: '1.5rem', lineHeight: '1.6' }}>
                            Por favor, informe seu e-mail para continuar.
                        </p>

                        {error && (
                            <div style={{ padding: '1rem', background: 'rgba(255,0,0,0.1)', border: '1px solid rgba(255,0,0,0.2)', borderRadius: '8px', color: '#ff6b6b', marginBottom: '1.5rem' }}>
                                {error}
                            </div>
                        )}

                        <div style={{ marginBottom: '1.5rem' }}>
                            <input
                                type="email"
                                placeholder="seu@email.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                style={{
                                    width: '100%',
                                    padding: '12px',
                                    borderRadius: '8px',
                                    border: '1px solid var(--glass-border)',
                                    background: 'rgba(255,255,255,0.05)',
                                    color: 'white',
                                    outline: 'none',
                                    fontSize: '1rem'
                                }}
                            />
                        </div>

                        <button
                            type="submit"
                            className="btn-primary"
                            style={{ width: '100%', padding: '12px' }}
                            disabled={loading}
                        >
                            {loading ? 'Processando...' : 'Continuar'}
                        </button>
                    </form>
                )}

                {/* STEP: Non-Client (0800) */}
                {step === 'non-client' && (
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📞</div>
                        <h2 style={{ marginBottom: '1rem' }}>Cadastro não encontrado</h2>
                        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
                            Não localizamos seu e-mail em nossa base de clientes.
                            Para suporte, entre em contato com nossa central:
                        </p>

                        <div style={{
                            background: 'rgba(59, 130, 246, 0.1)',
                            border: '1px solid rgba(59, 130, 246, 0.3)',
                            borderRadius: '12px',
                            padding: '1.5rem',
                            marginBottom: '2rem'
                        }}>
                            <div style={{ fontSize: '0.9rem', color: '#60a5fa', marginBottom: '0.5rem' }}>Central de Atendimento</div>
                            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white' }}>0800 123 4567</div>
                        </div>

                        <button
                            onClick={() => {
                                setStep(1);
                                setEmail('');
                            }}
                            style={{
                                background: 'transparent',
                                border: '1px solid var(--glass-border)',
                                color: 'white',
                                padding: '10px 20px',
                                borderRadius: '8px',
                                cursor: 'pointer'
                            }}
                        >
                            Tentar outro e-mail
                        </button>
                    </div>
                )}

                {/* STEP: Boleto Result */}
                {step === 'boleto-result' && boleto && (
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✅</div>
                        <h2 style={{ marginBottom: '1rem' }}>Boleto Gerado!</h2>

                        <div style={{
                            background: 'white',
                            color: 'black',
                            padding: '1.5rem',
                            borderRadius: '8px',
                            marginBottom: '1.5rem',
                            textAlign: 'left'
                        }}>
                            <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '0.5rem' }}>Código de Barras:</div>
                            <div style={{ fontFamily: 'monospace', fontSize: '1.1rem', wordBreak: 'break-all', fontWeight: 'bold' }}>
                                {boleto.codigo_barras}
                            </div>
                            <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'space-between' }}>
                                <div>
                                    <div style={{ fontSize: '0.8rem', color: '#666' }}>Valor</div>
                                    <div style={{ fontWeight: 'bold' }}>R$ {boleto.valor.toFixed(2)}</div>
                                </div>
                                <div>
                                    <div style={{ fontSize: '0.8rem', color: '#666' }}>Vencimento</div>
                                    <div style={{ fontWeight: 'bold' }}>{boleto.vencimento}</div>
                                </div>
                            </div>
                        </div>

                        <a
                            href={boleto.link_pdf}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn-primary"
                            style={{
                                display: 'block',
                                width: '100%',
                                padding: '12px',
                                textAlign: 'center',
                                textDecoration: 'none',
                                marginBottom: '1rem'
                            }}
                        >
                            Baixar PDF
                        </a>

                        <button
                            onClick={() => {
                                setStep(1);
                                setBoleto(null);
                                setEmail('');
                            }}
                            style={{
                                background: 'transparent',
                                border: 'none',
                                color: 'var(--text-secondary)',
                                cursor: 'pointer'
                            }}
                        >
                            Voltar ao início
                        </button>
                    </div>
                )}

                {/* STEP 2: Chat / Problem Description */}
                {step === 2 && (
                    <form onSubmit={handleCreateTicket}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem', paddingBottom: '1rem', borderBottom: '1px solid var(--glass-border)' }}>
                            <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: '#3b82f6', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                👤
                            </div>
                            <div>
                                <div style={{ fontWeight: 'bold' }}>Olá, {client.nome}</div>
                                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Como podemos ajudar hoje?</div>
                            </div>
                        </div>

                        <div style={{ marginBottom: '1.5rem' }}>
                            <textarea
                                rows="5"
                                placeholder="Descreva seu problema ou dúvida..."
                                value={message}
                                onChange={(e) => setMessage(e.target.value)}
                                required
                                style={{
                                    width: '100%',
                                    padding: '12px',
                                    borderRadius: '8px',
                                    border: '1px solid var(--glass-border)',
                                    background: 'rgba(255,255,255,0.05)',
                                    color: 'white',
                                    outline: 'none',
                                    fontSize: '1rem',
                                    resize: 'vertical'
                                }}
                            />
                        </div>

                        <button
                            type="submit"
                            className="btn-primary"
                            style={{ width: '100%', padding: '12px' }}
                            disabled={loading}
                        >
                            {loading ? 'Analisando com IA...' : 'Enviar Mensagem'}
                        </button>

                        <button
                            type="button"
                            onClick={() => setStep(1)}
                            style={{
                                width: '100%',
                                padding: '12px',
                                marginTop: '1rem',
                                background: 'transparent',
                                border: 'none',
                                color: 'var(--text-secondary)',
                                cursor: 'pointer'
                            }}
                        >
                            Voltar
                        </button>
                    </form>
                )}

                {/* STEP 3: AI Response */}
                {step === 3 && ticket && (
                    <div>
                        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                            <div style={{
                                width: '60px', height: '60px', borderRadius: '50%',
                                background: ticket.resolvido_automaticamente ? '#10b981' : '#f59e0b',
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                margin: '0 auto 1rem auto', fontSize: '2rem'
                            }}>
                                {ticket.resolvido_automaticamente ? '✅' : '👩‍💻'}
                            </div>
                            <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>
                                {ticket.resolvido_automaticamente ? 'Resolvido!' : 'Encaminhado'}
                            </h2>
                            <p style={{ color: 'var(--text-secondary)' }}>
                                Protocolo: #{ticket.chamado_id}
                            </p>
                        </div>

                        <div style={{
                            background: 'rgba(255,255,255,0.05)',
                            padding: '1.5rem',
                            borderRadius: '12px',
                            border: '1px solid var(--glass-border)',
                            marginBottom: '2rem'
                        }}>
                            <p style={{ lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>
                                {ticket.resposta}
                            </p>
                        </div>

                        {ticket.encaminhado_para_humano && (
                            <div style={{
                                background: 'rgba(245, 158, 11, 0.1)',
                                padding: '1rem',
                                borderRadius: '8px',
                                border: '1px solid rgba(245, 158, 11, 0.2)',
                                color: '#fbbf24',
                                fontSize: '0.9rem',
                                marginBottom: '2rem',
                                textAlign: 'center'
                            }}>
                                ⚠️ Seu caso foi classificado como prioritário e um de nossos especialistas entrará em contato em breve.
                            </div>
                        )}

                        <button
                            onClick={() => {
                                setStep(2);
                                setMessage('');
                                setTicket(null);
                            }}
                            className="btn-primary"
                            style={{ width: '100%', padding: '12px' }}
                        >
                            Nova Solicitação
                        </button>


                    </div>
                )}
            </div>
            <ChatWidget />
        </div>
    );
}
