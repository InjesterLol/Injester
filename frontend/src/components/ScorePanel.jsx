export default function ScorePanel({
  rawScore,
  optimizedScore,
  loopLog,
  agentRawScore,
  agentOptimizedScore,
  taskResults,
  activeTaskIndex,
  loading,
}) {
  return (
    <div className="panel">
      <div className="panel-header">
        <h2>Panel 3 — Benchmark</h2>
        <span className="panel-label label-score">Proof it works</span>
      </div>
      <div className="panel-content">
        {/* Agent Scores — Big Numbers */}
        {(agentRawScore !== null || agentOptimizedScore !== null) && (
          <div className="score-comparison">
            <div className="score-card raw">
              <div className="value">{agentRawScore ?? '—'}</div>
              <div className="label">Raw Site</div>
            </div>
            <div className="score-card optimized">
              <div className="value">{agentOptimizedScore ?? '—'}</div>
              <div className="label">AI-Optimized</div>
            </div>
          </div>
        )}

        {/* Task Checklist */}
        {taskResults && taskResults.length > 0 && (
          <div className="task-list">
            <h3 style={{ fontSize: 13, color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: 12 }}>
              Agent Tasks
            </h3>
            {taskResults.map((task, i) => (
              <div
                key={task.task_id || i}
                className={`task-item ${
                  i === activeTaskIndex ? 'active' :
                  task.completed ? 'completed' :
                  task.completed === false ? 'failed' : 'pending'
                }`}
              >
                <span>
                  {i === activeTaskIndex ? '>' :
                   task.completed ? '+' :
                   task.completed === false ? 'x' : '-'}
                </span>
                <span>{task.task_name || task.name || `Task ${i + 1}`}</span>
              </div>
            ))}
          </div>
        )}

        {/* Karpathy Loop Log */}
        {loopLog && loopLog.length > 0 && (
          <div className="loop-log">
            <h3>Karpathy AutoResearch Loop</h3>
            {loopLog.map((entry, i) => (
              <div key={i} className="loop-entry">
                <span className="version">v{entry.version}</span>
                <span className="score" style={{
                  color: entry.score === entry.total ? 'var(--accent-green)' :
                         entry.score >= entry.total / 2 ? 'var(--accent-yellow)' :
                         'var(--accent-red)'
                }}>
                  {entry.score}/{entry.total}
                </span>
                {i < loopLog.length - 1 && <span className="arrow">→</span>}
                {entry.failed_questions && entry.failed_questions.length > 0 && (
                  <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                    missed: {entry.failed_questions.join(', ').slice(0, 50)}
                  </span>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Benchmark Q&A Scores */}
        {(rawScore !== null || optimizedScore !== null) && (
          <div style={{ padding: 16 }}>
            <h3 style={{ fontSize: 13, color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: 12 }}>
              Content Benchmark
            </h3>
            <div className="score-comparison">
              <div className="score-card raw">
                <div className="value" style={{ fontSize: 36 }}>{rawScore ?? '—'}</div>
                <div className="label">Raw Content</div>
              </div>
              <div className="score-card optimized">
                <div className="value" style={{ fontSize: 36 }}>{optimizedScore ?? '—'}</div>
                <div className="label">Optimized</div>
              </div>
            </div>
          </div>
        )}

        {loading && (
          <div className="loading-text">
            <div className="spinner" />
            <p style={{ marginTop: 12 }}>Running benchmark...</p>
          </div>
        )}

        {!loading && !rawScore && !agentRawScore && !loopLog && (
          <div className="loading-text">
            <div className="score-big">
              <div className="score-number" style={{ color: 'var(--border)' }}>—/5</div>
              <div className="score-label">Tasks completed score</div>
            </div>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              Big numbers, readable from back of room
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
