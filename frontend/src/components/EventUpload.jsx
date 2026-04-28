import React, { useState } from 'react'
import { postBulkEvents } from '../api'
import './EventUpload.css'

const SAMPLE_EVENTS = [
  { user_external_id: 'user_001', event_type: 'page_view', stage: 'awareness' },
  { user_external_id: 'user_001', event_type: 'ad_click', stage: 'interest' },
  { user_external_id: 'user_001', event_type: 'product_view', stage: 'consideration' },
  { user_external_id: 'user_001', event_type: 'add_to_cart', stage: 'intent' },
  { user_external_id: 'user_001', event_type: 'purchase', stage: 'purchase' },
  { user_external_id: 'user_002', event_type: 'page_view', stage: 'awareness' },
  { user_external_id: 'user_002', event_type: 'ad_click', stage: 'interest' },
  { user_external_id: 'user_002', event_type: 'product_view', stage: 'consideration' },
  { user_external_id: 'user_003', event_type: 'page_view', stage: 'awareness' },
  { user_external_id: 'user_003', event_type: 'ad_click', stage: 'interest' },
  { user_external_id: 'user_004', event_type: 'page_view', stage: 'awareness' },
  { user_external_id: 'user_005', event_type: 'page_view', stage: 'awareness' },
  { user_external_id: 'user_005', event_type: 'ad_click', stage: 'interest' },
  { user_external_id: 'user_005', event_type: 'product_view', stage: 'consideration' },
  { user_external_id: 'user_005', event_type: 'add_to_cart', stage: 'intent' },
]

export default function EventUpload({ onDataLoaded }) {
  const [jsonText, setJsonText] = useState('')
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleLoadSample = () => {
    setJsonText(JSON.stringify(SAMPLE_EVENTS, null, 2))
    setStatus(null)
  }

  const handleSubmit = async () => {
    try {
      const events = JSON.parse(jsonText)
      if (!Array.isArray(events)) throw new Error('Expected a JSON array')
      setLoading(true)
      setStatus(null)
      const res = await postBulkEvents(events)
      setStatus({ type: 'success', message: `✅ Created ${res.data.created} events successfully!` })
      if (onDataLoaded) onDataLoaded()
    } catch (e) {
      setStatus({ type: 'error', message: `❌ Error: ${e.message}` })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="upload-card">
      <h2>Upload Event Data</h2>
      <p className="upload-desc">
        Paste a JSON array of events. Each event needs{' '}
        <code>user_external_id</code>, <code>event_type</code>, and{' '}
        <code>stage</code> (one of: awareness, interest, consideration, intent,
        purchase).
      </p>
      <div className="upload-actions">
        <button className="btn-secondary" onClick={handleLoadSample}>
          Load Sample Data
        </button>
      </div>
      <textarea
        className="json-input"
        value={jsonText}
        onChange={(e) => setJsonText(e.target.value)}
        placeholder='[{"user_external_id": "user_1", "event_type": "page_view", "stage": "awareness"}]'
        rows={16}
      />
      {status && (
        <div className={`status-msg ${status.type}`}>{status.message}</div>
      )}
      <button
        className="btn-primary"
        onClick={handleSubmit}
        disabled={loading || !jsonText.trim()}
      >
        {loading ? 'Uploading…' : 'Upload Events'}
      </button>
    </div>
  )
}
