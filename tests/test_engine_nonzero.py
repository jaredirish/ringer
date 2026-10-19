"""A passing check cannot conceal an engine failure unless explicitly allowed."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import ringer


class EngineNonzeroTests(unittest.TestCase):
    def test_verdict_precedence(self) -> None:
        cases = [
            (1, False, None, True, False, False, "ENGINE_FAILED"),
            (2, False, None, True, False, False, "ENGINE_FAILED"),
            (-9, False, None, True, False, False, "ENGINE_FAILED"),
            (0, False, None, True, False, False, "PASS"),
            (None, False, None, True, False, False, "PASS"),
            (1, False, None, True, False, True, "PASS"),
            (1, False, None, False, False, False, "FAIL"),
            (1, False, None, False, False, True, "FAIL"),
            (1, True, None, True, False, True, "TIMEOUT"),
            (1, False, None, True, True, False, "TIMEOUT"),
            (1, True, "spawn failed", True, True, False, "ERROR"),
        ]
        for rc, timeout, error, ok, check_timeout, allow, expected in cases:
            with self.subTest(rc=rc, timeout=timeout, error=error, ok=ok,
                              check_timeout=check_timeout, allow=allow):
                worker = ringer.WorkerResult(rc, timeout, None, error=error)
                verify = ringer.VerifyResult(ok, 0 if ok else 1, check_timeout, "")
                self.assertEqual(expected, ringer.verdict_for(worker, verify, allow))

    def test_manifest_default_and_opt_in(self) -> None:
        task = {"key": "engine", "spec": "Write expected.txt", "check": "test -s expected.txt"}
        self.assertIs(False, ringer.TaskSpec.from_obj(task).allow_engine_nonzero)
        self.assertIs(True, ringer.TaskSpec.from_obj({**task, "allow_engine_nonzero": True}).allow_engine_nonzero)

    def test_manifest_rejects_non_bool(self) -> None:
        for value in ("yes", 1, 0, None, [], {}):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "task engine: allow_engine_nonzero must be true or false"):
                    ringer.TaskSpec.from_obj({
                        "key": "engine", "spec": "Write expected.txt",
                        "check": "test -s expected.txt", "allow_engine_nonzero": value,
                    })

    def run_engine(self, rc: int, *, allow: bool = False, preexisting: bool = False) -> tuple:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        work = root / "work"
        taskdir = work / "engine"
        taskdir.mkdir(parents=True)
        if preexisting:
            (taskdir / "expected.txt").write_text("expected\n")
        worker = root / "worker.py"
        worker.write_text(
            "from pathlib import Path\n"
            + ("" if preexisting else "Path('expected.txt').write_text('expected\\n')\n")
            + f"raise SystemExit({rc})\n"
        )
        config = root / "config.toml"
        config.write_text(
            f"state_dir = {json.dumps(str(root / 'state'))}\n"
            "[eval]\nbackend = 'jsonl'\n"
            f"jsonl_path = {json.dumps(str(root / 'eval.jsonl'))}\n"
            "[artifact]\nenabled = false\n"
            f"[engines.fake]\nbin = {json.dumps(sys.executable)}\n"
            f"args_template = [{json.dumps(str(worker))}]\n"
            "sandbox_args = []\nfull_access_args = []\n"
        )
        manifest = root / "manifest.json"
        manifest.write_text(json.dumps({
            "run_name": "engine-exit", "workdir": str(work), "tasks": [{
                "key": "engine", "engine": "fake", "spec": "Write expected.txt with expected text.",
                "check": "cat expected.txt", "expect_files": ["expected.txt"],
                "max_attempts": 3, "allow_engine_nonzero": allow,
            }],
        }))
        result = subprocess.run(
            [sys.executable, str(ROOT / "ringer.py"), "run", str(manifest),
             "--config", str(config), "--no-dashboard", "--identity", "engine-exit-test"],
            cwd=ROOT, env={**os.environ, "RINGER_NO_SELF_UPDATE": "1",
                           "RINGER_HOME": str(root / "home"), "HOME": str(root / "home"),
                           "XDG_CONFIG_HOME": str(root / "config")},
            capture_output=True, text=True, timeout=30,
        )
        states = list((root / "state" / "runs").glob("*.json"))
        self.assertEqual(1, len(states), result.stdout + result.stderr)
        state = json.loads(states[0].read_text())
        rows = [json.loads(line) for line in (root / "eval.jsonl").read_text().splitlines()]
        return result, state, rows

    def assert_engine_failed(self, result, state, rows) -> None:
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        task = state["tasks"][0]
        self.assertEqual(("fail", "ENGINE_FAILED", 1), (task["status"], task["verdict"], task["attempts"]))
        self.assertEqual(1, task["worker_returncode"])
        self.assertEqual(0, task["check_returncode"])
        self.assertEqual((0, 1), (state["totals"]["pass"], state["totals"]["fail"]))
        self.assertEqual((0, 1), (state["summary"]["pass"], state["summary"]["fail"]))
        self.assertEqual(1, len(rows))
        self.assertEqual("ENGINE_FAILED", rows[0]["verdict"])
        self.assertIn("worker_returncode=1", rows[0]["notes"])
        self.assertIn("Engine exited with code 1", result.stdout)
        self.assertEqual("Engine exited with code 1", task["failure_reason"])
        event = ringer.plain_transition_event("engine", "running", "fail", task)
        self.assertIn("Engine exited with code 1", event["catch"])
        page = ringer.render_work_group(task, state=state, renderer=None, page_path=None)
        self.assertIn("Engine exited with code 1", page)
        self.assertIn('class="state fail"', page)
        self.assertNotIn("Failed its check", page)

    def test_existing_file_does_not_hide_failure_or_trigger_retry(self) -> None:
        self.assert_engine_failed(*self.run_engine(1, preexisting=True))

    def test_engine_writes_file_then_exits_one(self) -> None:
        self.assert_engine_failed(*self.run_engine(1))

    def test_zero_exit_passes(self) -> None:
        result, state, rows = self.run_engine(0)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(("pass", "PASS"), (state["tasks"][0]["status"], rows[0]["verdict"]))

    def test_explicit_opt_in_passes(self) -> None:
        result, state, rows = self.run_engine(1, allow=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(("pass", "PASS", 1), (state["tasks"][0]["status"], rows[0]["verdict"], state["tasks"][0]["attempts"]))


if __name__ == "__main__":
    unittest.main()
