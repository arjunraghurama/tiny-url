const API_BASE = 'http://localhost:8000';

/**
 * Helper to build headers with optional auth token.
 */
function authHeaders(token) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export async function shortenUrl(url, token) {
  const response = await fetch(`${API_BASE}/api/shorten`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Please sign in to shorten URLs');
    }
    const error = await response.json();
    throw new Error(error.detail || 'Failed to shorten URL');
  }

  return response.json();
}

export async function getRecentUrls(token) {
  const response = await fetch(`${API_BASE}/api/urls/recent`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  if (!response.ok) {
    throw new Error('Failed to fetch recent URLs');
  }

  return response.json();
}

export async function getUrlStats(shortCode) {
  const response = await fetch(`${API_BASE}/api/urls/${shortCode}/stats`);

  if (!response.ok) {
    throw new Error('Failed to fetch URL stats');
  }

  return response.json();
}
