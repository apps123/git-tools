---

description: "Task list for implementing GitHub Developer Contribution Analytics Tools"
---

# Tasks: GitHub Developer Contribution Analytics Tools

**Input**: Design documents from `/specs/001-github-contribution-tools/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Tests are REQUIRED by the constitution (Test-First). All story-specific implementation tasks must be preceded by corresponding test tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project layout (from `plan.md`):
  - Source: `src/github_tools/`
  - Tests: `tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure.

- [x] T001 Create Python project structure per implementation plan (`src/github_tools/`, `tests/`, `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`)
- [x] T002 Initialize test framework with `pytest` configuration in `pytest.ini` and `tests/__init__.py`
- [x] T003 [P] Configure linting and formatting tools (`ruff`, `black`) and add settings to `pyproject.toml`
- [x] T004 [P] Configure logging basics and log format helpers in `src/github_tools/utils/logging.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T005 Define core domain models (`Developer`, `Repository`, `Contribution`, `TimePeriod`) in `src/github_tools/models/` per `data-model.md`
- [x] T005a [P] Extend `Developer` model in `src/github_tools/models/developer.py` with `is_internal` boolean field (True if member of organization/enterprise, False if outside collaborator)
- [x] T006 Implement configuration loader using `pydantic` in `src/github_tools/utils/config.py` (GitHub token, org, base URL, cache paths)
- [x] T007 Implement file-based cache utilities (JSON/CSV, optional SQLite hooks) in `src/github_tools/utils/cache.py`
- [x] T008 Implement GitHub API client wrapper using `PyGithub` or `github3.py` in `src/github_tools/api/client.py`
- [x] T008a [P] Add organization membership checking methods to API client in `src/github_tools/api/client.py` (check if user is member of organization/enterprise vs outside collaborator with repository-specific access)
- [x] T009 [P] Implement rate limit and retry/backoff logic with resumable checkpoints in `src/github_tools/api/rate_limiter.py`
- [x] T010 Implement common filtering helpers for repositories, developers, and time periods in `src/github_tools/utils/filters.py`
- [x] T010a Implement contributor classification logic in `src/github_tools/utils/filters.py` (determine internal vs external: internal = organization/enterprise member, external = outside collaborator with repository-specific access)
- [x] T011 Add basic CLI entrypoint module `src/github_tools/cli/__init__.py` and top-level `github-tools` console script wiring in `pyproject.toml`
- [x] T012 Configure test fixtures for GitHub API mocks and sample data in `tests/fixtures/` (JSON responses, sample contributions)
- [x] T012a [P] Add unit tests for internal/external contributor classification in `tests/unit/test_contributor_classification.py` (test org membership detection, outside collaborator detection, edge cases like deleted accounts)

**Checkpoint**: Foundation ready – core models (including internal/external classification), config, caching, API access (including org membership checking), contributor classification logic, and CLI skeleton are in place.

---

## Phase 3: User Story 1 - Generate Developer Activity Report (Priority: P1) 🎯 MVP

**Goal**: Generate developer activity reports across repositories for a given time period, with per-developer and per-repository breakdowns.  
**Independent Test**: Run a `developer-report` command for a specific time period and verify that it produces structured metrics (commits, PRs, reviews, issues) per developer with accurate attribution.

### Tests for User Story 1 (write FIRST)

- [x] T013 [P] [US1] Add contract test for developer activity report output schema in `tests/contract/test_developer_report_contract.py`
- [x] T014 [P] [US1] Add integration test for end-to-end developer report flow in `tests/integration/test_developer_report_flow.py`
- [x] T015 [P] [US1] Add unit tests for developer metric aggregation logic in `tests/unit/test_developer_analyzer.py`
- [x] T015a [P] [US1] Add targeted integration test for attribution accuracy (≥95%) using curated sample dataset in `tests/integration/test_attribution_accuracy.py` with ground-truth contributor mappings in `tests/integration/fixtures/attribution_ground_truth.json`

### Implementation for User Story 1

- [x] T016 [P] [US1] Implement contribution collection pipeline for commits/PRs/reviews/issues in `src/github_tools/collectors/contribution_collector.py`
- [x] T017 [P] [US1] Implement developer activity analyzer to compute `DeveloperMetrics` in `src/github_tools/analyzers/developer_analyzer.py`
- [x] T018 [US1] Implement developer report generation logic (Markdown/JSON/CSV) in `src/github_tools/reports/generator.py` and templates in `src/github_tools/reports/templates/`
- [x] T019 [US1] Implement `developer-report` CLI command in `src/github_tools/cli/developer_report.py` (args: dates, repos, developers, teams)
- [x] T020 [US1] Wire `developer-report` command into main CLI group in `src/github_tools/cli/__init__.py`
- [x] T021 [US1] Ensure logging, error handling, and exit codes for `developer-report` follow contracts (`cli-contracts.md`)

**Checkpoint**: User Story 1 fully functional and testable independently via CLI.

---

## Phase 4: User Story 2 - Analyze Repository Contribution Patterns (Priority: P2)

**Goal**: Provide repository-level contribution metrics and patterns to highlight activity levels, contributor diversity, and trends.  
**Independent Test**: Run a `repository-report` command and verify it produces metrics per repository (total contributions, active contributors, trends, distribution).

### Tests for User Story 2 (write FIRST)

- [x] T022 [P] [US2] Add contract test for repository report output schema in `tests/contract/test_repository_report_contract.py`
- [x] T023 [P] [US2] Add integration test for repository analysis workflow in `tests/integration/test_repository_report_flow.py`
- [x] T024 [P] [US2] Add unit tests for repository trend and distribution calculations in `tests/unit/test_repository_analyzer.py`

### Implementation for User Story 2

- [x] T025 [P] [US2] Implement repository-level aggregation and metrics calculation in `src/github_tools/analyzers/repository_analyzer.py`
- [x] T026 [US2] Extend report generator and templates for repository-level sections in `src/github_tools/reports/generator.py` and `src/github_tools/reports/templates/`
- [x] T027 [US2] Implement `repository-report` CLI command in `src/github_tools/cli/repository_report.py`
- [x] T028 [US2] Integrate repository filters and options (e.g., multiple repos) into `repository-report` CLI and plumbing

**Checkpoint**: User Stories 1 and 2 both independently testable; repository reports do not depend on team/department metrics.

---

## Phase 5: User Story 3 - Track Team and Department Contribution Metrics (Priority: P3)

**Goal**: Aggregate individual contributions into team and department-level metrics for organizational insights.  
**Independent Test**: Run a `team-report` command with team membership data and verify it aggregates contributions correctly into team and department metrics.

### Tests for User Story 3 (write FIRST)

- [x] T029 [P] [US3] Add contract test for team/department report output schema in `tests/contract/test_team_report_contract.py`
- [x] T030 [P] [US3] Add integration test for team/department aggregation flow in `tests/integration/test_team_report_flow.py`
- [x] T031 [P] [US3] Add unit tests for team and department metric calculations in `tests/unit/test_team_analyzer.py`

### Implementation for User Story 3

- [x] T032 [P] [US3] Implement team and department analyzers to compute `TeamMetrics` and `DepartmentMetrics` in `src/github_tools/analyzers/team_analyzer.py`
- [x] T033 [US3] Implement `team-report` CLI command in `src/github_tools/cli/team_report.py` (inputs: team config, date range)
- [x] T034 [US3] Extend report generator/templates for team and department sections in `src/github_tools/reports/generator.py` and `src/github_tools/reports/templates/`

**Checkpoint**: Team and department reports available and verified without depending on PR summaries or anomaly detection.

---

## Phase 6: User Story 4 - Generate Periodic Pull Request Summary Reports (Priority: P2)

**Goal**: Produce concise, contextual summaries of PRs merged to main branches over a period, grouped by repository.  
**Independent Test**: Run a `pr-summary-report` command for a daily/weekly/monthly period and verify it lists only PRs merged to main, each with a ≤4‑line summary.

### Tests for User Story 4 (write FIRST)

- [x] T035 [P] [US4] Add contract test for PR summary report structure and 4-line limit in `tests/contract/test_pr_summary_report_contract.py`
- [x] T036 [P] [US4] Add integration test for PR summary generation across multiple repositories in `tests/integration/test_pr_summary_report_flow.py`
- [x] T037 [P] [US4] Add unit tests for PR summary generation and context handling in `tests/unit/test_pr_summarizer.py`

### Implementation for User Story 4

- [x] T038 [P] [US4] Implement PR collection logic using GitHub API in `src/github_tools/collectors/pr_collector.py` (only PRs merged to main or configured primary branch)
- [x] T039 [P] [US4] Implement repository context analysis helper in `src/github_tools/summarizers/context_analyzer.py`
- [x] T040 [US4] Implement LLM-based PR summarizer in `src/github_tools/summarizers/pr_summarizer.py` (enforce 4-line limit, handle rate limits and errors)
- [x] T041 [US4] Implement `pr-summary-report` CLI command in `src/github_tools/cli/pr_summary_report.py`
- [x] T042 [US4] Extend report generator and templates for PR summary sections in `src/github_tools/reports/generator.py` and `src/github_tools/reports/templates/`

**Checkpoint**: PR summary reports independently testable; they rely on foundational collectors and summarizers but not on team/anomaly features.

---

## Phase 6a: User Story 4a - Local AI Agent Support for PR Summarization (Priority: P2 - Enhancement)

**Goal**: Enable PR summarization using locally installed AI agents (Cursor, Claude Desktop) and cloud providers (Gemini) as alternatives to OpenAI API for enterprise use cases.  
**Parent Story**: User Story 4  
**Independent Test**: Run `pr-summary-report` with `--llm-provider claude-local` or `--llm-provider gemini` and verify summaries are generated using the selected provider (local agents avoid external API calls, cloud providers use their respective APIs).

### Tests for User Story 4a (write FIRST)

- [ ] T055 [P] [US4a] Add unit tests for LLM provider interface abstraction in `tests/unit/summarizers/providers/test_base.py`
- [ ] T056 [P] [US4a] Add unit tests for OpenAI provider refactoring in `tests/unit/summarizers/providers/test_openai_provider.py`
- [ ] T057 [P] [US4a] Add unit tests for Claude local provider in `tests/unit/summarizers/providers/test_claude_local_provider.py`
- [ ] T058 [P] [US4a] Add unit tests for Cursor provider in `tests/unit/summarizers/providers/test_cursor_provider.py`
- [ ] T059 [P] [US4a] Add unit tests for Gemini provider in `tests/unit/summarizers/providers/test_gemini_provider.py`
- [ ] T060 [P] [US4a] Add unit tests for generic HTTP provider in `tests/unit/summarizers/providers/test_generic_http_provider.py`
- [ ] T061 [P] [US4a] Add unit tests for provider registry and factory in `tests/unit/summarizers/providers/test_registry.py`
- [ ] T061a [P] [US4a] Add unit tests for provider detection logic in `tests/unit/summarizers/providers/test_detector.py`
- [ ] T062 [P] [US4a] Add integration test for provider auto-detection with priority ordering in `tests/integration/test_provider_detection.py`
- [ ] T063 [P] [US4a] Add integration test for PR summarization with all providers in `tests/integration/test_pr_summary_local_agents.py`
- [ ] T063a [P] [US4a] Add integration test for provider fallback and batch retry logic in `tests/integration/test_provider_fallback.py`
- [ ] T063b [P] [US4a] Add integration test for batch processing retry with next available provider in `tests/integration/test_batch_retry_logic.py`
- [ ] T064 [US4a] Add contract test for provider interface and configuration in `tests/contract/test_llm_provider_contract.py`

### Implementation for User Story 4a

- [ ] T065 [P] [US4a] Create LLM provider abstract base class in `src/github_tools/summarizers/providers/base.py`
- [ ] T066 [P] [US4a] Refactor existing OpenAI logic into `OpenAIProvider` class in `src/github_tools/summarizers/providers/openai_provider.py`
- [ ] T067 [P] [US4a] Implement provider registry and factory in `src/github_tools/summarizers/providers/registry.py`
- [ ] T068 [P] [US4a] Implement Claude local provider in `src/github_tools/summarizers/providers/claude_local_provider.py`
- [ ] T069 [P] [US4a] Implement Cursor provider in `src/github_tools/summarizers/providers/cursor_provider.py`
- [ ] T070 [P] [US4a] Implement Gemini provider in `src/github_tools/summarizers/providers/gemini_provider.py`
- [ ] T071 [P] [US4a] Implement generic HTTP provider for OpenAI-compatible APIs in `src/github_tools/summarizers/providers/generic_http_provider.py`
- [ ] T072 [P] [US4a] Implement provider auto-detection logic with priority ordering in `src/github_tools/summarizers/providers/detector.py`
- [ ] T072a [P] [US4a] Implement retry logic with exponential backoff (1s, 2s, 4s) in provider base class in `src/github_tools/summarizers/providers/base.py`
- [ ] T072b [US4a] Implement batch processing with automatic retry using next available provider in `src/github_tools/collectors/pr_summary_collector.py`
- [ ] T073 [US4a] Refactor `LLMSummarizer` to use provider registry and interface in `src/github_tools/summarizers/llm_summarizer.py`
- [ ] T074 [US4a] Add LLM provider configuration schema to `AppConfig` in `src/github_tools/utils/config.py` (support JSON/TOML/YAML config files)
- [ ] T075 [US4a] Update `pr-summary-report` CLI command with `--llm-provider` option and provider-specific options in `src/github_tools/cli/pr_summary_report.py`
- [ ] T075a [US4a] Implement error message formatting with provider detection status and configuration hints in `src/github_tools/summarizers/providers/detector.py`
- [ ] T076 [US4a] Add configuration file examples and documentation for all providers (including Gemini) in `README.md` and `specs/001-github-contribution-tools/quickstart.md`

**Checkpoint**: PR summarization works with local AI agents and cloud providers (Gemini); auto-detection functional; backward compatibility maintained.

---

## Phase 6b: User Story 4b - Multi-Dimensional PR Impact Analysis (Priority: P2 - Enhancement)

**Goal**: Extend PR summarization to analyze impacts across 7 critical dimensions (Security, Cost/FinOps, Operations, Architecture, Mentorship, Data Governance, AI Governance) using changed files and structured LLM analysis.  
**Parent Story**: User Story 4  
**Independent Test**: Run `pr-summary-report` and verify summaries include all 7 dimensions with appropriate impact levels and descriptions, using the structured format with emoji indicators.

### Tests for User Story 4b (write FIRST)

- [ ] T077 [P] [US4b] Add unit tests for file pattern detector in `tests/unit/summarizers/test_file_pattern_detector.py`
- [ ] T078 [P] [US4b] Add unit tests for security impact analyzer in `tests/unit/summarizers/test_security_analyzer.py`
- [ ] T079 [P] [US4b] Add unit tests for cost/FinOps impact analyzer in `tests/unit/summarizers/test_cost_analyzer.py`
- [ ] T080 [P] [US4b] Add unit tests for operational impact analyzer in `tests/unit/summarizers/test_operational_analyzer.py`
- [ ] T081 [P] [US4b] Add unit tests for architectural integrity analyzer in `tests/unit/summarizers/test_architectural_analyzer.py`
- [ ] T082 [P] [US4b] Add unit tests for mentorship insights analyzer in `tests/unit/summarizers/test_mentorship_analyzer.py`
- [ ] T083 [P] [US4b] Add unit tests for data governance impact analyzer in `tests/unit/summarizers/test_data_governance_analyzer.py`
- [ ] T084 [P] [US4b] Add unit tests for AI governance impact analyzer (SAIF) in `tests/unit/summarizers/test_ai_governance_analyzer.py`
- [ ] T085 [P] [US4b] Add unit tests for multi-dimensional analyzer orchestrator in `tests/unit/summarizers/test_multi_dimensional_analyzer.py`
- [ ] T086 [P] [US4b] Add integration test for multi-dimensional PR summary generation in `tests/integration/test_pr_summary_multi_dimensional.py`
- [ ] T087 [US4b] Add contract test for multi-dimensional summary format in `tests/contract/test_pr_summary_multidimensional_contract.py`

### Implementation for User Story 4b

- [ ] T088 [P] [US4b] Implement file pattern detector in `src/github_tools/summarizers/file_pattern_detector.py` (detect IAC files, AI/ML models, data files, config files)
- [ ] T089 [P] [US4b] Implement security impact analyzer in `src/github_tools/summarizers/dimensions/security_analyzer.py`
- [ ] T090 [P] [US4b] Implement cost/FinOps impact analyzer in `src/github_tools/summarizers/dimensions/cost_analyzer.py`
- [ ] T091 [P] [US4b] Implement operational impact analyzer in `src/github_tools/summarizers/dimensions/operational_analyzer.py`
- [ ] T092 [P] [US4b] Implement architectural integrity analyzer in `src/github_tools/summarizers/dimensions/architectural_analyzer.py`
- [ ] T093 [P] [US4b] Implement mentorship insights analyzer in `src/github_tools/summarizers/dimensions/mentorship_analyzer.py`
- [ ] T094 [P] [US4b] Implement data governance impact analyzer in `src/github_tools/summarizers/dimensions/data_governance_analyzer.py`
- [ ] T095 [P] [US4b] Implement AI governance impact analyzer (SAIF framework) in `src/github_tools/summarizers/dimensions/ai_governance_analyzer.py`
- [ ] T096 [US4b] Implement multi-dimensional analyzer orchestrator in `src/github_tools/summarizers/multi_dimensional_analyzer.py`
- [ ] T097 [US4b] Create structured prompt templates for dimensional analysis in `src/github_tools/summarizers/prompts/dimensional_prompts.py`
- [ ] T098 [US4b] Update LLMSummarizer to integrate multi-dimensional analysis in `src/github_tools/summarizers/llm_summarizer.py`
- [ ] T099 [US4b] Update PR file collection to include file diffs in `src/github_tools/collectors/pr_collector.py`
- [ ] T100 [US4b] Update report generator templates for multi-dimensional format in `src/github_tools/reports/templates/pr_summary_multidimensional.md`
- [ ] T101 [US4b] Add response parser for structured dimensional output in `src/github_tools/summarizers/parsers/dimensional_parser.py`
- [ ] T102 [US4b] Update CLI to support dimensional analysis output format in `src/github_tools/cli/pr_summary_report.py`
- [ ] T103 [US4b] Create validation test suite for analysis accuracy with ground truth dataset in `tests/integration/test_dimensional_accuracy.py` and ground truth PR annotations in `tests/integration/fixtures/dimensional_ground_truth.json`
- [ ] T104 [US4b] Implement performance benchmarking for multi-dimensional analysis to meet NFR-4b-002 targets in `tests/performance/test_dimensional_performance.py`
- [ ] T105 [US4b] Implement LLM token optimization and caching strategies to meet NFR-4b-003 targets in `src/github_tools/summarizers/prompts/dimensional_prompts.py` (prompt template optimization, response caching)

**Checkpoint**: PR summaries include all 7 dimensions of impact analysis with structured format; performance targets met; accuracy validated; works with all LLM providers.

---

## Phase 7: User Story 5 - Identify Contribution Trends and Anomalies (Priority: P3)

**Goal**: Detect significant changes and anomalies in contribution patterns over time for developers, teams, and repositories.  
**Independent Test**: Run a `trends` command with historical data and verify it flags drops/spikes >50% and highlights trend direction.

### Tests for User Story 5 (write FIRST)

- [x] T043 [P] [US5] Add contract test for trend/anomaly report structure in `tests/contract/test_trends_report_contract.py`
- [x] T044 [P] [US5] Add integration test for trends/anomalies across multiple periods in `tests/integration/test_trends_flow.py`
- [x] T045 [P] [US5] Add unit tests for anomaly detection thresholds and trend calculations in `tests/unit/test_anomaly_detector.py`
- [x] T045a [P] [US5] Add targeted integration test for anomaly detection recall (≥80%) using curated sample dataset in `tests/integration/test_anomaly_recall.py` with known anomaly events (drops/spikes >50%) in `tests/integration/fixtures/anomaly_ground_truth.json`

### Implementation for User Story 5

- [x] T046 [P] [US5] Implement anomaly detector and trend analysis logic in `src/github_tools/analyzers/anomaly_detector.py`
- [x] T047 [US5] Implement `trends` CLI command in `src/github_tools/cli/trends.py`
- [x] T048 [US5] Extend report generator/templates for trend and anomaly sections in `src/github_tools/reports/generator.py` and `src/github_tools/reports/templates/`

**Checkpoint**: Trends and anomalies reporting independently testable and can be run over existing contribution metrics.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and overall quality.

- [ ] T049 [P] Add detailed usage examples and CLI reference to `README.md` and update `specs/001-github-contribution-tools/quickstart.md`
- [ ] T050 Refine logging levels and message formats across `src/github_tools/` (avoid sensitive data in logs)
- [ ] T051 [P] Add additional edge case tests for rate limits, missing data, and large histories in `tests/integration/test_edge_cases.py`
- [ ] T052 Performance profiling and optimization for large organizations (500 repos, 100K commits) in core analyzers and collectors
- [ ] T053 [P] Verify privacy posture and documentation for internal-only outputs per `NFR-001` in `README.md` and tool help
- [x] T054 [P] Implement JSON/TOML/YAML configuration file support in `src/github_tools/utils/config.py` (support nested and flat config structures, file format detection)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies – can start immediately.  
- **Foundational (Phase 2)**: Depends on Setup completion – BLOCKS all user stories.  
- **User Stories (Phases 3–7)**: All depend on Foundational phase completion.
  - User stories can proceed in parallel (if team capacity allows).
  - Priority order from spec: P1 (US1), P2 (US2, US4, US4a, US4b), P3 (US3, US5).
  - **Phase 6a (US4a)**: Depends on Phase 6 (US4) completion.
  - **Phase 6b (US4b)**: Depends on Phase 6 (US4) completion; can proceed in parallel with Phase 6a.
- **Polish (Phase 8)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational – no dependencies on other stories (MVP).
- **User Story 2 (P2)**: Can start after Foundational – may share collectors with US1 but is independently testable.
- **User Story 3 (P3)**: Can start after Foundational – depends on Developer/Contribution data but not on PR summaries.
- **User Story 4 (P2)**: Can start after Foundational – depends on PR collectors and summarizers only.
- **User Story 4a (P2 Enhancement)**: Must start after User Story 4 completion – extends PR summarization with multi-provider LLM support. Depends on existing LLMSummarizer implementation.
- **User Story 5 (P3)**: Can start after Foundational – depends on historical metrics but does not require completion of other stories for basic functionality.

### Within Each User Story

- Tests (contract, integration, unit) MUST be written and FAIL before implementation tasks start.
- Implement collectors/analyzers before CLI commands.
- Implement report templates and generator extensions before wiring CLI outputs.
- Each user story should be independently testable via its CLI command(s).

---

## Parallel Opportunities

- Setup tasks T003 and T004 can run in parallel after T001–T002.  
- Foundational tasks T005a, T007–T009, T012, and T012a can proceed in parallel where they touch different files (T005a extends Developer model, T008a extends API client, T010a adds classification logic, T012a adds tests).  
- Within each user story:
  - Contract, integration, and unit tests marked [P] (e.g., T013–T015a, T022–T024, T043–T045a) can be created in parallel.
  - Collector/analyzer implementations marked [P] (e.g., T016, T017, T025, T032, T038, T039, T046) can be developed in parallel across different modules.
- Different user stories (US2, US3, US4, US5) can be developed in parallel after Phase 2, as long as their file paths do not conflict.
- **User Story 4a**: Provider implementations (T068–T071) can be developed in parallel. Tests (T057–T060) can be written in parallel.

---

## Parallel Example: User Story 1

```bash
# In parallel (different files):
# Tests
- [ ] T013 [P] [US1] Contract test in tests/contract/test_developer_report_contract.py
- [ ] T014 [P] [US1] Integration test in tests/integration/test_developer_report_flow.py
- [ ] T015 [P] [US1] Unit tests in tests/unit/test_developer_analyzer.py

