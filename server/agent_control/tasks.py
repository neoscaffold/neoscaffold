"""Complex-task set for the agent-control experiment.

Each task is harder than a one-liner and carries edge-case hidden tests that a
one-shot solution often misses. ``reference_solution`` is a known-correct program
used both to validate the task set itself and by the offline model stub.
"""

from __future__ import annotations

from typing import Any, Dict, List

TASKS: List[Dict[str, Any]] = [
    {
        "id": "balanced_brackets",
        "title": "Balanced brackets",
        "statement": (
            "Read one line containing a string of brackets from among ()[]{}. "
            "Print 'YES' if every bracket is correctly matched and nested, else "
            "'NO'. An empty line is balanced ('YES')."
        ),
        "public_samples": [
            {"input": "()[]{}\n", "output": "YES\n"},
            {"input": "(]\n", "output": "NO\n"},
        ],
        "hidden_tests": [
            {"input": "\n", "output": "YES\n"},
            {"input": "([{}])\n", "output": "YES\n"},
            {"input": "([)]\n", "output": "NO\n"},
            {"input": "(((\n", "output": "NO\n"},
            {"input": ")(\n", "output": "NO\n"},
        ],
        "reference_solution": (
            "import sys\n"
            "s = sys.stdin.readline().rstrip('\\n')\n"
            "pairs = {')': '(', ']': '[', '}': '{'}\n"
            "st = []\n"
            "ok = True\n"
            "for c in s:\n"
            "    if c in '([{':\n"
            "        st.append(c)\n"
            "    elif c in ')]}':\n"
            "        if not st or st.pop() != pairs[c]:\n"
            "            ok = False\n"
            "            break\n"
            "print('YES' if ok and not st else 'NO')\n"
        ),
    },
    {
        "id": "rle_encode",
        "title": "Run-length encoding",
        "statement": (
            "Read one line string s. Output its run-length encoding: for each "
            "maximal run of a repeated character, output the character followed "
            "by the run length. E.g. 'aaabbc' -> 'a3b2c1'. Empty input -> empty output."
        ),
        "public_samples": [
            {"input": "aaabbc\n", "output": "a3b2c1\n"},
            {"input": "abc\n", "output": "a1b1c1\n"},
        ],
        "hidden_tests": [
            {"input": "a\n", "output": "a1\n"},
            {"input": "\n", "output": "\n"},
            {"input": "aaaa\n", "output": "a4\n"},
            {"input": "aabbaa\n", "output": "a2b2a2\n"},
        ],
        "reference_solution": (
            "import sys\n"
            "s = sys.stdin.readline().rstrip('\\n')\n"
            "out = []\n"
            "i = 0\n"
            "while i < len(s):\n"
            "    j = i\n"
            "    while j < len(s) and s[j] == s[i]:\n"
            "        j += 1\n"
            "    out.append(s[i] + str(j - i))\n"
            "    i = j\n"
            "print(''.join(out))\n"
        ),
    },
    {
        "id": "roman_to_int",
        "title": "Roman numeral to integer",
        "statement": (
            "Read an uppercase Roman numeral (I, V, X, L, C, D, M) and print its "
            "integer value. Handles subtractive forms like IV=4, IX=9, CM=900."
        ),
        "public_samples": [
            {"input": "MCMXCIV\n", "output": "1994\n"},
            {"input": "IV\n", "output": "4\n"},
        ],
        "hidden_tests": [
            {"input": "III\n", "output": "3\n"},
            {"input": "IX\n", "output": "9\n"},
            {"input": "LVIII\n", "output": "58\n"},
            {"input": "MMXXIV\n", "output": "2024\n"},
        ],
        "reference_solution": (
            "s = input().strip()\n"
            "v = {'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}\n"
            "total = 0\n"
            "prev = 0\n"
            "for c in reversed(s):\n"
            "    x = v[c]\n"
            "    if x < prev:\n"
            "        total -= x\n"
            "    else:\n"
            "        total += x\n"
            "        prev = x\n"
            "print(total)\n"
        ),
    },
    {
        "id": "merge_intervals",
        "title": "Merge intervals",
        "statement": (
            "First line: integer n. Next n lines each contain two integers l r "
            "(l <= r). Merge all overlapping or touching intervals and print the "
            "merged intervals sorted by start, one 'l r' per line."
        ),
        "public_samples": [
            {"input": "3\n1 3\n2 6\n8 10\n", "output": "1 6\n8 10\n"},
        ],
        "hidden_tests": [
            {"input": "2\n1 4\n4 5\n", "output": "1 5\n"},
            {"input": "1\n5 7\n", "output": "5 7\n"},
            {"input": "2\n1 10\n2 3\n", "output": "1 10\n"},
            {"input": "3\n8 10\n1 3\n2 6\n", "output": "1 6\n8 10\n"},
        ],
        "reference_solution": (
            "import sys\n"
            "data = sys.stdin.read().split()\n"
            "n = int(data[0])\n"
            "nums = list(map(int, data[1:1 + 2 * n]))\n"
            "iv = sorted((nums[i], nums[i + 1]) for i in range(0, 2 * n, 2))\n"
            "res = []\n"
            "for l, r in iv:\n"
            "    if res and l <= res[-1][1]:\n"
            "        res[-1][1] = max(res[-1][1], r)\n"
            "    else:\n"
            "        res.append([l, r])\n"
            "print('\\n'.join(f'{l} {r}' for l, r in res))\n"
        ),
    },
    {
        "id": "kth_largest",
        "title": "K-th largest element",
        "statement": (
            "First line: two integers n and k. Second line: n integers. Print the "
            "k-th largest value (1-indexed; duplicates count by position)."
        ),
        "public_samples": [
            {"input": "5 2\n3 1 4 1 5\n", "output": "4\n"},
        ],
        "hidden_tests": [
            {"input": "5 1\n3 1 4 1 5\n", "output": "5\n"},
            {"input": "5 5\n3 1 4 1 5\n", "output": "1\n"},
            {"input": "3 2\n-1 -2 -3\n", "output": "-2\n"},
            {"input": "4 2\n7 7 7 7\n", "output": "7\n"},
        ],
        "reference_solution": (
            "import sys\n"
            "d = sys.stdin.read().split()\n"
            "n, k = int(d[0]), int(d[1])\n"
            "a = list(map(int, d[2:2 + n]))\n"
            "a.sort(reverse=True)\n"
            "print(a[k - 1])\n"
        ),
    },
    {
        "id": "caesar_cipher",
        "title": "Caesar cipher",
        "statement": (
            "First line: integer shift (0..25). Second line: text of lowercase "
            "letters and spaces. Shift each letter forward by 'shift' (wrapping "
            "z->a); leave spaces unchanged. Print the result."
        ),
        "public_samples": [
            {"input": "3\nabc xyz\n", "output": "def abc\n"},
        ],
        "hidden_tests": [
            {"input": "0\nhello world\n", "output": "hello world\n"},
            {"input": "25\nabc\n", "output": "zab\n"},
            {"input": "1\nz\n", "output": "a\n"},
            {"input": "13\nhello there\n", "output": "uryyb gurer\n"},
        ],
        "reference_solution": (
            "import sys\n"
            "sh = int(sys.stdin.readline())\n"
            "s = sys.stdin.readline().rstrip('\\n')\n"
            "out = ''.join(\n"
            "    chr((ord(c) - 97 + sh) % 26 + 97) if 'a' <= c <= 'z' else c\n"
            "    for c in s\n"
            ")\n"
            "print(out)\n"
        ),
    },
    {
        "id": "int_to_roman",
        "title": "Integer to Roman numeral",
        "statement": (
            "Read an integer n (1 <= n <= 3999) and print its Roman numeral, "
            "using subtractive forms (4=IV, 9=IX, 40=XL, 90=XC, 400=CD, 900=CM)."
        ),
        "public_samples": [
            {"input": "1994\n", "output": "MCMXCIV\n"},
            {"input": "4\n", "output": "IV\n"},
        ],
        "hidden_tests": [
            {"input": "9\n", "output": "IX\n"},
            {"input": "40\n", "output": "XL\n"},
            {"input": "58\n", "output": "LVIII\n"},
            {"input": "3999\n", "output": "MMMCMXCIX\n"},
            {"input": "944\n", "output": "CMXLIV\n"},
        ],
        "reference_solution": (
            "n = int(input())\n"
            "vals = [(1000,'M'),(900,'CM'),(500,'D'),(400,'CD'),(100,'C'),(90,'XC'),\n"
            "        (50,'L'),(40,'XL'),(10,'X'),(9,'IX'),(5,'V'),(4,'IV'),(1,'I')]\n"
            "out = []\n"
            "for v, sym in vals:\n"
            "    while n >= v:\n"
            "        out.append(sym)\n"
            "        n -= v\n"
            "print(''.join(out))\n"
        ),
    },
    {
        "id": "excel_column",
        "title": "Spreadsheet column title",
        "statement": (
            "Read an integer n (n >= 1) and print its spreadsheet column title, "
            "where 1 -> A, 26 -> Z, 27 -> AA, 28 -> AB, and so on (bijective base 26)."
        ),
        "public_samples": [
            {"input": "1\n", "output": "A\n"},
            {"input": "28\n", "output": "AB\n"},
        ],
        "hidden_tests": [
            {"input": "26\n", "output": "Z\n"},
            {"input": "27\n", "output": "AA\n"},
            {"input": "52\n", "output": "AZ\n"},
            {"input": "702\n", "output": "ZZ\n"},
            {"input": "703\n", "output": "AAA\n"},
        ],
        "reference_solution": (
            "n = int(input())\n"
            "out = []\n"
            "while n > 0:\n"
            "    n, r = divmod(n - 1, 26)\n"
            "    out.append(chr(65 + r))\n"
            "print(''.join(reversed(out)))\n"
        ),
    },
]

TASKS_BY_ID: Dict[str, Dict[str, Any]] = {t["id"]: t for t in TASKS}
TASK_IDS: List[str] = [t["id"] for t in TASKS]


def get_task(task_id: str) -> Dict[str, Any]:
    return TASKS_BY_ID[task_id]
