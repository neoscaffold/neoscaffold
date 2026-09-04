"""Agent-control experiment.

A self-contained harness for testing whether we can *control* a coding agent on
more complex tasks: an iterative control loop that runs the agent's solution
against hidden tests and feeds failures back for another attempt, compared
against a single one-shot attempt.

Offline/deterministic by default (inject a model function) so the control loop
is unit-testable without an API key; a live OpenAI client (default
``gpt-5.6-terra``) drives the real experiment.
"""
