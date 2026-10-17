import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import { useMemo, useState } from 'react'
import './App.css'

type Artifact = {
  id: string
  filename: string
  downloadUrl: string
  status: string
  preview: {
    width: number
    depth: number
    height: number
  }
}

function ModelPreview({ artifact }: { artifact: Artifact | null }) {
  const scale = useMemo(() => {
    if (!artifact) return [1.6, 1.2, 0.8] as const
    const maxDim = Math.max(
      artifact.preview.width,
      artifact.preview.depth,
      artifact.preview.height,
    )
    return [
      artifact.preview.width / maxDim,
      artifact.preview.height / maxDim,
      artifact.preview.depth / maxDim,
    ] as const
  }, [artifact])

  return (
    <Canvas camera={{ position: [3.2, 2.2, 3.5], fov: 50 }}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 6, 3]} intensity={1.3} />
      <directionalLight position={[-4, 2, -3]} intensity={0.7} />
      <mesh rotation={[0.32, 0.58, 0.1]}>
        <boxGeometry args={scale} />
        <meshStandardMaterial color="#f97316" metalness={0.18} roughness={0.42} />
      </mesh>
      <gridHelper args={[6, 12, '#eab308', '#fef3c7']} position={[0, -0.7, 0]} />
      <OrbitControls enablePan={false} />
    </Canvas>
  )
}

function App() {
  const [sessionId] = useState(() => crypto.randomUUID())
  const [message, setMessage] = useState('')
  const [description, setDescription] = useState('Rounded cable clip for a 3.5mm cable.')
  const [machine, setMachine] = useState('Bambu Lab A1 mini')
  const [material, setMaterial] = useState('PLA')
  const [history, setHistory] = useState<string[]>([
    'Agent: I can draft geometry and create downloadable 3MF files that are ready for slicing.',
  ])
  const [artifact, setArtifact] = useState<Artifact | null>(null)
  const [busy, setBusy] = useState(false)

  async function sendChat() {
    if (!message.trim()) return
    setBusy(true)
    try {
      setHistory((prev) => [...prev, `You: ${message}`])
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message }),
      })
      const data = await response.json()
      setHistory((prev) => [...prev, `Agent: ${data.reply}`])
      setMessage('')
    } catch {
      setHistory((prev) => [...prev, 'Agent: Chat endpoint is not reachable yet.'])
    } finally {
      setBusy(false)
    }
  }

  async function generate3mf() {
    setBusy(true)
    try {
      const response = await fetch('/api/design', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          description,
          machine,
          material,
        }),
      })
      const data = await response.json()
      setArtifact(data.artifact)
      setHistory((prev) => [...prev, `Agent: ${data.reply}`])
    } catch {
      setHistory((prev) => [...prev, 'Agent: 3MF generation failed. Is the backend running?'])
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="layout">
      <section className="panel header">
        <p className="badge">Foundry Agent Scaffold</p>
        <h1>3doodle</h1>
        <p>
          Multiturn design chat, downloadable .3mf creation, and visual simulation preview
          for slicing-ready output.
        </p>
      </section>

      <section className="grid">
        <article className="panel controls">
          <h2>Agent Inputs</h2>
          <label>
            Design description
            <textarea
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              rows={5}
            />
          </label>

          <div className="row">
            <label>
              Machine
              <select value={machine} onChange={(event) => setMachine(event.target.value)}>
                <option>Bambu Lab A1 mini</option>
                <option>Prusa MK4S</option>
                <option>Creality K1C</option>
              </select>
            </label>
            <label>
              Material
              <select value={material} onChange={(event) => setMaterial(event.target.value)}>
                <option>PLA</option>
                <option>PETG</option>
                <option>ABS</option>
              </select>
            </label>
          </div>

          <button type="button" onClick={generate3mf} disabled={busy}>
            {busy ? 'Generating...' : 'Generate .3mf'}
          </button>

          {artifact && (
            <div className="artifact">
              <p>File: {artifact.filename}</p>
              <p>Status: {artifact.status}</p>
              <a href={artifact.downloadUrl}>Download .3mf</a>
            </div>
          )}
        </article>

        <article className="panel preview">
          <h2>Model Simulation</h2>
          <div className="canvas-wrap">
            <ModelPreview artifact={artifact} />
          </div>
          <p className="hint">
            Preview is a geometry simulation from agent output metadata; plug in a 3MF parser for
            exact mesh rendering in production.
          </p>
        </article>
      </section>

      <section className="panel chat">
        <h2>Multiturn Chat</h2>
        <div className="history">
          {history.map((entry, index) => (
            <p key={`${entry}-${index}`}>{entry}</p>
          ))}
        </div>
        <div className="chat-row">
          <input
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="Ask for tolerance, overhang strategy, or wall thickness..."
          />
          <button type="button" onClick={sendChat} disabled={busy}>
            Send
          </button>
        </div>
      </section>
    </main>
  )
}

export default App
