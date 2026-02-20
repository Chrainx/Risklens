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

type SimulationResponse = {
  profits: number[]
  mean_profit: number
  std_profit: number
  prob_loss: number
}

type FormState = {
  price: number
  base_demand: number
  price_elasticity: number
  unit_cost: number
  fixed_cost: number
  demand_noise_distribution: 'normal' | 'lognormal'
  demand_noise_sigma: number
  elasticity_noise_distribution: 'normal' | 'lognormal'
  elasticity_noise_sigma: number
  num_runs: number
  random_seed: number
}

export default function Home() {
  const [form, setForm] = useState<FormState>({
    price: 15,
    base_demand: 100,
    price_elasticity: 0.1,
    unit_cost: 3,
    fixed_cost: 50,
    demand_noise_distribution: 'normal',
    demand_noise_sigma: 1,
    elasticity_noise_distribution: 'normal',
    elasticity_noise_sigma: 0.1,
    num_runs: 1000,
    random_seed: 42,
  })

  const [result, setResult] = useState<SimulationResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target

    setForm({
      ...form,
      [name]:
        name.includes('distribution')
          ? value
          : value === ''
          ? 0
          : parseFloat(value),
    } as FormState)
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)

    try {
      const res = await fetch('http://localhost:8000/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail?.message || 'Request failed')
      }

      setResult(data)
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message)
      else setError('Unknown error')
    }
  }

  // Histogram generator
  const getHistogramData = (profits: number[]) => {
    const bins = 20
    const min = Math.min(...profits)
    const max = Math.max(...profits)

    if (min === max) {
      return [
        {
          range: min.toFixed(2),
          count: profits.length,
        },
      ]
    }

    const binSize = (max - min) / bins

    const histogram = Array.from({ length: bins }, (_, i) => ({
      range: `${(min + i * binSize).toFixed(0)}`,
      count: 0,
    }))

    profits.forEach((p) => {
      const index = Math.min(
        Math.floor((p - min) / binSize),
        bins - 1
      )
      histogram[index].count += 1
    })

    return histogram
  }

  return (
    <div style={{ padding: 40 }}>
      <h1>RiskLens – Monte Carlo Pricing Simulator</h1>

      <form onSubmit={handleSubmit}>
        {Object.entries(form).map(([key, value]) => {
          if (key.includes('distribution')) {
            return (
              <div key={key}>
                <label>{key}: </label>
                <select
                  name={key}
                  value={value as string}
                  onChange={handleChange}
                >
                  <option value="normal">normal</option>
                  <option value="lognormal">lognormal</option>
                </select>
              </div>
            )
          }

          return (
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
          )
        })}

        <button type="submit">Run Simulation</button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {result && (
        <>
          <div style={{ marginTop: 30, height: 400 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={getHistogramData(result.profits)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="range" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <h3>Expected Profit: {result.mean_profit.toFixed(2)}</h3>
          <p>Std Dev: {result.std_profit.toFixed(2)}</p>
          <p>
            Probability of Loss:{' '}
            {(result.prob_loss * 100).toFixed(2)}%
          </p>
          <p>Runs: {result.profits.length}</p>
        </>
      )}
    </div>
  )
}