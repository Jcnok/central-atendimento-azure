import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styles from './Home.module.css';

export default function Home() {
    const navigate = useNavigate();
    const [showChatBalloon, setShowChatBalloon] = useState(true);

    return (
        <div className={styles.container}>
            {/* Header */}
            <header className={styles.header}>
                <div className={styles.logo}>Central<span className={styles.logoHighlight}>Inteligente</span></div>
                <nav className={styles.nav}>
                    <a href="#internet">Internet</a>
                    <a href="#movel">Móvel</a>
                    <a href="#tv">TV</a>
                    <a href="#ajuda">Ajuda</a>
                </nav>
                <div className={styles.authButtons}>
                    <Link to="/login" className={styles.loginButton}>Minha Conta</Link>
                </div>
            </header>

            {/* Hero Section */}
            <section className={styles.hero}>
                <div className={styles.heroContent}>
                    <h1>O futuro da conexão chegou.</h1>
                    <p>Internet Fibra, 5G e TV 4K com a melhor experiência de atendimento do Brasil.</p>
                    <button className={styles.ctaButton}>Conheça os Planos</button>
                </div>
            </section>

            {/* Plans Section */}
            <section id="planos" className={styles.plansSection}>
                <h2>Escolha o plano ideal para você</h2>
                <div className={styles.plansGrid}>
                    <div className={styles.planCard}>
                        <h3>Internet Fibra</h3>
                        <div className={styles.speed}>500 MEGA</div>
                        <div className={styles.price}>R$ 120,00<span>/mês</span></div>
                        <ul>
                            <li>Wi-Fi 6 Grátis</li>
                            <li>Instalação Grátis</li>
                        </ul>
                        <button className={styles.planButton}>Assinar</button>
                    </div>
                    <div className={styles.planCard + ' ' + styles.featured}>
                        <div className={styles.badge}>MAIS VENDIDO</div>
                        <h3>Combo Total</h3>
                        <div className={styles.speed}>1 GIGA + 5G</div>
                        <div className={styles.price}>R$ 200,00<span>/mês</span></div>
                        <ul>
                            <li>Fibra 1GB</li>
                            <li>Móvel 5G Ilimitado</li>
                            <li>TV 4K</li>
                        </ul>
                        <button className={styles.planButton}>Assinar</button>
                    </div>
                    <div className={styles.planCard}>
                        <h3>Móvel 5G</h3>
                        <div className={styles.speed}>ILIMITADO</div>
                        <div className={styles.price}>R$ 89,90<span>/mês</span></div>
                        <ul>
                            <li>Apps Ilimitados</li>
                            <li>Roaming Nacional</li>
                        </ul>
                        <button className={styles.planButton}>Assinar</button>
                    </div>
                </div>
            </section>

            {/* Chat Balloon */}
            {showChatBalloon && (
                <div className={styles.chatBalloon}>
                    <div className={styles.balloonHeader}>
                        <button onClick={() => setShowChatBalloon(false)}>×</button>
                    </div>
                    <div className={styles.balloonContent}>
                        <p><strong>Oi! Precisa de ajuda?</strong></p>
                        <p>Posso te ajudar a consultar faturas, tirar dúvidas e muito mais.</p>
                        <Link to="/login" className={styles.balloonLink}>Acessar Atendimento</Link>
                    </div>
                    <div className={styles.balloonFooter}>
                        Ligue para contratar: <strong>0800 123 4567</strong>
                    </div>
                </div>
            )}
        </div>
    );
}
