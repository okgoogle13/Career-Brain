
export enum Template {
  PROFESSIONAL_CLASSIC = 'Professional Classic',
  MODERN_MINIMALIST = 'Modern Minimalist',
}

export interface MatchCategory {
  name: string;
  score: number;
}

export interface MatchAnalysis {
  overall: number;
  categories: MatchCategory[];
}

export interface Report {
  atsScore: number;
  matchAnalysis: MatchAnalysis;
  gapAnalysis?: string[];
  improvementPriorities?: string[];
  keywordReport?: string;
  complianceConfirmation?: string;
}

export interface OptimizedJob {
  role: string;
  company: string;
  dates: string;
  achievements: string[];
}

export interface OptimizedSkills {
  category: string;
  items: string;
}

export interface OptimizedResumeContent {
  headline: string;
  professionalSummary: string;
  experience: OptimizedJob[];
  skills: OptimizedSkills[];
  name: string;
  contact: string;
}

export interface StrategicReport {
  transformationSummary: string;
}

export interface GeminiApiResponse {
  initialAnalysis: Report;
  optimizedResume: OptimizedResumeContent;
  improvementReport: Report;
  strategicReport: StrategicReport;
}
