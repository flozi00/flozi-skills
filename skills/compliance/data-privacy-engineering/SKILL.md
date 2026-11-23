---
name: data-privacy-engineering
description: "PII inventory, retention, export/erasure, anonymization."
license: MIT
compatibility: Any stack with persistent storage; needs schema access, a data map, and authority to change retention and deletion paths.
metadata:
  author: Florian Zimmermeister (flozi00)
  version: "0.1.0"
---

# Data Privacy Engineering

Privacy obligations become real at the storage layer: a field exists, a
copy exists, a job deletes it or does not. This skill is the engineering
side of DSGVO/GDPR — inventory, minimization, pseudonymization,
retention, export, erasure, consent, logs, test data, and third-party
flows — expressed as implementable patterns with verification. It does
not replace legal advice or the control register; it makes the technical
claims in that register true.

The governing rule: **every store that holds a person's data must be in
the inventory, and every right must be executable against every store.**
A store added later is the standard failure — new cache, new index, new
warehouse table, new log sink, new vendor SDK.

## When to Use

- Designing or reviewing a schema that will hold personal data.
- Implementing Art. 15/20 export or Art. 17 erasure.
- Adding retention, TTL, or deletion jobs.
- Introducing a new store, pipeline, log sink, or third-party SDK.
- Preparing a DPIA, records of processing (Art. 30), or a privacy review.
- After a leak: PII in logs, test data, or an unexpected copy.
- **When NOT to use:** legal interpretation of a processing purpose;
  pure compliance paperwork with no technical surface (use
  `compliance-audit`); security review of authz and injection (use
  `security-review-pentest`).

## PII Inventory and Classification

One row per field, not per table. The inventory is the source of truth
for export, erasure, and retention — if a field is missing here, it will
be missing there.

| Field | Meaning |
|---|---|
| Data element | `table.column`, event field, log field, object key |
| Category | identifier, contact, financial, location, behavioral, biometric, health, special category (Art. 9), free text |
| Purpose | Why it is processed; one purpose per row |
| Lawful basis | Art. 6 (and Art. 9 for special categories) |
| Stores | Primary DB, cache, search index, warehouse, object storage, queue, logs, metrics, traces, backups, exports, third parties |
| Retention | Duration plus the trigger that starts it |
| Export | Included in subject export? |
| Erasure | Deleted, anonymized, or legally retained? |
| Owner | One accountable person |

Discovery is mechanical, confirmation is human: scan schemas and
migrations, profile sample values, run classifiers for emails, phones,
IBANs, IDs, addresses, and free-text fields, then have the owner confirm
each row. Free-text columns are the usual blind spot — support notes,
comments, and JSON blobs absorb PII without a schema change.

Derived copies count as stores. Enumerate: read replicas, caches,
materialized views, search indices, analytics/warehouse tables, event
streams and dead-letter queues, object storage and exports, log
platforms, APM traces, metric labels, error trackers, email and support
systems, and every processor.

## Data Minimization in the Schema

Minimization is a schema decision, not a policy sentence.

- **Do not store what the purpose does not need.** Question every field
  at design time; deleting a column later is a migration, not adding it.
- **Separate identity from domain data.** A PII vault (subject id →
  attributes) or tokenization keeps business tables free of personal
  data and makes erasure a single-row operation.
- **No PII in primary keys, foreign keys, URLs, or filenames.** Keys
  leak into logs, caches, and analytics; use opaque ids.
- **No PII in event payloads by default.** Publish ids; let consumers
  resolve attributes through the vault, with access control.
- **Prefer nullable over fake defaults.** `unknown` beats a fabricated
  birthdate that later looks like real data.
- **Constrain free text.** Length limits, structured fields instead of
  prose, and a documented rule that free-text fields are in scope for
  export and erasure.
- **Column-level encryption for special categories** and for fields
  whose compromise is the incident; keep the key outside the database.
- **Collect at the point of need.** Progressive forms, optional fields
  truly optional, no "just in case" collection.

## Pseudonymization and Anonymization

Pseudonymized data is still personal data: reversible with the key, in
scope for every right. Anonymization is irreversible and must resist
re-identification — singling out, linkability, and inference.

