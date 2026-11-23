---
name: compliance-audit
description: "DSGVO, ISO 27001, C5, BSI: controls, evidence, gaps."
license: MIT
compatibility: Any organization and stack; framework catalogs are jurisdiction-neutral, evidence is technical or organizational.
metadata:
  author: Florian Zimmermeister (flozi00)
  version: "0.1.0"
---

# Compliance Audit

Compliance is a control system with evidence, not a document set. The
register is the single source of truth: every control, its framework
reference, its evidence, its owner, its status, and its next review. A
control without current evidence is open — not met. This skill covers
DSGVO/GDPR, ISO 27001, BSI C5, BSI IT-Grundschutz, and the EU AI Act, and
gives you the recurring loop that keeps the register honest.

## When to Use

- Before an audit or certification (ISO 27001, C5 attestation, BSI
  Grundschutz).
- Quarterly compliance review; annual management review.
- A new feature, vendor, or incident that touches personal data or
  security.
- Customer security questionnaires and tender requirements.
- When asked "are we compliant?" — answer from the register, never from
  opinion.

## The Register (core artifact)

One row per control. Template: `templates/compliance-register.md`.

| Field | Meaning |
|---|---|
| ID | Stable identifier, e.g. `DSGVO-32-ENC`, `ISO-A.8.24`, `C5-CRY-02` |
| Framework | DSGVO / ISO 27001 / C5 / BSI Grundschutz / AI Act |
| Requirement | One sentence: the actual obligation |
| Applicability | In scope, or not applicable with a reason |
| Evidence | What proves it, where it lives, dated |
| Owner | One accountable person |
| Status | `met` / `partial` / `open` / `risk-accepted` / `not-applicable` |
| Last verified | Date the evidence was last checked |
| Next review | Date |
| Gap | What is missing, linked to the gap plan |

Status vocabulary is strict: **met** requires current evidence; **partial**
means some evidence exists but a criterion is unmet; **open** means no
evidence; **risk-accepted** requires a named signer and a date.

## The Loop

1. **Scope** — which frameworks, systems, locations, and legal entities.
2. **Map** — controls from the framework catalogs into the register.
3. **Collect evidence** — verifiable, dated, reproducible.
4. **Assess** — met/partial/open against the requirement, not the
   intention.
5. **Gap plan** — owner, due date, or signed risk acceptance for every
   open item.
6. **Remediate and re-verify** — evidence updated, status changed.
7. **Report** — counts by status, open items, overdue reviews, trend.

Cadence: **quarterly** full pass; **trigger-based** partial passes (new
feature, new vendor, incident, org change); **annual** management review
and internal audit (ISO 27001 clauses 9.2/9.3).

## Framework Maps (condensed — full catalogs in `references/frameworks.md`)

### DSGVO / GDPR

- **Art. 5** principles: lawfulness, purpose limitation, minimization,
  accuracy, storage limitation, integrity/confidentiality, accountability.
- **Art. 6** lawful basis; **Art. 7** consent; **Art. 13/14** information
  duties.
- **Art. 15–22** data subject rights: access, rectification, erasure,
  restriction, portability, objection, automated decisions.
- **Art. 25** privacy by design/default; **Art. 28** processor agreements
  (AVV); **Art. 30** records of processing.
- **Art. 32** TOMs: pseudonymization/encryption, confidentiality/
  integrity/availability/resilience, rapid recovery, regular effectiveness
  review.
- **Art. 33/34** breach notification: 72 hours to the supervisory
  authority.
- **Art. 35** DPIA for high-risk processing; **Art. 37–39** DPO.
- **Art. 44+** international transfers (adequacy, SCCs).
- Retention and deletion defined per purpose and enforced technically.

### ISO 27001:2022

- **ISMS clauses 4–10**: context, leadership, planning, support,
  operation, performance evaluation, improvement.
- **Annex A: 93 controls in 4 themes** — A.5 Organizational (37),
  A.6 People (8), A.7 Physical (14), A.8 Technological (34).
- **Statement of Applicability (SoA)**: every Annex A control with
  applicability and justification.
- Risk assessment and treatment (6.1.2/6.1.3); internal audit (9.2);
  management review (9.3); corrective actions (10.1).
- 11 new controls in 2022: threat intelligence, cloud services, ICT
  readiness, physical monitoring, configuration management, information
  deletion, data masking, DLP, monitoring activities, web filtering,
  secure coding.

### BSI C5:2020

- **121 basic criteria in 17 domains**: OIS, SP, HR, AM, PS, OPS, IDM,
  CRY, COS, PI, DEV, SSO, SIM, BCM, COM, INQ, PSS — plus BC-01..BC-06
  general conditions.
- Audit types: **Type 1** (design) vs **Type 2** (design + effectiveness
  over a period).
- C5 is an attestation, not a certification; evidence is policies, logs,
  test reports, audit reports.

### BSI IT-Grundschutz

- **BSI-Standard 200-1** (ISMS), **200-2** (methodology), **200-3** (risk
  analysis).
- Three approaches: **Basis-Absicherung** (entry), **Standard-Absicherung**
  (normal protection need), **Kern-Absicherung** (core).
- **Schutzbedarf**: normal / hoch / sehr hoch per confidentiality,
  integrity, availability.
- **Kompendium modules** (APP, SYS, NET, INF, IND, …) with Basis/Standard
  requirements; high protection need requires additional risk analysis
  per 200-3.

### EU AI Act

- **4 risk levels**: prohibited (since 2 Feb 2025), high-risk
  (obligations from 2 Dec 2027), limited (transparency, Art. 50 from
  2 Aug 2026), minimal.
- High-risk obligations: risk management, data quality, documentation,
  transparency, human oversight, accuracy, cybersecurity, conformity
  assessment, registration.
- GPAI obligations since 2 Aug 2025.

## Evidence Discipline

- Evidence must be **verifiable, dated, reproducible**: config export,
  log sample, test result, signed policy, dated screenshot.
- "We think it's fine" is not evidence; "the policy says so" is not
  evidence of implementation.
- Evidence has an **expiry** — re-verify at the review cadence.
- Redact secrets and personal data in evidence artifacts.

## Gap Management

- Every open/partial control has: owner, due date, or a signed risk
  acceptance with a named signer.
- The gap plan is visible to management, not buried in a spreadsheet.
- Overdue items escalate; repeated deferral is itself a finding.

## Automation

- **Automate**: access reviews (export + diff), backup restore tests,
  dependency and secret scans, encryption config checks, log retention
  checks, patch status, certificate expiry.
- **Manual**: policies, training, management review, supplier
  assessments.
- Automate evidence collection where possible; the register links to the
  artifact.

## Pitfalls

- **Checkbox compliance** — documents exist, implementation doesn't.
- **Evidence theater** — screenshots without dates, policies without
  versions.
- **Stale register** — last verified older than the review cadence.
- **Scope creep** — every framework mapped to everything; scope
  explicitly and justify exclusions.
- **One-time project** — compliance decays without the loop.
- **Auditor-driven only** — fixing findings but not the system that
  produced them.

## Verification

- [ ] Register covers every in-scope framework control
- [ ] Every `met` has current, dated evidence
- [ ] Every open/partial has owner, due date, or signed risk acceptance
- [ ] Review cadence met; overdue items visible
- [ ] Evidence redacted (no secrets or personal data)
- [ ] Gap plan reviewed by management
- [ ] Automation covers what is deterministic
- [ ] Report shows counts by status and trend
