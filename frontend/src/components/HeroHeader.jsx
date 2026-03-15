import { useState, useMemo } from 'react'

const PHASE_LABELS = {
  idle: 'Ready',
  extracting: 'Extracting content...',
  optimizing: 'Karpathy AutoResearch...',
  generation_complete: 'HTML generated',
  agent_running_raw: 'Agent on raw site...',
  agent_running_optimized: 'Agent on optimized site...',
  complete: 'Demo complete!',
}

// Default dates: 5 days from now, return 5 days after
function defaultDates() {
  const now = new Date()
  const dep = new Date(now)
  dep.setDate(dep.getDate() + 5)
  const ret = new Date(dep)
  ret.setDate(ret.getDate() + 5)
  const fmt = (d) => d.toISOString().split('T')[0]
  return { departure: fmt(dep), returnDate: fmt(ret) }
}

function detectType(url) {
  if (/united\.com/i.test(url)) return 'united'
  if (/airbnb\.com/i.test(url)) return 'airbnb'
  return null
}

export default function HeroHeader({ phase, onIngest, onDemo, onReset, loading }) {
  const [url, setUrl] = useState('')
  const [siteType, setSiteType] = useState('auto')
  const [maxIterations, setMaxIterations] = useState('3')
  const [objective, setObjective] = useState('')

  const defaults = useMemo(defaultDates, [])
  const [fromAirport, setFromAirport] = useState('SFO')
  const [toAirport, setToAirport] = useState('JFK')
  const [departureDate, setDepartureDate] = useState(defaults.departure)
  const [returnDate, setReturnDate] = useState(defaults.returnDate)
  const [passengers, setPassengers] = useState('1')
  const [guests, setGuests] = useState('2')

  // Resolved site type (auto-detect from URL or manual selection)
  const resolvedType = siteType === 'auto' ? (detectType(url) || 'general') : siteType

  const buildTripDetails = () => {
    if (resolvedType === 'united') {
      return {
        from_airport: fromAirport,
        to_airport: toAirport,
        departure_date: departureDate,
        return_date: returnDate,
        passengers,
      }
    }
    if (resolvedType === 'airbnb') {
      return {
        check_in: departureDate,
        check_out: returnDate,
        guests,
      }
    }
    return {
      departure_date: departureDate,
      return_date: returnDate,
    }
  }

  const handleIngest = () => {
    if (url.trim()) onIngest(url.trim(), resolvedType, buildTripDetails(), parseInt(maxIterations) || 3, objective.trim() || null)
  }

  const handleReset = () => {
    setUrl('')
    setObjective('')
    onReset()
  }

  return (
    <header className="hero-header">
      <div className="hero-row hero-row-main">
        <div className="hero-left">
          <h1 className="hero-logo">injester<span>.lol</span></h1>
        </div>

        <div className="hero-center">
          <input
            type="text"
            className="hero-url-input"
            placeholder="Drop any URL — e.g., airbnb.com/rooms/123, united.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleIngest()}
            disabled={loading}
          />
          <select
            className="hero-select"
            value={siteType}
            onChange={(e) => setSiteType(e.target.value)}
          >
            <option value="auto">Auto-detect</option>
            <option value="united">United Airlines</option>
            <option value="airbnb">Airbnb</option>
          </select>
          <button
            className="btn btn-primary"
            onClick={handleIngest}
            disabled={loading || !url.trim()}
          >
            Ingest
          </button>
          <button
            className="btn btn-demo"
            onClick={() => onDemo(resolvedType === 'general' ? 'united' : resolvedType, buildTripDetails(), parseInt(maxIterations) || 3)}
            disabled={loading}
          >
            {loading ? 'Running...' : 'Demo'}
          </button>
          {phase !== 'idle' && (
            <button className="btn btn-reset" onClick={handleReset} disabled={loading}>
              Clear
            </button>
          )}
        </div>

        <div className="hero-right">
          <span className={`phase-badge phase-${phase}`}>
            {PHASE_LABELS[phase] || phase}
          </span>
        </div>
      </div>

      {/* Settings row: iterations + objective */}
      <div className="hero-row hero-row-settings">
        <label className="trip-field trip-field-small">
          <span>Iterations</span>
          <select value={maxIterations} onChange={e => setMaxIterations(e.target.value)} disabled={loading}>
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="5">5</option>
            <option value="10">10</option>
          </select>
        </label>
        <label className="trip-field trip-field-wide">
          <span>Objective</span>
          <input
            type="text"
            value={objective}
            onChange={e => setObjective(e.target.value)}
            placeholder="e.g., Book a flight, Find cheapest option, Extract pricing..."
            disabled={loading}
          />
        </label>
      </div>

      {/* Trip details row */}
      <div className="hero-row hero-row-trip">
        {resolvedType === 'united' && (
          <>
            <label className="trip-field">
              <span>From</span>
              <input type="text" value={fromAirport} onChange={e => setFromAirport(e.target.value)} disabled={loading} maxLength={4} />
            </label>
            <label className="trip-field">
              <span>To</span>
              <input type="text" value={toAirport} onChange={e => setToAirport(e.target.value)} disabled={loading} maxLength={4} />
            </label>
            <label className="trip-field">
              <span>Depart</span>
              <input type="date" value={departureDate} onChange={e => setDepartureDate(e.target.value)} disabled={loading} />
            </label>
            <label className="trip-field">
              <span>Return</span>
              <input type="date" value={returnDate} onChange={e => setReturnDate(e.target.value)} disabled={loading} />
            </label>
            <label className="trip-field trip-field-small">
              <span>Pax</span>
              <input type="number" min="1" max="9" value={passengers} onChange={e => setPassengers(e.target.value)} disabled={loading} />
            </label>
          </>
        )}

        {resolvedType === 'airbnb' && (
          <>
            <label className="trip-field">
              <span>Check-in</span>
              <input type="date" value={departureDate} onChange={e => setDepartureDate(e.target.value)} disabled={loading} />
            </label>
            <label className="trip-field">
              <span>Check-out</span>
              <input type="date" value={returnDate} onChange={e => setReturnDate(e.target.value)} disabled={loading} />
            </label>
            <label className="trip-field trip-field-small">
              <span>Guests</span>
              <input type="number" min="1" max="16" value={guests} onChange={e => setGuests(e.target.value)} disabled={loading} />
            </label>
          </>
        )}

        {resolvedType === 'general' && (
          <>
            <label className="trip-field">
              <span>Start date</span>
              <input type="date" value={departureDate} onChange={e => setDepartureDate(e.target.value)} disabled={loading} />
            </label>
            <label className="trip-field">
              <span>End date</span>
              <input type="date" value={returnDate} onChange={e => setReturnDate(e.target.value)} disabled={loading} />
            </label>
          </>
        )}
      </div>
    </header>
  )
}
