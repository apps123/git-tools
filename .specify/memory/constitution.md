<!--
Sync Impact Report:
Version change: N/A → 1.0.0 (initial constitution)
Modified principles: N/A (all new)
Added sections: Core Principles (5 principles), Development Workflow, Governance
Removed sections: N/A
Templates requiring updates:
  ✅ plan-template.md - Constitution Check section already references constitution
  ✅ spec-template.md - No direct constitution references, structure aligns
  ✅ tasks-template.md - No direct constitution references, structure aligns
  ✅ checklist-template.md - No direct constitution references
  ✅ agent-file-template.md - No direct constitution references
Follow-up TODOs: None
-->

# git-tools Constitution

## Core Principles

### I. Library-First

Every tool starts as a standalone library. Libraries MUST be self-contained, independently testable, and documented. Each library MUST have a clear purpose - no organizational-only libraries. Tools are composed from libraries, ensuring reusability and maintainability.

### II. CLI Interface

Every library exposes functionality via a command-line interface. Text in/out protocol: stdin/args → stdout, errors → stderr. Support both JSON and human-readable output formats. CLI tools MUST be composable and scriptable, following Unix philosophy principles.

### III. Test-First (NON-NEGOTIABLE)

Test-Driven Development is mandatory. Process: Tests written → User approved → Tests fail → Then implement. Red-Green-Refactor cycle strictly enforced. All new functionality MUST have tests before implementation begins.

### IV. Integration Testing

Focus areas requiring integration tests: New tool contract tests, Contract changes, Git repository operations, Inter-tool communication, Shared data formats. Integration tests MUST validate real git operations in isolated test repositories.

### V. Observability & Versioning

Text I/O ensures debuggability. Structured logging required for all operations. Semantic versioning: MAJOR.MINOR.PATCH format. Breaking changes require MAJOR version bump and migration documentation. Tools MUST log operations at appropriate levels (DEBUG, INFO, WARN, ERROR).

## Development Workflow

All feature development follows the speckit workflow: specification → plan → tasks → implementation. Constitution compliance MUST be verified at plan stage (Constitution Check gate). Code reviews MUST verify constitution compliance. Complexity MUST be justified in plan.md Complexity Tracking section.

## Governance

This constitution supersedes all other development practices. Amendments require documentation, approval rationale, and migration plan if principles change. All PRs and reviews MUST verify compliance with constitution principles. Use `.specify/templates/` for runtime development guidance. Version changes follow semantic versioning: MAJOR for backward-incompatible changes, MINOR for new principles or sections, PATCH for clarifications and typo fixes.

**Version**: 1.0.0 | **Ratified**: 2025-12-28 | **Last Amended**: 2025-12-28
