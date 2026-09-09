# Voice Authenticity Profile — Nishant Dougall

**Generated:** 2026-09-05
**Version:** 2026-09-05
**Status:** Career-Brain-local authority for job-application voice. Supersedes the anti-slop
section of `gem_system_prompt.md` (§6) and the ad-hoc `QUALITY BAR` in `tools/content_engine.py`.
**Scope:** Career-Brain only. This document is not sourced from, synchronised with, or governed
by `comms-hub-v2`. The four references to `~/comms-hub-v2/comms/voice-profile.md` below are
scholarly citations of one register constraint; they do not create an upstream dependency.
**Enforcement source:** `config/ats_rules.json` (machine-checkable floor — phrase lists and
spelling maps only).
**Runtime consumer:** `tools/generate_document.py` → `scan_voice_phrases()` (warn-only) and the
Australian-spelling substitution loop.

**Sources analysed:**

| Source | What it contributed |
|---|---|
| `database/ksc_curated.json` — 550 own-authored narratives across 54 source documents | All verbatim evidence, all credibility markers, all frequency counts |
| `database/career_history_enriched.json` — 105 role clusters / 1,017 bullets | Fact cross-checking for dates and titles |
| `database/Career_Brain_Knowledge.md` | DFFH/TGV inclusive-language glossary, action-verb bank |
| `~/comms-hub-v2/comms/voice-profile.md` | The `Formal` register constraint: outcome first, no apology openers, *"polished but keep my directness; don't sand it generic"* |
| `~/comms-hub-v2/comms/comms-examples.local.md` | Confirmed cover-letter voice was an **unfilled gap** — no prior worked example existed |
| `gem_system_prompt.md` §5 | Output format contracts (CAR/SAO word bands, bullet shape, CAO hook) — reused, not redefined |

**Machine-enforced subset:** `config/ats_rules.json` → `vocabulary.banned_phrases`,
`vocabulary.review_phrases`, `vocabulary.overclaim_terms`, `terminology.australian_spelling`.
Enforced by `scan_voice_phrases()` and the substitution loop in `tools/generate_document.py`.
**Change the config to change behaviour.** This document carries the judgement; the config
carries only the mechanically checkable floor.

***

## How to read this document

Three labels appear throughout and are never blurred:

| Label | Meaning |
|---|---|
| **VERBATIM CORPUS EXCERPT** | Unmodified text from `ksc_curated.json`, with its `source_lineage`. Wrapped in `<!-- voice-audit:ignore -->` markers so the self-audit does not flag preserved slop as a new violation. |
| **GENERATED REWRITE** | Authored for this profile from verified facts. **Nishant has never sent this text.** It is a style anchor, not content to paste. |
| **INFERRED PATTERN** | A generalisation drawn across the corpus. Not a quotable fact. |

***

## The core finding

**The corpus is strong evidence and weak style.** Two things are true at once:

1. Nishant's own writing contains passages no other candidate could produce — specific, honest,
   and occasionally startling. These are the differentiator.
2. The same documents are laced with generic filler, and 270 instances of US spelling.

`quality_tier` in `ksc_curated.json` cannot tell these apart. It scores length + STAR keyword
hits + a metric regex (`pipeline/curate_narratives.py:73-114`) — **there is no voice axis**. The
tier-1 / score-10 record is a 2018 cover letter containing *"mind blowing"* and *"like many
other Gen Y's"*. **Never select an exemplar by tier.** Select by the patterns below.

The sharpest illustration: two criteria responses in the **same document** on the **same day**
(`20240211 THH Peer Worker Role - Responses to Key Selection Criteria.pdf`). One is the best
writing in the corpus. The other is pure template. The difference is not skill — it is whether
he was recalling something that actually happened.

***

## Banned phrases (corporate slop)

Auto-flagged as `banned_phrase_detected` by `scan_voice_phrases()`. **Never auto-rewritten** —
a replacement needs an author's judgement about what the sentence was trying to say.

Counts are occurrences in Nishant's own 550 narratives.

