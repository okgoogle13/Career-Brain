# Optimize AI Studio Prompt for Gemini 3.1 Pro

The goal is to polish and optimize the prompt located at `optimised_ai_studio_prompt.md` to leverage the specific capabilities of Gemini 3.1 Pro. While the current prompt is well-designed for Gemini 2.5 Pro, 3.1 Pro benefits from tighter structural boundaries, enhanced Chain of Thought (CoT), and strict System/User instruction separation.

## User Review Required

> [!IMPORTANT]
> Please review the proposed optimization strategies below. If you approve, I will proceed to rewrite `optimised_ai_studio_prompt.md` implementing these changes. If you would prefer me to adjust any of the strategies (e.g., if you want Gemini to output JSON directly instead of Phase 2 Claude), let me know.

## Open Questions

- The current pipeline relies on Gemini outputting text specs, which Claude then converts to JSON in Phase 2. Gemini 3.1 Pro is highly capable of structured JSON output using `response_schema`. Do you want to strictly preserve the two-phase pipeline, or should we explore having Gemini 3.1 Pro output the v2.3 JSON directly? (The current plan assumes preserving the two-phase pipeline as dictated by the current prompt).

## Proposed Optimization Strategies

Based on evidence-based best practices for Gemini 3.1 Pro, here are the key strategies to polish the prompt:

### 1. XML Semantic Tagging
Gemini 3.1 Pro has exceptional adherence to instructions when distinct contextual blocks are separated by XML tags.
- **Action**: Replace markdown headers (like `ROLE BOUNDARIES:`) with explicit XML blocks (`<role_boundaries>`, `<global_constraints>`, `<differentiation_matrix>`). This prevents attention bleed between the role definition and the strict rules.

### 2. Strict System vs. User Instruction Separation
The current prompt mixes system rules (how to format the output) into the Task Instructions.
- **Action**: Move all formatting rules, output templates, and step-by-step instructions into the **System Instructions**. The **User Instructions** should be extremely lean, containing only the runtime trigger (e.g., "Here are the PDFs. Execute the extraction sequence.").

### 3. Enhanced Chain of Thought (CoT) Scaffold
The current `<design_critique>` block is a great start. Gemini 3.1 Pro's reasoning can be further sharpened by forcing explicit "Checks" before "Decisions".
- **Action**: Add an internal `<differentiation_check>` step within the critique where the model must explicitly compare its proposed motif against the 10 existing themes *before* synthesizing the output.

### 4. Positive and Negative Constraint Pairing
Gemini 3.1 Pro follows constraints best when a negative rule is paired with a positive alternative.
- **Action**: Refine constraints like "NEVER on body text" to "If an accent color is used, apply it EXCLUSIVELY to headings or thin rules. NEVER apply it to body text."

### 5. Few-Shot Exemplar Injection
Providing a micro-example of the exact expected reasoning path drastically reduces format hallucination.
- **Action**: Provide a brief inline example of how the `<design_critique>` scoring and the subsequent concept output should look, establishing the exact tone and formatting density expected.

## Proposed Changes

### `optimised_ai_studio_prompt.md`

#### [MODIFY] [optimised_ai_studio_prompt.md](file:///Users/okgoogle13/.gemini/antigravity-ide/brain/b251b2a2-7532-4e79-abac-71c053e6263f/optimised_ai_studio_prompt.md)
We will rewrite the prompt content to reflect the above strategies. The structure will look like:

**System Instructions:**
```xml
<persona>...</persona>
<global_constraints>...</global_constraints>
<existing_library>...</existing_library>
<task_workflow>
  <step_1_critique>...</step_1_critique>
  <step_2_synthesis>...</step_2_synthesis>
</task_workflow>
<output_template>...</output_template>
```

**Task Instructions:**
```
Here are the source PDFs, the Master Schema, and an example theme.
Execute the extraction sequence as defined in your system instructions.
```

## Verification Plan

### Manual Verification
- Review the updated prompt structure to ensure all v2.3 Schema fields and constraints from the original prompt are preserved.
- The prompt can be tested in Google AI Studio with Gemini 3.1 Pro to verify adherence to the `<design_critique>` structure and output formatting.
