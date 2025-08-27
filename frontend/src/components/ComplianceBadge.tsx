import React from 'react';

interface ComplianceBadgeProps {
  needsCompliance: boolean;
}

export const ComplianceBadge: React.FC<ComplianceBadgeProps> = ({ needsCompliance }) => {
  const baseClasses = 'px-3 py-1 text-sm font-semibold rounded-full inline-flex items-center';
  
  const statusConfig = needsCompliance
    ? {
        text: 'Compliance Required',
        classes: 'bg-red-500/20 text-red-300 border border-red-500/50',
      }
    : {
        text: 'No Action Needed',
        classes: 'bg-green-500/20 text-green-300 border border-green-500/50',
      };

  return (
    <span className={`${baseClasses} ${statusConfig.classes}`}>
        <span className={`h-2 w-2 rounded-full mr-2 ${needsCompliance ? 'bg-red-400' : 'bg-green-400'}`}></span>
        {statusConfig.text}
    </span>
  );
};