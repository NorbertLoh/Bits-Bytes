import React from 'react';

interface FeatureTypeBadgeProps {
  featureType: string;
}

export const FeatureTypeBadge: React.FC<FeatureTypeBadgeProps> = ({ featureType }) => {
  const baseClasses = 'px-3 py-1 text-sm font-semibold rounded-full inline-flex items-center';

  const getStatusConfig = (featureType: string) => {
    if (featureType === "Business Driven") {
      return {
        text: 'Business Driven',
        classes: 'bg-red-500/20 text-red-300 border border-red-500/50',
        dot: 'bg-red-400',
      };
    }
    if (featureType === "Legal Requirement") {
      return {
        text: 'Legal Requirement',
        classes: 'bg-green-500/20 text-green-300 border border-green-500/50',
        dot: 'bg-green-400',
      };
    }
    return {
      text: 'Unclassified',
      classes: 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/50',
      dot: 'bg-yellow-400',
    };
  };

  const statusConfig = getStatusConfig(featureType);

  return (
    <span className={`${baseClasses} ${statusConfig.classes}`}>
      <span className={`h-2 w-2 rounded-full mr-2 ${statusConfig.dot}`}></span>
      {statusConfig.text}
    </span>
  );
};