| Phrase | Count | Found in | Replace with |
|---|---:|---|---|
| `excel in roles` / `excel in this role` | 23 | THH Peer Worker CL; cohealth CL | Name the task: *"Most of my work is one-to-one intake with people in crisis."* |
| `proven track record` | 5 | Master resume; TGD Peer Navigator | The record itself: *"Conducted over 400 client interviews between 2022 and 2024."* |
| `strong communication skills` | 5 | PLC THH KSC | The communication act: *"Prepared meeting agendas, documented decisions and actions, presented to stakeholders."* |
| `excellent communication skills` | 4 | headspace CL | As above |
| `ideal candidate` | 4 | THH Peer Worker KSC | Delete. Never assert the conclusion the panel is paid to reach. |
| `unique blend of` / `unique skillset` / `unique combination of` | 7 | Launch IAP CL; ASRC CL | Name both halves plainly: *"Nine years in banking project delivery, four in community services."* |
| `self-starter` | 2 | Master resume | *"Worked on-site alone for six months, escalating risks to my manager weekly."* |
| `synergy` | 2 | PLC THH KSC | *"…balancing autonomous work with the team's reporting rhythm."* |
| `team player` | 1 | Master resume | Delete, or give the team fact. |
| `results-driven`, `dedicated professional`, `track record of delivering`, `wealth of experience`, `hit the ground running`, `passion for excellence`, `innovative disruptor`, `perfect fit` | 0 | — | Preventive. **`dedicated professional` and `track record of delivering` are currently emitted by `tools/content_engine.py:640`** — the generator produces slop this profile bans. See *Known gaps*. |

### Review phrases (context-dependent)

Flagged as `review_phrase_flagged` — a **different warning class**, because these are sometimes
right. A human decides. Highest-volume offenders in the corpus:

| Phrase | Count | Verdict |
|---|---:|---|
| `responsible for` | 41 | Almost always weak. Swap for the action verb — the bank is in `Career_Brain_Knowledge.md` Part 2. |
| `passionate about` / `passion for` | 56 | The single most overused construction in the corpus. Passion asserted is worthless; passion demonstrated by an unpaid four-year volunteering record is not. Cut the word, keep the record. |
| `confident that` / `strong candidate` / `I believe I` | 31 | Self-assessment addressed to a panel whose job is assessment. Cut. |
| `demonstrated ability` / `demonstrated understanding` | 20 | Fine as a *criterion heading* quoted from the PD. Slop when it opens your own answer. |
| `all walks of life` | 11 | Cliché. Name the actual cohorts. |
| `extensive experience` | 5 | Quantify it or cut it. |
| `dynamic` | 5 | All five are *"dynamic environments"*. Whole-word matching, so **group dynamics / family dynamics / power dynamics do not trip this.** |
| `spearheaded` | 2 | Corporate-register verb. `led`, `set up`, `ran`. |

***

## Authentic voice patterns

### Pattern 1: The named-service chain

**Description:** The strongest passages follow a referral or escalation all the way through to a
named service and a dated outcome. Generic writing stops at *"I referred the client to appropriate
supports."* Nishant's best writing names the team, the hospital, the suburb, and what happened next.

**Exemplar — VERBATIM CORPUS EXCERPT** (`20240211 THH Peer Worker Role - Responses to Key Selection Criteria.pdf`)

<!-- voice-audit:ignore-start -->
> An example of my empathic nature and ability to show compassion occurred during a recent
> interview with a client who wasn't talking or engaging very much and initially only requested
> basic minimal food support. By actively listening, and by creating a space free of judgement
> and discrimination, and by asking the right questions, the client eventually broke down and
> disclosed that they were experiencing psychosis and suicidal ideation and worried about they
> might harm themselves. […] as per DVCS policy and process, I helped him to call the Crisis
> Assessment Team at Austin Health in Heidelberg. Based on the assessment completed by this
> team, the client was admitted to the psychiatric ward of the Austin as an in-patient the
> following week.
<!-- voice-audit:ignore-end -->

