# Dependency Upgrades — Sources

Research basis for the dependency-upgrades skill (verified 2026-11-23):

- **Sonatype — State of the Software Supply Chain**
  https://www.sonatype.com/state-of-the-software-supply-chain/introduction
  Annual data on open-source malware volume, registry scale and dependency
  graph growth. The evidence base for treating upgrades as a security
  control, not hygiene.

- **SLSA — Supply Chain Threats**
  https://slsa.dev/spec/v1.1/threats
  Threat model (A)–(I) across source, build, distribution and dependencies,
  each mapped to mitigations. Use it to explain *why* a given upgrade or
  provenance check matters.

- **OWASP — NPM Security Cheat Sheet**
  https://cheatsheetseries.owasp.org/cheatsheets/NPM_Security_Cheat_Sheet
  Lockfiles, `npm ci` vs. `npm install`, lifecycle-script risk, typosquatting,
  provenance and 2FA on publish. Concrete registry-side hardening.

- **npm Docs — Auditing package dependencies**
  https://docs.npmjs.com/auditing-package-dependencies-for-security-vulnerabilities
  `npm audit` / `npm audit fix` semantics, severity levels, and the limits of
  automated remediation (breaking changes, no fix available).

- **Renovate — Configuration Options**
  https://docs.renovatebot.com/configuration-options/
  `packageRules`, grouping, scheduling, `rangeStrategy`, automerge and
  stability days. The reference for "newest deps ≥72h old" style policies.

- **GitHub Docs — Dependabot version updates**
  https://docs.github.com/code-security/concepts/supply-chain-security/dependabot-version-updates
  Difference between security updates and version updates, ecosystem config,
  PR grouping and review workflow.

- **PyPI — Trusted Publishing**
  https://docs.pypi.org/trusted-publishers/
  OIDC-based short-lived publishing tokens instead of long-lived API keys —
  removes the most common package-account takeover path.

- **OpenSSF Scorecard**
  https://github.com/ossf/scorecard
  Automated health checks (branch protection, pinned dependencies, review
  requirements, dangerous workflows) for scoring a dependency before adopting
  it.
