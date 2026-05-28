import { Type } from "@google/genai";

export const GEMINI_MODEL = 'gemini-2.5-flash';

export const SYSTEM_INSTRUCTION = `You are a world-class career coach and resume writer with deep expertise in the Australian community services, social work, and public sector recruitment landscape. Your primary goal is to transform a user's resume into a highly effective, ATS-optimized document that precisely targets a specific job.

Based on the user's inputs (Job Description, Key Selection Criteria, and Current Resume), you must perform a two-stage process and return a single JSON object.

**Stage 1: Initial Analysis**
Analyze the user's current resume against the job description and KSC.
- Calculate an ATS Compliance Score (0-100).
- Calculate a Position Match Percentage for various categories.
- Identify gaps and list improvement priorities.

**Stage 2: Strategic Optimization & Reporting**
Rewrite and reformat the entire resume to maximize its impact and ATS compatibility.
- Create a new resume with a powerful headline, summary, STAR/CAR-based experience, and a targeted skills section. Infer the user's name and contact info from the resume.
- Generate a new, improved ATS score and match analysis.
- Create a strategic report summarizing the changes.

Produce a single JSON object that strictly follows the provided schema. Do not include any text outside the JSON object.`;

export const getGeminiPrompt = (jobDesc: string, ksc: string, resume: string): string => `
<JobDescription>
${jobDesc}
</JobDescription>

<KeySelectionCriteria>
${ksc}
</KeySelectionCriteria>

<CurrentResume>
${resume}
</CurrentResume>
`;

export const RESPONSE_SCHEMA = {
  type: Type.OBJECT,
  properties: {
    initialAnalysis: {
      type: Type.OBJECT,
      description: "Analysis of the original resume.",
      properties: {
        atsScore: { type: Type.INTEGER, description: "Score from 0-100 for original resume's ATS compatibility." },
        matchAnalysis: {
          type: Type.OBJECT,
          properties: {
            overall: { type: Type.INTEGER, description: "Overall match score from 0-100." },
            categories: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  name: { type: Type.STRING, description: "e.g., Essential Skills Match" },
                  score: { type: Type.INTEGER, description: "Score for this category, 0-100." }
                }
              }
            }
          }
        },
        gapAnalysis: {
          type: Type.ARRAY,
          description: "Specific areas where the resume falls short.",
          items: { type: Type.STRING }
        },
        improvementPriorities: {
          type: Type.ARRAY,
          description: "Top 5 changes needed for better performance.",
          items: { type: Type.STRING }
        }
      }
    },
    optimizedResume: {
      type: Type.OBJECT,
      description: "The complete, rewritten, and optimized resume content.",
      properties: {
        name: { type: Type.STRING, description: "Applicant's full name, inferred from resume." },
        contact: { type: Type.STRING, description: "Applicant's contact info (phone | email | linkedin), inferred from resume." },
        headline: { type: Type.STRING, description: "A concise, keyword-rich headline for the resume." },
        professionalSummary: { type: Type.STRING, description: "A compelling 3-4 line summary." },
        experience: {
          type: Type.ARRAY,
          items: {
            type: Type.OBJECT,
            properties: {
              role: { type: Type.STRING },
              company: { type: Type.STRING },
              dates: { type: Type.STRING },
              achievements: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Bullet points rewritten using STAR/CAR method." }
            }
          }
        },
        skills: {
          type: Type.ARRAY,
          items: {
            type: Type.OBJECT,
            properties: {
              category: { type: Type.STRING, description: "e.g., 'Core Competencies', 'Technical Skills'" },
              items: { type: Type.STRING, description: "Comma-separated list of skills." }
            }
          }
        }
      }
    },
    improvementReport: {
      type: Type.OBJECT,
      description: "Analysis of the optimized resume.",
      properties: {
        atsScore: { type: Type.INTEGER, description: "The improved ATS score from 0-100." },
        matchAnalysis: {
          type: Type.OBJECT,
          properties: {
            overall: { type: Type.INTEGER },
            categories: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  name: { type: Type.STRING },
                  score: { type: Type.INTEGER }
                }
              }
            }
          }
        },
        keywordReport: { type: Type.STRING, description: "List of strategic keywords added and their placement." },
        complianceConfirmation: { type: Type.STRING, description: "Confirmation of formatting and structure improvements." }
      }
    },
    strategicReport: {
      type: Type.OBJECT,
      description: "High-level summary of the transformation.",
      properties: {
        transformationSummary: { type: Type.STRING, description: "Overview of major changes made with reference to community services best practices." }
      }
    }
  }
};