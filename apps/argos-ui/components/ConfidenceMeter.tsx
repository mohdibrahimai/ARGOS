import React from 'react'

interface ConfidenceMeterProps {
  value: number
}

export const ConfidenceMeter: React.FC<ConfidenceMeterProps> = ({ value }) => {
  const pct = Math.round(value * 100)
  return (
    <div className="my-4">
      <div className="text-sm font-semibold mb-1">Overall Confidence: {pct}%</div>
      <div className="w-full bg-gray-200 rounded-full h-3 dark:bg-gray-700">
        <div
          className="bg-green-500 h-3 rounded-full"
          style={{ width: `${pct}%` }}
        ></div>
      </div>
    </div>
  )
}