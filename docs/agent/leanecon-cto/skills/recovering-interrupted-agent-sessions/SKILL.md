---
name: recovering-interrupted-agent-sessions
description: "Recover a dead agent session's plan, edits, failure point."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [Agent-Recovery, Forensics, Codex, Session-Reconstruction, Autonomous-Agents]
    related_skills: [codex, hermes-agent, merge-reconciler]
---

# Recovering an Interrupted Agent Session

When an autonomous coding agent (Codex CLI, Claude Code, aider, or
similar) stops mid-goal — usage limit hit, killed process, lost
shell, OAuth rejection — the on-disk evidence in that agent's state
directory is enough to fully recover the task list, the last
successful edits, and the failure boundary. **Do not ask the user
to re-explain. Reconstruct from the repo and the agent's state.**

The user's standing preference is "infer the work in progress from
the git history to define next steps" — and that means *both* the
project's `git log` *and* the agent's own session history. A dead
agent session is recoverable state, not lost context.

## When to use

- A `codex exec`, `claude code`, or `aider --message` run stopped
  before it said "done" / `task_complete` on its objective.
- The agent hit a token budget cap (OpenAI / Anthropic plan limit,
  per-session `--max-tokens`, etc.).
- A parallel worktree or kanban campaign lost a worker to a
  network/credential/auth failure.
- The user is asking "where did the agent get to?" / "what did it
  finish?" / "can you pick up from there?".

## When NOT to use

- The agent is still running — use `process(action="poll"|"log")`
  instead.
- The agent finished cleanly and the work is committed — go read
  the diff.
- The user is debugging their *own* code and the agent is just a
  tool that ran fine.

## General recovery method (agent-agnostic)

Every autonomous agent CLI keeps some form of persistent state
under a dot-directory in `$HOME`. The shape varies, but the
information is the same:

1. **A thread/session index** — one row per session with id, cwd,
   model, status, timestamps, last-user-message preview.
2. **A goals / objectives table** — keyed by session id, with
   `status` (active / usage_limited / budget_limited / blocked /
   complete), `tokens_used`, `objective` text.
3. **A rollout / transcript** — the full conversation:
   user messages, assistant text, tool calls, tool results,
   token counts, completion markers.
4. **A patch / edit log** — the actual file mutations the agent
   performed, with success/failure per change.
5. **A session log table** — per-event log rows keyed by
   session id, useful for token-count timelines.

The recipe is always the same: **find the directory → pick the
right session by cwd + recency → read the goal row → walk the
transcript → cross-check against `git status` → verify the
green claims by hand.**

## Codex CLI (the most common case)

The Codex state layout and full recovery recipe are documented in
[`references/codex-recovery.md`](references/codex-recovery.md). The
short version:

| What | Where (macOS / Linux) |
|---|---|
| Thread directory | `~/.codex/state_*.sqlite` (`threads` table) |
| Goal state | `~/.codex/goals_*.sqlite` (`thread_goals` table) |
| Full transcript | `~/.codex/sessions/YYYY/MM/DD/rollout-<ts>-<thread_id>.jsonl` |
| Session index | `~/.codex/session_index.jsonl` |
| Per-event log | `~/.codex/logs_*.sqlite` |

Disambiguation rule when two threads share a cwd: pick the one
with the latest `updated_at`; the other is usually a sibling
`codex-auto-review` thread spawned by an orchestrator. Filter on
the `model` column or `model_provider` to be sure.

Status semantics:

| `thread_goals.status` | Meaning | Next move |
|---|---|---|
| `usage_limited` | User's plan cap hit | The user's plan choice, not code |
| `budget_limited` | Session `--max-tokens` cap | Raise the cap, restart |
| `blocked` | Tool approval was rejected | Show the user the `Err` text |
| `paused` | Explicitly stopped (often via `Esc`) | Resume if the user wants |
| `active` | Still running | Use `process(action="poll")` instead |
| `complete` | Done | Don't reconstruct, the work should be on disk |

## What to report to the user

Produce, in this order:

1. **Repo + branch + last commit** (from `git status -sb`).
2. **Session id, model, wall-clock span, final token count** (from
   the rollout).
3. **The task list** the agent was working through, in its own
   words. If the agent proposed a ranked list, quote the list
   verbatim.
4. **Per-task status table** with on-disk evidence columns. Mark
   each task **DONE / PARTIAL / NOT STARTED** and link to the
   specific files the agent touched.
5. **The failure boundary** — the literal error message and the
   last two tool-call results, so the user can see *where* it
   stopped. Quote the error verbatim.
6. **What you re-verified by hand** (real tool output, not the
   agent's self-report) and what you did not. Agent status
   messages are **self-reports**; the system-prompt rule for
   `delegate_task` applies equally to recovering a dead session.
7. **One thing to flag before they push** — usually an attribution
   / governance / protocol gap, because most agents do not
   follow the user's project review policy or DECISION_LOG
   discipline unless prompted. Surface it as a question, not a
   blocker.

## Pitfalls

- **The first user message in the transcript is not always the
  kickoff.** A later user message can re-scope the session
  ("take over lead engineering, give me the top 5 tasks"). Always
  walk all `user_message` events before claiming you have the
  task list.
- **`first_user_message` in the session-row is a preview, not a
  full record.** If it is short, the real prompt is in the
  transcript file.
- **A `task_complete` event after a tool-call rejection is the
  runtime's, not the agent's.** If the last assistant text is
  followed by a tool-call `Err`, the agent never finished — the
  `task_complete` is just the runtime closing the session.
- **Transcript files are large.** A 30-minute session can be 1+
  MB. Stream them with `execute_code` / chunked `read_file`
  rather than `terminal cat` (which will page and lose content).
- **Do not "resume" by re-running the same prompt.** You will
  re-burn the same tokens and almost certainly get a different
  plan. Instead, write down the current state and pick up from
  the next concrete step.
- **Cross-check against `git status`.** Every successful patch
  should be a modified or untracked file in the worktree. If a
  patch is in the transcript but not on disk, the user
  unstashed/reset between the agent's death and now — note it
  and surface it; do not silently re-apply.
- **Re-verify the agent's green claims.** If the agent said
  "203 passing tests", run `pytest -q` again and quote the real
  count. Agents are good at claiming work is done; only the
  on-disk state is evidence.

## Worked example (Codex, Aug 14 2026)

User: "I was working on a rank of 5 tasks with codex in my vscode
until it run out of tokens mid-goal, can you infer the work in
progress from the git history to define next steps?"

Recovered: repo `~/Desktop/leanecon_v4_work`, branch
`v3/phase1-wire-loop`, thread `01a00360-…-a4dc5ee1078a`, model
`gpt-5.6-terra`, 5.59 M tokens, killed by `usage_limited` MCP
rejection ("You've hit your usage limit. Upgrade to Plus…").
The agent had proposed 5 tasks, completed task 1 (release-truth
plumbing) and ~70% of task 2 (eval protocol scaffolding), and
was killed reading `ArtifactStore` to wire the eval script into
the protocol. The per-task status table and on-disk evidence
allowed the user to commit the work in a single review and pick
up at the next concrete step without re-running Codex.