# Core implementation
- [ ] T016 [P] [US1] Collector in src/github_tools/collectors/contribution_collector.py
- [ ] T017 [P] [US1] Analyzer in src/github_tools/analyzers/developer_analyzer.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.  
2. Complete Phase 2: Foundational (CRITICAL – blocks all stories).  
3. Complete Phase 3: User Story 1 (`developer-report` only).  
4. **STOP and VALIDATE**: Run all US1 tests and manual CLI checks.  
5. Demo/deploy MVP for feedback.

### Incremental Delivery

1. Setup + Foundational → foundation ready.  
2. Add US1 (developer reports) → test → deploy/demo.  
3. Add US2 (repository patterns) and/or US4 (PR summaries) → test → deploy/demo.  
4. Add US3 (team/department metrics) → test → deploy/demo.  
5. Add US5 (trends/anomalies) → test → deploy/demo.  
6. Perform Phase 8 Polish once core stories are stable.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together.  
2. After Phase 2:
   - Developer A: User Story 1 (US1).  
   - Developer B: User Story 2 (US2).  
   - Developer C: User Story 4 (US4).  
   - Developer D (if available): User Story 3 (US3) or User Story 5 (US5).  
3. Integrate and validate each story independently before merging to main.

---

## Summary Metrics

- **Total Tasks**: 110 (4 foundational classification tasks + 2 quality validation test tasks + 27 local agent tasks + 29 multi-dimensional analysis tasks)  
- **Tasks per User Story**:
  - US1: 10 tasks (T013–T015a, T016–T021) including attribution accuracy validation  
  - US2: 7 tasks (T022–T028)  
  - US3: 7 tasks (T029–T034)  
  - US4: 8 tasks (T035–T042)  
  - US4a: 27 tasks (T055–T076 including T061a, T063a, T063b, T072a, T072b, T075a) local AI agent support enhancement (includes Gemini, retry logic, batch processing)
  - US4b: 29 tasks (T077–T105) multi-dimensional PR impact analysis (Security, Cost, Operations, Architecture, Mentorship, Data Governance, AI Governance) including validation and performance tasks
  - US5: 7 tasks (T043–T045a, T046–T048) including anomaly detection recall validation  
- **Foundational Classification Tasks**: 4 tasks (T005a, T008a, T010a, T012a) for internal/external contributor identification
- **Quality Validation Tests**: 2 tasks (T015a for attribution accuracy ≥95%, T045a for anomaly recall ≥80%) using curated sample datasets  
- **Local Agent Enhancement Tasks**: 27 tasks (T055–T076 with sub-tasks) for supporting Cursor, Claude Desktop, Gemini, and generic local LLM providers, including retry logic, batch processing enhancements, and comprehensive error handling
- **Multi-Dimensional Analysis Tasks**: 26 tasks (T077–T102) for implementing 7-dimensional impact analysis (Security, Cost/FinOps, Operations, Architecture, Mentorship, Data Governance, AI Governance)
- **Parallelizable Tasks ([P])**: Majority of tests and core analyzers/collectors (explicitly marked).  
- **Suggested MVP Scope**: Phases 1–3 (Setup, Foundational, User Story 1).


