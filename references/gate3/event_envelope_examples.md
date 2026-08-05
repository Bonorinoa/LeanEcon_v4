# Event Envelope Examples

Illustrative records only; they are not executable schemas.

## Interpretation review required

```json
{"schema_version":"1.0.0","event_id":"event-7","event_type":"CLAIM_STATE_CHANGED","claim_id":"claim-123","run_id":"run-7","emitted_at":"2026-08-05T12:00:00Z","source_component":"interpreter","actor":"system","state_before":"INTERPRETED","state_after":"REVIEW_REQUIRED","reason_codes":[],"payload_class":"PROJECT","trace_ref":"trace-7"}
```

## Restricted request denied

```json
{"schema_version":"1.0.0","event_id":"event-8","event_type":"PROVIDER_REQUEST_BLOCKED","claim_id":"claim-123","run_id":"run-8","emitted_at":"2026-08-05T12:01:00Z","source_component":"provider-boundary","actor":"policy-boundary","state_before":"ACCEPTED","state_after":"BLOCKED","reason_codes":["RESTRICTED_BLOCKED"],"payload_class":"RESTRICTED","trace_ref":"trace-8"}
```

## Verification accepted

```json
{"schema_version":"1.0.0","event_id":"event-9","event_type":"VERIFICATION_COMPLETED","claim_id":"claim-123","run_id":"run-9","emitted_at":"2026-08-05T12:02:00Z","source_component":"verifier","actor":"verifier","state_before":"PROVING","state_after":"VERIFIED","reason_codes":[],"payload_class":"PROJECT","trace_ref":"bundle-9"}
```
