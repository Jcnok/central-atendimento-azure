import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Layout({ children }) {
    const { user, logout } = useAuth();
    const location = useLocation();
    const navigate = useNavigate();

    const menuItems = [
        { path: '/dashboard', label: 'Dashboard', icon: '📊' },
        { path: '/tickets', label: 'Chamados', icon: '🎫' },
        { path: '/clients', label: 'Clientes', icon: '👥' },
        { path: '/agent', label: 'Agente IA', icon: '🤖' },
        { path: '/settings', label: 'Configurações', icon: '⚙️' },
    ];

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div style={{ display: 'flex', minHeight: '100vh' }}>
            {/* Sidebar */}
            <aside style={{
                width: '250px',
                background: 'rgba(15, 23, 42, 0.6)',
                backdropFilter: 'blur(10px)',
                borderRight: '1px solid var(--glass-border)',
                padding: '2rem 1rem',
                display: 'flex',
                flexDirection: 'column',
                position: 'fixed',
                height: '100vh',
                zIndex: 10
            }}>
                <div className="logo" style={{ marginBottom: '3rem', paddingLeft: '1rem' }}>
                    Central.AI
                </div>

                <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: 1 }}>
                    {menuItems.map((item) => {
                        const isActive = location.pathname === item.path;
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '1rem',
                                    padding: '12px 16px',
                                    borderRadius: '12px',
                                    textDecoration: 'none',
                                    color: isActive ? 'white' : 'var(--text-secondary)',
                                    background: isActive ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
                                    transition: 'all 0.2s',
                                    fontWeight: isActive ? 600 : 400
                                }}
                            >
                                <span>{item.icon}</span>
                                {item.label}
                            </Link>
                        );
                    })}
                </nav>

                <div style={{ borderTop: '1px solid var(--glass-border)', paddingTop: '1rem' }}>
                    <div style={{ padding: '0 1rem', marginBottom: '1rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                        {user?.username}
                    </div>
                    <button
                        onClick={handleLogout}
                        style={{
                            width: '100%',
                            padding: '10px',
                            background: 'rgba(255, 0, 0, 0.1)',
                            border: '1px solid rgba(255, 0, 0, 0.2)',
                            color: '#ff6b6b',
                            borderRadius: '8px',
                            cursor: 'pointer'
                        }}
                    >
                        Sair
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main style={{ flex: 1, marginLeft: '250px', padding: '2rem' }}>
                {children}
            </main>
        </div>
    );
}
