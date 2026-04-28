import React, { useState } from 'react'
import Dashboard from './components/Dashboard'
import EventUpload from './components/EventUpload'
import './App.css'

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [refreshKey, setRefreshKey] = useState(0)

  const handleDataLoaded = () => {
    setRefreshKey((k) => k + 1)
    setActiveTab('dashboard')
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>📊 Marketing Funnel Analyzer</h1>
        <nav>
          <button
            className={activeTab === 'dashboard' ? 'active' : ''}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={activeTab === 'upload' ? 'active' : ''}
            onClick={() => setActiveTab('upload')}
          >
            Upload Events
          </button>
        </nav>
      </header>
      <main className="app-main">
        {activeTab === 'dashboard' ? (
          <Dashboard key={refreshKey} />
        ) : (
          <EventUpload onDataLoaded={handleDataLoaded} />
        )}
      </main>
    </div>
  )
}
