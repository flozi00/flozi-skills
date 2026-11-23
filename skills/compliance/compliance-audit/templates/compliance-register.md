# Compliance Register

Single source of truth for control status. One row per control. Copy this
file per scope (organization, product, deployment) and keep it under
version control.

## Status vocabulary

| Status | Meaning | Requires |
|---|---|---|
| `met` | Requirement fulfilled | Current, dated evidence |
| `partial` | Some evidence exists, a criterion is unmet | Gap description + owner |
| `open` | No evidence | Owner + due date or signed risk acceptance |
| `risk-accepted` | Deliberately not implemented | Named signer + date + rationale |
| `not-applicable` | Out of scope | Written justification |

## Register

| ID | Framework | Requirement | Applicability | Evidence | Owner | Status | Last verified | Next review | Gap |
|---|---|---|---|---|---|---|---|---|---|
| DSGVO-32-ENC | DSGVO | Encryption of personal data at rest and in transit (Art. 32(1)(a)) | In scope | `docs/evidence/encryption-config-2026-11.pdf` | CTO | met | 2026-11-01 | 2027-02-01 | — |
| DSGVO-33-BREACH | DSGVO | Breach notification process within 72 h (Art. 33) | In scope | `docs/evidence/incident-runbook-v3.pdf` | DPO | partial | 2026-10-15 | 2027-01-15 | Tabletop exercise missing |
| ISO-A.8.24 | ISO 27001 | Use of cryptography: policy + key management | In scope | `docs/evidence/crypto-policy-v2.pdf` | CTO | met | 2026-11-01 | 2027-02-01 | — |
| ISO-A.5.7 | ISO 27001 | Threat intelligence process | In scope | — | CISO | open | — | 2026-12-15 | No process defined |
| C5-CRY-02 | C5 | Transport encryption for all connections | In scope | `docs/evidence/tls-scan-2026-11.txt` | Platform | met | 2026-11-05 | 2027-02-05 | — |
| C5-OPS-08 | C5 | Regular testing of data backup recovery | In scope | `docs/evidence/restore-test-2026-Q3.pdf` | Platform | met | 2026-09-30 | 2026-12-31 | — |
| BSI-APP.3.1 | BSI Grundschutz | Web application: secure configuration | In scope | `docs/evidence/hardening-checklist.pdf` | Platform | partial | 2026-10-01 | 2027-01-01 | CSP not enforced |
| AIACT-50 | AI Act | Transparency: users informed they interact with AI | In scope | `docs/evidence/ui-disclosure.png` | Product | met | 2026-11-10 | 2027-02-10 | — |
| ISO-A.7.4 | ISO 27001 | Physical security monitoring | Not applicable | — | — | not-applicable | 2026-11-01 | 2027-11-01 | Fully remote, no own premises |

## Gap plan

| Gap | Control | Owner | Due | Risk acceptance (signer, date) | Status |
|---|---|---|---|---|---|
| Tabletop exercise for breach response | DSGVO-33-BREACH | DPO | 2026-12-31 | — | in progress |
| Threat intelligence process | ISO-A.5.7 | CISO | 2027-01-31 | — | open |
| CSP not enforced | BSI-APP.3.1 | Platform | 2026-12-15 | — | in progress |

## Review log

| Date | Reviewer | Scope | Result |
|---|---|---|---|
| 2026-11-15 | CTO | Full pass Q4 | 6 met, 2 partial, 1 open, 1 n/a |
