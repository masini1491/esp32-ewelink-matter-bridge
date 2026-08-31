#!/usr/bin/env python3
"""Bounded, local-only direct-child runner with cross-command result handoff."""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path

MAX_TIMEOUT_SECONDS = 300
TERMINATION_GRACE_SECONDS = 2
RUN_ID_RE = re.compile(r"^d2a-[0-9a-f]{32}$")
MARKER = ".d2a-run"


def _private_directory(path):
    path.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(path, 0o700)
    except OSError:
        pass


def _atomic_json(path, document):
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, sort_keys=True, separators=(",", ":"))
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _run_directory(state_dir, run_id):
    if not RUN_ID_RE.fullmatch(run_id):
        raise ValueError("invalid run id")
    candidate = state_dir / run_id
    if candidate.parent != state_dir:
        raise ValueError("run directory escapes state directory")
    return candidate


def _result_path(run_dir):
    return run_dir / "result.json"


def run_child(timeout, state_dir, argv):
    if not 0 < timeout <= MAX_TIMEOUT_SECONDS:
        raise ValueError("timeout must be greater than zero and within the hard limit")
    if not argv:
        raise ValueError("child argv is required")
    _private_directory(state_dir)
    run_id = "d2a-" + uuid.uuid4().hex
    run_dir = _run_directory(state_dir, run_id)
    _private_directory(run_dir)
    (run_dir / MARKER).touch(exist_ok=False)
    stdout_path = run_dir / "stdout.bin"
    stderr_path = run_dir / "stderr.bin"
    started = time.monotonic()
    returncode = None
    timed_out = False
    status = "COMPLETED"
    try:
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            try:
                process = subprocess.Popen(argv, shell=False, stdout=stdout, stderr=stderr)
            except OSError:
                status = "LAUNCH_FAILED"
            else:
                try:
                    returncode = process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    status = "TIMED_OUT"
                    process.terminate()
                    try:
                        returncode = process.wait(timeout=TERMINATION_GRACE_SECONDS)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        try:
                            returncode = process.wait(timeout=TERMINATION_GRACE_SECONDS)
                        except subprocess.TimeoutExpired:
                            status = "TERMINATION_FAILED"
                if status == "COMPLETED" and returncode != 0:
                    status = "COMPLETED"
    finally:
        duration_ms = round((time.monotonic() - started) * 1000)
        for raw_file in (stdout_path, stderr_path):
            if not raw_file.exists():
                raw_file.touch()
            try:
                os.chmod(raw_file, 0o600)
            except OSError:
                pass
        result = {
            "schema_version": 1,
            "run_id": run_id,
            "status": status,
            "returncode": returncode,
            "timed_out": timed_out,
            "duration_ms": duration_ms,
            "stdout_bytes": stdout_path.stat().st_size,
            "stderr_bytes": stderr_path.stat().st_size,
            "raw_stdout": stdout_path.name,
            "raw_stderr": stderr_path.name,
            "direct_child_only": True,
        }
        _atomic_json(_result_path(run_dir), result)
    return result


def read_status(state_dir, run_id):
    run_dir = _run_directory(state_dir, run_id)
    marker = run_dir / MARKER
    if not marker.is_file():
        raise ValueError("not a runner-owned run directory")
    return json.loads(_result_path(run_dir).read_text(encoding="utf-8"))


def cleanup(state_dir, run_id):
    run_dir = _run_directory(state_dir, run_id)
    if not (run_dir / MARKER).is_file():
        raise ValueError("not a runner-owned run directory")
    for child in run_dir.iterdir():
        if child.is_file():
            child.unlink()
        else:
            raise ValueError("unexpected nested runtime directory")
    run_dir.rmdir()


def _parser():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    run = subparsers.add_parser("run")
    run.add_argument("--timeout", type=float, required=True)
    run.add_argument("--state-dir", type=Path, required=True)
    run.add_argument("argv", nargs=argparse.REMAINDER)
    for action in ("status", "cleanup"):
        item = subparsers.add_parser(action)
        item.add_argument("--state-dir", type=Path, required=True)
        item.add_argument("run_id")
    return parser


def main():
    args = _parser().parse_args()
    try:
        if args.action == "run":
            argv = args.argv[1:] if args.argv[:1] == ["--"] else args.argv
            result = run_child(args.timeout, args.state_dir, argv)
        elif args.action == "status":
            result = read_status(args.state_dir, args.run_id)
        else:
            cleanup(args.state_dir, args.run_id)
            result = {"status": "CLEANED", "run_id": args.run_id}
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "RUNNER_ERROR", "reason": str(error)}))
        return 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
