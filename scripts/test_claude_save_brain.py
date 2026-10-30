#!/usr/bin/env python3
"""Tests: save-brain archives a handoff.md/AGENTS.md that git does not hold before overwriting it."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("claude_save_brain.py")
HANDOFF = {
    "current_work": "New objective.",
    "working_set": ["src/a.sh"],
    "decisions": ["None."],
    "verification": ["None."],
    "next_actions": ["None."],
    "blockers": ["None."],
}
OLD = "# Handoff\n\n## Current Work\n\nOld uncommitted notes.\n"


def run(root: Path, payload: dict) -> dict:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--project-root", str(root)],
        input=json.dumps(payload), capture_output=True, text=True, check=True,
    )
    return json.loads(proc.stdout)


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


class ArchiveBeforeOverwrite(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def init_repo(self) -> None:
        git(self.root, "init", "-q")
        git(self.root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "init")

    def commit_all(self) -> None:
        git(self.root, "add", "-A")
        git(self.root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "c")

    def archived(self) -> list[Path]:
        return sorted((self.root / ".archived").glob("handoff.md.*"))

    def test_dirty_tracked_handoff_is_archived(self):
        self.init_repo()
        (self.root / "handoff.md").write_text("# Handoff\n\ncommitted\n")
        self.commit_all()
        (self.root / "handoff.md").write_text(OLD)
        result = run(self.root, {"handoff": HANDOFF})
        files = self.archived()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].read_text(), OLD)
        self.assertEqual(result["archived_files"], [str(files[0])])

    def test_clean_tracked_handoff_is_not_archived(self):
        self.init_repo()
        (self.root / "handoff.md").write_text(OLD)
        self.commit_all()
        result = run(self.root, {"handoff": HANDOFF})
        self.assertEqual(self.archived(), [])
        self.assertNotIn("archived_files", result)

    def test_handoff_outside_git_is_archived(self):
        (self.root / "handoff.md").write_text(OLD)
        run(self.root, {"handoff": HANDOFF})
        files = self.archived()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].read_text(), OLD)

    def test_unchanged_content_is_not_archived(self):
        run(self.root, {"handoff": HANDOFF})
        run(self.root, {"handoff": HANDOFF})
        self.assertEqual(self.archived(), [])

    def test_dirty_agents_md_is_archived(self):
        self.init_repo()
        old_agents = "# AGENTS.md - Project Instructions\n\n## Project Scope\n\n- old uncommitted\n"
        (self.root / "AGENTS.md").write_text(old_agents)
        run(self.root, {"project_agents_md": "# AGENTS.md - Project Instructions\n\n## Project Scope\n\n- new\n"})
        files = sorted((self.root / ".archived").glob("AGENTS.md.*"))
        self.assertEqual([f.read_text() for f in files], [old_agents])


class BudgetFailure(unittest.TestCase):
    def test_failure_message_names_count_and_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = {"handoff": {**HANDOFF, "next_actions": [f"task {i}" for i in range(11)]}}
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--project-root", tmp],
                input=json.dumps(payload), capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("Next Actions items 11>10", proc.stderr)
            self.assertFalse((Path(tmp) / "handoff.md").exists())


if __name__ == "__main__":
    unittest.main()
