# MindClaw

[English](./README.md) | [简体中文](./README.zh-CN.md)

**Build autonomous agent teams on top of a powerful runtime core.**

MindClaw is an open-source multi-agent orchestration shell for autonomous coding teams.
It is designed to combine two things that are usually separated:

- powerful single-agent execution
- explicit team-level coordination

MindClaw aims to give you a practical way to build leader-worker agent systems that can split work, isolate execution, exchange messages, track task state, and plug into different runtime engines underneath.

> If this direction looks useful to you, consider giving the project a star to follow its development.

## Why MindClaw

Most agent systems lean too far in one direction:

- some are strong at single-agent execution but weak at team coordination
- some are strong at orchestration but weak at runtime intelligence
- some are powerful internally but expose very little explicit team state

MindClaw is being built to bridge that gap.

The goal is not just to run more agents.
The goal is to make multi-agent work understandable, composable, and open-source friendly.

## What MindClaw Is Trying to Do

With MindClaw, you should eventually be able to:

- create a leader + worker agent team
- split work into task graphs and execution stages
- isolate each worker in its own workspace
- route messages between agents through structured state
- observe progress from a unified shell or board
- plug different runtime engines under the same orchestration model

## Core Design Ideas

### 1. Team state should be explicit

MindClaw treats team membership, tasks, messages, workspaces, and lifecycle as first-class orchestration state.

### 2. Runtime execution should be pluggable

MindClaw should not be locked to a single agent runtime. It should be able to sit above different execution engines through a runtime adapter layer.

### 3. Isolation should be built in

Workers should be able to operate in separate workspaces so parallel execution is easier to reason about and safer to manage.

### 4. Open-source readability matters

The repository is being organized from the root as a clean standalone project so contributors can understand the system boundary, roadmap, and implementation direction quickly.

## High-Level Architecture

```text
User
  -> MindClaw CLI / Shell
    -> Orchestrator
      -> Team / Tasks / Messaging / Workspaces
        -> Runtime Adapter
          -> Agent Runtime
            -> Tools / Memory / Sessions / Models
```

At a high level:

- **MindClaw Shell** owns orchestration and team coordination
- **Runtime Adapter** translates worker intent into a concrete runtime
- **Agent Runtime** owns single-agent execution, memory, tools, and sessions

For more detail, see `docs/architecture.md`.

## Planned Capabilities

- team orchestration
- worker spawning and lifecycle management
- task dependency tracking
- isolated git workspaces
- inter-agent messaging
- runtime adapter layer
- board and monitoring UI
- reusable templates for common workflows
- runtime capability reporting and observability

## Example Use Cases

### Autonomous software engineering

One leader agent plans work, multiple workers implement isolated parts of a codebase, and the shell tracks progress and ownership.

### Research swarms

Different workers explore different hypotheses, tools, or experiment branches while the shell keeps the team state coherent.

### Long-running agent workflows

MindClaw is intended to support workflows where agent sessions, task state, and execution boundaries need to stay understandable over time.

### Reusable team templates

The long-term goal is to support reusable archetypes for common coordination patterns, such as engineering teams, research teams, and domain-specific swarms.

## Project Status

MindClaw is currently in **early-stage development**.

The current repository focus is:

- establishing the public project structure
- defining the architecture boundary
- creating the minimal CLI and package scaffold
- preparing the core orchestration model

This means the repo is already shaped for open-source development, but the deeper orchestration and runtime integration layers are still under active construction.

## Quick Start

MindClaw is still being scaffolded, but the repository is already installable.

```bash
git clone https://github.com/wanlixing-dream/MindClaw.git
cd MindClaw
pip install -e .
mindclaw --help
mindclaw doctor
```

## Repository Structure

```text
MindClaw/
├── README.md
├── README.zh-CN.md
├── ROADMAP.md
├── docs/
│   └── architecture.md
├── mindclaw/
│   ├── __init__.py
│   ├── __main__.py
│   └── cli/
├── tests/
└── pyproject.toml
```

## Roadmap

The project is currently moving through these early phases:

- **Phase 0** — repository foundation
- **Phase 1** — core domain model
- **Phase 2** — local orchestration MVP
- **Phase 3** — runtime integration

See `ROADMAP.md` for the full phase breakdown.

## Documentation

- `docs/architecture.md` — system architecture draft
- `ROADMAP.md` — implementation phases and delivery plan

More documentation, diagrams, and examples will be added as the core modules stabilize.

## Contributing

Contributions, feedback, architecture discussions, and experiments are welcome.

In the current phase, the most useful contributions are:

- architecture feedback
- naming and API design feedback
- orchestration model review
- early implementation experiments

A dedicated contribution guide will be added as the project stabilizes.

## License

MIT

## Acknowledgements

MindClaw is being developed as an original project inspired by the broader open-source agent ecosystem and practical work on agent runtimes, orchestration systems, and autonomous workflows.
