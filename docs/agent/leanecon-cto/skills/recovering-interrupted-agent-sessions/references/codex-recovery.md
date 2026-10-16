# Codex CLI — Session Recovery Reference

The Codex CLI stores everything needed to recover an interrupted
session in a small number of SQLite databases and JSONL files under
`~/.codex/`. This document is the schema reference; the procedural
recipe lives in the parent SKILL.md.

## File layout (macOS / Linux)

| File | Purpose | Size hint |
|---|---|---|
| `~/.codex/state_*.sqlite` | Thread / session directory | tens of MB; one row per `codex` invocation |
| `~/.codex/goals_*.sqlite` | Goal-tracking + status | small (~40 KB) |
| `~/.codex/logs_*.sqlite` | Per-event feedback log | large (~230 MB) — only needed for token timelines |
| `~/.codex/sessions/YYYY/MM/DD/rollout-<ts>-<thread_id>.jsonl` | Full conversation transcript | ~1 MB per 30-min session |
| `~/.codex/session_index.jsonl` | `id`, `thread_name`, `updated_at` per thread | small |
| `~/.codex/auth.json` | OAuth credentials (read-only — never edit) | small |
| `~/.codex/config.toml` | CLI config | small |

The `-wal` and `-shm` siblings (e.g. `state_5.sqlite-wal`) are
SQLite write-ahead logs; they commit back into the main file on
clean shutdown. If Codex was killed mid-write, query the main file
but expect partial state — fall back to `session_index.jsonl` if the
SQLite open fails.

## Thread directory (`state_*.sqlite`)

```sql
-- The minimum columns you actually need for recovery:
SELECT id, cwd, title, model, model_provider, first_user_message,
       rollout_path, tokens_used, created_at, updated_at
FROM threads
WHERE cwd LIKE '%<repo>%'
ORDER BY updated_at DESC
LIMIT 5;
```

`first_user_message` is a **preview** (often truncated to a few
hundred chars). If the real prompt is longer, it's in the rollout
JSONL. The full `threads` schema also has `git_sha`, `git_branch`,
`git_origin_url`, `name`, `preview`, `recency_at_ms` — useful
context but not required for recovery.

## Goal state (`goals_*.sqlite`)

```sql
SELECT thread_id, status, token_budget, tokens_used,
       time_used_seconds, created_at_ms, updated_at_ms
FROM thread_goals
WHERE thread_id = '<id>';
```

The CHECK constraint on `status` is the source of truth for the
allowed values:

```sql
CHECK(status IN (
    'active',
    'paused',
    'blocked',
    'usage_limited',
    'budget_limited',
    'complete'
))
```

`thread_goal_continuation_deferrals` is a one-row table keyed by
`thread_id` — presence means the model explicitly asked to be
continued on a fresh thread. Empty in normal runs.

## Session index (`session_index.jsonl`)

One JSON object per line, no trailing newline. Cheap to scan with
`grep` for a thread id or `thread_name` substring.

```json
{"id":"01a00360-…","thread_name":"Assess Hermes progress vs MVP","updated_at":"2026-08-15T03:04:45Z"}
```

Use this when SQLite is locked, corrupted, or you just want a fast
overview before opening the heavier DB.

## Per-event log (`logs_*.sqlite`)

```sql
SELECT id, ts, level, target, length(coalesce(feedback_log_body,''))
FROM logs
WHERE thread_id = '<id>'
ORDER BY id DESC LIMIT 10;
```

`target` is the Rust module that emitted the event
(`codex_core::stream_events_utils` is the most common — every
agent message goes through it). The body is gzipped or plain text
depending on the level; the bytes count is enough to gauge whether
it's worth opening.

## Transcript (`rollout-*.jsonl`)

The big one. Each line is a JSON event. Top-level `type` is one of:

- `session_meta` — thread id, model, cwd, cli_version (2 events
  per session, at start and on resume).
- `event_msg` — most of the surface area. `payload.type` is the
  sub-discriminator.
- `response_item` — OpenAI Responses API items: `role: user |
  assistant | None`, with `content` array of typed parts.
- `turn_context` — per-turn model/config snapshot.
- `world_state` — environment snapshot (cwd, sandbox).

### `event_msg.payload.type` values seen in practice

| Sub-type | Meaning | What to extract |
|---|---|---|
| `user_message` | The user's prompt | `message` (full text) |
| `agent_message` | The model's final reply text | `message` (often duplicated in the adjacent `response_item`) |
| `mcp_tool_call_end` | MCP tool result | `result.Ok.content[*].text` (JSON) **or** `result.Err` (string) — the failure boundary |
| `patch_apply_end` | `apply_patch` result | `changes: {path: {type: add\|update\|delete, ...}}` and `stdout` listing affected files |
| `token_count` | Per-turn cumulative tokens | `info.last_token_usage.total_tokens` (or `total_token_usage.total_tokens`) |
| `task_started` / `task_complete` | Session-level markers | The `task_complete` after a rejection is the **runtime's**, not the agent's |
| `entered_review_mode` | User entered review | Mostly noise for recovery |
| `patch_apply_begin` | Patch start | Rare; patch results are usually only in `patch_apply_end` |

### `response_item` shape

