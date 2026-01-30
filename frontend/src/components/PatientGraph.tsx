import { useEffect, useRef } from 'react'

interface PatientGraphProps {
  patientId: string
}

declare global {
  interface Window {
    NeoVis: any
  }
}

export default function PatientGraph({ patientId }: PatientGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const vizRef = useRef<any>(null)

  useEffect(() => {
    if (!containerRef.current || !patientId) return

    // Dynamically load NeoVis from CDN
    const loadNeoVis = async () => {
      // Check if NeoVis is already loaded
      if (!window.NeoVis) {
        const script = document.createElement('script')
        script.src = 'https://unpkg.com/neovis.js@2.1.0'
        script.async = true
        document.body.appendChild(script)
        
        await new Promise((resolve) => {
          script.onload = resolve
        })
      }

      // Clear previous visualization
      if (vizRef.current) {
        vizRef.current.clearNetwork()
      }

      // Get Neo4j credentials from environment or use defaults
      const neo4jUrl = import.meta.env.VITE_NEO4J_URL || 'bolt://localhost:7687'
      const neo4jUser = import.meta.env.VITE_NEO4J_USER || 'neo4j'
      const neo4jPassword = import.meta.env.VITE_NEO4J_PASSWORD || 'password'

      const config = {
        containerId: containerRef.current!.id,
        neo4j: {
          serverUrl: neo4jUrl,
          serverUser: neo4jUser,
          serverPassword: neo4jPassword,
        },
        visConfig: {
          nodes: {
            font: {
              size: 12,
              face: 'Inter, system-ui, sans-serif',
            },
          },
          edges: {
            arrows: {
              to: { enabled: true, scaleFactor: 0.5 },
            },
            font: {
              size: 10,
              align: 'middle',
            },
          },
          physics: {
            enabled: true,
            solver: 'forceAtlas2Based',
            forceAtlas2Based: {
              gravitationalConstant: -50,
              centralGravity: 0.01,
              springLength: 100,
              springConstant: 0.08,
            },
            stabilization: {
              iterations: 100,
            },
          },
        },
        labels: {
          Patient: {
            label: 'name',
            [window.NeoVis?.NEOVIS_ADVANCED_CONFIG]: {
              static: {
                color: '#4F46E5',
                size: 35,
                font: { color: '#1e293b' },
                shape: 'dot',
              },
            },
          },
          Condition: {
            label: 'display',
            [window.NeoVis?.NEOVIS_ADVANCED_CONFIG]: {
              static: {
                color: '#EF4444',
                size: 25,
                font: { color: '#1e293b' },
                shape: 'dot',
              },
            },
          },
          Medication: {
            label: 'display',
            [window.NeoVis?.NEOVIS_ADVANCED_CONFIG]: {
              static: {
                color: '#10B981',
                size: 25,
                font: { color: '#1e293b' },
                shape: 'diamond',
              },
            },
          },
          BodySystem: {
            label: 'name',
            [window.NeoVis?.NEOVIS_ADVANCED_CONFIG]: {
              static: {
                color: '#F59E0B',
                size: 30,
                font: { color: '#1e293b' },
                shape: 'star',
              },
            },
          },
        },
        relationships: {
          HAS_CONDITION: {
            [window.NeoVis?.NEOVIS_ADVANCED_CONFIG]: {
              static: {
                color: '#f87171',
                label: 'has',
              },
            },
          },
          TAKES_MEDICATION: {
            [window.NeoVis?.NEOVIS_ADVANCED_CONFIG]: {
              static: {
                color: '#34d399',
                label: 'takes',
              },
            },
          },
          AFFECTS: {
            [window.NeoVis?.NEOVIS_ADVANCED_CONFIG]: {
              static: {
                color: '#fbbf24',
                label: 'affects',
                dashes: true,
              },
            },
          },
          TREATS: {
            [window.NeoVis?.NEOVIS_ADVANCED_CONFIG]: {
              static: {
                color: '#a78bfa',
                label: 'treats',
                dashes: true,
              },
            },
          },
          TARGETS: {
            [window.NeoVis?.NEOVIS_ADVANCED_CONFIG]: {
              static: {
                color: '#60a5fa',
                label: 'targets',
                dashes: true,
              },
            },
          },
        },
        initialCypher: `
          MATCH (p:Patient {id: '${patientId}'})
          OPTIONAL MATCH (p)-[r1:HAS_CONDITION]->(c:Condition)
          OPTIONAL MATCH (p)-[r2:TAKES_MEDICATION]->(m:Medication)
          OPTIONAL MATCH (c)-[r3:AFFECTS]->(bs:BodySystem)
          OPTIONAL MATCH (m)-[r4:TREATS]->(tc:Condition)
          OPTIONAL MATCH (m)-[r5:TARGETS]->(tbs:BodySystem)
          RETURN p, r1, c, r2, m, r3, bs, r4, tc, r5, tbs
          LIMIT 100
        `,
      }

      try {
        vizRef.current = new window.NeoVis.default(config)
        vizRef.current.render()
      } catch (error) {
        console.error('Failed to render graph:', error)
      }
    }

    loadNeoVis()

    return () => {
      if (vizRef.current) {
        vizRef.current.clearNetwork()
      }
    }
  }, [patientId])

  return (
    <div className="relative">
      <div
        id="graph-container"
        ref={containerRef}
        className="w-full h-96 rounded-lg border border-slate-200"
        style={{ background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)' }}
      />
      
      {/* Legend */}
      <div className="absolute bottom-2 left-2 bg-white/90 backdrop-blur-sm rounded-lg p-2 text-xs space-y-1">
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-indigo-500"></span>
          <span className="text-slate-600">Patient</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-red-500"></span>
          <span className="text-slate-600">Condition</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-green-500"></span>
          <span className="text-slate-600">Medication</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-amber-500"></span>
          <span className="text-slate-600">Body System</span>
        </div>
      </div>
    </div>
  )
}
