import React, { useEffect, useState } from 'react'
import { getFunnelAnalysis, getChurnPredictions } from '../api'
import FunnelChart from './FunnelChart'
import ConversionChart from './ConversionChart'
import ChurnTable from './ChurnTable'
import './Dashboard.css'

export default function Dashboard() {
  const [funnel, setFunnel] = useState(null)
  const [churnData, setChurnData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([getFunnelAnalysis(), getChurnPredictions()])
      .then(([fRes, cRes]) => {
        setFunnel(fRes.data)
        setChurnData(cRes.data)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="loading">Loading analytics…</div>
  if (error) return <div className="error">Error: {error}</div>
  if (!funnel) return null

  const highRisk = churnData.filter((u) => u.risk_level === 'high').length
  const medRisk = churnData.filter((u) => u.risk_level === 'medium').length

  return (
    <div className="dashboard">
      {/* KPI Cards */}
      <div className="kpi-row">
        <div className="kpi-card">
          <span className="kpi-label">Total Users</span>
          <span className="kpi-value">{funnel.total_users}</span>
        </div>
        <div className="kpi-card">
          <span className="kpi-label">Funnel Stages</span>
          <span className="kpi-value">{funnel.stages.length}</span>
        </div>
        <div className="kpi-card kpi-danger">
          <span className="kpi-label">High Churn Risk</span>
          <span className="kpi-value">{highRisk}</span>
        </div>
        <div className="kpi-card kpi-warning">
          <span className="kpi-label">Medium Churn Risk</span>
          <span className="kpi-value">{medRisk}</span>
        </div>
      </div>

      {/* Charts Row */}
      <div className="charts-row">
        <div className="chart-card">
          <h2>Funnel Drop-off</h2>
          <FunnelChart stages={funnel.stages} />
        </div>
        <div className="chart-card">
          <h2>Stage Conversion Rates</h2>
          <ConversionChart stages={funnel.stages} />
        </div>
      </div>

      {/* Churn Table */}
      <div className="table-card">
        <h2>Churn Risk Predictions</h2>
        <ChurnTable data={churnData} />
      </div>
    </div>
  )
}