**Why this works:**
- Names the escalation pathway precisely: **Crisis Assessment Team, Austin Health, Heidelberg**.
- Cites the governing process (*"as per DVCS policy and process"*) — signals he works inside a framework rather than freelancing.
- The outcome is external and verifiable, not self-reported: an admission, with a timeframe.
- Describes his role accurately — *"I helped him to call"*, not *"I assessed"*. No clinical over-claim in a genuinely clinical situation.
- Starts from an ordinary request (food support) and shows what listening surfaced. That is the actual skill.

**Apply this by:** every escalation, referral or liaison must name the receiving service. If the
service name is not in the source record, write `[[NEEDS_REVIEW: which service?]]` — do not
write *"relevant support services"*.

***

### Pattern 2: Lived experience as method, not decoration

**Description:** Weak writing asserts lived experience as a credential. Nishant's strongest
passage uses it as a *deliberate practice decision*, then follows it through to a service design
proposal. Observation → judgement call → disclosure → rapport → structural suggestion.

**Exemplar — VERBATIM CORPUS EXCERPT** (`20240211 THH Peer Worker Role - Responses to Key Selection Criteria.pdf`)

<!-- voice-audit:ignore-start -->
> A memorable example was a group involving a participant who was a person of colour, with a
> similar ethnic background to me. They were not contributing as much as the white participants,
> and my instincts were telling me it would be helpful if I shared my own experiences of racism
> and discrimination in the queer community. Opening up about my own experience generated an
> immediate response. By showing empathy and compassion in regards to their circumstances, I was
> able to establish rapport and trust. The outcome was the participant feeling less isolated,
> and at a later meeting, I was able suggest a potential intervention in the form of a group
> specifically for queer M2Ms (men who have sex with men) of Asian backgrounds.
<!-- voice-audit:ignore-end -->

**Why this works:**
- Names what he noticed and *why it mattered* — differential participation along racial lines in a queer group. Most candidates cannot see this, let alone write it.
- The self-disclosure is framed as a **clinical-adjacent judgement**, not an identity statement.
- Ends at service design, not feelings. He proposed a new group.
- Correct sector register throughout: *participant*, *M2M*, *men who have sex with men*.
- Uses `[INFERRED PATTERN]` caution: `they/them` for the participant, which is also his own pronoun set.

**Apply this by:** never write *"my lived experience allows me to connect with clients."* Write
the moment the lived experience changed a decision, and what changed as a result.

***

### Pattern 3: Honest self-assessment

**Description:** The most distinctive feature of Nishant's writing — and the one no template
produces — is admitting a mistake and what he learned. It reads as supervision-ready.

**Exemplar — VERBATIM CORPUS EXCERPT** (`20240211 PLC THH Support Worker Role - Responses to Key Selection Criteria.pdf`)

<!-- voice-audit:ignore-start -->
> Setting and keeping boundaries was a hard lesson for me to learn! Several clients have asked if
> I wanted to be friends with them and asked for my number. It took this happening for me to
> realise that it never should have gotten to this point and that I had overshared and been more
> of a friend to the clients rather than being professional.
<!-- voice-audit:ignore-end -->

**Why this works:**
- Answers a boundaries criterion with evidence of *having had a boundary problem and resolved it*, which is far more convincing than asserting good boundaries.
- Signals supervision-readiness: someone who will name a problem before it becomes an incident.
- Unmistakably a real person.

**Apply this by:** use sparingly and deliberately — **one** honest-limitation passage per
application, placed against a criterion about reflective practice, supervision, boundaries or
self-care. It is a strength there and a liability against a criterion about competence.
Always close the loop: what changed in practice afterwards. The excerpt above does not close it
— that is its weakness, and the rewrite in `ksc-exemplars.local.md` fixes it.

**Register note:** drop the exclamation mark. `~/comms-hub-v2/comms/voice-profile.md` puts CVs
and cover letters in the **Formal** category — *"polished but keep my directness"*. Directness
survives; the exclamation mark does not.

***

### Pattern 4: Corporate past as transferable mechanics

**Description:** The pivot is credible when the corporate experience is described as concrete
mechanics that obviously transfer, and hollow when described as abstract qualities.

