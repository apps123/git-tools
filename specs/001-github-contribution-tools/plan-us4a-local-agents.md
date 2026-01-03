# Implementation Plan: Local AI Agent Support for PR Summarization (User Story 4a)

**Branch**: `001-github-contribution-tools` | **Date**: 2024-12-28 | **Spec**: [user-story-4a-local-agents.md](./user-story-4a-local-agents.md)  
**Input**: Feature specification from `/specs/001-github-contribution-tools/user-story-4a-local-agents.md`  
**Parent Story**: User Story 4 (PR Summarization)

**Note**: This plan extends the existing PR summarization feature (User Story 4) with multi-provider LLM support. See [plan.md](./plan.md) for the main feature implementation plan.

## Summary

Enhancement to PR summarization feature that adds support for multiple LLM providers (Cursor Agent, Claude Desktop, Gemini, and extensible generic providers) as alternatives to OpenAI API. Implements provider abstraction pattern with auto-detection, configuration support, and graceful fallback handling. Maintains backward compatibility with existing OpenAI-based PR summarization.

## Technical Context

**Language/Version**: Python 3.11+ (inherited from parent feature)  
**Primary Dependencies** (in addition to existing):
- `google-generativeai` or `google-ai-generativelanguage` for Gemini API
- `httpx` or `requests` for local agent HTTP communication (may already exist)
- `pydantic` (already in use) for provider configuration validation

**Storage**: No changes - uses existing file-based caching and configuration system  
**Testing**: `pytest` with `pytest-mock` (existing) + provider-specific mocking  
**Target Platform**: Linux/macOS/Windows (cross-platform, same as parent)  
**Project Type**: Enhancement to existing single project  
**Performance Goals**: 
- Individual PR summary: ≤ 5 seconds per PR
- Batch operations: ≥ 10 PRs/minute per provider
- Provider detection: < 2 seconds total
- Timeout handling: Local agents (30s), Cloud providers (60s)

**Constraints**: 
- Must maintain backward compatibility with existing OpenAI implementation
- No breaking changes to CLI interface
- Provider abstraction must not degrade existing performance
- Must handle provider failures gracefully (retry, fallback)

**Scale/Scope**: 
- Support 4+ LLM providers (OpenAI, Claude Desktop, Cursor, Gemini, Generic)
- Auto-detect available providers from environment/configuration
- Support same scale as parent feature (500 repos, 50 team members, 1 year periods)

**Integration Points**:
- Extends existing `src/github_tools/summarizers/llm_summarizer.py`
- Integrates with existing `src/github_tools/utils/config.py`
- Updates `src/github_tools/cli/pr_summary_report.py`
- Uses existing rate limiting and error handling patterns

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Library-First ✅
- **Status**: COMPLIANT
- **Rationale**: Provider abstraction is implemented as library modules (`src/github_tools/summarizers/providers/`). Each provider is a standalone, testable library class. The registry and factory patterns ensure extensibility without coupling to CLI.

### II. CLI Interface ✅
- **Status**: COMPLIANT
- **Rationale**: Adds `--llm-provider` option to existing CLI. No changes to text in/out protocol. Backward compatible - existing commands work unchanged. New options are additive only.

### III. Test-First (NON-NEGOTIABLE) ✅
- **Status**: COMPLIANT
- **Rationale**: All provider implementations will have unit tests written first. Provider interface abstraction tests precede implementation. Integration tests for auto-detection and fallback written before implementation. TDD cycle strictly enforced.

### IV. Integration Testing ✅
- **Status**: COMPLIANT
- **Rationale**: Integration tests required for:
  - Provider detection and registry (multiple providers, priority ordering)
  - Batch processing with provider failures (retry logic, fallback)
  - Configuration loading (CLI, env vars, config files)
  - Provider-specific API contracts (mocked responses)

### V. Observability & Versioning ✅
- **Status**: COMPLIANT
- **Rationale**: Structured logging for provider selection, detection status, failures. Provider metadata logged for debugging. Error messages include actionable hints. Versioning: MINOR bump (new functionality, backward compatible).

**Gate Result**: ✅ PASS - All constitution principles satisfied. Proceed to Phase 0.

## Phase 0: Research & Design Decisions

### Research Areas

1. **LLM Provider API Interfaces**
   - Claude Desktop local API endpoint and authentication
   - Cursor Agent API structure and availability detection
   - Google Gemini API (Generative Language API) authentication and models
   - OpenAI-compatible API specification for generic provider support