| Technique | Use | Limit |
|---|---|---|
| Keyed hash (HMAC with secret pepper) | Stable pseudonym for joins and analytics | Reversible by dictionary attack if the input space is small and the key leaks |
| Unsalted hash | Never for PII | Emails and phone numbers are enumerable; this is not anonymization |
| Tokenization | Replace PII with a random token, vault holds the mapping | Vault becomes the crown jewel; protect and audit it |
| Format-preserving encryption | Keep length/format for legacy systems | Still reversible; treat as pseudonymization |
| Generalization / bucketing | Age bands, truncated postal code, coarse timestamps | Combinations of quasi-identifiers re-identify |
| Suppression | Drop rare values, small cells | Loses utility; document the threshold |
| k-anonymity / l-diversity | Released datasets | Vulnerable to homogeneity and background-knowledge attacks |
| Differential privacy | Aggregates and statistics | Needs a privacy budget; not a drop-in for row-level data |
| Synthetic data | Test and demo environments | Must be generated, not sampled; verify no real records survive |

Re-identification risk is a property of the **combination** of
quasi-identifiers, not of any single field. Test it: compute the
uniqueness of the quasi-identifier tuple on the release, check small
cell counts, and consider linkage with public data (postal code + birth
date + gender is famously unique). State the adversary model and the
measured uniqueness; "we removed names" is not an argument.

## Retention Enforcement

Retention is a job with an owner, a schedule, and a verification step —
not a sentence in a policy.

- **Define per data class and purpose:** duration, start trigger
  (creation, last activity, contract end), and what happens at expiry
  (delete, anonymize, archive).
- **Enforce at the lowest layer that can do it:** TTL indexes, partition
  drop, object-storage lifecycle rules, queue message expiry. These
  survive application bugs.
- **Application jobs for the rest:** batched, idempotent, resumable,
  rate-limited, with a dry-run mode and a per-run count.
- **Soft delete is a grace period, not retention.** A `deleted_at`
  column needs a purge job with its own deadline; otherwise "deleted"
  rows live forever.
- **Legal hold is an explicit exception** with a named owner and an
  expiry, not a silent skip.
- **Cascade to derived stores:** caches, indices, warehouse, exports,
  and backups follow the same clock or a documented shorter one.
- **Verify:** after each run, count remaining rows older than the
  window; alert when the count is non-zero or the job did not run.
  Record counts and durations, never the deleted values.

Backups deserve their own decision: either a retention shorter than the
restore window, or crypto-shredding (per-subject keys destroyed on
erasure), or a documented restore-and-reapply procedure using the
deletion log. Pick one and write it down; "backups expire eventually" is
not a procedure.

## Export (Art. 15/20)

One subject, every store, machine-readable, authenticated.

1. **Intake** — verify identity before assembling anything; the export
   itself is a disclosure.
2. **Collect** — query every store in the inventory by subject id,
   including derived and inferred data, and the metadata: purposes,
   recipients, retention, source.
3. **Format** — JSON (or CSV) with a stable schema, one file per
   domain, plus a manifest. Portability means structured, commonly
   used, machine-readable.
4. **Deliver** — asynchronous job, expiring signed link, encryption at
   rest, rate limit, and an audit record of who exported what and when.
5. **Exclude** — other people's data, trade secrets, and internal
   security notes; redact rather than omit silently.

Test the export against a seeded subject that has rows in every store;
a missing store shows up as a missing section, not as a support ticket.

## Erasure (Art. 17)

Erasure is an orchestration problem: many stores, one deadline.

- **Intake and verification** — same identity bar as export; log the
  request, the decision, and the deadline (one month, extendable with
  reason).
- **Orchestrate** — a deletion run per store, each idempotent and
  retryable, with a per-store result. Partial success is a failure that
  must be retried, not reported as done.
- **Cascade** — database `ON DELETE CASCADE` where the model allows it;
  application-level cascade for caches, search indices, object storage,
  queues, warehouse, and processors' APIs. Check the siblings: the
  table you deleted from usually has a copy.
- **Tombstones** — keep an opaque id plus a deletion marker where
  referential integrity or anti-resurrection requires it. A tombstone
  must contain no personal data and must not be re-hydrated by a later
  sync or import.
- **Anonymize where deletion is impossible** — financial or statutory
  records keep the transaction and lose the person: overwrite the PII
  columns, keep the aggregate.
- **Backups** — apply the chosen strategy (expiry, crypto-shred, or
  restore-and-reapply) and document the residual window.
- **Third parties** — call the processor's deletion API and keep the
  confirmation; a DPA clause is not a deletion.
- **Verify** — query every store for the subject id and assert zero
  rows (or only documented exceptions); issue a deletion receipt with
  per-store status and no personal data.

## Consent Tracking

Consent is a record with a lifecycle, not a boolean on the user row.

- Store: subject, purpose, scope, timestamp, notice version and text
  hash, channel, proof (double opt-in), and withdrawal timestamp.
- **Append-only history.** Current state is derived; the history is the
  evidence.
- **Check at processing time**, not only at collection: a marketing job
  must re-read consent before sending.
