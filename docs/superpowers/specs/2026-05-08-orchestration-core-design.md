# MindClaw 编排核心设计文档

**日期:** 2026-05-08
**范围:** Phase 2 — 本地编排 MVP（全链路 mock）
**状态:** 已确认

---

## 1. 目标

实现 MindClaw 的编排核心流水线，使用户可以通过一行 CLI 命令触发完整的多 agent 任务生命周期：

```bash
mindclaw run "Build a REST API with auth and React frontend"
```

MVP 阶段使用 mock worker（sleep 模拟执行），验证编排逻辑的正确性。后续 Phase 3 替换为真实 Hermes AIAgent。

---

## 2. 架构概览

```text
goal: str
  → Decomposer.decompose(goal) → TaskGraph
  → Scheduler.next_batch(graph) → Iterator[ReadyBatch]
  → WorkerPool.dispatch(task) → WorkerHandle
  → Tracker.update(task_id, status) → GlobalState
```

流水线由 `Orchestrator.run()` 驱动，串联四个独立模块。模块间通过数据类（dataclass）传递，无隐式耦合。

---

## 3. 数据模型

### 3.1 TaskNode

```python
@dataclass
class TaskNode:
    task_id: str
    title: str
    description: str
    depends_on: list[str]   # 前置任务 task_id 列表
    assigned_to: str = ""   # worker 名称（调度后填充）
    status: TaskStatus = TaskStatus.PENDING
```

### 3.2 TaskGraph

```python
@dataclass
class TaskGraph:
    goal: str
    nodes: dict[str, TaskNode]  # task_id → TaskNode

    def roots(self) -> list[TaskNode]: ...
    def dependents(self, task_id: str) -> list[TaskNode]: ...
    def all_completed(self) -> bool: ...
    def validate(self) -> None: ...  # 检测环和悬空依赖
```

### 3.3 TaskStatus

```python
class TaskStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
```

### 3.4 WorkerHandle

```python
@dataclass
class WorkerHandle:
    worker_id: str
    task_id: str
    status: str = "running"
```

---

## 4. 模块设计

### 4.1 decomposer/ — 任务分解器

**职责:** 将用户的高层目标字符串转换为 TaskGraph。

**接口:**
```python
class DecomposerBase(ABC):
    @abstractmethod
    def decompose(self, goal: str) -> TaskGraph: ...
```

**实现:**
- `MockDecomposer` — 返回固定的 TaskGraph（用于测试和 MVP 验证）
- `LLMDecomposer` — 调用 LLM（通过 Hermes AIAgent 或 OpenAI API）分解任务（Phase 3）

MockDecomposer 对任何目标返回一个 3-5 个节点的预设任务图，带依赖关系。

### 4.2 scheduler/ — 拓扑调度器

**职责:** 给定 TaskGraph，按拓扑序调度就绪任务。

**核心逻辑:**
```python
class Scheduler:
    def __init__(self, graph: TaskGraph): ...

    def get_ready_tasks(self) -> list[TaskNode]:
        """返回所有前置任务已完成、状态为 PENDING 的任务"""

    def mark_running(self, task_id: str) -> None: ...
    def mark_completed(self, task_id: str) -> None: ...
    def mark_failed(self, task_id: str) -> None: ...
    def is_finished(self) -> bool: ...
    def has_failed(self) -> bool: ...
```

**关键约束:**
- 检测循环依赖（在 TaskGraph.validate() 中实现）
- 支持并行就绪任务（同一批内的任务可以同时分配给不同 worker）

### 4.3 worker_pool/ — Worker 生命周期管理

**职责:** 管理 worker 的创建、任务分配和回收。

**接口:**
```python
class WorkerBackend(ABC):
    @abstractmethod
    def execute(self, task: TaskNode) -> WorkerHandle: ...

    @abstractmethod
    def poll(self, handle: WorkerHandle) -> str:
        """返回 'running' | 'completed' | 'failed'"""

    @abstractmethod
    def collect_result(self, handle: WorkerHandle) -> str:
        """返回执行结果摘要"""
```

**实现:**
- `MockBackend` — sleep 随机 1-3 秒，模拟任务执行，总是返回 completed
- `HermesBackend` — 实例化 Hermes AIAgent，调用 run_conversation()（Phase 3）

**WorkerPool 管理器:**
```python
class WorkerPool:
    def __init__(self, backend: WorkerBackend, max_workers: int = 4): ...
    def dispatch(self, task: TaskNode) -> WorkerHandle: ...
    def poll_all(self) -> dict[str, str]: ...  # task_id → status
    def active_count(self) -> int: ...
```

