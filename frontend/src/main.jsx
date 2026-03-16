import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import keycloak from './keycloak.js';

/**
 * Initialize Keycloak before rendering the React app.
 *
 * Uses 'check-sso' so returning users are silently re-authenticated
 * via an iframe check, but first-time visitors see the app immediately
 * without being forced to the login page.
 */
keycloak
  .init({
    onLoad: 'check-sso',
    silentCheckSsoRedirectUri:
      window.location.origin + '/silent-check-sso.html',
    checkLoginIframe: false,
  })
  .then((authenticated) => {
    console.log(
      `Keycloak initialized — ${authenticated ? 'authenticated' : 'not authenticated'}`
    );

    createRoot(document.getElementById('root')).render(
      <StrictMode>
        <App keycloak={keycloak} />
      </StrictMode>
    );
  })
  .catch((err) => {
    console.error('Keycloak init failed:', err);
    // Render app anyway without auth so the UI is still usable
    createRoot(document.getElementById('root')).render(
      <StrictMode>
        <App keycloak={null} />
      </StrictMode>
    );
  });
