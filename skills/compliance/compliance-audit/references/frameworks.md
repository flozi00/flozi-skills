# Framework Catalogs (condensed)

Official sources first; this file is a working index, not a substitute for
the normative text.

## DSGVO / GDPR

Official: https://eur-lex.europa.eu/eli/reg/2016/679/oj (German:
https://dsgvo-gesetz.de)

| Ref | Obligation |
|---|---|
| Art. 5 | Principles: lawfulness, purpose limitation, minimization, accuracy, storage limitation, integrity/confidentiality, accountability |
| Art. 6 | Lawful basis for processing |
| Art. 7 | Conditions for consent |
| Art. 13/14 | Information to the data subject |
| Art. 15 | Right of access |
| Art. 16 | Right to rectification |
| Art. 17 | Right to erasure |
| Art. 18 | Right to restriction |
| Art. 20 | Right to data portability |
| Art. 21 | Right to object |
| Art. 22 | Automated individual decision-making |
| Art. 25 | Data protection by design and by default |
| Art. 28 | Processor (AVV) |
| Art. 30 | Records of processing activities |
| Art. 32 | Security of processing (TOMs) |
| Art. 33 | Breach notification to authority — 72 hours |
| Art. 34 | Communication of a breach to the data subject |
| Art. 35 | Data protection impact assessment (DPIA) |
| Art. 37–39 | Data protection officer |
| Art. 44–49 | International transfers (adequacy, SCCs, BCRs) |

## ISO/IEC 27001:2022

Official: https://www.iso.org/standard/27001

- Clauses 4–10: ISMS requirements (context, leadership, planning,
  support, operation, performance evaluation, improvement).
- Annex A: 93 controls in four themes:
  - A.5 Organizational — 37 controls (5.1–5.37)
  - A.6 People — 8 controls (6.1–6.8)
  - A.7 Physical — 14 controls (7.1–7.14)
  - A.8 Technological — 34 controls (8.1–8.34)
- Statement of Applicability (SoA) required for every Annex A control.
- 11 new controls vs. 2013: 5.7 threat intelligence, 5.23 cloud services,
  5.30 ICT readiness, 7.4 physical security monitoring, 8.9 configuration
  management, 8.10 information deletion, 8.11 data masking, 8.12 DLP,
  8.16 monitoring activities, 8.23 web filtering, 8.28 secure coding.

## BSI C5:2020

Official: https://www.bsi.bund.de/EN/Themen/Unternehmen-und-Organisationen/Informationen-und-Empfehlungen/Cloud-Computing/cloud-computing_node.html

121 basic criteria in 17 domains:

| Code | Domain |
|---|---|
| OIS | Organization of Information Security |
| SP | Security Policies |
| HR | Human Resources |
| AM | Asset Management |
| PS | Physical Security |
| OPS | Operations Security |
| IDM | Identity and Access Management |
| CRY | Cryptography and Key Management |
| COS | Communication Security |
| PI | Portability and Interoperability |
| DEV | Development and Procurement |
| SSO | Supply Chain / Service Providers |
| SIM | Security Incident Management |
| BCM | Business Continuity Management |
| COM | Compliance |
| INQ | Investigation Requests |
| PSS | Product Safety and Security |

Plus BC-01..BC-06 (general conditions of the cloud service). Audit types:
Type 1 (design) and Type 2 (design + effectiveness over a period).

## BSI IT-Grundschutz

Official: https://www.bsi.bund.de/DE/Themen/Unternehmen-und-Organisationen/Standards-und-Zertifizierung/IT-Grundschutz/it-grundschutz_node.html

- BSI-Standard 200-1: ISMS requirements.
- BSI-Standard 200-2: IT-Grundschutz methodology — Basis-Absicherung,
  Standard-Absicherung, Kern-Absicherung.
- BSI-Standard 200-3: risk analysis for high/sehr hoch protection need.
- Schutzbedarf: normal / hoch / sehr hoch, assessed per confidentiality,
  integrity, availability.
- IT-Grundschutz-Kompendium: modules (APP applications, SYS systems, NET
  networks, INF infrastructure, IND industrial IT, …) with Basis and
  Standard requirements.

## EU AI Act (Regulation (EU) 2024/1689)

Official: https://eur-lex.europa.eu/eli/reg/2024/1689/oj

| Risk level | Consequence | Timeline |
|---|---|---|
| Unacceptable / prohibited | Banned practices (social scoring, manipulative systems, real-time remote biometric ID for law enforcement without justification, …) | Since 2 Feb 2025 |
| High-risk | Conformity assessment, risk management, data quality, documentation, transparency, human oversight, accuracy, cybersecurity, registration | Obligations from 2 Dec 2027 (product AI: 2 Aug 2028) |
| Limited | Transparency duties (AI interaction disclosure, deepfake marking, emotion recognition notice) | Art. 50 from 2 Aug 2026 |
| Minimal | No special obligations; voluntary codes | — |

GPAI (general-purpose AI) obligations apply since 2 Aug 2025.
