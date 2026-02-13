import Link from 'next/link'

export default function Home() {
  return (
    <div style={{ padding: 40 }}>
      <h1>RiskLens</h1>
      <p>Decision Intelligence for Pricing Optimization</p>

      <div style={{ marginTop: 20 }}>
        <Link href="/simulate">Single Price Simulation</Link>
      </div>

      <div style={{ marginTop: 10 }}>
        <Link href="/optimize">Profit Optimization Curve</Link>
      </div>
    </div>
  )
}
