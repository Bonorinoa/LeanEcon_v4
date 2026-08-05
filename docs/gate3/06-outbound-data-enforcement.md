# 3.6 Outbound Data Enforcement

All provider egress passes through one controlled boundary. No core service, prompt helper, worker, test shortcut, or retrieval component may call a provider directly or read arbitrary files to construct a request.

## MVP-thin data posture

The project has no public users in the near term. Gate 3 therefore proposes a deliberately small control floor rather than a complete privacy program:

| Class | MVP treatment |
|---|---|
| `PUBLIC` | May be sent after secrets/credentials are removed. |
| `PROJECT` | Default class for project work; may be sent to the approved provider through the single adapter boundary. |
| `RESTRICTED` | Denied outright in MVP with `RESTRICTED_BLOCKED`; no opt-in mechanism yet. |
| Unknown/mixed | Fail closed as `RESTRICTED`. |

Sealed gold artifacts, hidden labels, and v3 hidden evaluation material are always rejected, including from `PROJECT` requests. PII classification, full retention controls, and per-run restricted approval are future work before external users or a legitimate restricted-data use case.

## Enforcement contract

1. A typed request enters the single boundary with classification and intended capability.
2. The boundary validates the class and maps unknown/mixed content to denial.
3. The adapter removes secrets and credentials before transmission; no broad PII redaction pipeline is proposed now.
4. `RESTRICTED`, sealed gold, and hidden v3 material are denied without contacting the provider.
5. The adapter alone transmits the typed, redacted payload.
6. Minimal audit metadata records policy decision, classification, model/capability, request ID where available, and reason code. Full payload retention is not enabled by default.

## Test matrix (implementation acceptance contract)

| Test | Proves |
|---|---|
| Classifier accepts explicit classes and maps unknown/mixed to `RESTRICTED` | Fail-closed classification |
| `RESTRICTED` without current run approval is denied | Default deny |
| `RESTRICTED` request is denied and makes no outbound call | MVP default deny |
| Sealed gold/v3 hidden artifact is denied even when classified `PROJECT` | Evaluation integrity |
| Secret/token fields are absent from adapter payload | Minimal redaction before egress |
| Every provider request has exactly one boundary | Single egress path |
| Direct provider access from core is rejected by architecture test/static check | No bypass |
| Provider outage or malformed output produces a typed failure | Failure safety |
| Denial emits `RESTRICTED_BLOCKED` and no outbound request | Trace completeness |
| PII classification, per-run opt-in, and retention controls are explicitly marked future | Scope control |

Implementation and tests belong to Gate 4; this package specifies what they must prove.

## Glossary

- **Egress:** data leaving the service for an external provider.
- **Redaction:** removing sensitive fields before transmission.
- **Fail closed:** uncertainty causes denial rather than permission.
- **Gold artifact:** evaluator-only reference material unavailable to runtime agents.

**Attribution:** Prepared by Hermes Agent (Nous Research) under CTO direction; data-policy decisions require CTO approval.
