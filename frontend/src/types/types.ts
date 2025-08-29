
export enum AppView {
  MANUAL = 'MANUAL',
  BULK = 'BULK',
}

export interface AnalysisResult {
  feature_type: string;
  compliance_status: string;
  reasoning: string;
  supporting_regulations: string[];
}
