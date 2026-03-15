function getNodeColor(score, total) {
  if (score === total) return 'var(--accent-green)'
  if (score >= total / 2) return 'var(--accent-yellow)'
  return 'var(--accent-red)'
}

function formatChars(n) {
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`
  return String(n)
}

export default function ScoreReveal({
  rawScore,
  optimizedScore,
  totalTasks,
  tokenReduction,
  iterationsUsed,
  loopLog,
  stats,
  visible,
  optimizeOnly,
}) {
  if (!visible) return null

  const total = totalTasks || 5

  // Compute best AutoResearch score from loop log
  const bestLoopScore = loopLog?.length
    ? Math.max(...loopLog.map(e => e.score))
    : null
  const loopTotal = loopLog?.[0]?.total || 5

  return (
    <section className={`story-section ${visible ? 'section-visible' : ''}`}>
      <div className="section-label">THE RESULTS</div>

      {/* Agent Task Score (full mode only) */}
      {!optimizeOnly && (
        <>
          <h3 className="results-sub-header" style={{ marginBottom: 12 }}>Agent Task Completion</h3>
          <div className="score-reveal">
            <div className="score-reveal-card score-reveal-raw">
              <div className="score-reveal-number">{rawScore ?? 0}/{total}</div>
              <div className="score-reveal-label">Raw Site</div>
            </div>

            <div className="score-reveal-arrow">→</div>

            <div className="score-reveal-card score-reveal-optimized">
              <div className="score-reveal-number">{optimizedScore ?? 0}/{total}</div>
              <div className="score-reveal-label">AI-Optimized</div>
            </div>
          </div>
        </>
      )}

      {/* AutoResearch Content Score */}
      {bestLoopScore != null && (
        <>
          <h3 className="results-sub-header" style={{ marginTop: optimizeOnly ? 0 : 32, marginBottom: 12 }}>
            AutoResearch Content Quality
          </h3>
          <div className="score-reveal" style={optimizeOnly ? {} : { transform: 'scale(0.8)', transformOrigin: 'center' }}>
            <div className="score-reveal-card score-reveal-optimized">
              <div className="score-reveal-number">{bestLoopScore}/{loopTotal}</div>
              <div className="score-reveal-label">Questions Answered</div>
            </div>
          </div>
        </>
      )}

      {/* Metrics row */}
      <div className="score-reveal-metrics">
        {tokenReduction != null && tokenReduction > 0 && (
          <div className="metric">
            <div className="metric-value">{tokenReduction}%</div>
            <div className="metric-label">Content Reduction</div>
          </div>
        )}
        {iterationsUsed != null && (
          <div className="metric">
            <div className="metric-value">{iterationsUsed}</div>
            <div className="metric-label">AutoResearch Iterations</div>
          </div>
        )}
        {stats?.raw_content_chars > 0 && (
          <div className="metric">
            <div className="metric-value">{formatChars(stats.raw_content_chars)}</div>
            <div className="metric-label">Raw Content</div>
          </div>
        )}
        {stats?.optimized_json_chars > 0 && (
          <div className="metric">
            <div className="metric-value">{formatChars(stats.optimized_json_chars)}</div>
            <div className="metric-label">Structured Data</div>
          </div>
        )}
        {stats?.optimized_html_chars > 0 && (
          <div className="metric">
            <div className="metric-value">{formatChars(stats.optimized_html_chars)}</div>
            <div className="metric-label">Generated HTML</div>
          </div>
        )}
        {stats?.extraction_method && (
          <div className="metric">
            <div className="metric-value" style={{ fontSize: 24, textTransform: 'capitalize' }}>
              {stats.extraction_method}
            </div>
            <div className="metric-label">Extraction Method</div>
          </div>
        )}
      </div>

      {/* Karpathy AutoResearch breakdown */}
      {loopLog && loopLog.length > 0 && (
        <div className="results-loop-breakdown">
          <h3 className="results-sub-header">AutoResearch Iteration Breakdown</h3>
          <div className="results-loop-table">
            <div className="results-loop-header-row">
              <span>Iteration</span>
              <span>Score</span>
              <span>Status</span>
              <span>Details</span>
            </div>
            {loopLog.map((entry, i) => {
              const color = getNodeColor(entry.score, entry.total)
              const isPerfect = entry.score === entry.total
              const failedCount = entry.failed_questions?.length || 0
              return (
                <div key={i} className="results-loop-row">
                  <span className="results-loop-version">v{entry.version}</span>
                  <span className="results-loop-score" style={{ color }}>
                    {entry.score}/{entry.total}
                  </span>
                  <span>
                    {isPerfect ? (
                      <span className="results-badge results-badge-green">PERFECT</span>
                    ) : (
                      <span className="results-badge results-badge-yellow">{failedCount} failed</span>
                    )}
                  </span>
                  <span className="results-loop-detail">
                    {isPerfect
                      ? 'All questions answered correctly'
                      : entry.failed_questions?.map((q, qi) => (
                          <span key={qi} className="results-failed-q">{q}</span>
                        ))
                    }
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Benchmark questions used */}
      {stats?.questions_used && stats.questions_used.length > 0 && (
        <div className="results-questions">
          <h3 className="results-sub-header">Benchmark Questions (Content Quality)</h3>
          <div className="results-questions-list">
            {stats.questions_used.map((q, i) => (
              <div key={i} className="results-question-item">
                <span className="results-question-num">{i + 1}</span>
                <span>{q}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  )
}
