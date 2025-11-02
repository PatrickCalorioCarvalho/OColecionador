import React from 'react';
import './Login.css';
import logo from './assets/icon.png';

export default function Login() {
  const isMobile = new URLSearchParams(window.location.search).get('mobile') === 'true';

  const redirectToProvider = (provider: 'github' | 'google') => {
    const clientId = provider === 'github' ? process.env.REACT_APP_GITHUB_CLIENT_ID : process.env.REACT_APP_GOOGLE_CLIENT_ID;
    const redirectUri = 'http://localhost:5000/auth/callback';
    const state = encodeURIComponent(JSON.stringify({ Provider: provider, Mobile: isMobile }));

    const authUrl =
      provider === 'github'
        ? `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&state=${state}`
        : `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=profile email&state=${state}`;

    window.location.href = authUrl;
  };

  return (
    <div className="login-container">
      <img src={logo} alt="Logo OColecionador" className="logo-image" />
      <h1>OColecionador</h1>
      <p>Escolha um provedor para entrar:</p>
      <div className="button-group">
        <button className="login-button github" onClick={() => redirectToProvider('github')}>
          <img src="https://pngimg.com/uploads/github/github_PNG80.png" alt="GitHub" />
          Entrar com GitHub
        </button>
        <button className="login-button google" onClick={() => redirectToProvider('google')}>
          <img src="https://developers.google.com/identity/images/g-logo.png" alt="Google" />
          Entrar com Google
        </button>
      </div>
    </div>
  );
}
