import React from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'

export default function ConversionChart({ stages }) {
  const data = stages
    .filter((s) => s.conversion_rate !== null && s.conversion_rate !== undefined)
    .map((s) => ({ name: s.stage, rate: s.conversion_rate }))

  if (data.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: '#aaa' }}>
        No conversion data yet
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ left: 10, right: 20 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis domain={[0, 100]} unit="%" />
        <Tooltip formatter={(v) => [`${v}%`, 'Conversion']} />
        <ReferenceLine y={50} stroke="#f39c12" strokeDasharray="4 4" label="50%" />
        <Line
          type="monotone"
          dataKey="rate"
          stroke="#4f46e5"
          strokeWidth={2}
          dot={{ r: 5 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
