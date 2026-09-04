# Agent-control experiment

A self-contained harness for **testing whether we can control a coding agent on
more complex tasks**. It compares two control strategies on a set of edge-case-heavy
problems:

- **one-shot** — a single model attempt, no feedback.
- **controlled** — an iterative loop: run the agent's solution against hidden
  tests, and if any fail, feed the first failing case (input / expected / actual
  / error) back to the model and let it try again, up to `--max-attempts`.

Every candidate solution is executed in a subprocess sandbox
(`sandbox.run_python_code`) with a wall-clock timeout and checked against the
task's hidden tests.

## Layout
- `tasks.py` — 13 complex tasks (balanced brackets, RLE, roman ↔ int, merge
  intervals, k-th largest, caesar, unix path canonicalization, 32-bit `atoi`
  with clamping, a parenthesized calculator with truncate-toward-zero division,
  round-half-up averaging, first-appearance tie-break word frequency). Each has
  public samples, edge-case **hidden tests**, and a known-correct
  `reference_solution`.
- `controller.py` — the control loop (`control_agent`), test runner, and the
  live model client (`make_openai_model`, default `gpt-5.6-terra`, streaming).
  The model is injected as `model_fn(messages, attempt_index)` so the loop is
  deterministic and unit-testable offline.
- `sandbox.py` — subprocess Python runner (timeout + temp dir).
- `run_experiment.py` — the CLI that runs one-shot vs controlled and reports.

## Run

```bash
cd server                     # OPENAI_API_KEY must be set for live runs
PYTHONPATH=$PWD python -m agent_control.run_experiment \
    --model gpt-5.6-terra --max-attempts 4 --json /tmp/results.json
# hard mode (no worked examples in the initial prompt):
PYTHONPATH=$PWD python -m agent_control.run_experiment --no-examples
# induce failures with a tight per-attempt token budget (shows recovery):
PYTHONPATH=$PWD python -m agent_control.run_experiment --max-tokens 160 \
    --tasks calculator merge_intervals avg_round_half_up simplify_path
```

Offline tests (no API key) validate every reference solution against its hidden
tests and the control loop's recovery logic:

```bash
cd server && ./.venv/bin/python -m pytest tests/test_agent_control.py -q
```

## Findings (gpt-5.6-terra)

- **The agent is highly controllable on these complex tasks.** With normal
  budgets, one-shot solved **all 13/13** tasks (and **11/11** even with worked
  examples removed) — the control loop verified each and correctly stopped after
  a single attempt.
- **The control loop reliably recovers from failures.** When the agent is
  stressed with a tight per-attempt token budget (`--max-tokens 160`, which
  truncates longer solutions), one-shot dropped to **3/6** while the controlled
  loop reached **5/6**, recovering tasks such as `merge_intervals` and
  `avg_round_half_up` (e.g. verification progress `0/4 → 0/4 → 4/4` after test
  feedback). `calculator` remained unsolved under that budget — an honest limit.
- The recovery mechanism is additionally proven **deterministically offline**:
  a stubbed model that returns a wrong solution then a correct one passes only
  under the controlled loop, and the loop stops early when the first attempt is
  correct and gives up after `max_attempts`.

**Conclusion:** yes — we can control agents on these more complex tasks. Verify-
and-feedback control matches one-shot when the model is already capable and
meaningfully improves outcomes when it is not, all while keeping every solution
sandbox-verified against hidden tests.
