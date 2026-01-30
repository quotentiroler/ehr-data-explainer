interface Explanation {
  greeting: string
  body_explanation: string
  medication_explanation: string
  connections: string
  encouragement: string
  key_takeaways: string[]
}

interface ExplanationDisplayProps {
  patientName: string
  explanation: Explanation
}

export default function ExplanationDisplay({ patientName, explanation }: ExplanationDisplayProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-4 text-white">
        <p className="text-lg font-medium">{explanation.greeting}</p>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        {/* Body Explanation */}
        <section>
          <h3 className="font-semibold text-slate-700 mb-2 flex items-center gap-2">
            <span className="text-xl">🫀</span> What's Happening in Your Body
          </h3>
          <p className="text-slate-600 text-sm leading-relaxed">
            {explanation.body_explanation}
          </p>
        </section>

        {/* Medication Explanation */}
        <section>
          <h3 className="font-semibold text-slate-700 mb-2 flex items-center gap-2">
            <span className="text-xl">💊</span> How Your Medications Help
          </h3>
          <p className="text-slate-600 text-sm leading-relaxed">
            {explanation.medication_explanation}
          </p>
        </section>

        {/* Connections */}
        <section>
          <h3 className="font-semibold text-slate-700 mb-2 flex items-center gap-2">
            <span className="text-xl">🔗</span> How Things Connect
          </h3>
          <p className="text-slate-600 text-sm leading-relaxed">
            {explanation.connections}
          </p>
        </section>

        {/* Encouragement */}
        <section className="bg-green-50 -mx-4 px-4 py-3 border-y border-green-100">
          <p className="text-green-700 text-sm leading-relaxed">
            💚 {explanation.encouragement}
          </p>
        </section>

        {/* Key Takeaways */}
        <section>
          <h3 className="font-semibold text-slate-700 mb-2 flex items-center gap-2">
            <span className="text-xl">📝</span> Key Takeaways
          </h3>
          <ul className="space-y-2">
            {explanation.key_takeaways.map((point, index) => (
              <li
                key={index}
                className="flex items-start gap-2 text-sm text-slate-600"
              >
                <span className="text-blue-500 font-bold">✓</span>
                {point}
              </li>
            ))}
          </ul>
        </section>

        {/* Disclaimer */}
        <p className="text-xs text-slate-400 pt-2 border-t border-slate-100">
          This explanation is for educational purposes. Always consult your healthcare provider for medical advice.
        </p>
      </div>
    </div>
  )
}
