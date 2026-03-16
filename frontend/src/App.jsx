import { useState, useEffect, useCallback } from 'react';
import ShortenForm from './components/ShortenForm';
import RecentURLs from './components/RecentURLs';
import UserMenu from './components/UserMenu';
import { getRecentUrls } from './api';
import './index.css';

function App({ keycloak }) {
  const [recentUrls, setRecentUrls] = useState([]);
  const [loading, setLoading] = useState(true);

  const getToken = useCallback(async () => {
    if (!keycloak?.authenticated) return null;
    // Refresh token if expiring within 30 seconds
    try {
      await keycloak.updateToken(30);
    } catch {
      // Token refresh failed — user will need to re-login
      return null;
    }
    return keycloak.token;
  }, [keycloak]);

  const fetchRecentUrls = useCallback(async () => {
    try {
      const token = await getToken();
      const data = await getRecentUrls(token);
      setRecentUrls(data);
    } catch (err) {
      console.error('Failed to fetch recent URLs:', err);
    } finally {
      setLoading(false);
    }
  }, [getToken]);

  useEffect(() => {
    fetchRecentUrls();
  }, [fetchRecentUrls]);

  const isAuthenticated = keycloak?.authenticated || false;

  return (
    <div className="app">
      <div className="bg-gradient" />
      <div className="container">
        <header className="header">
          <div className="header-top">
            <div className="logo">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="url(#logoGradient)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <defs>
                  <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#818cf8" />
                    <stop offset="100%" stopColor="#c084fc" />
                  </linearGradient>
                </defs>
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
              </svg>
              <h1>TinyURL</h1>
            </div>
            <UserMenu keycloak={keycloak} />
          </div>
          <p className="tagline">
            Shorten your links, amplify your reach
          </p>
        </header>

        <main>
          <ShortenForm
            onUrlCreated={fetchRecentUrls}
            isAuthenticated={isAuthenticated}
            getToken={getToken}
            onLogin={() => keycloak?.login()}
          />
          <RecentURLs urls={recentUrls} loading={loading} />
        </main>

        <footer className="footer">
          <p>
            A system design learning project — FastAPI · PostgreSQL · Valkey · Keycloak · React
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;
