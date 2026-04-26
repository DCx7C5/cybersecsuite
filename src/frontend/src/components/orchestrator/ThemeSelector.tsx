import { useState } from 'react'

type Theme = 'light' | 'dark' | 'auto'

export default function ThemeSelector() {
  const [theme, setTheme] = useState<Theme>('auto')

  const handleThemeChange = (newTheme: Theme) => {
    setTheme(newTheme)
    localStorage.setItem('theme-preference', newTheme)
    if (newTheme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark')
    } else if (newTheme === 'light') {
      document.documentElement.setAttribute('data-theme', 'light')
    } else {
      document.documentElement.removeAttribute('data-theme')
    }
  }

  return (
    <div className="theme-selector" data-testid="theme-selector">
      <h3>Theme</h3>
      <div className="theme-options">
        <button
          className={`theme-btn ${theme === 'light' ? 'active' : ''}`}
          onClick={() => handleThemeChange('light')}
          data-testid="theme-light"
          title="Light theme"
        >
          ☀️ Light
        </button>
        <button
          className={`theme-btn ${theme === 'dark' ? 'active' : ''}`}
          onClick={() => handleThemeChange('dark')}
          data-testid="theme-dark"
          title="Dark theme"
        >
          🌙 Dark
        </button>
        <button
          className={`theme-btn ${theme === 'auto' ? 'active' : ''}`}
          onClick={() => handleThemeChange('auto')}
          data-testid="theme-auto"
          title="Auto (system preference)"
        >
          🔄 Auto
        </button>
      </div>

      <style jsx>{`
        .theme-selector {
          margin-bottom: 1.5rem;
          padding-bottom: 1.5rem;
          border-bottom: 1px solid var(--border);
        }

        .theme-selector h3 {
          margin: 0 0 1rem 0;
          font-size: 0.875rem;
          text-transform: uppercase;
          color: var(--text-muted);
          letter-spacing: 0.5px;
        }

        .theme-options {
          display: flex;
          gap: 0.75rem;
          flex-wrap: wrap;
        }

        .theme-btn {
          flex: 1;
          min-width: 100px;
          padding: 0.75rem;
          border: 1px solid var(--border);
          background: var(--surface-2);
          color: var(--text);
          cursor: pointer;
          border-radius: 4px;
          font-size: 0.875rem;
          transition: all 0.2s;
        }

        .theme-btn:hover {
          background: var(--surface-3);
        }

        .theme-btn.active {
          background: var(--accent);
          color: white;
          border-color: var(--accent);
        }

        @media (max-width: 768px) {
          .theme-options {
            flex-direction: column;
          }

          .theme-btn {
            width: 100%;
          }
        }
      `}</style>
    </div>
  )
}
