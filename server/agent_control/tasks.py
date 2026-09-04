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
    {
        "id": "simplify_path",
        "title": "Simplify a Unix path",
        "statement": (
            "Read a Unix-style absolute path and print its canonical form: '.' means "
            "current directory, '..' goes up one level (no-op at root), collapse "
            "repeated slashes, and no trailing slash except the root '/'."
        ),
        "public_samples": [
            {"input": "/home//foo/\n", "output": "/home/foo\n"},
            {"input": "/a/./b/../../c/\n", "output": "/c\n"},
        ],
        "hidden_tests": [
            {"input": "/\n", "output": "/\n"},
            {"input": "/../\n", "output": "/\n"},
            {"input": "/a/../../b\n", "output": "/b\n"},
            {"input": "/a//b////c/d//././/..\n", "output": "/a/b/c\n"},
            {"input": "/...\n", "output": "/...\n"},
        ],
        "reference_solution": (
            "p = input().strip()\n"
            "parts = [x for x in p.split('/') if x not in ('', '.')]\n"
            "st = []\n"
            "for x in parts:\n"
            "    if x == '..':\n"
            "        if st:\n"
            "            st.pop()\n"
            "    else:\n"
            "        st.append(x)\n"
            "print('/' + '/'.join(st))\n"
        ),
    },
    {
        "id": "myatoi",
        "title": "String to 32-bit integer (atoi)",
        "statement": (
            "Read one line and convert it to an integer like C's atoi: skip leading "
            "spaces, then an optional single '+' or '-', then digits until a "
            "non-digit (ignore the rest). If there are no digits, the value is 0. "
            "Clamp the result to the signed 32-bit range [-2147483648, 2147483647] "
            "and print it."
        ),
        "public_samples": [
            {"input": "   -42abc\n", "output": "-42\n"},
            {"input": "4193 with words\n", "output": "4193\n"},
        ],
        "hidden_tests": [
            {"input": "words and 987\n", "output": "0\n"},
            {"input": "-91283472332\n", "output": "-2147483648\n"},
            {"input": "91283472332\n", "output": "2147483647\n"},
            {"input": "+1\n", "output": "1\n"},
            {"input": "  +0 123\n", "output": "0\n"},
        ],
        "reference_solution": (
            "s = input()\n"
            "i, n = 0, len(s)\n"
            "while i < n and s[i] == ' ':\n"
            "    i += 1\n"
            "sign = 1\n"
            "if i < n and s[i] in '+-':\n"
            "    if s[i] == '-':\n"
            "        sign = -1\n"
            "    i += 1\n"
            "num = 0\n"
            "while i < n and s[i].isdigit():\n"
            "    num = num * 10 + int(s[i])\n"
            "    i += 1\n"
            "num *= sign\n"
            "num = max(-2147483648, min(2147483647, num))\n"
            "print(num)\n"
        ),
    },
    {
        "id": "calculator",
        "title": "Arithmetic expression evaluator",
        "statement": (
            "Evaluate an arithmetic expression of non-negative integers with the "
            "operators + - * / and parentheses. Standard precedence; '/' is integer "
            "division that truncates toward zero (e.g. 7/(3-5) = -3). Spaces may "
            "appear anywhere. Print the integer result."
        ),
        "public_samples": [
            {"input": "3+2*2\n", "output": "7\n"},
            {"input": "(1+2)*3\n", "output": "9\n"},
        ],
        "hidden_tests": [
            {"input": "14/3\n", "output": "4\n"},
            {"input": "7/(3-5)\n", "output": "-3\n"},
            {"input": "2*(3+4*(5-2))\n", "output": "30\n"},
            {"input": "100/7/2\n", "output": "7\n"},
            {"input": " (2+3) * (4-1) \n", "output": "15\n"},
        ],
        "reference_solution": (
            "s = input().replace(' ', '')\n"
            "pos = 0\n"
            "def peek():\n"
            "    return s[pos] if pos < len(s) else ''\n"
            "def expr():\n"
            "    global pos\n"
            "    val = term()\n"
            "    while peek() in ('+', '-'):\n"
            "        op = s[pos]; pos += 1\n"
            "        r = term()\n"
            "        val = val + r if op == '+' else val - r\n"
            "    return val\n"
            "def term():\n"
            "    global pos\n"
            "    val = factor()\n"
            "    while peek() in ('*', '/'):\n"
            "        op = s[pos]; pos += 1\n"
            "        r = factor()\n"
            "        if op == '*':\n"
            "            val = val * r\n"
            "        else:\n"
            "            q = abs(val) // abs(r)\n"
            "            val = -q if (val < 0) != (r < 0) else q\n"
            "    return val\n"
            "def factor():\n"
            "    global pos\n"
            "    if peek() == '(':\n"
            "        pos += 1\n"
            "        val = expr()\n"
            "        pos += 1\n"
            "        return val\n"
            "    num = 0\n"
            "    while peek().isdigit():\n"
            "        num = num * 10 + int(s[pos]); pos += 1\n"
            "    return num\n"
            "print(expr())\n"
        ),
    },
    {
        "id": "avg_round_half_up",
        "title": "Average with round-half-up to 2 decimals",
        "statement": (
            "First line: integer n. Second line: n integers. Print their average "
            "rounded to exactly 2 decimal places using round-half-up (ties round "
            "AWAY from zero, e.g. 0.125 -> 0.13, -0.125 -> -0.13). Always show 2 "
            "decimal places."
        ),
        "public_samples": [
            {"input": "2\n1 2\n", "output": "1.50\n"},
            {"input": "3\n1 1 2\n", "output": "1.33\n"},
        ],
        "hidden_tests": [
            {"input": "8\n1 0 0 0 0 0 0 0\n", "output": "0.13\n"},
            {"input": "2\n1 4\n", "output": "2.50\n"},
            {"input": "8\n-1 0 0 0 0 0 0 0\n", "output": "-0.13\n"},
            {"input": "4\n1 2 3 4\n", "output": "2.50\n"},
        ],
        "reference_solution": (
            "from decimal import Decimal, ROUND_HALF_UP\n"
            "n = int(input())\n"
            "a = list(map(int, input().split()))\n"
            "avg = Decimal(sum(a)) / Decimal(n)\n"
            "print(avg.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))\n"
        ),
    },
    {
        "id": "most_frequent_word",
        "title": "Most frequent word (first-appearance tie-break)",
        "statement": (
            "Read one line of lowercase words separated by single spaces. Print the "
            "most frequent word. If several words tie for the highest count, print "
            "the one that appears EARLIEST in the input (not the lexicographically "
            "smallest)."
        ),
        "public_samples": [
            {"input": "a b a b\n", "output": "a\n"},
            {"input": "cat dog cat\n", "output": "cat\n"},
        ],
        "hidden_tests": [
            {"input": "b a b a\n", "output": "b\n"},
            {"input": "z y x\n", "output": "z\n"},
            {"input": "the the a a a\n", "output": "a\n"},
            {"input": "dog cat cat dog bird\n", "output": "dog\n"},
        ],
        "reference_solution": (
            "from collections import Counter\n"
            "words = input().split()\n"
            "counts = Counter(words)\n"
            "best = max(words, key=lambda w: (counts[w], -words.index(w)))\n"
            "print(best)\n"
        ),
    },
]

TASKS_BY_ID: Dict[str, Dict[str, Any]] = {t["id"]: t for t in TASKS}
TASK_IDS: List[str] = [t["id"] for t in TASKS]


def get_task(task_id: str) -> Dict[str, Any]:
    return TASKS_BY_ID[task_id]
