"""Problem set for the agent-swarm integration test.

Each entry is keyed by a Codeforces problem id (the ones the user listed) and
carries a self-contained, verifiable coding task: a statement, sample I/O, and a
known-correct ``reference_solution``. The reference solution lets the OFFLINE
coder produce deterministic, verifiable output (so automated tests need no API
key), while the live OpenAI coder ignores it and writes its own solution that is
then checked against the same samples.

Note: the statements here are integration-test workloads assigned to each
Codeforces id, not the original (April-Fools) problem statements — the goal is
to exercise 10 concurrent solve/verify agents, not to reproduce those puzzles.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

PROBLEMS: Dict[str, Dict[str, Any]] = {
    "codeforces/409/F": {
        "codeforces_id": "codeforces/409/F",
        "title": "Sum of two integers",
        "statement": "Read two space-separated integers a and b on one line. Print a + b.",
        "samples": [
            {"input": "2 3\n", "output": "5\n"},
            {"input": "10 -4\n", "output": "6\n"},
        ],
        "reference_solution": "a, b = map(int, input().split())\nprint(a + b)\n",
    },
    "codeforces/784/A": {
        "codeforces_id": "codeforces/784/A",
        "title": "Reverse a string",
        "statement": "Read a single line string s. Print s reversed.",
        "samples": [
            {"input": "hello\n", "output": "olleh\n"},
            {"input": "abc\n", "output": "cba\n"},
        ],
        "reference_solution": "s = input()\nprint(s[::-1])\n",
    },
    "codeforces/952/A": {
        "codeforces_id": "codeforces/952/A",
        "title": "Maximum of a list",
        "statement": "First line: integer n. Second line: n space-separated integers. Print the maximum.",
        "samples": [
            {"input": "3\n1 5 2\n", "output": "5\n"},
            {"input": "1\n-7\n", "output": "-7\n"},
        ],
        "reference_solution": "n = int(input())\nprint(max(map(int, input().split())))\n",
    },
    "codeforces/656/A": {
        "codeforces_id": "codeforces/656/A",
        "title": "Even or odd",
        "statement": "Read integer n. Print 'even' if it is even, otherwise 'odd'.",
        "samples": [
            {"input": "4\n", "output": "even\n"},
            {"input": "7\n", "output": "odd\n"},
        ],
        "reference_solution": "n = int(input())\nprint('even' if n % 2 == 0 else 'odd')\n",
    },
    "codeforces/1145/B": {
        "codeforces_id": "codeforces/1145/B",
        "title": "Greatest common divisor",
        "statement": "Read two space-separated integers a and b. Print gcd(a, b).",
        "samples": [
            {"input": "12 18\n", "output": "6\n"},
            {"input": "7 5\n", "output": "1\n"},
        ],
        "reference_solution": "import math\na, b = map(int, input().split())\nprint(math.gcd(a, b))\n",
    },
    "codeforces/656/D": {
        "codeforces_id": "codeforces/656/D",
        "title": "Factorial",
        "statement": "Read integer n (0 <= n <= 12). Print n! (the factorial of n).",
        "samples": [
            {"input": "5\n", "output": "120\n"},
            {"input": "0\n", "output": "1\n"},
        ],
        "reference_solution": "import math\nprint(math.factorial(int(input())))\n",
    },
    "codeforces/290/B": {
        "codeforces_id": "codeforces/290/B",
        "title": "Count vowels",
        "statement": "Read a lowercase line string s. Print the number of vowels (a, e, i, o, u).",
        "samples": [
            {"input": "hello\n", "output": "2\n"},
            {"input": "xyz\n", "output": "0\n"},
        ],
        "reference_solution": "s = input()\nprint(sum(c in 'aeiou' for c in s))\n",
    },
    "codeforces/784/D": {
        "codeforces_id": "codeforces/784/D",
        "title": "Fibonacci number",
        "statement": "Read integer n (1 <= n <= 30). Print the n-th Fibonacci number where F1 = 1 and F2 = 1.",
        "samples": [
            {"input": "1\n", "output": "1\n"},
            {"input": "7\n", "output": "13\n"},
        ],
        "reference_solution": "n = int(input())\na, b = 1, 1\nfor _ in range(n - 1):\n    a, b = b, a + b\nprint(a)\n",
    },
    "codeforces/290/A": {
        "codeforces_id": "codeforces/290/A",
        "title": "Palindrome check",
        "statement": "Read a line string s. Print 'YES' if it is a palindrome, otherwise 'NO'.",
        "samples": [
            {"input": "level\n", "output": "YES\n"},
            {"input": "cat\n", "output": "NO\n"},
        ],
        "reference_solution": "s = input()\nprint('YES' if s == s[::-1] else 'NO')\n",
    },
    "codeforces/171/B": {
        "codeforces_id": "codeforces/171/B",
        "title": "Sum of a list",
        "statement": "First line: integer n. Second line: n space-separated integers. Print their sum.",
        "samples": [
            {"input": "3\n1 2 3\n", "output": "6\n"},
            {"input": "2\n10 20\n", "output": "30\n"},
        ],
        "reference_solution": "n = int(input())\nprint(sum(map(int, input().split())))\n",
    },
}

# Canonical ordering used when fanning out the swarm.
PROBLEM_IDS: List[str] = list(PROBLEMS.keys())


def get_problem(problem_id: str) -> Optional[Dict[str, Any]]:
    return PROBLEMS.get(problem_id)
