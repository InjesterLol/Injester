import { useState, useCallback } from 'react'
import URLInput from './components/URLInput'
import RawPanel from './components/RawPanel'
import OptimizedPanel from './components/OptimizedPanel'
import ScorePanel from './components/ScorePanel'
import AgentStream from './components/AgentStream'

function App() {
  const [loading, setLoading] = useState(false)
  const [rawUrl, setRawUrl] = useState(null)
  const [optimizedUrl, setOptimizedUrl] = useState(null)
  const [rawScore, setRawScore] = useState(null)
  const [optimizedScore, setOptimizedScore] = useState(null)
  const [loopLog, setLoopLog] = useState(null)
  const [agentRawScore, setAgentRawScore] = useState(null)
  const [agentOptimizedScore, setAgentOptimizedScore] = useState(null)
  const [taskResults, setTaskResults] = useState(null)
  const [activeTaskIndex, setActiveTaskIndex] = useState(-1)
  const [agentActive, setAgentActive] = useState(false)
  const [status, setStatus] = useState('Ready')

  const handleIngest = useCallback(async (url, siteType) => {
    setLoading(true)
    setStatus('Extracting + optimizing...')
    setRawUrl(url)
    setOptimizedUrl(null)
    setLoopLog(null)
    setRawScore(null)
    setOptimizedScore(null)
    setAgentRawScore(null)
    setAgentOptimizedScore(null)
    setTaskResults(null)

    try {
      // Step 1: Generate optimized HTML (includes Karpathy loop)
      const genRes = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, site_type: siteType }),
      })
      const genData = await genRes.json()

      if (!genRes.ok) throw new Error(genData.detail || 'Generation failed')

      setOptimizedUrl(genData.generated_url)
      setLoopLog(genData.loop_log)
      setStatus(`Optimized! Karpathy loop: ${genData.best_score} in ${genData.karpathy_iterations} iterations`)

      // Step 2: Run benchmark
      setStatus('Running benchmark...')
      const benchRes = await fetch('/api/benchmark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, site_type: siteType }),
      })
      const benchData = await benchRes.json()

      if (benchRes.ok) {
        setRawScore(`${benchData.raw_benchmark.score}/${benchData.raw_benchmark.total}`)
        setOptimizedScore(`${benchData.optimized_benchmark.score}/${benchData.optimized_benchmark.total}`)
      }

      setStatus('Ready — click "Run Agent" to test booking')
    } catch (err) {
      setStatus(`Error: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }, [])

  const handleDemo = useCallback(async (siteType) => {
    setLoading(true)
    setAgentActive(true)
    setStatus('Running full demo...')
    setRawUrl(null)
    setOptimizedUrl(null)
    setLoopLog(null)
    setRawScore(null)
    setOptimizedScore(null)
    setAgentRawScore(null)
    setAgentOptimizedScore(null)
    setTaskResults(null)

    try {
      const res = await fetch('/api/demo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ site_type: siteType, max_iterations: 3 }),
      })
      const data = await res.json()

      if (!res.ok) throw new Error(data.detail || 'Demo failed')

      setRawUrl(data.proxy_url)
      setOptimizedUrl(data.generated_url)
      setLoopLog(data.karpathy?.log)
      setAgentRawScore(data.raw_agent?.score)
      setAgentOptimizedScore(data.optimized_agent?.score)

      // Build task results from agent data
      const tasks = data.optimized_agent?.task_results || []
      setTaskResults(tasks)

      setStatus(`Demo complete! Raw: ${data.raw_agent?.score} → Optimized: ${data.optimized_agent?.score}`)
    } catch (err) {
      setStatus(`Error: ${err.message}`)
    } finally {
      setLoading(false)
      setAgentActive(false)
    }
  }, [])

  const handleRunAgent = useCallback(async () => {
    if (!rawUrl) return
    setAgentActive(true)
    setStatus('Running agent on raw site...')

    try {
      // Run on raw site
      const rawRes = await fetch('/api/run-agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: rawUrl, site_type: 'united' }),
      })
      const rawData = await rawRes.json()
      setAgentRawScore(rawData.score)

      // Run on optimized site
      if (optimizedUrl) {
        setStatus('Running agent on optimized site...')
        const optRes = await fetch('/api/run-agent', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            url: `${window.location.origin}${optimizedUrl}`,
            site_type: 'united',
          }),
        })
        const optData = await optRes.json()
        setAgentOptimizedScore(optData.score)
        setTaskResults(optData.task_results)
      }

      setStatus('Agent runs complete!')
    } catch (err) {
      setStatus(`Agent error: ${err.message}`)
    } finally {
      setAgentActive(false)
    }
  }, [rawUrl, optimizedUrl])

  return (
    <>
      <div className="header">
        <h1>injester<span>.lol</span></h1>
        <div className="header-controls">
          {optimizedUrl && (
            <button className="btn btn-agent" onClick={handleRunAgent} disabled={loading || agentActive}>
              {agentActive ? 'Agent Running...' : 'Run Agent'}
            </button>
          )}
        </div>
      </div>

      <URLInput onIngest={handleIngest} onDemo={handleDemo} loading={loading} />

      <div className="panels">
        <RawPanel url={rawUrl} />
        <OptimizedPanel url={optimizedUrl} loading={loading} />
        <div className="panel">
          <div className="panel-header">
            <h2>Panel 3 — Results</h2>
            <span className="panel-label label-score">Proof it works</span>
          </div>
          <div className="panel-content" style={{ overflow: 'auto' }}>
            <ScorePanel
              rawScore={rawScore}
              optimizedScore={optimizedScore}
              loopLog={loopLog}
              agentRawScore={agentRawScore}
              agentOptimizedScore={agentOptimizedScore}
              taskResults={taskResults}
              activeTaskIndex={activeTaskIndex}
              loading={loading}
            />
            {agentActive && <AgentStream active={agentActive} />}
          </div>
        </div>
      </div>

      <div className="status-bar">
        <div className="status-item">
          <span className={`status-dot ${loading || agentActive ? 'loading' : 'connected'}`} />
          <span>{status}</span>
        </div>
        <div className="status-item">
          <span style={{ color: 'var(--text-secondary)' }}>Powered by Nebius + Tavily</span>
        </div>
      </div>
    </>
  )
}

export default App
