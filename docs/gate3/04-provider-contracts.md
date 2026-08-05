# 3.4 Provider-Neutral Contracts

The v4 core depends on capabilities, not vendors. A provider adapter is the only component that knows a vendor API, credential name, retry policy, rate limit, response quirks, or vendor error taxonomy. Gate 3 specifies interfaces and ownership only; it does not implement an adapter.

## Capability contract

| Capability | Input | Output | Safe statuses |
|---|---|---|---|
| `interpret` | English claim plus approved context and typed policy metadata | Versioned `EconomicInterpretation` candidate | `HEALTHY`, `DEGRADED`, `UNAVAILABLE` |
| `formalize` | Accepted interpretation and typed formalization context | Candidate formal statement plus provenance | Same |
| `prove_or_repair` | Formal candidate, diagnostics, bounded budget | Candidate repair/proof attempt and diagnostics | Same |
| `semantic_triage` | Interpretation candidate | Non-authoritative flags/questions | Same; never approval |

The core sends typed requests through one provider boundary and receives normalized responses with request metadata and failure reason codes. Capability status is a small diagnostic output used by A1 probes and verification-bundle metadata; it is not emitted as a platform-wide health matrix. No core contract contains credentials or arbitrary file access.

## Adapter responsibilities

Adapters own API calls, credentials, timeouts, retries/backoff, rate limits, response normalization, provider metadata, and provider-specific failures. They must honor the outbound data policy, redact before transmission, and emit audit metadata without retaining sensitive payloads by default.

## MVP mapping (configuration, not implementation)

- interpretation and explanation → `mistral-medium-3-5`;
- Lean formalization, proof, and repair → `labs-leanstral-1-5`;
- semantic triage → Mistral capability, explicitly non-authoritative.

Model identifiers remain configuration outside core contracts. MVP proposes no silent fallback to another model; fallback behavior, model version pinning, and threshold values require Gate 4 operational approval.

## Failure semantics

Malformed provider output is `FAILED` with `PROVIDER_INVALID_OUTPUT` when a request ran. Credential failure, outage, or exhausted safe retry is `BLOCKED` with `PROVIDER_UNAVAILABLE`. A degraded response may be used only when the capability contract says the limitation is safe and the trace records it.

Credentials are referenced by name only and remain outside the repository.

**Attribution:** Prepared by Hermes Agent (Nous Research) under CTO direction; provider semantics require CTO approval.

**Gate 4 boundary:** adapter implementation, live probes, retry thresholds, and model-version pinning are explicitly deferred.

## Glossary

- **Capability:** a typed service function the core can request.
- **Adapter:** provider-specific boundary implementation.
- **Kernel:** Lean's trusted checker; it is not the language model.
- **Mathlib:** the external Lean theorem library whose revision must be pinned for reproducibility.
- **`sorry`:** an incomplete proof placeholder, forbidden in `VERIFIED` results.
- **Axiom:** an admitted premise; every dependency and axiom must be audited.

**Attribution:** Prepared by Hermes Agent (Nous Research) under CTO direction; provider semantics require CTO approval.
