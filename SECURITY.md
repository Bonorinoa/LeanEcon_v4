# Security Policy

## Supported status

LeanEcon v4 is in early, pre-release development. There is **no supported
production release** yet; the repository contains governance scaffold only.

## Reporting a vulnerability

Please do **not** open a public issue for security problems.

- Report privately by contacting the repository owner (`@Bonorinoa`) via a
  private channel (GitHub security advisory, or direct contact as agreed).
- Include: affected file(s) if known, a minimal description, and any suggested
  mitigation.
- Do not include credentials or live provider payloads in the report.

## Secrets policy

- Credentials never belong in this repository. If you find a committed secret,
  treat it as compromised: rotate it, then report it.
- The migration policy forbids importing v3 secrets, provider credentials, or
  generated state into v4.

## Out-of-scope for automated handling

- Semantic approval and release decisions are human-owned. Automated agents may
  triage, but never approve meaning or promote results to `VERIFIED` without
  the complete verification bundle.
