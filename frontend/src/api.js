const API_BASE = 'http://localhost:8000';

export async function shortenUrl(url) {
  const response = await fetch(`${API_BASE}/api/shorten`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to shorten URL');
  }

  return response.json();
}

export async function getRecentUrls() {
  const response = await fetch(`${API_BASE}/api/urls/recent`);

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
