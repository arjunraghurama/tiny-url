import { useState, useEffect, useRef } from 'react';

/**
 * UserMenu — displays auth state in the header.
 *
 * Logged out: "Sign In" button
 * Logged in: User avatar + name + dropdown with "Sign Out"
 */
export default function UserMenu({ keycloak }) {
  const [open, setOpen] = useState(false);
  const menuRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClick = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  if (!keycloak?.authenticated) {
    return (
      <button
        id="sign-in-btn"
        className="auth-btn sign-in-btn"
        onClick={() => keycloak?.login()}
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
          <polyline points="10 17 15 12 10 7" />
          <line x1="15" y1="12" x2="3" y2="12" />
        </svg>
        Sign In
      </button>
    );
  }

  const username = keycloak.tokenParsed?.preferred_username || 'User';
  const initial = username.charAt(0).toUpperCase();

  return (
    <div className="user-menu" ref={menuRef}>
      <button
        id="user-menu-btn"
        className="user-menu-trigger"
        onClick={() => setOpen(!open)}
      >
        <div className="user-avatar">{initial}</div>
        <span className="user-name">{username}</span>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={`chevron ${open ? 'chevron-up' : ''}`}>
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>

      {open && (
        <div className="user-dropdown">
          <div className="dropdown-header">
            <div className="dropdown-avatar">{initial}</div>
            <div className="dropdown-info">
              <span className="dropdown-name">{username}</span>
              <span className="dropdown-email">
                {keycloak.tokenParsed?.email || ''}
              </span>
            </div>
          </div>
          <div className="dropdown-divider" />
          <button
            id="sign-out-btn"
            className="dropdown-item sign-out-item"
            onClick={() => keycloak.logout()}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            Sign Out
          </button>
        </div>
      )}
    </div>
  );
}
