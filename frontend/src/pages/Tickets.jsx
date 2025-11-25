import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

export default function Tickets() {
    const { token } = useAuth();
    const [tickets, setTickets] = useState([]);
    const [clients, setClients] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [newTicket, setNewTicket] = useState({ cliente_id: '', canal: 'site', mensagem: '' });
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchTickets();
        fetchClients();
    }, []);

    const fetchTickets = async () => {
        try {
            const response = await fetch('/api/chamados/', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setTickets(data);
            }
        } catch (err) {
            console.error('Erro ao buscar chamados:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchClients = async () => {
        try {
            const response = await fetch('/api/clientes/', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setClients(data);
            }
        } catch (err) {
            console.error('Erro ao buscar clientes:', err);
        }
    };

    const handleCreateTicket = async (e) => {
        e.preventDefault();
        setError(null);
        try {
            const response = await fetch('/api/chamados/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(newTicket)
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Erro ao criar chamado');
            }

            await fetchTickets();
            setShowModal(false);
            setNewTicket({ cliente_id: '', canal: 'site', mensagem: '' });
        } catch (err) {
            setError(err.message);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'resolvido': return '#10b981'; // green
            case 'encaminhado': return '#f59e0b'; // orange
            default: return '#3b82f6'; // blue
        }
    };

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h2 style={{ margin: 0 }}>Chamados</h2>
                <button className="btn-primary" onClick={() => setShowModal(true)}>+ Novo Chamado</button>
            </div>

            {loading ? (
                <p>Carregando...</p>
            ) : (
                <div className="glass-panel" style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '800px' }}>
                        <thead>
                            <tr style={{ borderBottom: '1px solid var(--glass-border)', textAlign: 'left' }}>
                                <th style={{ padding: '1rem' }}>ID</th>
                                <th style={{ padding: '1rem' }}>Cliente (ID)</th>
                                <th style={{ padding: '1rem' }}>Canal</th>
                                <th style={{ padding: '1rem' }}>Mensagem</th>
                                <th style={{ padding: '1rem' }}>Status</th>
                                <th style={{ padding: '1rem' }}>Resposta IA</th>
                            </tr>
                        </thead>
                        <tbody>
                            {tickets.map((ticket) => (
                                <tr key={ticket.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                    <td style={{ padding: '1rem' }}>#{ticket.id}</td>
                                    <td style={{ padding: '1rem' }}>{ticket.cliente_id}</td>
                                    <td style={{ padding: '1rem', textTransform: 'capitalize' }}>{ticket.canal}</td>
                                    <td style={{ padding: '1rem', maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                        {ticket.mensagem}
                                    </td>
                                    <td style={{ padding: '1rem' }}>
                                        <span style={{
                                            padding: '4px 8px',
                                            borderRadius: '4px',
                                            background: getStatusColor(ticket.status),
                                            color: 'white',
                                            fontSize: '0.85rem',
                                            textTransform: 'capitalize'
                                        }}>
                                            {ticket.status}
                                        </span>
                                    </td>
                                    <td style={{ padding: '1rem', maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', color: 'var(--text-secondary)' }}>
                                        {ticket.resposta_automatica || '-'}
                                    </td>
                                </tr>
                            ))}
                            {tickets.length === 0 && (
                                <tr>
                                    <td colSpan="6" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                                        Nenhum chamado encontrado.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Modal de Criação */}
            {showModal && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100
                }}>
                    <div className="glass-panel" style={{ padding: '2rem', width: '100%', maxWidth: '500px', background: '#1e293b' }}>
                        <h3 style={{ marginTop: 0 }}>Novo Chamado</h3>

                        {error && <div style={{ color: '#ff6b6b', marginBottom: '1rem' }}>{error}</div>}

                        <form onSubmit={handleCreateTicket} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            <div>
                                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Cliente</label>
                                <select
                                    value={newTicket.cliente_id}
                                    onChange={e => setNewTicket({ ...newTicket, cliente_id: e.target.value })}
                                    required
                                    style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: '#1e293b', color: 'white' }}
                                >
                                    <option value="">Selecione um cliente...</option>
                                    {clients.map(client => (
                                        <option key={client.id} value={client.id}>{client.nome} ({client.email})</option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Canal</label>
                                <select
                                    value={newTicket.canal}
                                    onChange={e => setNewTicket({ ...newTicket, canal: e.target.value })}
                                    style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: '#1e293b', color: 'white' }}
                                >
                                    <option value="site">Site</option>
                                    <option value="whatsapp">WhatsApp</option>
                                    <option value="email">Email</option>
                                </select>
                            </div>

                            <div>
                                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Mensagem</label>
                                <textarea
                                    rows="4"
                                    value={newTicket.mensagem}
                                    onChange={e => setNewTicket({ ...newTicket, mensagem: e.target.value })}
                                    required
                                    placeholder="Descreva o problema..."
                                    style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'rgba(255,255,255,0.05)', color: 'white', resize: 'vertical' }}
                                />
                            </div>

                            <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', justifyContent: 'flex-end' }}>
                                <button type="button" onClick={() => setShowModal(false)} style={{ padding: '10px 20px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'transparent', color: 'white', cursor: 'pointer' }}>Cancelar</button>
                                <button type="submit" className="btn-primary">Criar Chamado</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