- **Withdrawal is as easy as grant** and propagates downstream —
  suppression lists, analytics, third-party audiences, and caches.
- **Do not bundle.** Terms acceptance, newsletter, and analytics consent
  are separate purposes with separate records.
- Pre-checked boxes and "by continuing you agree" are not consent.

## Log Hygiene

Logs are a data store with the worst access control and the longest
tail.

- **Allowlist fields at the logger**, not redaction at call sites; call
  sites forget.
- Never log request or response bodies, headers, cookies, tokens, or
  full URLs wholesale — query strings carry PII into access logs.
- Mask identifiers (email, phone, IBAN, national id) at the serializer;
  log a stable pseudonym when correlation is needed.
- **No PII in metric labels or trace attributes** — high cardinality
  and permanent retention.
- Scrub error trackers and crash reports; stack traces include locals.
- Short retention, restricted access, and an audit trail for log access.
- Test with a canary value: seed a known fake PII string, exercise the
  flows, assert it never appears in any log sink.

## Test Data

Production PII must never reach development, test, demo, or CI.

- Generate synthetic fixtures from the schema and the inventory; keep
  them deterministic and versioned.
- If a production snapshot is unavoidable, transform irreversibly with a
  documented, tested process, and verify by scanning the output for the
  original values.
- Separate environments with separate credentials; no shared buckets,
  no shared databases, no "read-only" production access from dev.
- Check the forgotten copies: seed scripts, fixtures in the repo, demo
  data, screenshots, notebooks, object-storage dumps, and CI caches.
- Treat test data as data: it still needs retention and access control.

## Third-Party Data Flows

Every SDK, tag manager, and webhook is a data flow with a recipient.

- Inventory processors and sub-processors: categories sent, purpose,
  region, transfer mechanism, DPA, deletion and export SLAs.
- **Minimize what leaves:** server-side events, hashed identifiers
  where the vendor supports it, no free-text payloads.
- **Gate scripts on consent** before they load; a tag manager can add a
  vendor without a code change, so review its configuration too.
- Audit SDK defaults — analytics and crash reporters collect more than
  the integration suggests.
- Webhooks and event streams carry PII as well; the receiving side is a
  store in your inventory.
- Keep the deletion and export paths for each vendor, and test them.

## Pitfalls

- **PII in logs, traces, and metric labels** — the most common leak, and
  the hardest to retract.
- **Deletion that misses derived stores** — cache, index, warehouse,
  queue, backup, vendor.
- **Unsalted hash sold as anonymization** — emails are enumerable.
- **Soft delete treated as erasure** — the row is still there.
- **Backups forgotten** — the subject reappears after a restore.
- **Export covers only the primary database** — the answer is
  incomplete and provably so.
- **Retention job that silently fails** — no alert, no count, no proof.
- **Deletion without verification** — "the job ran" is not evidence.
- **Pseudonymized data declared out of scope** — it is still personal
  data.
- **Free-text fields** — support notes and comments absorb PII.
- **PII in URLs and filenames** — leaks into logs, caches, and referrers.
- **Consent as a boolean** — no version, no proof, no withdrawal path.
- **Production data in test** — one dump undoes the whole program.
- **New store added later** — the inventory, export, and erasure were
  not updated.

## Verification

- [ ] Inventory covers every field and every store, including derived
      copies and third parties
- [ ] Every field has purpose, lawful basis, retention, and owner
- [ ] Schema minimized: no PII in keys, URLs, filenames, or event
      payloads by default
- [ ] Pseudonymization keyed and documented; anonymization backed by a
      measured re-identification assessment
- [ ] Retention enforced at the storage layer or by a monitored job
- [ ] Retention run verified by count; failure alerts exist
- [ ] Backup strategy chosen and documented (expiry, crypto-shred, or
      reapply)
- [ ] Export tested against a subject seeded in every store
- [ ] Erasure tested end to end; per-store results; zero rows on
      re-query; receipt issued
- [ ] Tombstones contain no personal data and cannot be re-hydrated
- [ ] Consent stored with version, proof, and withdrawal; checked at
      processing time
- [ ] Canary PII test passes: no PII in any log, trace, or metric sink
- [ ] Test and demo environments contain no production PII
- [ ] Third-party flows inventoried, minimized, consent-gated, and
      deletable

## Related Skills

- `compliance-audit` — control register, evidence, Art. 30 records, and
  the review loop that keeps this inventory honest.
- `security-review-pentest` — boundary enumeration, leak detection, and
  the privacy row in the boundary table.
- `database-migrations` — schema changes for minimization, backfills,
  cascade constraints, and reversible rollout of deletion logic.
