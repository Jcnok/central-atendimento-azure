import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Dashboard() {
    const { user, token } = useAuth();
    const navigate = useNavigate();
    const [metrics, setMetrics] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchMetrics();
    }, []);

    const fetchMetrics = async () => {
        try {
            const response = await fetch('/api/metricas/', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setMetrics(data);
            }
        } catch (err) {
            console.error('Erro ao buscar métricas:', err);
        } finally {
            setLoading(false);
        }
    };

    const StatCard = ({ title, value, icon, color }) => (
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem', flex: 1, minWidth: '200px' }}>
            <div style={{
                width: '50px', height: '50px', borderRadius: '12px',
                background: color, display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '1.5rem'
            }}>
                {icon}
            </div>
            <div>
                <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>{title}</div>
                <div style={{ fontSize: '1.8rem', fontWeight: 'bold' }}>{value}</div>
            </div>
        </div>
    );

    return (
        <div>
            <h1 style={{ marginBottom: '0.5rem' }}>Olá, {user?.username} 👋</h1>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>Aqui está o resumo do atendimento hoje.</p>

            {loading ? (
                <p>Carregando métricas...</p>
            ) : metrics ? (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.5rem', marginBottom: '3rem' }}>
                    <StatCard
                        title="Total de Chamados"
                        value={metrics.total_chamados}
                        icon="🎫"
                        color="rgba(59, 130, 246, 0.2)"
                    />
                    <StatCard
                        title="Resolvidos por IA"
                        value={metrics.chamados_resolvidos_automaticamente}
                        icon="🤖"
                        color="rgba(16, 185, 129, 0.2)"
                    />
                    <StatCard
                        title="Taxa de Resolução"
                        value={metrics.taxa_resolucao_automatica}
                        icon="📈"
                        color="rgba(139, 92, 246, 0.2)"
                    />
                    <StatCard
                        title="Total de Clientes"
                        value={metrics.total_clientes}
                        icon="👥"
                        color="rgba(245, 158, 11, 0.2)"
                    />
                </div>
            ) : (
                <p>Não foi possível carregar as métricas.</p>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
                <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center' }}>
                    <h3>Ações Rápidas</h3>
                    <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginTop: '1.5rem' }}>
                        <button className="btn-primary" onClick={() => navigate('/tickets')}>Ver Chamados</button>
                        <button className="btn-primary" onClick={() => navigate('/clients')} style={{ background: 'transparent', border: '1px solid white' }}>Gerenciar Clientes</button>
                    </div>
                </div>

                <div className="glass-panel" style={{ padding: '2rem' }}>
                    <h3>Status do Sistema</h3>
                    <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span>API Backend</span>
                            <span style={{ color: '#10b981' }}>● Online</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span>Banco de Dados</span>
                            <span style={{ color: '#10b981' }}>● Conectado</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span>IA Classifier</span>
                            <span style={{ color: '#10b981' }}>● Ativo</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
