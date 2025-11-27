import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import styles from './Dashboard.module.css';

export default function Dashboard() {
    const { token, logout } = useAuth();
    const [kpis, setKpis] = useState(null);
    const [tickets, setTickets] = useState([]);
    const [agentQuery, setAgentQuery] = useState('');
    const [agentResponse, setAgentResponse] = useState('');
    const [loadingAgent, setLoadingAgent] = useState(false);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            const headers = { 'Authorization': `Bearer ${token}` };

            const kpiRes = await fetch('/api/dashboard/kpis', { headers });
            const kpiData = await kpiRes.json();
            setKpis(kpiData);

            const ticketRes = await fetch('/api/dashboard/tickets', { headers });
            const ticketData = await ticketRes.json();
            setTickets(ticketData);
        } catch (error) {
            console.error("Error fetching dashboard data:", error);
        }
    };

    const handleAgentSubmit = async (e) => {
        e.preventDefault();
        if (!agentQuery.trim()) return;

        setLoadingAgent(true);
        setAgentResponse('');

        try {
            const response = await fetch('/api/dashboard/agent', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ query: agentQuery })
            });

            const data = await response.json();
            setAgentResponse(data.response);
        } catch (error) {
            setAgentResponse("Erro ao consultar o agente. Tente novamente.");
        } finally {
            setLoadingAgent(false);
        }
    };

    return (
        <div className={styles.container}>
            <header className={styles.header}>
                <h1>Dashboard Administrativo</h1>
                <button onClick={logout} className={styles.logoutButton}>Sair</button>
            </header>

            {/* KPIs Section */}
            <section className={styles.kpiSection}>
                <div className={styles.kpiCard}>
                    <h3>Total Clientes</h3>
                    <div className={styles.value}>{kpis?.total_clientes || '-'}</div>
                </div>
                <div className={styles.kpiCard}>
                    <h3>Contratos Ativos</h3>
                    <div className={styles.value}>{kpis?.contratos_ativos || '-'}</div>
                </div>
                <div className={styles.kpiCard}>
                    <h3>Chamados Abertos</h3>
                    <div className={styles.value}>{kpis?.chamados_abertos || '-'}</div>
                </div>
                <div className={styles.kpiCard}>
                    <h3>NPS Médio</h3>
                    <div className={styles.value}>{kpis?.nps_medio || '-'}</div>
                </div>
            </section>

            <div className={styles.mainGrid}>
                {/* Recent Tickets */}
                <section className={styles.ticketsSection}>
                    <h2>Chamados Recentes</h2>
                    <table className={styles.table}>
                        <thead>
                            <tr>
                                <th>Protocolo</th>
                                <th>Status</th>
                                <th>Prioridade</th>
                                <th>Data</th>
                            </tr>
                        </thead>
                        <tbody>
                            {tickets.map(t => (
                                <tr key={t.id}>
                                    <td>{t.protocolo}</td>
                                    <td><span className={`${styles.badge} ${styles[t.status]}`}>{t.status}</span></td>
                                    <td>{t.prioridade}</td>
                                    <td>{new Date(t.data).toLocaleDateString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </section>

                {/* CRM Agent */}
                <section className={styles.agentSection}>
                    <h2>🤖 Agente CRM (SQL)</h2>
                    <p>Pergunte sobre dados da base (ex: "Quantos clientes cancelaram este mês?", "Liste clientes com faturas atrasadas")</p>

                    <form onSubmit={handleAgentSubmit} className={styles.agentForm}>
                        <textarea
                            value={agentQuery}
                            onChange={(e) => setAgentQuery(e.target.value)}
                            placeholder="Digite sua pergunta..."
                            rows="3"
                        />
                        <button type="submit" disabled={loadingAgent}>
                            {loadingAgent ? 'Consultando...' : 'Perguntar'}
                        </button>
                    </form>

                    {agentResponse && (
                        <div className={styles.agentResult}>
                            <strong>Resposta:</strong>
                            <p>{agentResponse}</p>
                        </div>
                    )}
                </section>
            </div>
        </div>
    );
}
