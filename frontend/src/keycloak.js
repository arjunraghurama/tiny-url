import Keycloak from 'keycloak-js';

/**
 * Keycloak instance configuration.
 *
 * Points to the Keycloak server running in Docker,
 * using the 'myrealm' realm and 'react-client' public client.
 */
const keycloak = new Keycloak({
  url: 'http://localhost:8080',
  realm: 'myrealm',
  clientId: 'react-client',
});

export default keycloak;
