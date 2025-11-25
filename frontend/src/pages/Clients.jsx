import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

export default function Clients() {
    const { token } = useAuth();
    const [clients, setClients] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [newClient, setNewClient] = useState({ nome: '', email: '', telefone: '', canal_preferido: 'whatsapp' });
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchClients();
    }, []);

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
        } finally {
            setLoading(false);
        }
    };

    const handleCreateClient = async (e) => {
        e.preventDefault();
        setError(null);
        try {
            const response = await fetch('/api/clientes/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(newClient)
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Erro ao criar cliente');
            }

            await fetchClients();
            setShowModal(false);
            setNewClient({ nome: '', email: '', telefone: '', canal_preferido: 'whatsapp' });
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h2 style={{ margin: 0 }}>Gerenciar Clientes</h2>
                <button className="btn-primary" onClick={() => setShowModal(true)}>+ Novo Cliente</button>
            </div>

            {loading ? (
                <p>Carregando...</p>
            ) : (
                <div className="glass-panel" style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '600px' }}>
                        <thead>
                            <tr style={{ borderBottom: '1px solid var(--glass-border)', textAlign: 'left' }}>
                                <th style={{ padding: '1rem' }}>Nome</th>
                                <th style={{ padding: '1rem' }}>Email</th>
                                <th style={{ padding: '1rem' }}>Telefone</th>
                                <th style={{ padding: '1rem' }}>Canal Preferido</th>
                            </tr>
                        </thead>
                        <tbody>
                            {clients.map((client) => (
                                <tr key={client.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                    <td style={{ padding: '1rem' }}>{client.nome}</td>
                                    <td style={{ padding: '1rem' }}>{client.email}</td>
                                    <td style={{ padding: '1rem' }}>{client.telefone}</td>
                                    <td style={{ padding: '1rem' }}>
                                        <span style={{
                                            padding: '4px 8px',
                                            borderRadius: '4px',
                                            background: 'rgba(255,255,255,0.1)',
                                            fontSize: '0.85rem',
                                            textTransform: 'capitalize'
                                        }}>
                                            {client.canal_preferido}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                            {clients.length === 0 && (
                                <tr>
                                    <td colSpan="4" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                                        Nenhum cliente encontrado.
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
                        <h3 style={{ marginTop: 0 }}>Novo Cliente</h3>

                        {error && <div style={{ color: '#ff6b6b', marginBottom: '1rem' }}>{error}</div>}

                        <form onSubmit={handleCreateClient} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            <input
                                placeholder="Nome Completo"
                                value={newClient.nome}
                                onChange={e => setNewClient({ ...newClient, nome: e.target.value })}
                                required
                                style={{ padding: '10px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'rgba(255,255,255,0.05)', color: 'white' }}
                            />
                            <input
                                placeholder="Email"
                                type="email"
                                value={newClient.email}
                                onChange={e => setNewClient({ ...newClient, email: e.target.value })}
                                required
                                style={{ padding: '10px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'rgba(255,255,255,0.05)', color: 'white' }}
                            />
                            <input
                                placeholder="Telefone"
                                value={newClient.telefone}
                                onChange={e => setNewClient({ ...newClient, telefone: e.target.value })}
                                style={{ padding: '10px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'rgba(255,255,255,0.05)', color: 'white' }}
                            />
                            <select
                                value={newClient.canal_preferido}
                                onChange={e => setNewClient({ ...newClient, canal_preferido: e.target.value })}
                                style={{ padding: '10px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: '#1e293b', color: 'white' }}
                            >
                                <option value="whatsapp">WhatsApp</option>
                                <option value="email">Email</option>
                                <option value="site">Site</option>
                            </select>

                            <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', justifyContent: 'flex-end' }}>
                                <button type="button" onClick={() => setShowModal(false)} style={{ padding: '10px 20px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'transparent', color: 'white', cursor: 'pointer' }}>Cancelar</button>
                                <button type="submit" className="btn-primary">Salvar</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
