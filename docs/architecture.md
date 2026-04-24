# MindClaw Architecture

## Goal

MindClaw is intended to be a multi-agent orchestration shell that coordinates teams of autonomous agents while delegating single-agent execution to a runtime core.

## Design Principles

- keep team state and orchestration explicit
- keep runtime execution pluggable
- separate shell responsibilities from runtime responsibilities
- optimize for open-source readability and extensibility

## Proposed Layers

### 1. Shell Layer

Responsible for:

- CLI entrypoints
- orchestration flows
- team lifecycle
- task graph management
- message routing
- board and monitoring surfaces

### 2. Core Coordination Layer

Responsible for:

- team models
- task models
- message/event models
- worker lifecycle policies
- workspace management
- orchestration state transitions

### 3. Runtime Adapter Layer

Responsible for:

- translating MindClaw worker intent into runtime-specific bootstrapping
- passing agent identity, task context, and workspace context
- collecting runtime status in a normalized format

### 4. Runtime Layer

Responsible for:

- single-agent execution
- tools
- memory
- sessions
- model/provider interaction
- runtime-local delegation

## Architectural Boundary

MindClaw should remain the source of truth for:

- team membership
- task status
- inter-agent messaging
- workspace ownership
- orchestration state

The runtime should remain the source of truth for:

- conversation/session state
- memory and skills
- tool execution details
- provider/model routing

## Execution Flow

```text
User goal
  -> MindClaw CLI
    -> Orchestrator creates team state
      -> Worker bootstrap context is created
        -> Runtime adapter launches worker runtime
          -> Worker executes task in isolated workspace
            -> Worker reports status/messages back to MindClaw
```

## Near-Term Implementation Plan

1. define the domain models
2. define the runtime adapter interface
3. add a local-only orchestration MVP
4. add one runtime integration path
5. build observability and demos
