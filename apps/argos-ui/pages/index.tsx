import React, { useState } from 'react'
import axios from 'axios'
import { ConfidenceMeter } from '../components/ConfidenceMeter'

interface Citation {
  source_id: string
  start: number
  end: number
}

interface Sentence {
  text: string
  citations: Citation[]
  verifier: {
    label: string
    confidence: number
    unsupported_spans: [number, number][]
  }
}

interface Source {
  source_id: string
  title: string
  url: string
  snippet: string
}

interface AnswerResponse {
  trace_id: string
  answer_html: string
  sentences: Sentence[]
  sources: Source[]
  confidence_overall: number
  metrics_snapshot: {
    support_rate: number
    ner: number
    cr: number
    ece: number
  }
}

const Home: React.FC = () => {
  const [query, setQuery] = useState('')
  const [mode, setMode] = useState<'fast' | 'strict'>('fast')
  const [answer, setAnswer] = useState<AnswerResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setAnswer(null)
    try {
      const traceId = Math.random().toString(36).substring(2)
      const resp = await axios.post<AnswerResponse>('http://localhost:8000/v1/answer', {
        query,
        mode,
        top_k: 6,
        trace_id: traceId,
      })
      setAnswer(resp.data)
    } catch (err: any) {
      setError(err.message || 'Error fetching answer')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="max-w-3xl mx-auto py-10 px-4">
      <h1 className="text-3xl font-bold mb-6">ARGOS Answering System</h1>
      <form onSubmit={handleSubmit} className="mb-4">
        <textarea
          className="w-full border rounded p-2 mb-2"
          rows={3}
          placeholder="Enter your question..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        ></textarea>
        <div className="flex items-center mb-2">
          <label className="mr-2 font-medium">Mode:</label>
          <select
            className="border rounded p-1"
            value={mode}
            onChange={(e) => setMode(e.target.value as 'fast' | 'strict')}
          >
            <option value="fast">Fast</option>
            <option value="strict">Strict</option>
          </select>
        </div>
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded"
          disabled={loading || query.trim().length === 0}
        >
          {loading ? 'Searching…' : 'Search'}
        </button>
      </form>
      {error && <p className="text-red-600 mb-4">{error}</p>}
      {answer && (
        <div className="answer">
          <ConfidenceMeter value={answer.confidence_overall} />
          <div className="mb-4" dangerouslySetInnerHTML={{ __html: answer.answer_html }}></div>
          <div className="space-y-2">
            {answer.sentences.map((sent, idx) => (
              <p
                key={idx}
                className={`p-2 rounded ${sent.verifier.label}`}
                title={`Confidence: ${sent.verifier.confidence.toFixed(2)}`}
              >
                {sent.text}
              </p>
            ))}
          </div>
          <h2 className="text-xl font-semibold mt-6 mb-2">Sources</h2>
          <ul className="list-disc list-inside space-y-1">
            {answer.sources.map((src) => (
              <li key={src.source_id}>
                <a href={src.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">
                  {src.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </main>
  )
}

export default Home