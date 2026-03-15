import URLCard from './URLCard';

export default function RecentURLs({ urls, loading }) {
  if (loading) {
    return (
      <div className="recent-urls">
        <h2 className="section-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12 6 12 12 16 14" />
          </svg>
          Recent URLs
        </h2>
        <div className="loading-skeleton">
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton-card" />
          ))}
        </div>
      </div>
    );
  }

  if (!urls || urls.length === 0) {
    return (
      <div className="recent-urls">
        <h2 className="section-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12 6 12 12 16 14" />
          </svg>
          Recent URLs
        </h2>
        <div className="empty-state">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
            <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
          </svg>
          <p>No URLs shortened yet. Paste a URL above to get started!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="recent-urls">
      <h2 className="section-title">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" />
          <polyline points="12 6 12 12 16 14" />
        </svg>
        Recent URLs
      </h2>
      <div className="url-grid">
        {urls.map((url) => (
          <URLCard key={url.short_code} url={url} />
        ))}
      </div>
    </div>
  );
}
