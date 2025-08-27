import React from 'react';
import type { AnalysisResult } from '../types/types';

interface ResultCardProps {
  result: AnalysisResult;
}

const CheckCircleIcon: React.FC<{className?: string}> = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className || "w-6 h-6"}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
    </svg>
);

const ExclamationTriangleIcon: React.FC<{className?: string}> = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className || "w-6 h-6"}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
    </svg>
);


const ResultCard: React.FC<ResultCardProps> = ({ result }) => {
  const { needsComplianceLogic, reasoning, relatedRegulations } = result;

  const cardClasses = needsComplianceLogic
    ? 'bg-red-900/40 border-red-500/30'
    : 'bg-green-900/40 border-green-500/30';
    
  const titleClasses = needsComplianceLogic
    ? 'text-red-400'
    : 'text-green-400';
    
  const icon = needsComplianceLogic 
    ? <ExclamationTriangleIcon className="w-6 h-6 text-red-400" /> 
    : <CheckCircleIcon className="w-6 h-6 text-green-400" />;

  return (
    <div className={`p-5 rounded-lg border ${cardClasses}`}>
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">{icon}</div>
        <div>
          <h3 className={`text-lg font-semibold ${titleClasses}`}>
            {needsComplianceLogic
              ? 'Geo-Specific Compliance Logic Required'
              : 'No Geo-Specific Compliance Logic Detected'}
          </h3>
          
          <div className="mt-3 text-sm text-slate-300">
            <p className="font-semibold text-slate-200">Reasoning:</p>
            <p className="mt-1">{reasoning}</p>
          </div>

          {relatedRegulations && relatedRegulations.length > 0 && (
            <div className="mt-4 text-sm text-slate-300">
              <p className="font-semibold text-slate-200">Potentially Related Regulations:</p>
              <ul className="list-disc list-inside mt-1 space-y-1">
                {relatedRegulations.map((reg, index) => (
                  <li key={index}>{reg}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResultCard;