import React, { useEffect, useState } from 'react';
import './Dashboard.css';

export default function Dashboard() {
  const rawToken = localStorage.getItem('token');
  const [user, setUser] = useState<{ name: string; picture: string } | null>(null);

  useEffect(() => {
    if (!rawToken) return;

    const [provider, token] = rawToken.split('_OC_');

    console.log('Provider:', provider);
    console.log('Token:', token);

    const fetchUser = async () => {
      try {
        let res;
        if (provider === 'google') {
          res = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
            headers: { Authorization: `Bearer ${token}` },
          });
          const data = await res.json();
          setUser({ name: data.name, picture: data.picture });
        } else if (provider === 'github') {
          res = await fetch('https://api.github.com/user', {
            headers: {
              Authorization: `Bearer ${token}`,
              'User-Agent': 'OColecionador',
            },
          });
          const data = await res.json();
          setUser({ name: data.name || data.login, picture: data.avatar_url });
        }
      } catch (err) {
        console.error('Erro ao buscar perfil:', err);
      }
    };

    fetchUser();
  }, [rawToken]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/login';
  };

  if (!rawToken) return <p>Acesso negado.</p>;

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        {user && (
          <div className="header-user">
            <img src={user.picture} alt="Avatar" className="header-avatar" />
            <span className="header-name">{user.name}</span>
            <button className="header-logout" onClick={handleLogout} title="Sair">
              ➔
            </button>
          </div>
        )}
      </header>

      <div className="dashboard-card">
        <h1 className="dashboard-title">Dashboard</h1>
      </div>
    </div>
  );
}
