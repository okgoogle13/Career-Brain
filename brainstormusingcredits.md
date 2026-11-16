Analyzed ai_sharing_policy.json:L1-120
Analyzed manifesto.md:L1-197
Analyzed ai_sharing_policy.json:L121-159
Analyzing gemini_sharing_policy.json:L1-100
Analyzed query_brain.py:L1-150
Analyzed content_engine.py:L1-150
Analyzed content_engine.py:L151-450
Analyzed curate_narratives.py:L1-120
Analyzed inject_metrics.py:L1-120
Analyzed compile_brain.py:L1-140
Analyzed content_engine.py:L451-750
Analyzed ats_rules.json:L1-120
Analyzed content_engine.py:L751-1198

Here are **6 substantive architectural proposals** for integrating Google Cloud Discovery Engine (`discoveryengine.googleapis.com`) into Career-Brain on project `gen-lang-client-0040796260`, ordered from **highest leverage-to-effort ratio (fastest to implement, zero cloud state)** to **most ambitious**.

> **Note on Policy File Resolution:** The repository’s canonical sharing policy is [`config/ai_sharing_policy.json`](file:///Users/okgoogle13/Projects/Career-Brain/config/ai_sharing_policy.json) (which governs `gemini_targets` and `claude_targets` and corresponds to `config/gemini_sharing_policy.json` in your brief). All proposals below enforce its Green/Amber/Red data tiers and [`redaction`](file:///Users/okgoogle13/Projects/Career-Brain/config/ai_sharing_policy.json#L145-L158) rules, keeping [`source_docs/`](file:///Users/okgoogle13/Projects/Career-Brain/docs/manifesto.md#L21-L25) strictly local.

---

## Proposal 1 (Quick Win #1): Rosetta-Augmented Cross-Encoder & Global Bipartite KSC Matcher

### 1. Proposal Name & Core Mechanism
* **Module Target:** Drop-in enhancement to [`tools/content_engine.py`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py) (`select_roles`, `select_bullets`, `select_narratives`, and `build_ksc_response`).
* **Core API:** `google.cloud.discoveryengine_v1.RankServiceClient.rank()` (`discoveryengine.googleapis.com/v1/projects/gen-lang-client-0040796260/locations/global/rankingConfigs/default_ranking_config:rank`) using `model="semantic-ranker-default@latest"`.
* **Execution Posture:** **100% Stateless (In-Memory Payload).** Zero Data Stores, zero Cloud Storage buckets, zero persistent state. Can be built and tested in ~120 lines of Python.

### 2. Problem Solved in Career-Brain
Currently, Phase 5 content selection in [`tools/content_engine.py`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py) suffers from three structural retrieval bottlenecks:
1. **Brittle Lexical Substring Matching:** [`extract_job_ad_keywords()`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py#L116-L139) and [`_build_criterion()`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py#L988-L1000) match criteria solely via exact lowercased substring hits against [`competency_tag_keywords`](file:///Users/okgoogle13/Projects/Career-Brain/config/ats_rules.json#L12-L26) in [`config/ats_rules.json`](file:///Users/okgoogle13/Projects/Career-Brain/config/ats_rules.json). If a government Position Description asks for *"demonstrated capacity to navigate intersecting statutory service systems with consumers experiencing co-occurring complexity"*, and doesn't use the literal substring `"case management"` or `"referral"`, [`_build_criterion()`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py#L988-L1000) extracts zero `service_coordination` tags.
2. **Blindness to Rosetta Stone Transfers During Retrieval:** [`apply_rosetta_stone()`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py#L391-L451) only runs *after* a bullet is selected. A corporate finance bullet about multi-party regulatory audit governance is under-scored for a community services governance criterion because the cross-domain bridge isn't injected into the candidate representation at retrieval time.
3. **Greedy Sequential Narrative Starvation:** In [`build_ksc_response()`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py#L1003-L1081), narratives are assigned greedily in order (`Criterion 1 -> Criterion 6`) via `used_narratives.add(id(narrative))`. If Story A scores `0.92` on Criterion 1 and `0.95` on Criterion 4, while Story B scores `0.89` on Criterion 1 and `0.30` on Criterion 4, greedy assignment gives Story A to Criterion 1 and leaves Criterion 4 with a weak match.

### 3. Data Flow & Privacy Boundary
* **Inputs:**
  * Job ad / KSC criteria strings ($K \le 6$ criteria).
  * Green-tier exports governed by [`gemini_ksc_context`](file:///Users/okgoogle13/Projects/Career-Brain/config/ai_sharing_policy.json#L76-L87): `database/career_history_enriched.json` (filtering out `needs_review == True`), `database/ksc_curated_tier1.json` (or Tier 1+2 from `ksc_curated.json`), and `database/skills_and_taxonomy.json`.
* **Pre-Flight Privacy Gate:** Before building `RankingRecord` objects, a local filter strips `source_lineage` filenames (or hashes them to an opaque local lookup key `rec_001..rec_200`) and runs the regex redaction scanner defined in [`config/ai_sharing_policy.json` (`redaction.fields_to_scan`)](file:///Users/okgoogle13/Projects/Career-Brain/config/ai_sharing_policy.json#L145-L158).
* **Rosetta-Enriched Payload Shape:**
  For each narrative/bullet, we synthesize a composite `RankingRecord` that pre-bakes the [`ROSETTA_STONE`](file:///Users/okgoogle13/Projects/Career-Brain/pipeline/compile_brain.py#L123-L140) translation into the record's `title` and `content`:
  ```python
  # Request payload per criterion k in 1..K (sent concurrently via asyncio/ThreadPoolExecutor)
  RankRequest(
      ranking_config="projects/gen-lang-client-0040796260/locations/global/rankingConfigs/default_ranking_config",
      model="semantic-ranker-default@latest",
      query=f"Selection Criterion: {criterion_text}\nTarget Role: {target_role} ({employer_type})",
      top_n=len(records),  # Up to 200 records scored in a single call
      ignore_record_details_in_response=True,  # Saves bandwidth; returns only id + score
      records=[
          RankingRecord(
              id=f"nar_{idx}",  # Opaque local ID, no PII or raw filename
              title=f"{n['narrative_type']} | Tier {n['quality_tier']} | Competencies: {', '.join(n['competency_tags'])} | Rosetta Bridge: {rosetta_title}",
              content=f"{n['full_text']}\n[Transferable Mechanism: {rosetta_contextual_bridge}]",
          )
          for idx, n in enumerate(candidate_narratives[:200])
      ],
  )
  ```
* **Global Hungarian Assignment Step:** The $K$ calls return a dense $K \times N$ matrix of calibrated cross-encoder relevance scores $S_{k,i} \in [0, 1]$. We combine $S_{k,i}$ with local priors (e.g., `+0.08` for `quality_tier == 1`, `+0.05` for hard metric presence) and solve the maximum-weight bipartite matching over the $K \le 6$ criteria (solvable in $<1\text{ ms}$ via dynamic programming or `scipy.optimize.linear_sum_assignment` / pure-Python Kuhn-Munkres) so no STAR story is reused and total application evidence strength is globally maximized.

### 4. Why This Exploits the Credit Uniquely
* **Cross-Encoder Attention vs. Bi-Encoder Embeddings:** Unlike standard vector embeddings (which compress a 350-word STAR story into a single fixed vector and lose fine-grained multi-clause alignment), `RankService.rank()` runs a full transformer **cross-encoder** with joint token-to-token attention between the full KSC criterion prompt and every clause of the STAR story + Rosetta bridge.
* **Zero Direct API Cost:** Calling `RankService.rank()` bills `discoveryengine.googleapis.com` directly against the \$1,000 GenAI App Builder credit (~$1 per 1,000 requests of up to 200 records each), delivering 6-criterion × 200-record joint cross-attention in ~180 ms parallel wall-clock time without touching `aiplatform.googleapis.com` or `generativelanguage.googleapis.com`.

### 5. Failure Modes & Trade-offs
* **200-Record Hard Limit per `RankRequest`:** `RankService.rank()` accepts at most 200 `RankingRecord` items per call.
  * *Mitigation:* `ksc_curated_tier1.json` is well under 200 narratives. For all achievement bullets across `career_history_enriched.json` (if $>200$), either pre-filter out `needs_review=True` and pure duplicates, or chunk into two 200-record batches since scores from `semantic-ranker-default@latest` are logit-calibrated in $[0, 1]$ and directly comparable across batches for the same `query`.
* **Token Truncation per Record:** The ranker truncates `title + content` beyond ~512–1,024 tokens.
  * *Mitigation:* Place `competency_tags`, `metric_outcome`, and the Rosetta bridge summary in `title` and the first 400 words of the STAR story in `content`.

---

## Proposal 2 (Quick Win #2): Span-Exact Grounding, Cross-Role Chimera Detector & Auto-`[[NEEDS_REVIEW]]` Gate

### 1. Proposal Name & Core Mechanism
* **Module Target:** Post-generation verification hook in [`tools/content_engine.py`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py) (wrapping `_rewrite_car_with_llm` and cover letter / summary builders) plus a standalone CLI audit subcommand in [`pipeline/query_brain.py`](file:///Users/okgoogle13/Projects/Career-Brain/pipeline/query_brain.py).
* **Core API:** `google.cloud.discoveryengine_v1.GroundedGenerationServiceClient.check_grounding()` (`discoveryengine.googleapis.com/v1/projects/gen-lang-client-0040796260/locations/global/groundingConfigs/default_grounding_config:checkGrounding`).
* **Execution Posture:** **100% Stateless (In-Memory Payload).** Fast implementation (~150 lines of Python), zero cloud persistence.

### 2. Problem Solved in Career-Brain
Career-Brain's current hallucination and overclaim defenses have three critical blind spots:
1. **Unverified Prompt Self-Policing:** In [`get_recruiter_system_prompt()`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py#L758-L760), the LLM is instructed: *"Any word, phrase, or sentence you add that is not directly evidenced in the source MUST be wrapped in `[[NEEDS_REVIEW: <your addition>]]`."* In practice, LLMs routinely hallucinate plausible connective claims, inflated caseload numbers, or implied clinical authority without emitting the `[[NEEDS_REVIEW: ...]]` wrapper.
2. **Lexical-Only Overclaim Detection:** [`overclaim_terms`](file:///Users/okgoogle13/Projects/Career-Brain/config/ats_rules.json#L108-L120) in `config/ats_rules.json` only catches literal strings (`"clinician"`, `"psychologist"`, `"provided therapy"`). It cannot catch **factual overclaims** where the draft states *"Led a team of 12 case managers across three crisis housing sites"* when the underlying achievement bullet in `career_history_enriched.json` actually says *"Collaborated within a 12-person multidisciplinary team"*.
3. **"Frankenstein" Cross-Role Chimera Blending:** In [`_rewrite_car_with_llm()`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py#L877-L887), a single source narrative is sent alongside up to 8 `SUPPORTING CAREER EVIDENCE` bullets pulled across *different* employers and roles ([`_extract_grounding_evidence`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py#L831-L852)). The LLM frequently grafts a metric from Role B (e.g., a corporate finance SLA or another NFP's caseload) onto the story from Role A, creating a factually false hybrid story.

### 3. Data Flow & Privacy Boundary
* **Inputs:**
  * Amber-tier `answer_candidate`: The drafted KSC CAR response (`context + action + result`) or cover letter body, permitted under [`gemini_application_review`](file:///Users/okgoogle13/Projects/Career-Brain/config/ai_sharing_policy.json#L88-L102) (`requires_active_task: true`).
  * Green-tier `facts`: The specific source narrative from `ksc_curated_tier1.json` (Fact `0`, tagged as `primary_narrative`) and the specific achievement bullets from `career_history_enriched.json` (Facts `1..M`, tagged with their `role_fingerprint`, `company`, and `sector`).
* **Request Payload Shape:**
  ```python
  CheckGroundingRequest(
      grounding_config="projects/gen-lang-client-0040796260/locations/global/groundingConfigs/default_grounding_config",
      answer_candidate=drafted_car_text,
      facts=[
          GroundingFact(
              fact_text=source_narrative["full_text"],
              attributes={
                  "fact_type": "primary_narrative",
                  "organisation_context": source_narrative.get("organisation_context") or "unspecified",
                  "lineage_id": sha256_short(source_narrative["source_lineage"]),
              },
          ),
          *[
              GroundingFact(
                  fact_text=bullet["raw_text"],
                  attributes={
                      "fact_type": "supporting_bullet",
                      "role_fingerprint": role["fingerprint"],
                      "company": role["company"],
                      "sector": role.get("sector") or "unknown",
                  },
              )
              for role, bullet in candidate_evidence_bullets
          ],
      ],
      grounding_spec=CheckGroundingSpec(citation_threshold=0.70),
  )
  ```
* **Deterministic Post-Processing & Chimera Audit:**
  `CheckGroundingResponse` returns `support_score` (overall $[0.0, 1.0]$) and `claims` (`list[CheckGroundingResponse.Claim]`), where each claim has exact UTF-8 byte/char offsets (`start_pos`, `end_pos`), `claim_text`, `grounding_check_required` (`bool`), and `citation_indices` (`list[int]`). Our local Python gate executes three deterministic rules:
  1. **Auto-`[[NEEDS_REVIEW]]` Wrapping:** Working backward from highest `start_pos` to lowest (to preserve string offsets), any claim with `grounding_check_required == True` and `len(citation_indices) == 0` is automatically rewritten in-place as `[[NEEDS_REVIEW (Ungrounded Claim): <claim_text>]]`.
  2. **Hard Metric Verification:** If `METRIC_PATTERN` ([`curate_narratives.py` L61-L68](file:///Users/okgoogle13/Projects/Career-Brain/pipeline/curate_narratives.py#L61-L68)) matches inside `claim_text`, the gate verifies that the exact numerical token appears in at least one cited `facts[i].fact_text` for $i \in \text{citation\_indices}$. If not, it flags `[[OVERCLAIM_METRIC_MISMATCH: <claim_text>]]`.
  3. **Cross-Role Chimera Detection:** If claims inside the `context`/`action`/`result` of a single event cite `GroundingFact` indices belonging to *more than one* distinct `role_fingerprint` (unless explicitly separated in `support_bullet_1`/`2`), the gate raises a `CHIMERA_ROLE_MIX_WARNING` in `database/doc_generation_report.json` before Phase 5 Google Docs export.

### 4. Why This Exploits the Credit Uniquely
* **Dedicated NLI Fact-Verification Model:** `check_grounding()` runs Google's specialized fine-tuned Natural Language Inference (NLI) attribution model that decomposes prose into atomic claims, distinguishes rhetorical framing (`grounding_check_required=False`) from factual assertions (`grounding_check_required=True`), and computes calibrated entailment scores per fact.
* **Enforces Career-Brain's Approval Gate Deterministically:** [`AGENTS.md`](file:///Users/okgoogle13/Projects/Career-Brain/AGENTS.md) mandates: *"Before generating or submitting application copy, review every banned-phrase, review-phrase, and overclaim warning; only spelling may be auto-corrected."* This turns subjective LLM honesty into a deterministic, offset-accurate verification gate funded 100% by the Discovery Engine trial credit.

### 5. Failure Modes & Trade-offs
* **Max 200 `GroundingFact` Entries & 10,000-Char `answer_candidate` Limit:** `check_grounding` accepts up to 200 facts per request.
  * *Mitigation:* A single KSC response or cover letter is 250–500 words (~2,500 chars) and only needs the 1–3 selected source narratives plus 15–30 role-relevant achievement bullets (well under 50 facts).
* **False Positives on Rosetta Stone Conceptual Framing:** If a sentence bridges corporate governance to community service coordination without asserting a new empirical event, `check_grounding` might mark it ungrounded if `citation_threshold` is too high.
  * *Mitigation:* Include the matched [`TaxonomyTranslation.contextual_bridge`](file:///Users/okgoogle13/Projects/Career-Brain/pipeline/compile_brain.py#L123-L129) from `skills_and_taxonomy.json` in `facts` with `attributes={"fact_type": "rosetta_translation"}` so the NLI model recognizes approved terminology bridges as grounded.

---

## Proposal 3 (Quick Win #3): Stateless Inline Grounded Generation for CAR Rewrites & Voice Curation

### 1. Proposal Name & Core Mechanism
* **Module Target:** Direct replacement for the paid `generativelanguage.googleapis.com` calls in [`tools/content_engine.py::_rewrite_car_with_llm()`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py#L855-L915) and [`pipeline/curate_narratives.py::_call_gemini_voice()`](file:///Users/okgoogle13/Projects/Career-Brain/pipeline/curate_narratives.py#L108-L120).
* **Core API:** `google.cloud.discoveryengine_v1.GroundedGenerationServiceClient.generate_grounded_content()` (`discoveryengine.googleapis.com/v1/projects/gen-lang-client-0040796260/locations/global:generateGroundedContent`) using **`GroundingSource.inline_source` (`InlineSource(grounding_facts=...)`)**.
* **Execution Posture:** **100% Stateless (In-Memory Payload).** No Data Store creation required—`generate_grounded_content` natively accepts inline facts on every API call.

### 2. Problem Solved in Career-Brain
Right now, Career-Brain has two places where LLM inference is called via `google.genai.Client(api_key=os.environ["GEMINI_API_KEY"])`:
1. **Phase 5 KSC Rewriting ([`_rewrite_car_with_llm`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py#L890-L901)):** Calls `gemini-2.5-flash` on `generativelanguage.googleapis.com`, which **bypasses the \$1,000 Discovery Engine credit and bills the credit card directly** (or hits free-tier rate limits).
2. **Phase 3 Narrative Voice Scoring ([`_call_gemini_voice`](file:///Users/okgoogle13/Projects/Career-Brain/pipeline/curate_narratives.py#L108-L120)):** Scores narratives on the 5 authentic voice patterns (`P1 named_service_chain` through `P5 pivot_with_thesis`). Because it costs direct Gemini API quota, [`curate_narratives.py`](file:///Users/okgoogle13/Projects/Career-Brain/pipeline/curate_narratives.py#L15-L18) restricts voice scoring by default to boundary scores (`5–8`) and skips the rest unless `--full-voice-score` is passed.

By switching both functions to `GroundedGenerationService.generate_grounded_content()` with `InlineSource`, **100% of Career-Brain's generative LLM calls move under `discoveryengine.googleapis.com`**—consuming the \$1,000 trial credit while simultaneously returning built-in claim-level grounding citations in the generation response!

### 3. Data Flow & Privacy Boundary
* **Inputs:**
  * For CAR Rewrite: `get_recruiter_system_prompt()` ([`content_engine.py` L679](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py#L679)) as `system_instruction`, the KSC `criterion_text` in `contents`, and the selected Green-tier narrative + supporting bullets passed in `grounding_source.inline_source.grounding_facts`.
  * For Voice Scoring: `_VOICE_SCORE_SYSTEM` ([`curate_narratives.py` L75-L104](file:///Users/okgoogle13/Projects/Career-Brain/pipeline/curate_narratives.py#L75-L104)) as `system_instruction`, the narrative text in `contents`, and the 5 voice pattern definitions + exemplars from `docs/voice/voice-authenticity-profile.md` as `inline_source.grounding_facts`.
* **Request Payload Shape:**
  ```python
  GenerateGroundedContentRequest(
      location="projects/gen-lang-client-0040796260/locations/global",
      system_instruction=GenerateGroundedContentRequest.Content(
          role="system",
          parts=[GenerateGroundedContentRequest.Part(text=get_recruiter_system_prompt())],
      ),
      contents=[
          GenerateGroundedContentRequest.Content(
              role="user",
              parts=[GenerateGroundedContentRequest.Part(
                  text=f"SELECTION CRITERION:\n{criterion_text}\nCOMPETENCIES: {', '.join(competencies)}\nRewrite into JSON with keys context, action, result."
              )],
          )
      ],
      generation_spec=GenerateGroundedContentRequest.GenerationSpec(
          model_id="gemini-2.5-flash",  # Executed inside Discovery Engine SKU
          temperature=0.25,
          max_output_tokens=2048,
      ),
      grounding_spec=GenerateGroundedContentRequest.GroundingSpec(
          grounding_sources=[
              GenerateGroundedContentRequest.GroundingSource(
                  inline_source=GenerateGroundedContentRequest.InlineSource(
                      grounding_facts=[
                          GroundingFact(fact_text=full_text, attributes={"source": "tier1_narrative"}),
                          *[GroundingFact(fact_text=b, attributes={"source": "career_history"}) for b in evidence_bullets],
                      ]
                  )
              )
          ]
      ),
  )
  ```
* **Privacy Enforcement:** Uses ADC (`google.auth.default()`) scoped to project `gen-lang-client-0040796260` (or `op run --env-file=".env"`). Only Green-tier structured narratives/bullets are sent in `inline_source`; zero data is persisted in any Data Store.

### 4. Why This Exploits the Credit Uniquely
* **Turns Direct-Billed Gemini Calls into Credit-Covered Discovery Engine Calls:** Calling `gemini-2.5-flash` via `aiplatform.googleapis.com` or `generativelanguage.googleapis.com` is excluded from the GenAI App Builder credit. Calling `generateGroundedContent` on `discoveryengine.googleapis.com` invokes Gemini *inside* the Discovery Engine Grounded Generation SKU, which is **100% covered by the \$1,000 trial credit**.
* **Unlocks `--full-voice-score` Across the Entire Narrative Vault for Free:** You can run `curate_narratives.py --full-voice-score` across every narrative in `ksc_and_narratives.json` using trial credit instead of rationing calls to `quality_score` 5–8.
* **Single-Trip Generation + Attribution:** `GenerateGroundedContentResponse.Candidate.grounding_metadata` returns `support_score` and `grounding_attributions` alongside the generated CAR JSON in a single API call.

### 5. Failure Modes & Trade-offs
* **No Native `responseMimeType="application/json"` Field in `GenerationSpec`:** Unlike `google-genai`'s `GenerateContentConfig`, `GenerateGroundedContentRequest.GenerationSpec` only exposes `model_id`, `temperature`, `top_p`, `top_k`, and `max_output_tokens`.
  * *Mitigation:* Keep the explicit JSON schema prompt in [`get_recruiter_system_prompt()`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py#L737-L749) and strip optional markdown fences (`` ```json ... ``` ``) with a 3-line regex before `json.loads()`.
* **Inline Fact Limit (Up to 200 Facts):** Easily satisfied since each CAR rewrite only passes 1 narrative + up to 8 supporting bullets + relevant Rosetta Stone mappings.

---

## Proposal 4 (Medium Effort, Stateless): Cross-Pillar Semantic Metric & Evidence Backfill Engine

### 1. Proposal Name & Core Mechanism
* **Module Target:** Phase 4 Pass 4 extension in [`pipeline/inject_metrics.py`](file:///Users/okgoogle13/Projects/Career-Brain/pipeline/inject_metrics.py) (`Pass 4: Cross-Pillar Semantic Entailment`).
* **Core APIs:** Two-stage stateless pipeline combining `RankServiceClient.rank()` (cross-pillar candidate metric retrieval) and `GroundedGenerationServiceClient.check_grounding()` (entailment verification that the metric genuinely applies to the target bullet).
* **Execution Posture:** **100% Stateless (In-Memory Batch Pass).** Reads local JSON engines, computes verified candidate metric annotations in memory, and writes human-reviewable candidates to `database/metric_injection_targets.md` (and approved annotations to `database/career_history_enriched.json`).

### 2. Problem Solved in Career-Brain
In [`pipeline/inject_metrics.py`](file:///Users/okgoogle13/Projects/Career-Brain/pipeline/inject_metrics.py), any achievement bullet $>20$ words without a numerical metric has `needs_review: true` set by [`pipeline/compile_brain.py`](file:///Users/okgoogle13/Projects/Career-Brain/docs/manifesto.md#L183), which **completely disqualifies it** from Phase 5 selection in [`select_bullets()`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py#L271-L272).
Currently, [`inject_metrics.py`](file:///Users/okgoogle13/Projects/Career-Brain/pipeline/inject_metrics.py#L10-L17) tries to rescue these bullets using:
* **Pass 2 (Cross-Source Inference):** Uses `difflib.SequenceMatcher` (`text_similarity >= 0.65`) within the same role in `career_history.json`.
* **Pass 3 (Sibling Context):** Checks sibling bullets in the same role sharing a `domain_tag`.

**Why this fails on real career history:**
1. `SequenceMatcher` is a character-level longest-common-contiguous-substring ratio. If Resume Version A says *"Redesigned intake triage workflow for high-risk outreach clients"* (no metric, `needs_review: true`) and Resume Version B says *"Cut intake wait times by 40% across 180 monthly referrals by overhauling triage protocols"*, `SequenceMatcher` scores `< 0.35` and misses the match completely.
2. **Cross-Pillar Isolation:** Often, the exact metric for an unquantified resume bullet in `career_history.json` (Pillar 1) is sitting inside a long-form STAR narrative in `ksc_curated.json` (Pillar 2) from a past KSC application! [`inject_metrics.py`](file:///Users/okgoogle13/Projects/Career-Brain/pipeline/inject_metrics.py) never inspects `ksc_curated.json`.

### 3. Data Flow & Privacy Boundary
* **Inputs:**
  * Target queries: All bullets in `database/career_history.json` where `needs_review == True` after Passes 1–3.
  * Candidate Metric Pool (Green-tier local JSONs only):
    1. All achievement bullets in `database/career_history.json` that pass `bullet_has_hard_metric(b) == True` ([`inject_metrics.py` L99-L101](file:///Users/okgoogle13/Projects/Career-Brain/pipeline/inject_metrics.py#L99-L101)).
    2. All metric-bearing sentences (`METRIC_EXTRACTOR.search(sentence)`) split from `database/ksc_curated.json` narratives.
* **Two-Stage Stateless Protocol:**
  1. **Stage 1 (`RankService.rank()`):** For each `needs_review: true` bullet $b$ in role $R$ (`company`, `role`, `sector`), build a `RankRequest` where `query = f"[{R['company']} - {R['role']}] {b['raw_text']}"` and `records` are all metric-bearing bullets and STAR narrative paragraphs matching the same `sector` or `organisation_context`. Retrieve top 5 candidates with cross-encoder score $\ge 0.60$.
  2. **Stage 2 (`GroundedGenerationService.check_grounding()`):** To prevent false-positive metric grafting (where two bullets are in the same domain but describe different projects), construct a synthetic candidate statement combining bullet $b$ with the extracted metric phrase $m_k$ from top candidate $k$, and run `check_grounding(answer_candidate=f"{b['raw_text']} ({m_k})", facts=[GroundingFact(fact_text=full_parent_narrative_or_role_context)])`.
  3. **Invariant-Safe Output:** Respecting [`AGENTS.md`](file:///Users/okgoogle13/Projects/Career-Brain/AGENTS.md) (*"`needs_review` is pipeline-managed; never remove it manually"*), high-entailment cross-pillar matches (`support_score >= 0.80`) are written to `database/metric_injection_targets.md` with exact source lineage, extracted metric, cross-encoder similarity, and NLI grounding score for one-click/approved Pass 2/3 promotion.

### 4. Why This Exploits the Credit Uniquely
* **Solves Entity & Event Coreference Across Pillars:** Combining `RankService.rank()` (cross-encoder semantic retrieval) with `check_grounding()` (NLI entailment verification) creates a high-precision event coreference pipeline across Pillar 1 (`career_history.json`) and Pillar 2 (`ksc_curated.json`) without training custom models or paying for external embedding databases.
* **Batch Efficiency:** Even if 80 bullets have `needs_review: true`, 80 `RankRequest` calls + 80 `CheckGroundingRequest` calls cost less than \$0.30 of the \$1,000 trial credit and complete in ~15 seconds.

### 5. Failure Modes & Trade-offs
* **Same-Employer Different-Project Confusion:** If the candidate led two separate projects at the same employer, a metric from Project X in a STAR narrative could be semantically close to an unquantified bullet from Project Y.
  * *Mitigation:* Stage 2 (`check_grounding`) tests whether the specific `task_responsibility` and `strategy_methodology` ([`AchievementBullet` schema](file:///Users/okgoogle13/Projects/Career-Brain/pipeline/compile_brain.py#L51-L65)) of bullet $b$ are entailed by the candidate STAR narrative—rejecting metrics whose surrounding action context does not match.

---

## Proposal 5 (Medium-High Effort, Stateful): Zero-GCS Schema-Filtered Career Knowledge Data Store

### 1. Proposal Name & Core Mechanism
* **Module Target:** New backend mode (`--engine discovery`) for [`pipeline/query_brain.py`](file:///Users/okgoogle13/Projects/Career-Brain/pipeline/query_brain.py) and [`tools/content_engine.py`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py), plus a sync utility `pipeline/sync_discovery_store.py`.
* **Core APIs:**
  * `DocumentServiceClient.import_documents()` using **`ImportDocumentsRequest.InlineSource`** (direct in-memory protobuf upload, **bypassing Google Cloud Storage completely**).
  * `SearchServiceClient.search()` using structured `filter`, `BoostSpec` (`ConditionBoostSpec`), `QueryExpansionSpec`, and `FacetSpec`.
* **Execution Posture:** **Stateful Structured Data Store (`discoveryengine.googleapis.com`)** populated exclusively from Green-tier JSON exports via inline gRPC batches (zero GCS buckets).

### 2. Problem Solved in Career-Brain
[`pipeline/query_brain.py`](file:///Users/okgoogle13/Projects/Career-Brain/pipeline/query_brain.py) currently supports only rigid single-dimension CLI filters (`bullets <tag>`, `star <competency>`, `role <company>`) using exact string matching or `difflib.get_close_matches`. Similarly, [`tools/content_engine.py`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py) scores roles and bullets with hardcoded linear weights (`recency * 0.6 + domain_normalised * 0.4` in [`select_roles`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py#L225)).
When tailoring an application for a specialized hybrid role (e.g., *Senior Service System Reform Officer — MARAM & Governance*), you cannot execute a single query that says:
> *"Semantic search for 'multi-agency risk governance and systemic reform', filtered to `needs_review = false` AND (`quality_tier <= 2` OR `has_hard_metric = true`), dynamically boosted by `car_quality_score` and `recency_rank`, with automatic query expansion across community services synonyms, returning facet counts by `competency_tags` and `domain_tags`."*

### 3. Data Flow & Privacy Boundary
* **Strict Green-Tier Scope & Redaction Gate:**
  * Only Green-tier files defined in [`gemini_ksc_context`](file:///Users/okgoogle13/Projects/Career-Brain/config/ai_sharing_policy.json#L76-L87) (`career_history_enriched.json`, `ksc_curated_tier1.json`, `skills_and_taxonomy.json`) are eligible.
  * Before constructing `discoveryengine.Document` protobufs, `source_lineage` raw filenames are replaced with salted SHA-256 hashes (stored in a local-only `database/.lineage_map.json` that never leaves disk), and the redaction scanner ([`config/ai_sharing_policy.json` L145-L158](file:///Users/okgoogle13/Projects/Career-Brain/config/ai_sharing_policy.json#L145-L158)) strips any residual Amber/Red patterns.
* **Zero-GCS Inline Ingestion (`ImportDocumentsRequest.InlineSource`):**
  Instead of uploading JSONL files to a GCS bucket (which would incur excluded Cloud Storage fees and leave data in a bucket), `DocumentService.import_documents()` accepts up to **100 `Document` objects per inline call** with `ReconciliationMode.FULL` or `INCREMENTAL`:
  ```python
  Document(
      id=f"ach_{role_fingerprint}_{ach_idx}",
      struct_data={
          "doc_kind": "achievement_bullet",      # "achievement_bullet" | "star_narrative" | "rosetta_bridge"
          "sector": role.get("sector", "hybrid"),
          "company": role["company"],
          "role_title": role["role"],
          "end_date_rank": _parse_date_rank(role.get("end_date")),
          "domain_tags": ach["domain_tags"],
          "competency_tags": matched_competencies,
          "has_hard_metric": _has_metric(ach["raw_text"]),
          "needs_review": ach["needs_review"],
          "car_quality_score": ach.get("car_quality_score", 0),
          "is_lived_experience": ach.get("is_lived_experience", False),
          "rosetta_community_terms": rosetta_kws,
          "lineage_hash": sha256_short(ach["source_lineage"]),
      },
      content=Document.Content(
          mime_type="text/plain",
          raw_bytes=f"{ach.get('suggested_rewrite') or ach['raw_text']}\n{rosetta_bridge}".encode("utf-8"),
      ),
  )
  ```
* **Search Payload with `BoostSpec` & `FacetSpec`:**
  ```python
  SearchRequest(
      serving_config="projects/gen-lang-client-0040796260/locations/global/collections/default_collection/dataStores/career-brain-green/servingConfigs/default_search",
      query=job_ad_or_criterion_query,
      filter='needs_review: ANY("false") AND doc_kind: ANY("achievement_bullet", "star_narrative")',
      query_expansion_spec=SearchRequest.QueryExpansionSpec(
          condition=SearchRequest.QueryExpansionSpec.Condition.AUTO
      ),
      boost_spec=SearchRequest.BoostSpec(
          condition_boost_specs=[
              SearchRequest.BoostSpec.ConditionBoostSpec(
                  condition='has_hard_metric: ANY("true")', boost=0.35
              ),
              SearchRequest.BoostSpec.ConditionBoostSpec(
                  condition='quality_tier = 1', boost=0.40
              ),
              SearchRequest.BoostSpec.ConditionBoostSpec(
                  condition='end_date_rank >= 24288', boost=0.20  # >= 2024 roles
              ),
          ]
      ),
      facet_specs=[
          SearchRequest.FacetSpec(
              facet_key=SearchRequest.FacetSpec.FacetKey(key="domain_tags"), limit=15
          ),
          SearchRequest.FacetSpec(
              facet_key=SearchRequest.FacetSpec.FacetKey(key="competency_tags"), limit=15
          ),
      ],
  )
  ```

### 4. Why This Exploits the Credit Uniquely
* **Hybrid Dense + Sparse Search with Structured Boosting:** Vertex AI Search combines semantic vector retrieval, BM25 keyword matching, automatic query expansion, and structured numerical/boolean `BoostSpec` conditioning inside a single managed index covered by the \$1,000 trial credit.
* **Instant Coverage Heatmaps via Facets:** A single `SearchService.search()` call with a full Position Description as the query returns `SearchResponse.facets` over `domain_tags` and `competency_tags`—instantly showing which competencies in the PD have deep evidence in your vault (`count >= 5`) vs. thin coverage (`count <= 1`).
* **Zero GCS Dependency:** Using `ImportDocumentsRequest.InlineSource` avoids Cloud Storage buckets completely, ensuring zero non-Discovery Engine billing.

### 5. Failure Modes & Trade-offs
* **100-Document Batch Cap on `InlineSource`:** `ImportDocumentsRequest.inline_source` allows at most 100 documents per request.
  * *Mitigation:* Career-Brain's Green-tier database contains ~150–400 total bullets + narratives + taxonomy mappings, which syncs in 2–4 sequential `import_documents` calls (~5 seconds total).
* **Index Warming Latency (~2–5 Minutes After Schema Creation):** First-time Data Store schema registration and initial indexing take a few minutes to become searchable.
  * *Mitigation:* Only run `sync_discovery_store.py` after an approved Phase 2–4 pipeline run (`compile_brain.py` / `curate_narratives.py` / `inject_metrics.py`), while keeping Proposal 1 (`RankService.rank()`) available for zero-wait stateless scoring.

---

## Proposal 6 (Most Ambitious): Multi-Hop Position Description Decomposer, Gap Analyzer & Panel Simulator

### 1. Proposal Name & Core Mechanism
* **Module Target:** New pre-Phase-5 strategic intelligence tool `tools/analyze_job_fit.py` (producing a structured Job-Fit & KSC Blueprint before `tools/generate_document.py` is approved to run).
* **Core APIs:**
  * `ConversationalSearchServiceClient.answer_query()` (`discoveryengine.googleapis.com/v1/projects/gen-lang-client-0040796260/locations/global/collections/default_collection/engines/career-brain-engine/servingConfigs/default_search:answer`) with `AnswerGenerationSpec`, `QueryUnderstandingSpec`, and `GroundingSpec`.
  * Chained with `RankServiceClient.rank()` (Proposal 1) and `GroundedGenerationServiceClient.check_grounding()` (Proposal 2).
* **Execution Posture:** **Hybrid Stateful/Stateless Multi-Step Pipeline** operating over the Green-tier Data Store (Proposal 5) and outputting a local markdown artifact + pre-validated placeholder JSON for `tools/generate_document.py`.

### 2. Problem Solved in Career-Brain
Currently, Career-Brain jumps straight from a raw job ad / criteria list into [`tools/generate_document.py`](file:///Users/okgoogle13/Projects/Career-Brain/tools/generate_document.py), filling Google Docs placeholders (`{{BULLET_1}}`, `{{KSC_1_CONTEXT}}`, etc.). That workflow misses the **pre-application strategic decision and panel-audit phase**:
1. **Unstated / Implicit Criteria in Position Descriptions:** Many NFP and Victorian public sector PDs embed critical evaluation points inside "Role Purpose" or "Organisational Context" (e.g., MARAM alignment, lived-experience supervision boundaries, DFFH reporting) that aren't isolated in the numbered KSC list.
2. **Evidence Gap & Rosetta Strategy Planning:** Before committing to an application or choosing between resume variants, the candidate needs to know: *Which KSC criteria are directly satisfied by community-sector roles, which require a corporate-to-community Rosetta Stone bridge, and where is the hardest panel pushback likely to occur?*
3. **Cross-Document Coherence (Resume + Cover Letter + KSC Pack):** In [`tools/content_engine.py`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py), `RESUME`, `COVER_LETTER`, and `KSC` runs execute independently. The cover letter's `MAX_COVER_LETTER_EVIDENCE = 2` paragraphs may accidentally duplicate or contradict the primary STAR stories chosen for the KSC pack.

### 3. Data Flow & Privacy Boundary
* **Inputs:**
  * User-supplied Position Description (PD) text and target role metadata.
  * Green-tier Discovery Engine Data Store (`career-brain-green` from Proposal 5) + local [`config/ats_rules.json`](file:///Users/okgoogle13/Projects/Career-Brain/config/ats_rules.json) and `docs/voice/voice-authenticity-profile.md`.
* **Three-Hop Discovery Engine Execution Flow:**
  1. **Hop 1 — PD Decomposition & Query Rephrasing (`QueryUnderstandingSpec` + `generateGroundedContent`):** Extracts all explicit KSCs, implicit sector frameworks (e.g., MARAM, NDIS, AOD harm reduction, corporate governance), and any potential [`overclaim_terms`](file:///Users/okgoogle13/Projects/Career-Brain/config/ats_rules.json#L108-L120) present in the PD itself (e.g., mandatory AHPRA/AASW registration vs. lived-experience/case-coordination scope).
  2. **Hop 2 — Multi-Hop Grounded Panel Synthesis (`ConversationalSearchService.answer_query`):**
     ```python
     AnswerQueryRequest(
         serving_config="projects/gen-lang-client-0040796260/locations/global/collections/default_collection/engines/career-brain-engine/servingConfigs/default_search",
         query=Query(text=structured_panel_audit_query),
         search_spec=AnswerQueryRequest.SearchSpec(
             search_params=AnswerQueryRequest.SearchSpec.SearchParams(
                 max_return_results=15,
                 filter='needs_review: ANY("false")',
             )
         ),
         query_understanding_spec=AnswerQueryRequest.QueryUnderstandingSpec(
             query_rephraser_spec=AnswerQueryRequest.QueryUnderstandingSpec.QueryRephraserSpec(
                 disable=False, max_rephrase_steps=3
             )
         ),
         answer_generation_spec=AnswerQueryRequest.AnswerGenerationSpec(
             model_spec=AnswerQueryRequest.AnswerGenerationSpec.ModelSpec(model_version="gemini-2.5-flash/answer_gen/v1"),
             prompt_spec=AnswerQueryRequest.AnswerGenerationSpec.PromptSpec(
                 preamble=panel_assessor_preamble_with_voice_and_ats_rules
             ),
             include_citations=True,
             ignore_low_relevant_content=True,
         ),
     )
     ```
  3. **Hop 3 — Unified Pack Allocation & Local Lineage Resolution:** Maps `Answer.citations` (`document_id` + character spans) back through local `database/.lineage_map.json` to display exact `source_lineage` filenames locally, coordinates non-overlapping evidence selection across Resume, Cover Letter, and KSC pack, and runs Proposal 2's `check_grounding` gate across all drafted sections.
* **Privacy Enforcement:** Raw `source_docs/` never leave disk; `source_lineage` hashes are resolved strictly locally after `AnswerQueryResponse` returns; Amber-tier output drafts are written only to the local task staging path (`~/Documents/job-pack` per [`config/ai_sharing_policy.json` L139](file:///Users/okgoogle13/Projects/Career-Brain/config/ai_sharing_policy.json#L139)).

### 4. Why This Exploits the Credit Uniquely
* **Multi-Step Query Rephrasing + Grounded Answer Synthesis under One SKU:** `ConversationalSearchService.answer_query()` with `max_rephrase_steps=3` automatically decomposes a complex multi-part Position Description query into up to 3 sub-queries against the Data Store, retrieves the union of top structured records, synthesizes an answer under your custom `PromptSpec.preamble`, and computes inline span citations—all billed as a single Discovery Engine Generative Answer request against the \$1,000 trial credit.

### 5. Failure Modes & Trade-offs
* **`PromptSpec.preamble` Length & Structural Constraints:** `AnswerGenerationSpec.PromptSpec.preamble` has tighter character limits (~4,000 chars) than raw Gemini system instructions and is optimized for grounded synthesis rather than deeply nested JSON schemas.
  * *Mitigation:* Use `answer_query` for the multi-hop Evidence Matrix, Gap Audit, and Panel Interrogation report (where inline citations and multi-query retrieval shine), and use Proposal 3 (`generate_grounded_content` with `InlineSource`) for the strict JSON `{"context", "action", "result"}` placeholder generation.
* **Requires Proposal 5's Data Store:** `answer_query` requires an active `SearchEngine` / `DataStore` resource in `discoveryengine.googleapis.com` (whereas Proposals 1–4 require zero cloud resources).

---

## Comparison Matrix

| Proposal | Core `discoveryengine` Primitive | Quick Win? | Setup Complexity | Zero-Persistence Compliance | Credit Burn Efficiency (\$1,000 Pool) | Impact on Application Quality |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| **1. Rosetta Cross-Encoder & Hungarian KSC Matcher** | `RankService.rank()` (`semantic-ranker-default@latest`) | **Yes (~2 hrs)** | **Very Low** (Stateless call in [`content_engine.py`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py); zero cloud infra) | **10/10** (100% ephemeral in-memory Green-tier payload) | **10/10** (~$0.006 per 6-KSC job pack; ~160,000 runs per \$1,000) | **High** (Eliminates substring misses & greedy story collisions across KSCs) |
| **2. Span-Exact Grounding, Chimera Detector & Auto-`[[NEEDS_REVIEW]]` Gate** | `GroundedGenerationService.check_grounding()` | **Yes (~2 hrs)** | **Very Low** (Stateless post-processor in [`content_engine.py`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py)) | **10/10** (100% ephemeral in-memory Green + task-scoped Amber payload) | **9.5/10** (~$0.005–$0.01 per full application audit) | **Very High** (Deterministically blocks ungrounded claims, metric inflation & cross-role blending) |
| **3. Stateless Inline Grounded CAR & Voice Scorer** | `GroundedGenerationService.generate_grounded_content()` (`InlineSource`) | **Yes (~3 hrs)** | **Low** (Replaces `google-genai` calls in [`content_engine.py`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py) & [`curate_narratives.py`](file:///Users/okgoogle13/Projects/Career-Brain/pipeline/curate_narratives.py)) | **10/10** (100% ephemeral `InlineSource` facts; no Data Store) | **9.5/10** (Moves 100% of direct-billed `GEMINI_API_KEY` calls onto the \$1,000 credit) | **High** (Enables full-vault voice scoring & grounded CAR rewrites at zero out-of-pocket cost) |
| **4. Cross-Pillar Semantic Metric Backfill Engine** | `RankService.rank()` + `check_grounding()` in [`inject_metrics.py`](file:///Users/okgoogle13/Projects/Career-Brain/pipeline/inject_metrics.py) | No (~1 day) | **Low–Medium** (Stateless Pass 4 in Phase 4 metric pipeline) | **10/10** (100% ephemeral in-memory batch pass over Green-tier JSONs) | **9/10** (~$0.25 per full-database metric backfill pass) | **High** (Rescues `needs_review: true` bullets using metrics buried in Pillar 2 STAR narratives) |
| **5. Zero-GCS Schema-Filtered Career Knowledge Store** | `DocumentService.import_documents` (`InlineSource`) + `SearchService.search` (`BoostSpec`, `FacetSpec`) | No (~2 days) | **Medium** (Requires provisioning 1 Structured Data Store; zero GCS buckets) | **8/10** (Stateful Green-tier index in Discovery Engine; `source_lineage` hashed locally; zero GCS) | **8.5/10** (Free inline indexing + pennies per faceted hybrid search) | **High** (Unlocks faceted competency coverage heatmaps, synonym expansion & metadata-boosted search) |
| **6. Multi-Hop PD Decomposer, Gap Analyzer & Panel Simulator** | `ConversationalSearchService.answer_query()` + `QueryRephraserSpec` + `AnswerGenerationSpec` | No (~3–4 days) | **High** (Builds on Proposal 5 Data Store + multi-stage orchestration) | **8/10** (Stateful Green-tier Data Store + local-only Amber staging in `~/Documents/job-pack`) | **8/10** (Multi-hop query expansion + Gemini synthesis covered by `Answer` SKU) | **Very High** (Full PD gap analysis, panel pushback simulation & cross-docResume/CL/KSC coherence) |

---

### Recommended Implementation Sequence
If you decide to implement these, the highest-leverage path is:
1. **Start with Proposals 1, 2, and 3 together** inside a single new helper module (`tools/discovery_client.py` wired into [`tools/content_engine.py`](file:///Users/okgoogle13/Projects/Career-Brain/tools/content_engine.py) and [`pipeline/curate_narratives.py`](file:///Users/okgoogle13/Projects/Career-Brain/pipeline/curate_narratives.py)). Because all three use **stateless inline RPCs** (`RankService.rank`, `GroundedGenerationService.check_grounding`, and `GroundedGenerationService.generate_grounded_content` with `InlineSource`), they require **zero cloud infrastructure setup**, **zero Data Stores**, and **zero storage footprint**, while immediately shifting your LLM generation and verification onto the \$1,000 `discoveryengine.googleapis.com` credit.
2. **Follow with Proposal 4** to enrich `database/career_history_enriched.json` across pillars.
3. **Add Proposals 5 & 6** once you want persistent faceted search (`query_brain.py`) and full Position Description panel simulation.