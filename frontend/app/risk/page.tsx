'use client'

import { useState } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts'

type MonteCarloResponse = {
  profits: number[]
  mean_profit: number
  std_profit: number
  prob_loss: number
}

type FormState = {
  price: number
  base_demand: number
  elasticity_mean: number
  elasticity_sigma: number
  unit_cost: number
  fixed_cost: number
  num_runs: number
}

export default function RiskPage() {
  const [form, setForm] = useState<FormState>({
    price: 15,
    base_demand: 100,
    elasticity_mean: 0.1,
    elasticity_sigma: 0.02,
    unit_cost: 3,
    fixed_cost: 50,
    num_runs: 1000,
  })

  const [data, setData] = useState<MonteCarloResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    const parsed = parseFloat(value)

    setForm({
      ...form,
      [name]: isNaN(parsed) ? 0 : parsed,
    })
  }

  const runSimulation = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)

    try {
      const res = await fetch('http://localhost:8000/simulate-monte-carlo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Request failed')
      }

      const result: MonteCarloResponse = await res.json()
      setData(result)
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message)
      else setError('Unknown error')
    }
  }

  // Convert raw profits into histogram bins
  const getHistogramData = (profits: number[]) => {
    const bins = 20
    const min = Math.min(...profits)
    const max = Math.max(...profits)
    const binSize = (max - min) / bins

    const histogram = Array.from({ length: bins }, (_, i) => ({
      range: `${(min + i * binSize).toFixed(0)}`,
      count: 0,
    }))

    profits.forEach((p) => {
      const index = Math.min(Math.floor((p - min) / binSize), bins - 1)
      histogram[index].count += 1
    })

    return histogram
  }

  return (
    <div style={{ padding: 40 }}>
      <h1>RiskLens – Monte Carlo Risk Analysis</h1>

      <form onSubmit={runSimulation}>
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

        <button type="submit">Run Monte Carlo</button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {data && (
        <>
          <div style={{ marginTop: 30, height: 400 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={getHistogramData(data.profits)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="range" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <h3>Expected Profit: {data.mean_profit.toFixed(2)}</h3>
          <p>Std Dev: {data.std_profit.toFixed(2)}</p>
          <p>Probability of Loss: {(data.prob_loss * 100).toFixed(2)}%</p>
        </>
      )}
    </div>
  )
}
