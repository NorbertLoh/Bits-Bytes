
export enum AppView {
  MANUAL = 'MANUAL',
  BULK = 'BULK',
}

export interface AnalysisResult {
  needsComplianceLogic: boolean;
  reasoning: string;
  relatedRegulations: string[];
}
