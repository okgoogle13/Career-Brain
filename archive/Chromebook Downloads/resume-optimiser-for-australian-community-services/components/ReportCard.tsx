
import React from 'react';
import { Report } from '../types';
import { ChartBarIcon, CheckCircleIcon } from './icons';

interface ReportCardProps {
  title: string;
  report: Report;
  isImprovement?: boolean;
}

const ScoreCircle = ({ score, isImprovement }: { score: number, isImprovement?: boolean }) => {
    const color = isImprovement ? 'text-green-500' : 'text-blue-500';
    return (
        <div className="relative w-24 h-24">
            <svg className="w-full h-full" viewBox="0 0 36 36">
                <path
                    className="text-gray-200"
                    strokeWidth="3.6"
                    stroke="currentColor"
                    fill="none"
                    d="M18 2.0845
                      a 15.9155 15.9155 0 0 1 0 31.831
                      a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path
                    className={color}
                    strokeWidth="3.6"
                    strokeDasharray={`${score}, 100`}
                    strokeLinecap="round"
                    stroke="currentColor"
                    fill="none"
                    d="M18 2.0845
                      a 15.9155 15.9155 0 0 1 0 31.831
                      a 15.9155 15.9155 0 0 1 0 -31.831"
                />
            </svg>
            <div className="absolute top-0 left-0 w-full h-full flex items-center justify-center">
                <span className={`text-2xl font-bold ${color}`}>{score}</span>
            </div>
        </div>
    )
};


const ReportCard = ({ title, report, isImprovement = false }: ReportCardProps) => {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <h3 className="text-xl font-bold text-navy mb-4">{title}</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="flex flex-col items-center space-y-2 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-semibold text-charcoal">ATS Score</h4>
            <ScoreCircle score={report.atsScore} isImprovement={isImprovement}/>
        </div>
        <div className="flex flex-col items-center space-y-2 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-semibold text-charcoal">Overall Match</h4>
            <ScoreCircle score={report.matchAnalysis.overall} isImprovement={isImprovement} />
        </div>
      </div>
      <div className="mt-6">
        <h4 className="font-semibold text-charcoal mb-2">Match Breakdown</h4>
        <ul className="space-y-2">
          {report.matchAnalysis.categories.map(cat => (
            <li key={cat.name} className="flex items-center justify-between">
              <span>{cat.name}</span>
              <span className="font-bold text-charcoal">{cat.score}/100</span>
            </li>
          ))}
        </ul>
      </div>

      {report.gapAnalysis && (
        <div className="mt-6">
          <h4 className="font-semibold text-charcoal mb-2">Gap Analysis</h4>
          <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
            {report.gapAnalysis.map((item, i) => <li key={i}>{item}</li>)}
          </ul>
        </div>
      )}
      {report.improvementPriorities && (
        <div className="mt-6">
          <h4 className="font-semibold text-charcoal mb-2">Improvement Priorities</h4>
          <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
            {report.improvementPriorities.map((item, i) => <li key={i}>{item}</li>)}
          </ul>
        </div>
      )}
      {report.keywordReport && (
        <div className="mt-6">
          <h4 className="font-semibold text-charcoal mb-2">Keyword Report</h4>
          <p className="text-sm text-gray-600">{report.keywordReport}</p>
        </div>
      )}
      {report.complianceConfirmation && (
        <div className="mt-6">
          <h4 className="font-semibold text-charcoal mb-2">Compliance Confirmation</h4>
          <p className="text-sm text-gray-600">{report.complianceConfirmation}</p>
        </div>
      )}
    </div>
  );
};

export default ReportCard;
