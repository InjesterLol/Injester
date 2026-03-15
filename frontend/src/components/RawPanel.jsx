export default function RawPanel({ url }) {
  return (
    <div className="panel">
      <div className="panel-header">
        <h2>Panel 1 — Human Web</h2>
        <span className="panel-label label-human">What a human sees</span>
      </div>
      <div className="panel-content">
        {url ? (
          <iframe src={url} title="Raw website" sandbox="allow-same-origin" />
        ) : (
          <div className="loading-text">
            <p>Drop a URL above to see the raw website</p>
            <p style={{ fontSize: 13, marginTop: 8, color: 'var(--text-secondary)' }}>
              Messy, hostile, overwhelming — what agents fail on
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