**Exemplar — VERBATIM CORPUS EXCERPT** (`20240211 PLC THH Support Worker Role - Responses to Key Selection Criteria.pdf`)

<!-- voice-audit:ignore-start -->
> I was the lead analyst on a project centred on significantly upgrading the Finance team's
> accounting software. A large part of my role was developing a project plan, which quantified
> the effort and time required to complete the necessary tasks […] I had to liaise with our tech
> suppliers and a variety of internal stakeholders and create a spreadsheet containing all of the
> required actions, who was responsible for each task, and when they were due to be completed.
> The planning document I drafted enabled the project manager to identify and plug resource gaps,
> get approval to proceed with the project, and, once in flight, track our progress.
<!-- voice-audit:ignore-end -->

**Contrast — VERBATIM CORPUS EXCERPT** (`20241022 Cover Letter ASRC.pdf`, spacing damaged in source)

<!-- voice-audit:ignore-start -->
> While my background in finance may seem unrelated, it was there that I honed my organisational
> skills, ability to manage multiple priorities, and talent for effectiv[e]…
<!-- voice-audit:ignore-end -->

**Why the first works:** named organisation (ITN), named artefact (the project plan), named
mechanism (who / what / when), named consequence (resource gaps identified, approval obtained).
The second asserts three abstractions and apologises for the background in the first clause.

**Apply this by:** never open a pivot sentence with *"While my background in finance may seem
unrelated"* — `~/comms-hub-v2/comms/voice-profile.md` is explicit that apology openers *"read as
a reliability flag."* State the transferable mechanic and let the reader draw the inference.

***

### Pattern 5: The pivot stated once, with a point of view

**Description:** The career change needs one direct sentence with an actual position in it — not
a generational cliché, and not repeated in every paragraph.

**Exemplar — VERBATIM CORPUS EXCERPT** (`20240211 PLC THH Support Worker Role - Responses to Key Selection Criteria.pdf`)

<!-- voice-audit:ignore-start -->
> It took me years to realise that the reason I was deeply unhappy working in the corporate
> sector, despite being good at my job […] was because, ultimately, the underlying purpose for
> everything I was doing, was to maximise the wealth of shareholders of financial institutions,
> which was increasing the already massive wealth gap between the rich and the poor.
<!-- voice-audit:ignore-end -->

**Contrast — VERBATIM CORPUS EXCERPT** (`20180808 Cover Letter - Bank Australia.pdf`)

<!-- voice-audit:ignore-start -->
> However, at this point in my career, like many other "Gen Y's", I have reevaluated my life and
> want to make significant changes in order to help create a brighter future for generations to
> come.
<!-- voice-audit:ignore-end -->

**Why the first works:** it has a **thesis** — that his labour was increasing the wealth gap.
A panel can agree or disagree with it, which is what makes it memorable. The second could have
been written by anyone about any job.

**Apply this by:** one pivot sentence, once, in the opening. Trim the corporate self-criticism
(*"despite being good at my job"* reads defensive). Do not restate the pivot in the closing.

***

### Pattern 6: Quantities that survive scrutiny

**Description:** The corpus has a small set of numbers that recur consistently and are therefore
safe. It also has one that drifts — and the drift is the kind of thing a reference check catches.

**Verified and consistent:**

| Claim | Occurrences | Role / period |
|---|---:|---|
| over 400 client interviews | 12 | Diamond Valley Community Support, 03/2022–10/2024 |
| 100+ clients, sex-on-premises venue outreach | 2 | Thorne Harbour Health, 12/2018–11/2019 |
| 30+ participants, peer support group | 2 | Thorne Harbour Health, 12/2019–11/2020 |
| 20 former international students, focus groups | 2 | headspace National, 03/2024–10/2024 |
| 50-page research findings report | 1 | headspace National |

**INFERRED PATTERN — the food-package drift.** One resume says *"Delivered over 1000 food
packages"* (first person). Four other records say *"**Our team** delivered over 2000 packages to
Positive Living Centre clients."* These are different claims: an individual figure and a team
figure. Using "2000" in the first person converts a team achievement into a personal one.

