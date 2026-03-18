# Hermes Agent + CaMeL

A publishable Hermes fork with CaMeL trust boundaries integrated into the runtime.

This fork is designed for operators who want the Hermes agent loop to distinguish between:

- trusted control: system prompt, approved skills, real user turns
- untrusted data: tool outputs, retrieved web content, browser content, files, session recall, MCP data

Sensitive tools are authorized against a trusted operator plan instead of instructions embedded in untrusted content.

## What This Fork Changes

This fork adds a runtime security layer centered on `agent/camel_guard.py` and the Hermes tool loop.

Main additions:

- trusted operator plan extraction from real user turns
- provenance-aware wrapping for untrusted tool outputs
- per-turn security envelope injected into the effective system context
- capability gating for sensitive tools
- gating for automatic memory flush and synthetic continuation turns
- stripping of internal CaMeL metadata before provider API calls

Sensitive capabilities gated by this integration include:

- terminal and command execution
- file mutation
- persistent memory writes
- external messaging
- scheduled actions
- skill mutation
- delegation and subagents
- browser interaction and selected external side effects

Read-only actions such as `send_message(action="list")` and `cronjob(action="list")` remain allowed.

## Threat Model

This fork is built to reduce indirect prompt injection risk in the normal Hermes workflow.

The target attack pattern is:

1. Hermes retrieves untrusted content from the web, a browser session, a file, session recall, or an MCP server.
2. That content contains hidden or explicit instructions such as "ignore previous instructions", "send a message", or "run this terminal command".
3. The model attempts to treat that content as control rather than evidence.
4. Hermes blocks the side effect unless the trusted operator plan explicitly authorizes that capability.

## Architecture

### 1. Trusted operator plan

Hermes derives trusted control from real user turns only. Synthetic system-control turns do not pollute the trusted plan.

### 2. Untrusted data channel

Tool outputs are treated as untrusted data by default and wrapped with provenance metadata before they re-enter model context.

### 3. Security envelope

Every turn includes a compact CaMeL security envelope describing the trusted goal, authorized capabilities, and current untrusted source inventory.

### 4. Capability gating

Side-effecting tools are checked against the trusted operator plan before execution.

### 5. Provider hygiene

Internal CaMeL metadata is removed before messages are sent to the configured model provider.

## Validation

### Hermes runtime compatibility

Validated against the Hermes runtime suite:

```bash
pytest -q tests/agent/test_camel_guard.py tests/test_run_agent.py
```

Result:

- `205 passed`

### Paper-aligned indirect injection benchmark

A Hermes-specific micro-benchmark aligned to the CaMeL paper/repo `important_instructions` attack shape was also run.

Observed outcomes:

- indirect terminal exfiltration attempt: blocked
- indirect external messaging attempt: blocked
- indirect persistent-memory write attempt: blocked
- indirect browser side-effect attempt: blocked
- explicitly authorized terminal use: allowed
- safe read-only list action: allowed

Detailed notes:

- [`docs/camel-benchmark.md`](docs/camel-benchmark.md)

## Install

### Fresh install from this fork

```bash
curl -fsSL https://raw.githubusercontent.com/nativ3ai/hermes-agent-camel/main/scripts/install.sh | bash
```

Then reload your shell and start Hermes:

```bash
source ~/.zshrc
hermes
```

### Existing upstream Hermes checkout

Use the `camelup` installer repo to apply this fork or switch an existing checkout to the CaMeL build.

## Developer setup

```bash
git clone https://github.com/nativ3ai/hermes-agent-camel.git
cd hermes-agent-camel
git submodule update --init mini-swe-agent
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
uv pip install -e "./mini-swe-agent"
pytest -q tests/agent/test_camel_guard.py tests/test_run_agent.py
```

## Files Of Interest

- `agent/camel_guard.py`
- `run_agent.py`
- `hermes_cli/config.py`
- `tests/agent/test_camel_guard.py`
- `tests/test_run_agent.py`
- `docs/camel-benchmark.md`

## Scope

This fork is inspired by the CaMeL paper and adapted to Hermes' runtime, tool semantics, and conversation loop.

It is not presented as a full reproduction of the paper's AgentDojo benchmark matrix. The benchmark here is Hermes-specific and focused on runtime trust boundaries plus paper-aligned indirect injection scenarios.

## Upstream Relation

This repository tracks Hermes Agent from Nous Research and carries the CaMeL integration as a focused runtime security extension.

- Upstream Hermes: https://github.com/NousResearch/hermes-agent
- CaMeL paper: https://arxiv.org/abs/2503.18813
- CaMeL repo: https://github.com/google-research/camel-prompt-injection
- Upstream PR: https://github.com/NousResearch/hermes-agent/pull/1992

For the original general-purpose Hermes README, see [`docs/upstream-readme.md`](docs/upstream-readme.md).
