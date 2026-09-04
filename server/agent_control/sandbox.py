"""Subprocess sandbox for running agent-authored Python (self-contained).

A fresh temp dir, captured stdout/stderr, and a hard wall-clock timeout. Not a
security boundary — a Docker/Cloudflare runner is the eventual target — but
enough to run and verify candidate solutions safely-ish during the experiment.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from typing import Optional

DEFAULT_TIMEOUT_SECONDS = 8.0


@dataclass
class CodeRunResult:
    ok: bool
    stdout: str = ""
    stderr: str = ""
    returncode: Optional[int] = None
    timed_out: bool = False
    duration_seconds: float = 0.0


def run_python_code(
    code: str, stdin: str = "", *, timeout: float = DEFAULT_TIMEOUT_SECONDS
) -> CodeRunResult:
    start = time.perf_counter()
    with tempfile.TemporaryDirectory() as work_dir:
        script_path = os.path.join(work_dir, "solution.py")
        with open(script_path, "w", encoding="utf-8") as handle:
            handle.write(code or "")
        try:
            proc = subprocess.run(
                [sys.executable, script_path],
                input=stdin,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=work_dir,
            )
            return CodeRunResult(
                ok=(proc.returncode == 0),
                stdout=proc.stdout,
                stderr=proc.stderr,
                returncode=proc.returncode,
                duration_seconds=time.perf_counter() - start,
            )
        except subprocess.TimeoutExpired:
            return CodeRunResult(
                ok=False,
                stderr="timeout",
                timed_out=True,
                duration_seconds=time.perf_counter() - start,
            )
