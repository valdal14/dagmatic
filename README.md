# dagmatic

[![CI Pipeline](https://github.com/valdal14/dagmatic/actions/workflows/ci.yml/badge.svg)](https://github.com/valdal14/dagmatic/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python)
![License](https://img.shields.io/badge/License-MIT-green)

**Dagmatic** is a lightweight, pure-Python orchestration engine designed to execute Directed Acyclic Graphs (DAGs) of tasks. Built entirely on the Python Standard Library with zero third-party runtime dependencies, Dagmatic provides a robust alternative to heavy orchestration middleware. It features strict topological sorting, multiprocess execution, and SQLite-backed state management, making it ideal for embedding custom data pipelines directly into Python environments without the overhead of external message brokers or complex infrastructure.

---

## 🗺️ Architectural Roadmap

### Core Engine (Phase 1)
- [x] **Task State Machine:** Isolated execution wrappers with `PENDING`, `RUNNING`, `SUCCESS`, and `FAILED` states.
- [x] **DAG Topology:** In-memory graph registry with $O(1)$ set-based dependency tracking.
- [x] **Mathematical Sorting:** Kahn's Algorithm implementation for linear topological sorting.
- [x] **Cycle Detection:** Defensive programming against self-loops and deep graph cycles.
- [x] **Cascade Failures:** Upstream auditing to gracefully skip downstream dependencies (`UPSTREAM_FAILED`) upon parent failure.
- [x] **Asynchronous Concurrency:** Generational graph batching running on the native `python3` `asyncio` event loop.

### Advanced Orchestration (Phase 2)
- [ ] **Cross-Task Communication (XComs):** Secure payload passing and centralized state memory between isolated tasks.
- [ ] **Task Retries & Timeouts:** Resilience mechanics for flaky network requests.
- [ ] **Dynamic Branching:** Ability for a task to selectively trigger/skip specific downstream paths based on conditional logic.

### Scheduling & Operations (Phase 3)
- [ ] **Scheduling Daemon:** Interval and Cron-based trigger mechanisms.
- [ ] **Audit Logging:** Emitting structured logs for pipeline observability.

---

## 🚀 Quick Start & Usage

**Dagmatic** allows you to mix synchronous CPU-bound functions with asynchronous I/O-bound coroutines in the same pipeline.

```python
import asyncio
from dagmatic.core.task import Task
from dagmatic.core.dag import DAG

# 1. Define your discrete workloads
async def query_snowflake():
    print("Extracting payload from Snowflake...")
    await asyncio.sleep(0.5)

def parse_xml_payload():
    print("Parsing XML string payload into dictionary...")

async def upload_to_aws():
    print("Pushing formatted data to AWS S3...")
    await asyncio.sleep(0.5)

async def send_slack_alert():
    print("Sending pipeline success metric to Slack...")

async def main():
    # 2. Initialize the Orchestrator
    pipeline = DAG()
    
    # 3. Register Tasks
    t_extract = Task(id="extract_db", target=query_snowflake)
    t_parse = Task(id="parse_xml", target=parse_xml_payload)
    t_upload = Task(id="upload_aws", target=upload_to_aws)
    t_alert = Task(id="alerting", target=send_slack_alert)
    
    for t in [t_extract, t_parse, t_upload, t_alert]:
        pipeline.add_task(t)
        
    # 4. Draw the Dependency Graph
    # Extract -> Parse -> Upload
    pipeline.add_dependency("extract_db", "parse_xml")
    pipeline.add_dependency("parse_xml", "upload_aws")
    
    # Alerting runs independently of the data flow, but waits for the final task
    pipeline.add_dependency("upload_aws", "alerting")

    # 5. Execute Asynchronously
    print("Starting pipeline execution...")
    await pipeline.execute_async()
    print("Pipeline finished successfully.")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🤝 Contributing

I very much welcome contributions from the community! To ensure the engine remains stable and maintainable, please adhere to the following workflow:

1. **Fork & Clone:** Fork the repository and clone it to your local machine.
2. **Short-Lived Branches:** Create a dedicated branch for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Test-Driven Development:** I strictly follow TDD. Before writing implementation code, write your tests in the tests/ directory. Ensure they fail, then write the code to make them pass.
    ```bash
    poetry run python3 -m pytest
    ```
4. **Code Standards:** All methods must include complete Python type hints (e.g., -> None, dict[str, int]). All classes and public methods must include professional docstrings explaining their purpose, arguments, and return types.

5. **Linter:**
    ```bash
    poetry run python3 -m ruff check .
    ```
6. Formatter: 
    ```bash
    poetry run python3 -m ruff format .
    ```
6. **Submit a Pull Request:** Once your tests are green and coverage is maintained, submit a PR to the main branch. Provide a clear commit message detailing the "why" and "how" of your changes.
