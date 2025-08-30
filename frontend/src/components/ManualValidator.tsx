import React, { useState, useCallback } from 'react';
import type { AnalysisResult } from '../types/types';
import ResultCard from './ResultCard';
import Spinner from './Spinner';
import { askQuestion } from '../service/service';
import { ManualValidatorProps } from '../props';

const ManualValidator: React.FC<ManualValidatorProps> = ({ memory }) => {
  const [description, setDescription] = useState<string>('');
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  const exampleTexts = [
    "Curfew login blocker with ASL and GH for Utah minors, To comply with the Utah Social Media Regulation Act, we are implementing a curfew-based login restriction for users under 18. The system uses ASL to detect minor accounts and routes enforcement through GH to apply only within Utah boundaries. The feature activates during restricted night hours and logs activity using EchoTrace for auditability. This allows parental control to be enacted without user-facing alerts, operating in ShadowMode during initial rollout.",
    "PF default toggle with NR enforcement for California teens, As part of compliance with California’s SB976, the app will disable PF by default for users under 18 located in California. This default setting is considered NR to override, unless explicit parental opt-in is provided. Geo-detection is handled via GH, and rollout is monitored with FR logs. The design ensures minimal disruption while meeting the strict personalization requirements imposed by the law.",
    "Geofences feature rollout in US for market testing.",
    "A video filter feature is available globally except KR.",
    "hello"
  ];

  const handleValidate = useCallback(async () => {
    if (!description.trim()) {
      setError("Please enter a feature description.");
      return;
    }
    setIsLoading(true);
    setError(null);
    setResult(null);
    try {
      const analysis = await askQuestion(description, memory);
      console.log('Analysis Result:', analysis);
      setResult(analysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred.");
    } finally {
      setIsLoading(false);
    }
  }, [description, memory]);
  
  const handleSetExample = (text: string) => {
      setDescription(text);
  };

  return (
    <div className="bg-slate-900 p-6 sm:p-8 rounded-xl border border-slate-700 max-w-3xl mx-auto">
      <h2 className="text-xl font-semibold text-slate-100">Single Feature Analysis</h2>
      <p className="mt-1 text-slate-400">
        Enter a feature description to check for potential geo-compliance requirements.
      </p>
      
       <div className="mt-4">
        <label htmlFor="feature-description" className="block text-sm font-medium text-slate-300 mb-1">
          Feature Description
        </label>
        <textarea
          id="feature-description"
          rows={6}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="e.g., 'This feature requires age verification for users in Utah under the Social Media Regulation Act.'"
          className="w-full p-3 bg-slate-800 border border-slate-600 text-slate-100 rounded-md shadow-sm focus:ring-cyan-400 focus:border-cyan-400 transition"
          disabled={isLoading}
        />
      </div>
       <div className="mt-2 text-sm text-slate-400">
          Or try an example:
          <div className="flex flex-wrap gap-2 mt-1">
            {exampleTexts.map((text, index) => (
                <button key={index} onClick={() => handleSetExample(text)} className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-md text-xs transition">
                    Example {index + 1}
                </button>
            ))}
          </div>
        </div>

      <div className="mt-4">
        <button
          onClick={handleValidate}
          disabled={isLoading}
          className="w-full flex justify-center items-center px-6 py-3 border border-transparent text-base font-bold rounded-md shadow-sm text-black bg-cyan-400 hover:bg-cyan-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-cyan-400 disabled:bg-slate-700 disabled:text-slate-400 disabled:cursor-not-allowed transition"
        >
          {isLoading ? <Spinner /> : 'Validate'}
        </button>
      </div>

      <div className="mt-6">
        {error && <div className="text-red-300 bg-red-900/50 p-3 rounded-md border border-red-500/50">{error}</div>}
        {result && <ResultCard result={result} />}
      </div>
    </div>
  );
};

export default ManualValidator;