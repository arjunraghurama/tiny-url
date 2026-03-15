export default function URLCard({ url }) {
  const truncate = (str, max = 50) =>
    str.length > max ? str.substring(0, max) + '...' : str;

  const timeAgo = (dateStr) => {
    const now = new Date();
    const date = new Date(dateStr);
    const seconds = Math.floor((now - date) / 1000);

    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  return (
    <div className="url-card">
      <div className="url-card-header">
        <a
          href={url.short_url}
          target="_blank"
          rel="noopener noreferrer"
          className="url-card-short"
        >
          {url.short_url.replace('http://localhost:8000/', '')}
        </a>
        <span className="url-card-time">{timeAgo(url.created_at)}</span>
      </div>
      <div className="url-card-original" title={url.original_url}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
          <polyline points="15 3 21 3 21 9" />
          <line x1="10" y1="14" x2="21" y2="3" />
        </svg>
        {truncate(url.original_url)}
      </div>
      <div className="url-card-footer">
        <div className="url-card-clicks">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
            <circle cx="12" cy="12" r="3" />
          </svg>
          {url.clicks} {url.clicks === 1 ? 'click' : 'clicks'}
        </div>
      </div>
    </div>
  );
}
