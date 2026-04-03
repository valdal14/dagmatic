# dagmatic

[![CI Pipeline](https://github.com/valdal14/dagmatic/actions/workflows/ci.yml/badge.svg)](https://github.com/valdal14/dagmatic/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python)
![License](https://img.shields.io/badge/License-MIT-green)

**Dagmatic** is a lightweight, pure-Python orchestration engine designed to execute Directed Acyclic Graphs (DAGs) of tasks. Built entirely on the Python Standard Library with zero third-party runtime dependencies, Dagmatic provides a robust alternative to heavy orchestration middleware. It features strict topological sorting, multiprocess execution, and SQLite-backed state management, making it ideal for embedding custom data pipelines directly into Python environments without the overhead of external message brokers or complex infrastructure.