WorkerPool 内部使用 ThreadPoolExecutor 实现并行。max_workers 控制并发数。

### 4.4 tracker/ — 状态追踪器

**职责:** 统一管理全局任务状态、发布状态变更、持久化到 JSON。

```python
class Tracker:
    def __init__(self, graph: TaskGraph): ...

    def update(self, task_id: str, status: TaskStatus, result: str = "") -> None: ...
    def snapshot(self) -> dict: ...   # 当前全局状态快照
    def summary(self) -> str: ...     # 人类可读的进度摘要
    def save(self, path: Path) -> None: ...
    def load(cls, path: Path) -> Tracker: ...
```

状态保存为 `.mindclaw/run-<id>/state.json`，支持断点恢复。

### 4.5 orchestrator/service.py — 流水线主控

**职责:** 串联所有模块，驱动编排循环。

```python
class Orchestrator:
    def __init__(
        self,
        decomposer: DecomposerBase,
        worker_backend: WorkerBackend,
        max_workers: int = 4,
    ): ...

    def run(self, goal: str) -> OrchestrationResult:
        graph = self.decomposer.decompose(goal)
        graph.validate()
        scheduler = Scheduler(graph)
        pool = WorkerPool(self.worker_backend, self.max_workers)
        tracker = Tracker(graph)

        while not scheduler.is_finished():
            # 1. 获取就绪任务
            ready = scheduler.get_ready_tasks()
            # 2. 分配给 worker
            for task in ready:
                handle = pool.dispatch(task)
                scheduler.mark_running(task.task_id)
                tracker.update(task.task_id, TaskStatus.RUNNING)
            # 3. 轮询进度
            statuses = pool.poll_all()
            for task_id, status in statuses.items():
                if status == "completed":
                    scheduler.mark_completed(task_id)
                    result = pool.collect_result(...)
                    tracker.update(task_id, TaskStatus.COMPLETED, result)
                elif status == "failed":
                    scheduler.mark_failed(task_id)
                    tracker.update(task_id, TaskStatus.FAILED)
            # 4. 打印进度
            print(tracker.summary())
            time.sleep(poll_interval)

        return OrchestrationResult(tracker.snapshot())
```

### 4.6 CLI — `mindclaw run` 命令

在 `cli/commands.py` 中添加 `run` 命令：

```python
@app.command("run")
def run_goal(
    goal: str = typer.Argument(..., help="High-level goal for the agent team."),
    workers: int = typer.Option(4, "--workers", help="Max parallel workers."),
):
    orchestrator = Orchestrator(
        decomposer=MockDecomposer(),
        worker_backend=MockBackend(),
        max_workers=workers,
    )
    result = orchestrator.run(goal)
    console.print(result.summary)
```

---

## 5. 文件结构

```text
mindclaw/
├── decomposer/
│   ├── __init__.py          # 导出 DecomposerBase, MockDecomposer
│   ├── interface.py         # DecomposerBase 抽象类
│   └── mock_decomposer.py  # MockDecomposer 实现
├── scheduler/
│   ├── __init__.py          # 导出 Scheduler, TaskGraph, TaskNode
│   ├── graph.py             # TaskGraph, TaskNode 数据结构
│   └── engine.py            # Scheduler 调度引擎
├── worker_pool/
│   ├── __init__.py          # 导出 WorkerBackend, WorkerPool, MockBackend
│   ├── interface.py         # WorkerBackend 抽象类
│   ├── mock_backend.py      # MockBackend 实现
│   └── manager.py           # WorkerPool 管理器
├── tracker/
│   ├── __init__.py          # 导出 Tracker
│   └── tracker.py           # Tracker 实现
├── orchestrator/
│   ├── __init__.py
│   ├── models.py            # OrchestrationResult
│   └── service.py           # Orchestrator 主控（重写）
```

---

## 6. 不做的事情（YAGNI）

- 不实现 LLM 分解（MockDecomposer 足够验证编排逻辑）
- 不实现 Hermes 运行时集成（MockBackend 足够验证 worker 管理）
- 不实现消息传递（agent 间通信留给 Phase 3）
- 不实现 workspace 隔离（git worktree 留给 Phase 3）
- 不实现 Web UI / board（CLI 输出足够）

---

## 7. 成功标准

1. `mindclaw run "any goal"` 执行完整流水线，输出任务进度表
2. 任务按依赖顺序执行（T1 完成后才启动依赖它的 T2、T3）
3. 并行任务同时运行（T2、T3、T4 同时启动，不互相阻塞）
4. 状态持久化到 JSON，崩溃后可查看最后状态
5. 所有模块可独立测试
