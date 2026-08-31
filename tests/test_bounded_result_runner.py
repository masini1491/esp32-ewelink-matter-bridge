import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))
import bounded_result_runner as runner


class BoundedResultRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.state = Path(self.temporary.name) / "state"

    def tearDown(self):
        self.temporary.cleanup()

    def test_normal_completion_and_safe_metadata(self):
        secret_like = "D2A_SYNTHETIC_OUTPUT"
        result = runner.run_child(3, self.state, [sys.executable, "-c", f"print('{secret_like}')"])
        payload = json.dumps(result)
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["returncode"], 0)
        self.assertGreater(result["stdout_bytes"], 0)
        self.assertNotIn(secret_like, payload)
        self.assertNotIn(sys.executable, payload)
        self.assertTrue((self.state / result["run_id"] / result["raw_stdout"]).is_file())
        self.assertTrue((self.state / result["run_id"] / result["raw_stderr"]).is_file())
        self.assertFalse((self.state / result["run_id"] / "result.tmp").exists())

    def test_nonzero_exit_is_recorded(self):
        result = runner.run_child(3, self.state, [sys.executable, "-c", "raise SystemExit(7)"])
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["returncode"], 7)

    def test_timeout_terminates_direct_child(self):
        pid_file = Path(self.temporary.name) / "pid"
        code = f"import os,time; open(r'{pid_file}','w').write(str(os.getpid())); time.sleep(10)"
        result = runner.run_child(0.2, self.state, [sys.executable, "-c", code])
        self.assertEqual(result["status"], "TIMED_OUT")
        self.assertTrue(result["timed_out"])
        self.assertLess(result["duration_ms"], 5000)
        pid = int(pid_file.read_text())
        with self.assertRaises(OSError):
            os.kill(pid, 0)

    def test_launch_failure_and_invalid_timeout(self):
        result = runner.run_child(3, self.state, ["d2a-command-does-not-exist"])
        self.assertEqual(result["status"], "LAUNCH_FAILED")
        with self.assertRaises(ValueError):
            runner.run_child(0, self.state, [sys.executable, "-c", "pass"])

    def test_cleanup_and_path_guard(self):
        result = runner.run_child(3, self.state, [sys.executable, "-c", "pass"])
        runner.cleanup(self.state, result["run_id"])
        self.assertFalse((self.state / result["run_id"]).exists())
        with self.assertRaises(ValueError):
            runner.cleanup(self.state, "../outside")

    def test_cli_uses_argv_not_shell(self):
        tool = Path(__file__).parents[1] / "tools" / "bounded_result_runner.py"
        completed = subprocess.run([sys.executable, str(tool), "run", "--timeout", "3", "--state-dir", str(self.state), "--", "d2a-not-a-command;echo", "unsafe"], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(completed.stdout)["status"], "LAUNCH_FAILED")


if __name__ == "__main__":
    unittest.main()
