import { useEffect, useRef, useState } from 'react'

export default function AgentStream({ active }) {
  const [screenshot, setScreenshot] = useState(null)
  const [log, setLog] = useState([])
  const [connected, setConnected] = useState(false)
  const wsRef = useRef(null)
  const logEndRef = useRef(null)

  useEffect(() => {
    if (!active) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/agent`)
    wsRef.current = ws

    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === 'screenshot') {
        setScreenshot(data.data)
      }

      if (data.type === 'action') {
        setLog(prev => [...prev, {
          type: 'action',
          text: `${data.action?.type} → ${data.llm_decision?.selector || 'unknown'}`,
          confidence: data.llm_decision?.confidence,
        }])
      }

      if (data.type === 'action_result') {
        setLog(prev => [...prev, {
          type: data.success ? 'success' : 'failure',
          text: data.success ? 'Action succeeded' : `Failed: ${data.error || 'unknown'}`,
        }])
      }

      if (data.type === 'task_start') {
        setLog(prev => [...prev, {
          type: 'info',
          text: `Starting: ${data.task_name}`,
        }])
      }

      if (data.type === 'task_complete') {
        setLog(prev => [...prev, {
          type: data.completed ? 'success' : 'failure',
          text: `${data.task_id}: ${data.completed ? 'COMPLETED' : 'FAILED'} — ${data.reasoning || ''}`,
        }])
      }

      if (data.type === 'demo_phase') {
        setLog(prev => [...prev, {
          type: 'info',
          text: `=== ${data.phase === 'raw_agent' ? 'Running agent on RAW site' : 'Running agent on OPTIMIZED site'} ===`,
        }])
      }

      if (data.type === 'agent_complete') {
        setLog(prev => [...prev, {
          type: 'info',
          text: `Agent finished: ${data.summary?.score}`,
        }])
      }
    }

    return () => {
      ws.close()
      wsRef.current = null
    }
  }, [active])

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [log])

  return (
    <div className="agent-stream">
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
        <span className={`status-dot ${connected ? 'connected' : 'disconnected'}`} />
        <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
          {connected ? 'Agent connected' : 'Waiting for agent...'}
        </span>
      </div>

      {screenshot && (
        <img
          className="agent-screenshot"
          src={`data:image/png;base64,${screenshot}`}
          alt="Agent browser view"
        />
      )}

      <div className="agent-log">
        {log.map((entry, i) => (
          <div key={i} className={`agent-log-entry ${entry.type}`}>
            <span className="icon">
              {entry.type === 'success' ? '+' :
               entry.type === 'failure' ? 'x' :
               entry.type === 'action' ? '>' : '-'}
            </span>
            <span>{entry.text}</span>
          </div>
        ))}
        <div ref={logEndRef} />
      </div>
    </div>
  )
}
