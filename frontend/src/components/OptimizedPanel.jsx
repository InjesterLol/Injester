export default function OptimizedPanel({ url, loading }) {
  return (
    <div className="panel">
      <div className="panel-header">
        <h2>Panel 2 — AI-Optimized</h2>
        <span className="panel-label label-ai">What an agent needs</span>
      </div>
      <div className="panel-content">
        {loading ? (
          <div className="loading-text">
            <div className="spinner" />
            <p style={{ marginTop: 12 }}>Optimizing with Karpathy loop...</p>
            <p style={{ fontSize: 13, marginTop: 8, color: 'var(--text-secondary)' }}>
              Tavily Extract → Nebius AI → Iterate → Generate HTML
            </p>
          </div>
        ) : url ? (
          <iframe src={url} title="AI-optimized website" sandbox="allow-same-origin" />
        ) : (
          <div className="loading-text">
            <p>AI-optimized version will appear here</p>
            <p style={{ fontSize: 13, marginTop: 8, color: 'var(--text-secondary)' }}>
              Clean, structured, typed — prices, dates, actions, entities
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
