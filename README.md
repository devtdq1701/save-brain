# save-brain

Claude Code skills and a writer script that save session state across three local surfaces without duplicating it:

| Skill | Owns |
|---|---|
| `claude-project-state` | The full `/save-brain` sweep, the state root, and project-root `AGENTS.md` |
| `session-handoff` | `handoff.md` only: compact restart state for the next session |
| `claude-state-memory` | Read/write gates for Claude Code auto-memory (`~/.claude/projects/<slug>/memory/`) |
| `claude-procedure-extraction` | Approval-gated candidates for new or updated skills |

`scripts/claude_save_brain.py` renders `handoff.md` and `AGENTS.md` from a JSON payload, enforces section and size budgets, refuses an over-budget write, and archives an uncommitted file to `<root>/.archived/` before overwriting it.

## Install

```bash
cp -r skills/* ~/.claude/skills/
mkdir -p ~/.claude/scripts && cp scripts/claude_save_brain.py ~/.claude/scripts/
```

The skills call the writer at `~/.claude/scripts/claude_save_brain.py`.

## Use

In Claude Code, say `save-brain` (or `save state`, `checkpoint everything`). The sweep writes `handoff.md`, evaluates `AGENTS.md`, checks for reusable procedures and memory, and reports one receipt line per gate.

## Test

```bash
python3 scripts/test_claude_save_brain.py
```
