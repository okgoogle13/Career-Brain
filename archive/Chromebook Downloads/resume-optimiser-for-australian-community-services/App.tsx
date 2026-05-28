
import React, { useState, useCallback } from 'react';
import { analyzeAndOptimizeResume } from './services/geminiService';
import { GeminiApiResponse, Template } from './types';
import Spinner from './components/Spinner';
import TemplateSelector from './components/TemplateSelector';
import OptimizedResumeView from './components/OptimizedResumeView';
import ReportCard from './components/ReportCard';
import { DocumentTextIcon, SparklesIcon } from './components/icons';

const App: React.FC = () => {
  const [jobDesc, setJobDesc] = useState('');
  const [ksc, setKsc] = useState('');
  const [resume, setResume] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiResponse, setApiResponse] = useState<GeminiApiResponse | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<Template>(Template.MODERN_MINIMALIST);

  const handleSubmit = useCallback(async () => {
    if (!jobDesc || !ksc || !resume) {
      setError("Please fill out all three fields.");
      return;
    }
    setError(null);
    setIsLoading(true);
    setApiResponse(null);
    try {
      const response = await analyzeAndOptimizeResume(jobDesc, ksc, resume);
      setApiResponse(response);
    } catch (e) {
      const err = e as Error;
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setIsLoading(false);
    }
  }, [jobDesc, ksc, resume]);
  
  const handleReset = () => {
      setJobDesc('');
      setKsc('');
      setResume('');
      setApiResponse(null);
      setError(null);
      setIsLoading(false);
  }

  const renderInputForm = () => (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-navy text-center">Resume Optimiser</h2>
      <p className="text-center text-subtle-gray max-w-2xl mx-auto">
        Paste your job description, key selection criteria, and current resume below. Our AI will analyze your documents and generate an optimized, ATS-friendly resume tailored for the role.
      </p>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <TextAreaInput id="job-desc" label="Job Description" value={jobDesc} onChange={setJobDesc} placeholder="Paste the full job description here..."/>
          <TextAreaInput id="ksc" label="Key Selection Criteria" value={ksc} onChange={setKsc} placeholder="Paste the KSC or key requirements..."/>
          <TextAreaInput id="resume" label="Current Resume" value={resume} onChange={setResume} placeholder="Paste your current resume text here..."/>
      </div>
      
      {error && <p className="text-red-500 text-center">{error}</p>}
      
      <div className="text-center pt-4">
        <button
          onClick={handleSubmit}
          disabled={isLoading}
          className="bg-slate-blue text-white font-bold py-3 px-8 rounded-lg hover:bg-navy transition-all duration-300 disabled:bg-gray-400 disabled:cursor-not-allowed inline-flex items-center space-x-2 shadow-lg hover:shadow-xl"
        >
          <SparklesIcon className="w-5 h-5" />
          <span>Optimize My Resume</span>
        </button>
      </div>
    </div>
  );
  
  const renderResults = () => {
    if (!apiResponse) return null;
    return (
        <div className="space-y-8">
            <div className="text-center">
                 <h2 className="text-3xl font-bold text-navy">Optimization Complete</h2>
                 <p className="text-subtle-gray mt-2">Here is your analysis and newly optimized resume.</p>
            </div>
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-8 items-start">
              <div className="space-y-8">
                <ReportCard title="Initial Compliance & Match Analysis" report={apiResponse.initialAnalysis} />
                <ReportCard title="Performance Improvement Report" report={apiResponse.improvementReport} isImprovement={true} />
                <TemplateSelector selectedTemplate={selectedTemplate} onSelectTemplate={setSelectedTemplate} />
                 <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h3 className="text-xl font-bold text-navy mb-4">Strategic Report</h3>
                    <p className="text-charcoal leading-relaxed">{apiResponse.strategicReport.transformationSummary}</p>
                </div>
              </div>
              <div className="xl:sticky top-8">
                <OptimizedResumeView resume={apiResponse.optimizedResume} template={selectedTemplate} />
              </div>
            </div>
            <div className="text-center pt-4">
                 <button
                    onClick={handleReset}
                    className="bg-gray-200 text-charcoal font-bold py-3 px-8 rounded-lg hover:bg-gray-300 transition-all duration-300"
                >
                    Start Over
                </button>
            </div>
        </div>
    );
  };
  
  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        <header className="flex items-center space-x-3 mb-8">
            <DocumentTextIcon className="w-10 h-10 text-slate-blue"/>
            <h1 className="text-2xl font-bold text-charcoal">Australian Community Services Resume Engine</h1>
        </header>
        <main className="bg-white/60 backdrop-blur-sm p-6 sm:p-8 rounded-2xl shadow-lg border border-gray-200">
          {isLoading ? <Spinner message="Analyzing and optimizing your resume..." /> : (apiResponse ? renderResults() : renderInputForm())}
        </main>
        <footer className="text-center text-sm text-gray-400 py-6">
            Powered by Gemini API
        </footer>
      </div>
    </div>
  );
};

const TextAreaInput = ({id, label, value, onChange, placeholder} : {id: string, label: string, value: string, onChange: (val: string) => void, placeholder: string}) => (
    <div className="flex flex-col space-y-2">
        <label htmlFor={id} className="font-semibold text-charcoal">{label}</label>
        <textarea
            id={id}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            rows={15}
            className="p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-blue focus:border-slate-blue transition-shadow duration-200 shadow-sm w-full"
        />
    </div>
);

export default App;
