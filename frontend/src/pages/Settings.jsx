export default function Settings() {
    return (
        <div className="glass-panel" style={{ padding: '2rem', maxWidth: '600px', margin: '0 auto' }}>
            <h2 style={{ marginBottom: '1.5rem', borderBottom: '1px solid var(--glass-border)', paddingBottom: '1rem' }}>
                Configurações
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>Notificações por Email</span>
                    <input type="checkbox" defaultChecked />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>Tema Escuro</span>
                    <input type="checkbox" defaultChecked disabled />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>Idioma</span>
                    <select style={{ padding: '5px', borderRadius: '4px' }}>
                        <option>Português (BR)</option>
                        <option>English</option>
                    </select>
                </div>
            </div>
        </div>
    );
}