**Apply this by:** use **1000, first person** for his own deliveries, or **2000 with "our team"**
attributed — never 2000 in the first person. Where the record cannot settle it, write
`[[NEEDS_REVIEW: individual vs team figure]]`. Attribution errors are the cheapest way to lose a
reference check.

***

## Sector register (Australian community services)

**Use these terms:**

| Use | Not |
|---|---|
| key selection criteria / KSC / Statement of Claims | competency questions |
| position description (PD) | job description |
| organisation | company |
| sector | industry |
| alcohol and other drugs (AOD) | substance abuse |
| people who use drugs | drug users, addicts |
| person experiencing homelessness | homeless person |
| lived and living experience | personal experience |
| participant / client / consumer — **match the service**: *consumer* in mental health, *participant* in NDIS, *client* in emergency relief and housing | one term used everywhere |
| Aboriginal and Torres Strait Islander; First Nations | indigenous (lowercase), ATSI |
| Naarm (for Melbourne) — see *Identity disclosure* below | — |
| headspace (lowercase h — the organisation styles it so) | Headspace |
| cohealth (lowercase c) | CoHealth |
| trauma-informed, person-centred, strengths-based, harm reduction | therapeutic |
| SCHADS Award; MARAM; Child Safe Standards; NDIS Practice Standards; DFFH | generic "compliance frameworks" |
| EthicalJobs | Seek (for sector roles) |

**Australian English is auto-corrected**, not merely requested: 74 explicit word mappings in
`config/ats_rules.json` → `terminology.australian_spelling`, applied case-preservingly. The
corpus contained **270 US-spelling instances** — `centralized` ×39, `utilizing` ×23,
`organization*` ×34, `marginalized` ×21, `prioritize*` ×31.

> **`program` is correct Australian usage in this sector and is deliberately excluded from the
> map.** It must never become `programme`. This is asserted by
> `test_program_never_mapped_to_programme`. Note that
> `pipeline/audit_and_repair_database.py` currently instructs an LLM to use *"programme"* — that
> is wrong for Australian community services and is logged under *Known gaps*.

### Accurate role descriptors

**Verified from the corpus — safe to claim:**

- Community Support Worker, Diamond Valley Community Support (03/2022 – 10/2024)
- Peer Support Group Facilitator, Thorne Harbour Health (12/2019 – 11/2020)
- Sex-on-premises Venue Outreach volunteer, Thorne Harbour Health (12/2018 – 11/2019)
- COVID-19 food delivery volunteer, Positive Living Centre / THH (03/2020 – 09/2020)
- Multicultural Practice Team intern, headspace National (03/2024 – 10/2024)
- Accredited **SMART Recovery Facilitator** (training completed)
- Corporate: Senior Business Analyst / Junior Project Manager — Royal Bank of Scotland, Coutts & Co, NAB, ITN
- Diploma of Community Services; Master of Finance; Bachelor of Business

**Do NOT claim** (flagged as `overclaim_term_flagged`, warn-only, human resolves each hit):
`therapist` · `psychotherapist` · `counsellor` · `psychologist` · `psychiatrist` ·
`social worker` · `clinician` · `case manager` · `registered nurse` · `clinical supervision` ·
`therapeutic intervention` · `provided/delivered therapy`

> **A real over-claim exists in the corpus.** One resume lists the Diamond Valley role as
> *"Client Social Worker"*. His verified title is **Community Support Worker**. *Social worker*
> is a protected professional title requiring an AASW-accredited qualification he does not hold.
> This must be corrected wherever it appears.

Two further corrections found:
- *"Facilitated a **therapeutic** program for LGBTIQ+ individuals"* (master resume) → use the
  wording his own harm-reduction resume already uses: *"peer support group using a harm
  reduction framework."*
- *"SMART Recovery **Facilitor**"* → **Facilitator** (typo in source).

