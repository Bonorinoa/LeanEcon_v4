# LeanEcon CTO agent foundation (archived 2026-10-15)

This folder keeps the knowledge of the Hermes profile `leanecon-cto`. The profile was retired on
2026-10-15 during a workspace declutter. The project itself continues from this repository.

| File | What it holds |
|---|---|
| `SOUL.md` | The CTO charter: role, scope, and the two general principles (Krakauer, Feynman). |
| `MEMORY.md` | Operating lessons: model posture (DL 57), the merge-gate quirk for `workflow_dispatch` suites, the bot account limits, the sandbox rule, and the review style Augusto expects. |
| `USER.md` | How Augusto works with the agent: attribution, the formal bot identity, visible deliverables in `docs/`, and pedagogy as a first-class field. |
| `skills/leanecon-verified-workflow/` | The A3 verified workflow, Core promotion, release versioning, and the v3 / v3.5 phase records in `references/`. |
| `skills/github-collaboration-governance/` | Branch protection and PR governance for the bot plus a human reviewer. |
| `skills/repository-migration-governance/` | The v3 to v4 repository migration rules. |
| `skills/recovering-interrupted-agent-sessions/` | How to resume an interrupted agent session from disk. |

The design lessons from v3 live in `docs/v3/` (for example `V3_NOT_EARNED.md`), `docs/v4/INIT_V4*.md`,
and `ENGINEERING_LOG.md`.

The full profile (42 sessions, configuration, caches) is kept off GitHub as
`~/.hermes/profile-exports/leanecon-cto-20261015-193753.tar.gz` on Augusto's machine.
To restore the agent, run `hermes profile import <that file>`. Then copy these skills into the new profile.
