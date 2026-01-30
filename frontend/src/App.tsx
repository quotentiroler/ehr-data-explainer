import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import axios from 'axios'
import PatientSelector from './components/PatientSelector'
import PatientGraph from './components/PatientGraph'
import ExplanationDisplay from './components/ExplanationDisplay'
import VideoPlayer from './components/VideoPlayer'

const API_BASE = '/api'

interface Explanation {
  greeting: string
  body_explanation: string
  medication_explanation: string
  connections: string
  encouragement: string
  key_takeaways: string[]
}

interface ExplainResponse {
  patient_name: string
  explanation: Explanation
  video_prompt: string | null
  video_url: string | null
  graph_data: {
    conditions: Array<{ code: string; display: string }>
    medications: Array<{ code: string; display: string }>
    body_systems: Array<{ system: string; description: string }>
  }
}

function App() {
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null)
  const [generateVideo, setGenerateVideo] = useState(true)

  // Mutation for generating explanation
  const explainMutation = useMutation({
    mutationFn: async (patientId: string) => {
      const response = await axios.post<ExplainResponse>(`${API_BASE}/explain`, {
        patient_id: patientId,
        reading_level: '6th grade',
        generate_video: generateVideo,
      })
      return response.data
    },
  })

  const handleExplain = () => {
    if (selectedPatientId) {
      explainMutation.mutate(selectedPatientId)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-3xl">🏥</span>
              <div>
                <h1 className="text-2xl font-bold text-slate-800">
                  Health Explainer
                </h1>
                <p className="text-sm text-slate-500">
                  Understanding your health, simply explained
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded">
                Neo4j
              </span>
              <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded">
                Claude
              </span>
              <span className="px-2 py-1 bg-green-100 text-green-700 rounded">
                Wan 2.2
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column - Patient Selection */}
          <div className="lg:col-span-3 space-y-4">
            <PatientSelector
              selectedId={selectedPatientId}
              onSelect={setSelectedPatientId}
            />

            {selectedPatientId && (
              <div className="bg-white rounded-xl shadow-sm p-4 space-y-4">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="generateVideo"
                    checked={generateVideo}
                    onChange={(e) => setGenerateVideo(e.target.checked)}
                    className="rounded text-blue-600"
                  />
                  <label htmlFor="generateVideo" className="text-sm text-slate-600">
                    Generate video explanation
                  </label>
                </div>

                <button
                  onClick={handleExplain}
                  disabled={explainMutation.isPending}
                  className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-blue-700 
                           text-white rounded-lg font-medium shadow-md
                           hover:from-blue-700 hover:to-blue-800 
                           disabled:opacity-50 disabled:cursor-not-allowed
                           transition-all duration-200"
                >
                  {explainMutation.isPending ? (
                    <span className="flex items-center justify-center gap-2">
                      <span className="animate-spin">⏳</span>
                      Generating...
                    </span>
                  ) : (
                    <span className="flex items-center justify-center gap-2">
                      ✨ Explain My Health
                    </span>
                  )}
                </button>

                {explainMutation.isError && (
                  <p className="text-sm text-red-600 bg-red-50 p-2 rounded">
                    Error: {(explainMutation.error as Error).message}
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Middle Column - Graph */}
          <div className="lg:col-span-5">
            <div className="bg-white rounded-xl shadow-sm p-4">
              <h2 className="text-lg font-semibold text-slate-800 mb-3 flex items-center gap-2">
                <span>🔗</span> Health Connections
              </h2>
              {selectedPatientId ? (
                <PatientGraph patientId={selectedPatientId} />
              ) : (
                <div className="h-96 flex items-center justify-center bg-slate-50 rounded-lg border-2 border-dashed border-slate-200">
                  <p className="text-slate-400">
                    Select a patient to view their health graph
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Video & Explanation */}
          <div className="lg:col-span-4 space-y-4">
            {explainMutation.data?.video_url && (
              <VideoPlayer videoUrl={explainMutation.data.video_url} />
            )}

            {explainMutation.data?.explanation ? (
              <ExplanationDisplay
                patientName={explainMutation.data.patient_name}
                explanation={explainMutation.data.explanation}
              />
            ) : (
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className="text-center text-slate-400 py-8">
                  <span className="text-4xl mb-4 block">💬</span>
                  <p>Click "Explain My Health" to generate</p>
                  <p className="text-sm">a personalized explanation</p>
                </div>
              </div>
            )}

            {/* Graph Data Summary */}
            {explainMutation.data?.graph_data && (
              <div className="bg-white rounded-xl shadow-sm p-4">
                <h3 className="font-semibold text-slate-700 mb-3">Quick Summary</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 bg-red-400 rounded-full"></span>
                    <span className="text-slate-600">
                      {explainMutation.data.graph_data.conditions.length} conditions
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 bg-green-400 rounded-full"></span>
                    <span className="text-slate-600">
                      {explainMutation.data.graph_data.medications.length} medications
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 bg-amber-400 rounded-full"></span>
                    <span className="text-slate-600">
                      {explainMutation.data.graph_data.body_systems.length} body systems
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-auto py-4 text-center text-sm text-slate-400">
        <p>
          Built for healthcare hackathon • FHIR + Neo4j + Claude + Wan 2.2
        </p>
      </footer>
    </div>
  )
}

export default App
