import { useState } from 'react'

export default function URLInput({ onIngest, onDemo, loading }) {
  const [url, setUrl] = useState('')
  const [siteType, setSiteType] = useState('united')

  const handleIngest = () => {
    if (url.trim()) {
      onIngest(url.trim(), siteType)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleIngest()
  }

  return (
    <div className="url-input-bar">
      <input
        type="text"
        placeholder="Drop any URL here — e.g., united.com/flights or airbnb.com/listing"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={loading}
      />
      <select value={siteType} onChange={(e) => setSiteType(e.target.value)}>
        <option value="united">United Airlines</option>
        <option value="airbnb">Airbnb</option>
      </select>
      <button className="btn btn-primary" onClick={handleIngest} disabled={loading || !url.trim()}>
        {loading ? <span className="spinner" /> : 'Ingest'}
      </button>
      <button className="btn btn-demo" onClick={() => onDemo(siteType)} disabled={loading}>
        Demo Mode
      </button>
    </div>
  )
}