**Warn-only, never auto-rewritten** — because these terms legitimately appear when quoting a
position description or describing a colleague (*"worked alongside social workers and
clinicians"* is accurate and fine).

***

## Identity disclosure — opt-in, per application

This file is committed to a repository with a **public** remote, so it does not enumerate
Nishant's personal details. The disclosure register — the actual list of facts, tiered by
sensitivity — lives in `docs/voice/ksc-exemplars.local.md`, which is git-ignored. This section
governs *how* disclosure decisions are made; that file holds *what* may be disclosed.

**Nothing in the register is ever auto-inserted.** It is an *availability register* — facts that
exist and may be deployed — and the decision is Nishant's alone, per application.

Disclosure sensitivity runs in four tiers. Each tier's threshold is higher than the last:

| Tier | Category | Threshold for use |
|---|---|---|
| 1 | Pronouns, First Nations place names | Organisation signals the same convention in its own materials; used consistently within a document |
| 2 | Community membership and cultural identity | Criterion asks for lived experience or cultural competence, or the role is identified |
| 3 | Lived experience of a service system (AOD, housing, FDV) | The criterion's substance *is* that service system — never as general colour |
| 4 | Protected health information — including any HIV-related status and any named clinical diagnosis | An **identified peer role in that exact domain**, and nowhere else. For a general consumer or lived-experience criterion, the *fact* of psychosocial disability carries the claim; the diagnostic list adds nothing and cannot be withdrawn once sent. |

**Rule:** disclose the minimum that makes the claim land, at the level of specificity the
criterion actually asks for. Following `~/comms-hub-v2/comms/voice-profile.md`: *"Getting the
wording wrong I can edit; getting the disclosure level wrong I can't."* If a template would
pre-fill any of the above, it is wrong — leave the slot empty and ask.

***

## Credibility markers (what makes him stand out)

Ranked by how rare they are in an applicant pool:

1. **Sees and acts on differential participation.** Noticing a POC participant contributing less
   than white participants in a queer group, and proposing a targeted group in response.
   Practically no applicant writes this.
2. **Names escalation pathways precisely.** Crisis Assessment Team, Austin Health, Heidelberg —
   with the governing policy cited and the outcome stated.
3. **Admits a boundary failure and what changed.** Supervision-ready honesty.
4. **Genuinely unusual pairing, evidenced on both sides.** Nine years of banking project
   delivery (RBS, Coutts & Co, NAB, ITN) *and* four years in community services — with concrete
   mechanics from both, not just the claim.
5. **Sustained unpaid commitment.** Multiple years volunteering at Thorne Harbour Health
   *before* and alongside paid work — including through the pandemic.
6. **Was a client of the service he then worked in.** Re-Wired Program participant → peer work
   via Re-Wired v2.0. Rare, and directly relevant to peer roles.
7. **Consistent volumes across four years of documents.** 400+ interviews, 100+ outreach
   clients, 30+ group participants, 20 focus group participants. They do not inflate over time.
8. **Formal research output.** Thematic analysis and a 50-page findings report at headspace
   National, informing national resource design.

***

## Anti-slop verification checklist

Before any job application content is submitted:

1. [ ] `scan_voice_phrases()` returns no `banned_phrase_detected` warnings.
2. [ ] Every `review_phrase_flagged` warning has been read and consciously accepted or rewritten.
3. [ ] Every `overclaim_term_flagged` warning resolved — the term is quoted from the PD or
       describes someone else, never a claimed title.
4. [ ] Every claim carries a number, a named service, or a specific example. No abstract
       virtue paragraphs.
5. [ ] Every referral or escalation names the receiving service.
6. [ ] Role descriptors match the verified list. No *social worker*, no *therapeutic*.
7. [ ] Quantities match the verified table; the 1000/2000 package distinction is respected.
8. [ ] Australian English throughout (auto-applied, but confirm proper nouns were not corrupted
       — see *Known gaps*).
9. [ ] First person correct: **resume — no "I"**; cover letter and KSC — first person expected.
10. [ ] Tense correct: active past for history, present for current roles.
11. [ ] Identity disclosure is a deliberate decision for *this* application, not a default.
12. [ ] No apology opener; no *"I am confident that I am the ideal candidate"* closer.
13. [ ] Any inferred detail is wrapped in `[[NEEDS_REVIEW: …]]`.
14. [ ] At most one honest-limitation passage, and it closes the loop.

***

## Style anchors

Full before/after exemplars live in three companion files. They are **git-ignored** — they carry
verbatim personal disclosure, contact details, and referee information:

- `docs/voice/ksc-exemplars.local.md` — 5 KSC claims
- `docs/voice/cover-letter-exemplars.local.md` — 3 CAO hooks + 1 full letter
- `docs/voice/resume-bullet-exemplars.local.md` — 8 bullets

They are **style anchors, not content to paste.** Every "after" is a GENERATED REWRITE.

### The reference pair — concrete vs abstract

Both come from the same document (`20240211 THH Peer Worker Role - Responses to Key Selection
Criteria.pdf`), written on the same day, for the same application. They are the clearest
demonstration in the whole corpus that the difference is evidence, not effort or polish.

| | Criterion 5 — **concrete** | Criterion 6 — **abstract** |
|---|---|---|
| `ksc_curated.json` index | `[1243]` (and `[1285]`, a duplicate) | `[1244]` (and `[1288]`) |
| `quality_tier` | **1** | **3** |
| Length | 379 words | 171 words |
| Closes on | A named service, a decision, an outcome | *"I am confident that my passion, skills, and experience make me the ideal candidate."* |

Criterion 5 names the Crisis Assessment Team at Austin Health, states what was escalated and
why, and lets the reader judge the judgement. Criterion 6 asserts the same competence and
offers nothing checkable — it is the single most useful negative exemplar in the corpus,
because it is not badly written. It is fluent, warm, and entirely unfalsifiable.

**Use them as a paired test.** Draft a claim, then ask which of the two it resembles. If a
hiring manager could not disagree with a sentence, it is a criterion-6 sentence — cut it or
attach evidence to it.

> **Note on the tier tags.** Criterion 6 was re-tiered 2 → 3 by hand on 2026-09-05. This does
> not survive a Phase 3 re-run: `pipeline/curate_narratives.py` recomputes `quality_tier` from
> length, STAR keywords and a metric regex, and resets `vetted` to `False` on every record. The
> designation above is the durable record; the JSON tag is not. See Known gaps.

***

## Known gaps

1. **The generator emits slop this profile bans.** `tools/content_engine.py:640`
   (`generate_professional_summary`) produces *"Dedicated professional … track record of
   delivering … unique combination of …"* — three banned phrases in one template. Likewise
   `generate_closing_paragraph` (`:1112`) and `generate_bridge_paragraph` (`:454`). These are
   hardcoded f-strings and were **deliberately left untouched** in this pass. Until they are
   templated from this profile, every generated document will trip its own validator.
2. **`_RECRUITER_SYSTEM_PROMPT` (`tools/content_engine.py:656`) is a separate voice spec** with
   a *different* banned list. It should be composed from this profile. Deferred.
3. **`curate_narratives.py` remains voice-blind.** Tier is length + STAR keywords + a metric
   regex. Re-tiering 1,346 narratives is a Gate 3 change and out of scope here.
4. **`pipeline/audit_and_repair_database.py` instructs an LLM to use *"programme"*** — wrong for
   Australian community services. One-word fix behind Gate 3; reported, not applied.
5. **Spelling substitution can corrupt proper nouns.** *World Health Organization* becomes
   *World Health Organisation*. Whole-word case-preserving substitution cannot see proper nouns.
   Check organisation names in the final document.
6. **Slop by paraphrase is not detectable.** The config catches fixed strings only. A fresh
   generic sentence passes every automated check. That is what the patterns above are for.
7. **The raw source vault is gone.** `source_docs/` is git-ignored and the original ETL source
   tree no longer exists on disk. All evidence here comes from extracted `full_text` in
   `ksc_curated.json`, which carries PDF line-wrap damage. Some excerpts are lightly
   re-spaced for readability; none are reworded.
