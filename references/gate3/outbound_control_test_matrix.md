# Expanded Outbound-Control Test Matrix

These are acceptance-test specifications, not test code.

- **Classification:** explicit class round-trip; missing class; mixed content; sealed gold marker; hidden v3 artifact marker.
- **Authorization:** restricted no approval; wrong run; expired approval; scope mismatch; valid one-run approval; replay attempt.
- **Redaction:** token, password, API key, direct identifier, nested sensitive field, already-redacted value; assert post-redaction digest.
- **Boundary:** instrument provider calls and assert exactly one boundary; forbid imports/call sites outside adapter; verify typed payload only.
- **Failure:** unavailable/degraded adapter; retry exhaustion; malformed output; ensure no policy bypass or unapproved fallback.
- **Audit:** allow and deny events have required metadata; denial has `RESTRICTED_BLOCKED`; no raw restricted payload in logs.
- **Retention:** payload absent by default; explicit policy-controlled retention records approval and expiry.
