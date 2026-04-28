import React, {useState} from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const API = axios.create({ baseURL: import.meta.env.VITE_API || 'http://localhost:8000' })

export default function App(){
  const [file, setFile] = useState(null)
  const [steps, setSteps] = useState('visit,signup,trial_start,purchase')
  const [funnel, setFunnel] = useState(null)
  const [suggestions, setSuggestions] = useState(null)
  const [status, setStatus] = useState('')

  async function upload(e){
    e.preventDefault()
    if(!file){ setStatus('Choose CSV'); return }
    setStatus('Uploading...')
    const fd = new FormData()
    fd.append('file', file)
    try{
      const res = await API.post('/ingest/csv', fd, { headers: {'Content-Type':'multipart/form-data'} })
      setStatus(`Inserted ${res.data.inserted} rows`)
      await computeFunnel()
    }catch(err){
      setStatus('Upload error: ' + (err.response?.data?.detail || err.message))
    }
  }

  async function computeFunnel(){
    setStatus('Computing funnel...')
    try{
      const res = await API.get('/funnel', { params: { steps } })
      setFunnel(res.data)
      setStatus('Done')
    }catch(err){
      setStatus('Error: ' + err.message)
    }
  }

  async function getSuggestions(){
    setStatus('Running ML...')
    try{
      const res = await API.get('/suggestions', { params: { steps } })
      setSuggestions(res.data)
      setStatus('ML done')
    }catch(err){
      setStatus('ML error: ' + err.message)
    }
  }

  return (
    <div style={{maxWidth:1000, margin:'24px auto', fontFamily:'system-ui'}}>
      <h1>Automated Marketing Funnel Analyzer</h1>
      <div style={{marginBottom:12}}>
        <label>Funnel steps: </label>
        <input value={steps} onChange={(e)=>setSteps(e.target.value)} style={{width:600}} />
        <button onClick={computeFunnel} style={{marginLeft:8}}>Compute</button>
      </div>

      <form onSubmit={upload} style={{marginBottom:12}}>
        <input type="file" accept=".csv" onChange={e=>setFile(e.target.files[0])} />
        <button type="submit" style={{marginLeft:8}}>Upload CSV</button>
        <button type="button" onClick={getSuggestions} style={{marginLeft:8}}>Get Suggestions</button>
      </form>

      <div><strong>Status:</strong> {status}</div>

      {funnel && (
        <div style={{marginTop:20}}>
          <h2>Funnel</h2>
          <div style={{height:300}}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={funnel.steps.map((s,i)=>({name:s, count:funnel.counts[i]}))}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#3182ce" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <h3>Drop-offs</h3>
          <table style={{width:'100%', borderCollapse:'collapse'}}>
            <thead><tr><th>From</th><th>To</th><th>Count From</th><th>Count To</th><th>Drop Rate</th></tr></thead>
            <tbody>
              {funnel.dropoffs.map((d,i)=>(
                <tr key={i}><td>{d.from}</td><td>{d.to}</td><td>{d.count_from}</td><td>{d.count_to}</td><td>{(d.drop_rate*100).toFixed(1)}%</td></tr>
              ))}
            </tbody>
          </table>
          {funnel.top_dropoff && (<div style={{marginTop:12, padding:12, background:'#fff7ed'}}><strong>Top drop-off:</strong> {funnel.top_dropoff.from} → {funnel.top_dropoff.to} — {(funnel.top_dropoff.drop_rate*100).toFixed(1)}%</div>)}
        </div>
      )}

      {suggestions && (
        <div style={{marginTop:20}}>
          <h2>ML Suggestions</h2>
          {suggestions.feature_importances ? <ul>{suggestions.feature_importances.map(([f,i])=> <li key={f}>{f} — {i}</li>)}</ul> : <div>{JSON.stringify(suggestions)}</div>}
        </div>
      )}
    </div>
  )
}
