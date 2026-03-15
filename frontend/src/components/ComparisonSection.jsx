export default function ComparisonSection({ rawScreenshot, optimizedUrl, visible }) {
  if (!visible) return null

  return (
    <section className={`story-section ${visible ? 'section-visible' : ''}`}>
      <div className="section-label">BEFORE vs AFTER</div>

      <div className="comparison-grid">
        <div className="comparison-panel">
          <div className="comparison-label comparison-label-raw">Human Web</div>
          <div className="comparison-iframe-wrapper comparison-raw">
            {rawScreenshot ? (
              <img
                src={`data:image/png;base64,${rawScreenshot}`}
                alt="Raw website screenshot"
                style={{ width: '100%', display: 'block' }}
              />
            ) : (
              <div className="comparison-placeholder">
                <div className="spinner" />
                <p>Capturing...</p>
              </div>
            )}
          </div>
        </div>

        <div className="comparison-panel">
          <div className="comparison-label comparison-label-optimized">Agent-Ready</div>
          <div className="comparison-iframe-wrapper comparison-optimized">
            {optimizedUrl ? (
              <iframe
                src={optimizedUrl}
                title="AI-optimized website"
              />
            ) : (
              <div className="comparison-placeholder">Generating...</div>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