```json
{
  "type": "response_item",
  "payload": {
    "role": "assistant",          // or "user", or null
    "content": [
      {"type": "output_text", "text": "..."},
      {"type": "function_call", "name": "shell", "arguments": "{...}"},
      {"type": "reasoning", "summary": "..."}
    ]
  }
}
```

`output_text` is where the model's reasoning, plan, and status
updates live. **This is where a ranked task list appears** when
the agent proposes one — search for "priority order" /
"top 5" / "1. **<verb>" patterns. `function_call` items are the
MCP tool invocations; their `arguments` are JSON strings. `reasoning`
items are short CoT summaries (not always emitted).

## Status semantics — what to do next

| `thread_goals.status` | Cause | Next step for the human |
|---|---|---|
| `usage_limited` | OpenAI plan cap hit during this session | The user's plan choice (Plus / Team / API key). Not a code issue. |
| `budget_limited` | Per-session `--max-tokens` cap | Raise the cap and re-run. |
| `blocked` | Tool approval was rejected (e.g. `apply_patch` outside the sandbox) | Show the user the `Err` text and the affected paths. |
| `paused` | User pressed `Esc` | Resume if the user wants. |
| `active` | Still running (or runtime thinks it is) | Use `process(action="poll")` first — don't reconstruct. |
| `complete` | `task_complete` emitted by the agent itself | The work should be on disk; go read the diff. |

## Worked walkthrough — Aug 14 2026

User prompt: "I was working on a rank of 5 tasks with codex in my
vscode until it run out of tokens mid-goal, can you infer the
work in progress from the git history to define next steps?"

```bash
# 1. Find the thread
sqlite3 ~/.codex/state_5.sqlite \
  "SELECT id, cwd, title, model, rollout_path FROM threads
   WHERE cwd LIKE '%leanecon_v4_work%' ORDER BY updated_at DESC LIMIT 5;"

# 2. Read the goal
sqlite3 ~/.codex/goals_1.sqlite \
  "SELECT status, tokens_used, time_used_seconds
   FROM thread_goals WHERE thread_id='01a00360-...';"
# → usage_limited | 5,588,199 | 519

# 3. Walk the rollout (1.2 MB; use execute_code to stream)
python -c "
import json
for ln in open('~/.codex/sessions/2026/08/14/rollout-2026-08-14T20-04-39-01a00360-....jsonl'):
    obj = json.loads(ln)
    # ... extract user_message, agent_message, patch_apply_end, mcp_tool_call_end, token_count
"
```

Findings:

- Thread `01a00360-…`, model `gpt-5.6-terra`, cwd `leanecon_v4_work`,
  branch `v3/phase1-wire-loop`.
- 2 user messages: first was an assessment, second was "take over
  lead engineering, give me the top 5 tasks" — that's the prompt
  that scoped the work.
- 5 ranked tasks proposed in the assistant's reply.
- 6 `patch_apply_end` events covering 11 distinct files (all
  visible in `git status`).
- Last assistant text: "…moving on to the two product gaps: a
  sealed-evaluation protocol with semantic-review scoring, then
  the bounded prover."
- Last 2 `mcp_tool_call_end` events returned
  `result.Err = "You've hit your usage limit…"`.
- Final `token_count`: 5,588,199 cumulative.

Action: per-task status table + commit the uncommitted work +
write predictions file for the held-out eval step before any
re-run.

## Query cookbook

```sql
-- All threads on a given repo, newest first, with their status
SELECT t.id, t.title, g.status, g.tokens_used
FROM threads t
LEFT JOIN (
  SELECT thread_id, status, tokens_used
  FROM thread_goals
  WHERE rowid IN (SELECT MAX(rowid) FROM thread_goals GROUP BY thread_id)
) g ON g.thread_id = t.id
WHERE t.cwd LIKE '%<repo>%'
ORDER BY t.updated_at DESC;

-- Last MCP failure for a thread
SELECT payload
FROM logs
WHERE thread_id = '<id>'
  AND json_extract(payload, '$.type') = 'mcp_tool_call_end'
  AND json_extract(payload, '$.result.Err') IS NOT NULL
ORDER BY id DESC LIMIT 1;

-- Total patch count + file count for a thread
SELECT
  COUNT(*) AS patch_events,
  SUM(json_array_length(json_extract(payload, '$.changes'))) AS files_touched
FROM logs
WHERE thread_id = '<id>'
  AND json_extract(payload, '$.type') = 'patch_apply_end';
```

## Tooling pitfalls

- **`session_index.jsonl` is a JSONL, not JSON.** Trailing newlines
  vary; use line-by-line parsing, not `json.load(open(...))`.
- **WAL files are required to read recent state.** If the
  `state_*.sqlite` file looks stale, check that the
  corresponding `-wal` is present in the same directory; some
  SQLite clients (notably `sqlite3` CLI) need both for
  consistency.
- **Don't write to any of these files.** Even a stray VACUUM can
  corrupt Codex's runtime state. Read-only.
- **Rollout JSONL `ts` is in seconds; `ts_nanos` is the
  fractional part.** For wall-clock display, use only `ts`.
- **`feedback_log_body` in `logs_*.sqlite` can be huge** (>10 KB
  for tool results). Avoid `SELECT feedback_log_body` until you
  know which rows you want.
