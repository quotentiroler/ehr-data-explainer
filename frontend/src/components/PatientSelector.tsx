import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

interface Patient {
  id: string
  name: string
  gender: string
  birthDate?: string
  condition_count: number
}

interface PatientSelectorProps {
  selectedId: string | null
  onSelect: (id: string) => void
}

export default function PatientSelector({ selectedId, onSelect }: PatientSelectorProps) {
  const { data: patients, isLoading, error } = useQuery({
    queryKey: ['patients'],
    queryFn: async () => {
      const response = await axios.get<Patient[]>('/api/patients')
      return response.data
    },
  })

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-4">
        <h2 className="text-lg font-semibold text-slate-800 mb-3">Select a Patient</h2>
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-14 bg-slate-100 rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-4">
        <h2 className="text-lg font-semibold text-slate-800 mb-3">Select a Patient</h2>
        <div className="text-red-500 text-sm p-4 bg-red-50 rounded-lg">
          <p className="font-medium">Connection Error</p>
          <p className="text-red-400 mt-1">
            Could not connect to the server. Make sure the backend is running.
          </p>
        </div>
      </div>
    )
  }

  if (!patients || patients.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-4">
        <h2 className="text-lg font-semibold text-slate-800 mb-3">Select a Patient</h2>
        <div className="text-slate-500 text-sm p-4 bg-slate-50 rounded-lg text-center">
          <p className="font-medium">No patients found</p>
          <p className="text-slate-400 mt-1">
            Load FHIR data into Neo4j to see patients here.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-4">
      <h2 className="text-lg font-semibold text-slate-800 mb-3 flex items-center gap-2">
        <span>👤</span> Select a Patient
      </h2>
      <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
        {patients.map((patient) => (
          <button
            key={patient.id}
            onClick={() => onSelect(patient.id)}
            className={`
              w-full text-left p-3 rounded-lg transition-all duration-200
              ${selectedId === patient.id
                ? 'bg-blue-50 border-2 border-blue-400 shadow-sm'
                : 'bg-slate-50 border-2 border-transparent hover:bg-slate-100'
              }
            `}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className={`font-medium ${selectedId === patient.id ? 'text-blue-700' : 'text-slate-700'}`}>
                  {patient.name}
                </p>
                <p className="text-xs text-slate-400">
                  {patient.gender} {patient.birthDate ? `• ${patient.birthDate.split('T')[0]}` : ''}
                </p>
              </div>
              <div className="flex items-center gap-1">
                <span className={`
                  px-2 py-0.5 rounded-full text-xs font-medium
                  ${patient.condition_count > 0
                    ? 'bg-red-100 text-red-700'
                    : 'bg-slate-100 text-slate-500'
                  }
                `}>
                  {patient.condition_count} conditions
                </span>
              </div>
            </div>
          </button>
        ))}
      </div>
      <p className="text-xs text-slate-400 mt-3 text-center">
        {patients.length} patients loaded
      </p>
    </div>
  )
}