2. **Provider Detection Patterns**
   - Health check endpoints for local agents
   - Environment variable detection patterns
   - Process/service detection on different platforms (Windows/macOS/Linux)
   - Timeout strategies for detection checks

3. **Retry and Error Handling Patterns**
   - Exponential backoff implementation patterns
   - Transient vs permanent error classification
   - Provider-specific error codes and handling

4. **Configuration Management**
   - Provider-specific configuration schema validation
   - Environment variable precedence and merging
   - Configuration file format support (JSON/TOML/YAML)

### Technical Decisions Needed

- [ ] Claude Desktop API endpoint discovery (default ports, health checks)
- [ ] Cursor Agent API availability (official API vs CLI fallback)
- [ ] Gemini API client library choice (`google-generativeai` vs direct REST)
- [ ] Provider detection timeout strategy (per-provider vs global)
- [ ] Batch retry strategy (per-PR vs per-batch)

## Phase 1: Design Artifacts

### Data Model Extensions

Extend existing data models in `data-model.md`:

**New Entity: LLMProviderConfig**
- Fields: `provider_name`, `endpoint`, `api_key`, `timeout`, `model`, `retry_config`
- Relationships: Used by `LLMSummarizer`

**New Entity: ProviderMetadata**
- Fields: `name`, `version`, `type` (local/cloud), `is_available`, `detection_status`
- Relationships: Returned by `LLMProvider.get_metadata()`

### API Contracts

**Provider Interface Contract** (`contracts/llm-provider-contract.md`):
- `summarize(prompt, system_prompt, max_tokens, temperature) -> str`
- `is_available() -> bool`
- `get_metadata() -> ProviderMetadata`
- Error handling contract (retryable vs non-retryable)

**CLI Contract Extension** (update `contracts/cli-contracts.md`):
- `--llm-provider` option specification
- Provider-specific options (`--cursor-port`, `--claude-endpoint`, etc.)
- Auto-detection behavior contract

### Configuration Schema

Extend `src/github_tools/utils/config.py` with LLM provider configuration section (already partially defined in user story spec).

## Phase 2: Implementation Structure

### New Source Files

```
src/github_tools/summarizers/providers/
├── __init__.py
├── base.py                    # LLMProvider abstract base class
├── registry.py                # Provider registry and factory
├── detector.py                # Provider detection logic
├── openai_provider.py         # Refactored from llm_summarizer.py
├── claude_local_provider.py   # Claude Desktop provider
├── cursor_provider.py         # Cursor Agent provider
├── gemini_provider.py         # Google Gemini provider
└── generic_http_provider.py   # Generic OpenAI-compatible provider
```

### Modified Source Files

- `src/github_tools/summarizers/llm_summarizer.py` - Refactor to use provider registry
- `src/github_tools/utils/config.py` - Add LLM provider configuration support
- `src/github_tools/cli/pr_summary_report.py` - Add `--llm-provider` option

### Test Files

```
tests/unit/summarizers/providers/
├── test_base.py
├── test_openai_provider.py
├── test_claude_local_provider.py
├── test_cursor_provider.py
├── test_gemini_provider.py
├── test_generic_http_provider.py
├── test_registry.py
└── test_detector.py

tests/integration/
├── test_provider_detection.py
├── test_provider_fallback.py
└── test_batch_retry_logic.py
```

## Complexity Tracking

No constitution violations. Enhancement follows library-first pattern, maintains CLI compatibility, and adheres to test-first development. Provider abstraction adds moderate complexity but improves extensibility and maintainability.

## Dependencies

- User Story 4 (PR Summarization) must be complete and tested
- Access to provider APIs for testing:
  - Claude Desktop (local installation or mock)
  - Cursor Agent (if available, or mock)
  - Google Gemini API (test API key)
- Understanding of provider API documentation

## Risks & Mitigations

1. **Risk**: Provider APIs may change or be undocumented
   - **Mitigation**: Use abstraction layer; comprehensive error handling; fallback to OpenAI

2. **Risk**: Auto-detection may be unreliable across platforms
   - **Mitigation**: Allow manual provider selection; detailed detection logging; platform-specific detection strategies

3. **Risk**: Performance degradation from provider abstraction
   - **Mitigation**: Minimal abstraction overhead; benchmark existing vs new implementation; optimize hot paths

4. **Risk**: Configuration complexity for users
   - **Mitigation**: Sensible defaults; auto-detection as primary path; clear documentation and examples

## Next Steps

1. Complete Phase 0 research on provider APIs
2. Generate detailed design artifacts (data model, contracts)
3. Create task breakdown for implementation
4. Begin test-first implementation

