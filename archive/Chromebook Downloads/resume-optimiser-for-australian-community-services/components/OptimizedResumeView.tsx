
import React from 'react';
import { OptimizedResumeContent, Template } from '../types';

interface OptimizedResumeViewProps {
  resume: OptimizedResumeContent;
  template: Template;
}

const ModernMinimalist = ({ resume }: { resume: OptimizedResumeContent }) => (
  <div className="p-8 bg-off-white font-sans text-gray-700">
    <header className="flex justify-between items-center mb-8">
      <h1 className="text-4xl font-bold text-slate-blue">{resume.name}</h1>
      <p className="text-right text-sm text-gray-500">{resume.contact}</p>
    </header>
    <div className="border-l-4 border-teal-accent pl-4 mb-8">
      <h2 className="text-xl font-semibold text-slate-blue mb-2">Resume Headline</h2>
      <p className="text-lg">{resume.headline}</p>
    </div>
    <div className="mb-8">
      <h2 className="text-xl font-semibold text-slate-blue mb-2">Professional Summary</h2>
      <p className="text-base leading-relaxed">{resume.professionalSummary}</p>
    </div>
    <div className="mb-8">
      <h2 className="text-xl font-semibold text-slate-blue mb-4">Professional Experience</h2>
      {resume.experience.map((job, index) => (
        <div key={index} className="mb-6">
          <h3 className="text-lg font-semibold text-charcoal">{job.role}</h3>
          <p className="text-md font-medium text-gray-600">{job.company}</p>
          <p className="text-sm text-gray-500 mb-2">{job.dates}</p>
          <ul className="list-none pl-0 space-y-2">
            {job.achievements.map((ach, i) => (
              <li key={i} className="flex items-start">
                <span className="text-teal-accent font-bold mr-3 mt-1">•</span>
                <span>{ach}</span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
    <div>
      <h2 className="text-xl font-semibold text-slate-blue mb-4">Skills</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {resume.skills.map((skill, index) => (
          <div key={index}>
            <h3 className="text-md font-semibold text-charcoal mb-1">{skill.category}</h3>
            <p className="text-base">{skill.items}</p>
          </div>
        ))}
      </div>
    </div>
  </div>
);

const ProfessionalClassic = ({ resume }: { resume: OptimizedResumeContent }) => (
  <div className="p-8 bg-white font-serif text-charcoal">
    <header className="text-center mb-4">
      <h1 className="text-4xl font-bold text-navy">{resume.name}</h1>
      <p className="text-sm text-subtle-gray mt-1">{resume.contact}</p>
    </header>
    <hr className="border-t-2 border-navy mb-6" />
    <div className="mb-6">
      <h2 className="text-xl font-bold text-navy uppercase tracking-wider mb-2">Headline</h2>
      <p className="text-lg italic">{resume.headline}</p>
    </div>
    <div className="mb-6">
      <h2 className="text-xl font-bold text-navy uppercase tracking-wider mb-2">Summary</h2>
      <p className="text-base leading-relaxed">{resume.professionalSummary}</p>
    </div>
    <hr className="border-t border-gray-300 my-6" />
    <div className="mb-6">
      <h2 className="text-xl font-bold text-navy uppercase tracking-wider mb-4">Experience</h2>
      {resume.experience.map((job, index) => (
        <div key={index} className="mb-5">
          <h3 className="text-lg font-bold text-charcoal">{job.role}</h3>
          <div className="flex justify-between items-baseline">
            <p className="text-md font-semibold text-subtle-gray">{job.company}</p>
            <p className="text-sm font-normal text-subtle-gray">{job.dates}</p>
          </div>
          <ul className="list-disc list-outside pl-5 mt-2 space-y-1">
            {job.achievements.map((ach, i) => <li key={i}>{ach}</li>)}
          </ul>
        </div>
      ))}
    </div>
    <hr className="border-t border-gray-300 my-6" />
    <div>
      <h2 className="text-xl font-bold text-navy uppercase tracking-wider mb-4">Skills</h2>
      {resume.skills.map((skill, index) => (
        <div key={index} className="mb-3">
          <p><span className="font-bold">{skill.category}:</span> {skill.items}</p>
        </div>
      ))}
    </div>
  </div>
);

const OptimizedResumeView = ({ resume, template }: OptimizedResumeViewProps) => {
  const renderTemplate = () => {
    switch (template) {
      case Template.MODERN_MINIMALIST:
        return <ModernMinimalist resume={resume} />;
      case Template.PROFESSIONAL_CLASSIC:
        return <ProfessionalClassic resume={resume} />;
      default:
        return <ModernMinimalist resume={resume} />;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      {renderTemplate()}
    </div>
  );
};

export default OptimizedResumeView;
