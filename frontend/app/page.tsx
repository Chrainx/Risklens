'use client'

import { useState } from 'react'

type SimulationResponse = {
  demand: number
  revenue: number
  total_cost: number
  profit: number
}

type FormState = {
  price: number
  base_demand: number
  price_elasticity: number
  unit_cost: number
  fixed_cost: number
}

export default function Home() {
  const [form, setForm] = useState<FormState>({
    price: 10,
    base_demand: 100,
    price_elasticity: 0.1,
    unit_cost: 3,
    fixed_cost: 50,
  })

  const [result, setResult] = useState<SimulationResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target

    setForm({
      ...form,
      [name]: value === '' ? 0 : parseFloat(value),
    })
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)

    try {
      const res = await fetch('http://localhost:8000/simulate', {
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

      const data: SimulationResponse = await res.json()
      setResult(data)
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Unknown error')
      }
    }
  }

  return (
    <div style={{ padding: '40px', fontFamily: 'Arial' }}>
      <h1>RiskLens Pricing Simulator</h1>

      <form onSubmit={handleSubmit}>
        {Object.keys(form).map((key) => (
          <div key={key}>
            <label>{key}: </label>
            <input
              type="number"
              step="any"
              name={key}
              value={form[key as keyof FormState]}
              onChange={handleChange}
            />
          </div>
        ))}

        <button type="submit">Simulate</button>
      </form>

      {error && <p style={{ color: 'red' }}>Error: {error}</p>}

      {result && (
        <div style={{ marginTop: '20px' }}>
          <h3>Results:</h3>
          <p>Demand: {result.demand}</p>
          <p>Revenue: {result.revenue}</p>
          <p>Total Cost: {result.total_cost}</p>
          <p>Profit: {result.profit}</p>
        </div>
      )}
    </div>
  )
}
