import React from 'react';
import type { AnalysisResult } from '../types/types';
import { ComplianceBadge } from './ComplianceBadge';
import { LightbulbIcon, BookIcon, ShieldIcon } from './../icons/icons';

interface ResultCardProps {
  result: AnalysisResult;
}

const ResultCard: React.FC<ResultCardProps> = ({ result }) => {
  const { needsComplianceLogic, reasoning, relatedRegulations } = result;

  return (
    <div className="w-full bg-slate-800/50 border border-slate-700 rounded-lg p-6 space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-3">
          <ShieldIcon />
          Compliance Analysis
        </h2>
        <ComplianceBadge needsCompliance={needsComplianceLogic} />
      </div>

      <div className="space-y-4">
        <h3 className="font-semibold text-lg text-purple-400 flex items-center gap-2">
          <LightbulbIcon />
          Reasoning
        </h3>
        <p className="text-slate-300 bg-slate-800 p-4 rounded-md border border-slate-700">
          {reasoning}
        </p>
      </div>
      
      {relatedRegulations && relatedRegulations.length > 0 && (
        <div className="space-y-4">
          <h3 className="font-semibold text-lg text-cyan-400 flex items-center gap-2">
            <BookIcon />
            Potentially Related Regulations
          </h3>
          <ul className="space-y-2">
            {relatedRegulations.map((reg, index) => (
              <li key={index} className="bg-slate-800 p-3 rounded-md border border-slate-700 text-slate-300">
                {reg}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ResultCard;