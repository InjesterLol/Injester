import { useState } from 'react'

function getNodeColor(score, total) {
  if (score === total) return 'var(--accent-green)'
  if (score >= total / 2) return 'var(--accent-yellow)'
  return 'var(--accent-red)'
}

export default function ProcessTimeline({ loopLog, visible }) {
  const [expandedNode, setExpandedNode] = useState(null)

  if (!visible || !loopLog || loopLog.length === 0) return null

  return (
    <section className={`story-section ${visible ? 'section-visible' : ''}`}>
      <div className="section-label">KARPATHY AUTORESEARCH</div>

      <p className="section-tagline">
        Iteratively optimizing until the agent succeeds
      </p>

      <div className="timeline">
        {loopLog.map((entry, i) => {
          const color = getNodeColor(entry.score, entry.total)
          const isExpanded = expandedNode === i
          const isLast = i === loopLog.length - 1

          return (
            <div key={i} className="timeline-step">
              <div
                className="timeline-node"
                style={{ borderColor: color, color }}
                onClick={() => setExpandedNode(isExpanded ? null : i)}
              >
                <div className="timeline-version">v{entry.version}</div>
                <div className="timeline-score">{entry.score}/{entry.total}</div>
              </div>

              {isExpanded && entry.failed_questions && entry.failed_questions.length > 0 && (
                <div className="timeline-details">
                  <div className="timeline-details-title">Failed questions:</div>
                  {entry.failed_questions.map((q, qi) => (
                    <div key={qi} className="timeline-failed-q">— {q}</div>
                  ))}
                </div>
              )}

              {!isLast && (
                <div className="timeline-connector">
                  <span className="timeline-arrow">→</span>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </section>
  )
}
