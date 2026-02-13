'use client'

import { useState } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts'

type RangeResponse = {
  curve: { price: number; profit: number }[]
  optimal_price: number
  max_profit: number
}

type FormState = {
  base_demand: number
  price_elasticity: number
  unit_cost: number
  fixed_cost: number
  min_price: number
  max_price: number
  step: number
}

export default function Home() {
  const [form, setForm] = useState<FormState>({
    base_demand: 100,
    price_elasticity: 0.1,
    unit_cost: 3,
    fixed_cost: 50,
    min_price: 1,
    max_price: 50,
    step: 2,
  })

  const [data, setData] = useState<RangeResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    const parsed = parseFloat(value)

    setForm({
      ...form,
      [name]: isNaN(parsed) ? 0 : parsed,
    })
  }

  const generateCurve = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)

    try {
      const res = await fetch('http://localhost:8000/simulate-range', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(form),
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Request failed')
      }

      const result: RangeResponse = await res.json()
      setData(result)
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Unknown error')
      }
    }
  }

  return (
    <div style={{ padding: 40 }}>
      <h1>RiskLens – Profit Optimization</h1>

      <form onSubmit={generateCurve}>
        {Object.entries(form).map(([key, value]) => (
          <div key={key}>
            <label>{key}: </label>
            <input
              type="number"
              step="any"
              name={key}
              value={value}
              onChange={handleChange}
            />
          </div>
        ))}

        <button type="submit">Generate Curve</button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {data && (
        <>
          <div style={{ marginTop: 30, height: 400 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.curve}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="price" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="profit" stroke="#8884d8" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <h3 style={{ marginTop: 20 }}>Optimal Price: {data.optimal_price}</h3>
          <p>Max Profit: {data.max_profit}</p>
        </>
      )}
    </div>
  )
}
