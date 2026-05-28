import { GoogleGenAI, GenerateContentResponse } from "@google/genai";
import { GEMINI_MODEL, getGeminiPrompt, RESPONSE_SCHEMA, SYSTEM_INSTRUCTION } from '../constants';
import { GeminiApiResponse } from '../types';

if (!process.env.API_KEY) {
  throw new Error("API_KEY environment variable not set");
}

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

export const analyzeAndOptimizeResume = async (
  jobDesc: string,
  ksc: string,
  resume: string
): Promise<GeminiApiResponse> => {
  try {
    const prompt = getGeminiPrompt(jobDesc, ksc, resume);

    const response: GenerateContentResponse = await ai.models.generateContent({
      model: GEMINI_MODEL,
      contents: prompt,
      config: {
        systemInstruction: SYSTEM_INSTRUCTION,
        responseMimeType: "application/json",
        responseSchema: RESPONSE_SCHEMA,
        temperature: 0.2,
      },
    });

    const jsonText = response.text.trim();
    
    // With responseMimeType and responseSchema, the API should return a valid JSON string.
    // Direct parsing is preferred over manual string manipulation.
    const parsedData = JSON.parse(jsonText);
    
    // Basic validation to ensure the parsed data matches the expected structure
    if (
        !parsedData.initialAnalysis || 
        !parsedData.optimizedResume || 
        !parsedData.improvementReport ||
        !parsedData.strategicReport
    ) {
        console.error("API response is missing required fields. Full response:", jsonText);
        throw new Error("API response is missing required fields.");
    }

    return parsedData as GeminiApiResponse;

  } catch (error) {
    console.error("Error calling Gemini API:", error);
    if (error instanceof SyntaxError) {
        // This specifically catches JSON parsing errors.
        throw new Error(`Failed to process resume. The API returned an invalid format.`);
    }
    if (error instanceof Error) {
        throw new Error(`Failed to process resume. API Error: ${error.message}`);
    }
    throw new Error("An unknown error occurred while processing the resume.");
  }
};
