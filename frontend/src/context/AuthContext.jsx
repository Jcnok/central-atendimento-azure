import { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (token) {
            const username = localStorage.getItem('username');
            const role = localStorage.getItem('role');

            // If role is missing (legacy session), force logout to fix state
            if (!role) {
                logout();
                return;
            }

            setUser({ username, role });
        }
    }, [token]);

    const login = async (username, password) => {
        setLoading(true);
        setError(null);
        try {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const response = await fetch('/api/auth/login', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Falha no login');
            }

            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('username', username);
            setToken(data.access_token);
            setUser({ username });
            return true;
        } catch (err) {
            setError(err.message);
            return false;
        } finally {
            setLoading(false);
        }
    };

    const signup = async (username, email, password) => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, email, password }),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Falha no cadastro');
            }

            // Auto login after signup
            return await login(username, password);
        } catch (err) {
            setError(err.message);
            return false;
        } finally {
            setLoading(false);
        }
    };

    const setAuthToken = (accessToken, userData = {}) => {
        localStorage.setItem('token', accessToken);
        setToken(accessToken);

        // Set user data from provided userData or extract from localStorage
        const username = userData.username || localStorage.getItem('user_name') || 'User';
        const role = userData.role || 'admin';

        localStorage.setItem('username', username);
        localStorage.setItem('role', role);
        setUser({ username, role });
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        localStorage.removeItem('user_name');
        localStorage.removeItem('role');
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, login, signup, logout, setAuthToken, loading, error }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
