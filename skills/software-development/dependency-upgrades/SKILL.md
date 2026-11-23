---
name: dependency-upgrades
description: "Newest deps ≥72h old; security fixes immediately."
license: MIT
compatibility: Any package ecosystem (npm, PyPI, crates.io, Go modules, Maven, …); needs publish dates and a lockfile.
metadata:
  author: Florian Zimmermeister (flozi00)
  version: "0.1.0"
---

# Dependency Upgrades

Supply-chain attacks exploit the window right after a release: a
compromised maintainer account or a malicious publish is usually detected
and yanked within days. The policy: **always run the newest dependency
version that is at least 72 hours old** — and ignore the age rule only for
security fixes.

## When to Use

- Routine dependency refresh, or a scheduled upgrade pass.
- A security advisory or CVE affecting a version in use.
- Adding a new dependency — pick an eligible version from the start.
- **When NOT to use:** internal packages with no external publish and no
  supply-chain window; runtime or language major migrations that need
  their own plan.

## The Rule

1. **Default:** newest available version whose publish date is **≥ 72
   hours** ago.
2. If the newest version is younger than 72 h, take the newest one that is
   ≥ 72 h old. Do not wait for the clock to run out on the newest — pick
   the newest eligible.
3. **Exception:** a security vulnerability (known CVE, advisory, active
   exploit) → upgrade immediately to the fixed version, regardless of age.
4. Never upgrade to a version younger than 72 h "because it is newer" —
   that is exactly the window this rule exists to avoid.
5. Pin exact versions and commit the lockfile; verify checksums/signatures
   where the ecosystem provides them.

## Why 72 Hours

- Malicious releases are typically detected by the community, scanners,
  and maintainers within hours to days; registries yank them.
- A 72 h-old version has survived the highest-risk window: no reports of
  compromise, no yank, no advisory.
- The rule costs at most three days of freshness — negligible against the
  risk of a compromised dependency.

## The Upgrade Workflow

1. **List** outdated dependencies with current version, latest version,
   and publish date (per ecosystem: `npm view <pkg> time`, `pip index
   versions`, `cargo search`/`cargo update --dry-run`, `go list -m -u`,
   Maven metadata, …).
2. **Filter:** newest version with age ≥ 72 h; flag security advisories
   separately.
3. **Read** the changelog/release notes for breaking changes; inspect the
   diff for critical dependencies.
4. **Upgrade** one dependency (or one coherent group) at a time; run the
   full test suite; commit with the version bump.
5. **Verify:** lockfile updated, checksums verified, CI green.
6. **Record:** version, date, reason (routine vs. security).

## Security Hotpatch Path

- **Trigger:** CVE/advisory affecting a used version, with a fixed release.
- **Act immediately:** upgrade to the fixed version even if younger than
  72 h.
- **No fix yet:** mitigate (disable the feature, patch locally, vendor),
  document the risk acceptance, and track the upstream fix.
- **After the hotpatch:** verify the fix version's integrity (checksums,
  signatures), run the full suite, record the advisory ID.

## Automation

- A scheduled job (weekly) that lists outdated dependencies with publish
  dates and flags eligible upgrades (≥ 72 h) and security advisories.
- CI gate: dependency audit fails on known critical/high CVEs.
- Renovate/Dependabot-style tools: configure a **minimum release age of
  72 h** where supported; security updates bypass the age gate.

## Pitfalls

- **Upgrading to a < 72 h version "to be current"** — defeats the rule.
- **Batch-upgrading everything at once** — a failure cannot be attributed.
- **Skipping the changelog** — breaking changes surface in production.
- **Ignoring the lockfile** — floating ranges reintroduce the risk.
- **Treating the 72 h rule as a reason to delay a security fix** — the
  exception exists precisely for that.

## Verification

- [ ] Every upgraded dependency has a publish date ≥ 72 h (or a security reason)
- [ ] Lockfile committed; exact versions pinned
- [ ] Changelog read; breaking changes handled
- [ ] Full test suite green after the upgrade
- [ ] Security advisories checked; hotpatches applied immediately
- [ ] Upgrade recorded with date and reason

## Related Skills

- `security-review-pentest` — when an advisory needs impact assessment, not just a version bump.
- `commit-discipline` — when the upgrade must land as a green, revert-friendly commit.
