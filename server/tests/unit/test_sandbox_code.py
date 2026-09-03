"""Tests for the sandboxed code runner (server.harness.sandbox.run_python_code)."""

from server.harness.sandbox import run_python_code


def test_run_python_code_reads_stdin_and_prints():
    result = run_python_code("a,b=map(int,input().split())\nprint(a+b)\n", stdin="2 3\n")
    assert result.ok
    assert result.stdout.strip() == "5"
    assert result.returncode == 0
    assert not result.timed_out


def test_run_python_code_nonzero_exit_on_error():
    result = run_python_code("raise SystemExit(2)\n")
    assert not result.ok
    assert result.returncode == 2


def test_run_python_code_captures_stderr():
    result = run_python_code("import sys\nsys.stderr.write('boom')\nraise ValueError('x')\n")
    assert not result.ok
    assert "boom" in result.stderr or "ValueError" in result.stderr


def test_run_python_code_times_out():
    result = run_python_code("import time\ntime.sleep(5)\n", timeout=0.3)
    assert not result.ok
    assert result.timed_out
