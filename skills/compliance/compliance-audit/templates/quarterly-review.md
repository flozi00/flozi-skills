# Quarterly Compliance Review

Run this checklist every quarter. Record the date, reviewer, and result in
the register's review log. A "no" is a finding — it gets an owner and a
due date, not a shrug.

## 1. Register hygiene

- [ ] Every in-scope framework control has a row
- [ ] Every `met` row has evidence dated within the review period
- [ ] Every `partial`/`open` row has an owner and a due date or signed
      risk acceptance
- [ ] `not-applicable` rows have a written justification
- [ ] No row has `next review` in the past without a re-verification

## 2. DSGVO

- [ ] Records of processing (Art. 30) current — new features/vendors added
- [ ] Processor agreements (Art. 28) exist for every processor, incl.
      sub-processors
- [ ] Data subject rights: access/erasure/portability tested end-to-end
      this quarter
- [ ] Retention periods defined and technically enforced (deletion jobs
      verified)
- [ ] Breach process: contact list current, 72 h path tested or tabletop
      done
- [ ] DPIA done for new high-risk processing
- [ ] International transfers documented (adequacy/SCCs)
- [ ] TOMs (Art. 32) reviewed for effectiveness, not just existence

## 3. ISO 27001

- [ ] Risk register updated; new risks assessed and treated
- [ ] Statement of Applicability current (new controls justified)
- [ ] Internal audit performed per plan (clause 9.2)
- [ ] Management review held with minutes (clause 9.3)
- [ ] Corrective actions from last audit closed or tracked
- [ ] Access reviews done (joiners/movers/leavers)
- [ ] Supplier assessments current for critical suppliers
- [ ] Incident log reviewed; lessons applied

## 4. BSI C5 (if cloud service in scope)

- [ ] All 17 domains have evidence owners
- [ ] Logging/monitoring evidence current (OPS-10..17)
- [ ] Backup restore test done this period (OPS-08)
- [ ] Vulnerability management: scans run, findings tracked (OPS-18..23)
- [ ] Access rights reviewed (IDM-05)
- [ ] Encryption/key management evidence current (CRY-01..04)
- [ ] Incident management tested (SIM-01..05)
- [ ] BC/DR plan tested (BCM-04)

## 5. BSI IT-Grundschutz (if applicable)

- [ ] Schutzbedarf assessment current per asset/process
- [ ] Kompendium modules mapped; Basis/Standard requirements tracked
- [ ] High protection need: risk analysis per 200-3 done
- [ ] Measures from the security concept implemented or risk-accepted

## 6. EU AI Act (if AI features in scope)

- [ ] AI system inventory: every feature classified by risk level
- [ ] Prohibited practices checked (none in use)
- [ ] High-risk: conformity assessment, documentation, human oversight
      in place
- [ ] Transparency duties implemented (AI disclosure, deepfake marking)
- [ ] GPAI obligations tracked for used models

## 7. Technical evidence spot-check

- [ ] Secret scan of repo and history: clean
- [ ] Dependency audit: no unpatched critical/high CVEs
- [ ] Backup restore test: successful, documented
- [ ] Access review export: no orphaned accounts, no excess privileges
- [ ] Certificate expiry: nothing expiring within 30 days
- [ ] Log retention: matches policy, deletion verified

## 8. Reporting

- [ ] Counts by status per framework (met/partial/open/risk-accepted/n-a)
- [ ] Trend vs. last quarter (improving/stable/degrading)
- [ ] Overdue items listed with escalation
- [ ] Report shared with management; decisions recorded
