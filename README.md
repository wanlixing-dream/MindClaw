# MindClaw

[English](./README.md) | [简体中文](./README.zh-CN.md)

**Hermes is the most capable solo agent. MindClaw makes it a team.**

MindClaw is a multi-agent orchestration layer built on top of [Hermes Agent](https://github.com/NousResearch/hermes-agent). It takes Hermes' powerful single-agent runtime — 40+ tools, self-improving memory, any model provider — and adds structured team coordination: task decomposition, dependency scheduling, parallel execution, and real-time observability.

Inspired by the orchestration patterns of [ClawTeam](https://github.com/HKUDS/ClawTeam) and powered by the execution engine of [Hermes](https://github.com/NousResearch/hermes-agent).

> If this direction looks useful to you, consider giving the project a star to follow its development.

---

## The Problem

You're using Hermes for a complex project. You type your goal. The agent works for 30 minutes, the context window fills up, it loses track, starts going in circles.

You wish you could split the work across multiple agents — one doing backend, one doing frontend, one writing tests — but:

- Hermes' built-in `delegate_task` is **blocking** — the parent agent waits for all children to finish, you can't see intermediate progress
- It's **ephemeral** — if anything crashes, all state is lost
- It's **flat** — only parent-child relationships, no structured task graphs or team-level coordination

Other multi-agent frameworks (CrewAI, AutoGen) solve coordination but their agents are just LLM API wrappers — no terminal, no file system, no git, no real developer toolchain.

## The Solution

```bash
mindclaw run "Build a REST API with auth, a React frontend, and integration tests"
```

MindClaw decomposes your goal into a task graph, spawns a team of Hermes agents, schedules tasks by dependency order, and streams progress in real-time. Each agent gets a focused context window, dedicated tools, and a clear scope.

```
🧠 Decomposing goal into tasks...
  ├── T1: Design API schema and data models
  ├── T2: Implement JWT authentication (depends on T1)
  ├── T3: Build CRUD endpoints (depends on T1)
  ├── T4: Create React frontend (depends on T1)
  └── T5: Write integration tests (depends on T2, T3, T4)

🚀 Phase: execute
  ┌─────────────┬──────────┬───────────┐
  │ Task        │ Agent    │ Status    │
  ├─────────────┼──────────┼───────────┤
  │ T1: Schema  │ worker-1 │ ✅ done    │
  │ T2: Auth    │ worker-2 │ 🔄 running │
  │ T3: CRUD    │ worker-3 │ 🔄 running │
  │ T4: React   │ worker-4 │ 🔄 running │
  │ T5: Tests   │ —        │ ⏳ blocked │
  └─────────────┴──────────┴───────────┘
```

---

## Why MindClaw

### hermes alone vs hermes + MindClaw

| | `hermes` alone | `hermes` + MindClaw |
|---|---|---|
| Complex tasks | One agent handles everything, context overflows | Auto-split into sub-tasks, each agent stays focused |
| Parallel execution | `delegate_task` blocks, parent agent idles | True parallel, non-blocking, real-time observable |
| Crash recovery | All state lost, start over | Task state persisted, resume from checkpoint |
| Progress visibility | Can't see what sub-agents are doing | Live task board + agent activity stream |
| Team coordination | Only parent-child relationship | Leader-worker structure, inter-agent messaging |
| Getting started | Already a Hermes user: zero cost | `pip install mindclaw` → `mindclaw run` |

### Why not just use X?

**"Why not Hermes' built-in `delegate_task`?"**
`delegate_task` is in-process, short-lived delegation — the parent blocks, no persistence, no observability. Good for simple sub-tasks. MindClaw is persistent team orchestration — task graphs, dependency scheduling, parallel execution, state recovery. Built for complex projects that need multiple agents collaborating over time.

**"Why not ClawTeam?"**
ClawTeam manages agents as black-box CLI processes via tmux. MindClaw integrates Hermes at the Python API level — it controls each worker's model, tools, context, and iteration budget. No tmux, no extra CLI dependencies.

**"Why not CrewAI / AutoGen?"**
Their agents can only call LLM APIs. Each MindClaw worker is a full Hermes agent — with terminal, file system, browser, memory, and skills. It doesn't simulate a developer's toolchain. It **is** the toolchain.

---

## Architecture

```text
User Goal
  → MindClaw CLI
    → Decomposer (LLM-powered task splitting)
      → TaskGraph (DAG of dependent tasks)
        → Scheduler (topological ordering + readiness detection)
          → WorkerPool (Hermes AIAgent instances)
            → Tracker (real-time status + persistence)
```

**Key design decisions:**

- **Pipeline architecture** — each module (decomposer, scheduler, worker pool, tracker) is independent with clear interfaces. Replace any piece without touching the others.
- **Deep runtime integration** — workers are Hermes `AIAgent` objects instantiated via Python API, not black-box CLI processes. MindClaw controls model selection, toolsets, system prompts, and iteration budgets per worker.
- **Phase-driven orchestration** — inspired by ClawTeam's harness model: plan → execute → verify. Each phase has gate conditions that must pass before advancing.

---

## Quick Start

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
├── ROADMAP.md
├── docs/
│   └── architecture.md
├── mindclaw/
│   ├── cli/              # CLI commands
│   ├── decomposer/       # LLM-powered task decomposition
│   ├── scheduler/        # DAG topological scheduling
│   ├── worker_pool/      # Worker lifecycle management
│   ├── tracker/          # Real-time status tracking
│   ├── orchestrator/     # Pipeline controller
│   ├── team/             # Team and member models
│   ├── task/             # Task state and dependencies
│   ├── messaging/        # Inter-agent messaging
│   ├── workspace/        # Workspace isolation
│   ├── runtime/          # Runtime adapter interface
│   └── state/            # Persistent state store
├── tests/
└── pyproject.toml
```

## Roadmap

- **Phase 0** ✅ — repository foundation
- **Phase 1** ✅ — core domain model
- **Phase 2** 🔄 — local orchestration MVP (decomposer + scheduler + mock workers)
- **Phase 3** — Hermes runtime integration
- **Phase 4** — developer experience and templates

See `ROADMAP.md` for the full phase breakdown.

## Documentation

- `docs/architecture.md` — system architecture
- `ROADMAP.md` — implementation phases

## Contributing

Contributions, feedback, architecture discussions, and experiments are welcome.

## License

MIT

## Acknowledgements

MindClaw is built on top of the [Hermes Agent](https://github.com/NousResearch/hermes-agent) runtime by Nous Research, and draws orchestration design inspiration from [ClawTeam](https://github.com/HKUDS/ClawTeam) by HKUDS.
