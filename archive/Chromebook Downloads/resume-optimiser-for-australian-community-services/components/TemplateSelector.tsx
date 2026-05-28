
import React from 'react';
import { Template } from '../types';

interface TemplateSelectorProps {
  selectedTemplate: Template;
  onSelectTemplate: (template: Template) => void;
}

const TemplateOption = ({ name, selected, onClick }: { name: Template, selected: boolean, onClick: () => void }) => {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-lg border-2 transition-all duration-200 ${
        selected
          ? 'bg-slate-blue text-white border-slate-blue shadow-md'
          : 'bg-white text-charcoal border-gray-300 hover:border-slate-blue hover:shadow-sm'
      }`}
    >
      {name}
    </button>
  );
};

const TemplateSelector = ({ selectedTemplate, onSelectTemplate }: TemplateSelectorProps) => {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <h3 className="text-xl font-bold text-navy mb-4">Select a Template</h3>
      <div className="flex flex-wrap gap-4">
        <TemplateOption
          name={Template.MODERN_MINIMALIST}
          selected={selectedTemplate === Template.MODERN_MINIMALIST}
          onClick={() => onSelectTemplate(Template.MODERN_MINIMALIST)}
        />
        <TemplateOption
          name={Template.PROFESSIONAL_CLASSIC}
          selected={selectedTemplate === Template.PROFESSIONAL_CLASSIC}
          onClick={() => onSelectTemplate(Template.PROFESSIONAL_CLASSIC)}
        />
      </div>
    </div>
  );
};

export default TemplateSelector;
