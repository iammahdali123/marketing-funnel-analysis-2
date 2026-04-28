import React, { useState } from 'react'
import './ChurnTable.css'

const RISK_COLORS = { high: '#e74c3c', medium: '#f39c12', low: '#27ae60' }

export default function ChurnTable({ data }) {
  const [filter, setFilter] = useState('all')

  const filtered =
    filter === 'all' ? data : data.filter((u) => u.risk_level === filter)

  if (data.length === 0) {
    return (
      <p style={{ color: '#aaa', textAlign: 'center', padding: '1rem' }}>
        No users found. Upload events to generate predictions.
      </p>
    )
  }

  return (
    <div>
      <div className="filter-bar">
        {['all', 'high', 'medium', 'low'].map((f) => (
          <button
            key={f}
            className={filter === f ? 'active' : ''}
            onClick={() => setFilter(f)}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>
      <div className="table-wrapper">
        <table className="churn-table">
          <thead>
            <tr>
              <th>User ID</th>
              <th>Churn Probability</th>
              <th>Risk Level</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((u) => (
              <tr key={u.user_external_id}>
                <td>{u.user_external_id}</td>
                <td>
                  <div className="prob-bar-wrapper">
                    <div
                      className="prob-bar"
                      style={{
                        width: `${u.churn_probability * 100}%`,
                        background: RISK_COLORS[u.risk_level],
                      }}
                    />
                    <span>{(u.churn_probability * 100).toFixed(1)}%</span>
                  </div>
                </td>
                <td>
                  <span
                    className="risk-badge"
                    style={{ background: RISK_COLORS[u.risk_level] }}
                  >
                    {u.risk_level}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
