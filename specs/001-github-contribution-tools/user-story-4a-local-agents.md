# User Story 4a: Local AI Agent Support for PR Summarization (Priority: P2 - Enhancement)

**Feature Branch**: `001-github-contribution-tools`  
**Created**: 2024-12-28  
**Status**: Draft  
**Parent Story**: User Story 4 (PR Summarization)  
**Priority**: P2 (Enhancement)

## Overview

As an **enterprise developer** or **engineering manager**, I want to use locally installed AI agents (Cursor Agent, Claude Desktop, Gemini, or other local LLM providers) for PR summarization, so that I can:
- Maintain data privacy and security (no external API calls for local agents)
- Leverage existing enterprise AI infrastructure
- Avoid API costs and rate limits
- Meet compliance requirements for sensitive codebases
- Choose from multiple provider options based on organizational preferences

## Clarifications

### Session 2024-12-28

- Q: What should happen when auto-detection finds no available providers (including OpenAI)? → A: Fail with clear error message listing attempted providers and configuration hints
- Q: What should happen when a provider fails during batch PR processing? → A: Continue with remaining PRs, mark failed ones with error indicator, retry failed PRs with next available provider if auto-detection enabled
- Q: What are acceptable latency targets for PR summarization? → A: Individual PR summary ≤ 5 seconds, batch operations complete at least 10 PRs/minute per provider
- Q: What should be the default timeout values for providers? → A: Local agents: 30 seconds, Cloud providers (OpenAI/Gemini): 60 seconds
- Q: What should be the retry logic specifics? → A: Maximum 3 retries with exponential backoff (1s, 2s, 4s) for transient errors (timeouts, 5xx, rate limits), no retries for authentication or 4xx client errors

## Background

User Story 4 currently supports PR summarization via OpenAI API. This enhancement extends support to multiple AI providers that are commonly available in enterprise environments:
- **Cursor Agent**: Local AI coding assistant with PR analysis capabilities
- **Claude Desktop**: Anthropic's local Claude agent interface
- **Gemini (Google)**: Google's Gemini API (cloud-based) or local implementations
- **Other Local LLMs**: Extensible architecture for future providers (Ollama, LocalAI, etc.)

## User Scenarios

### Scenario 1: Using Cursor Agent (Local)

**Given** Cursor Agent is installed and running locally  
**When** I run PR summarization with `--llm-provider cursor`  
**Then** PR summaries are generated using the local Cursor Agent  
**And** No external API calls are made  
**And** Summaries maintain the same quality and format as OpenAI

```bash
# Using Cursor Agent
github-tools pr-summary-report \
  --start-date 1w \
  --end-date today \
  --llm-provider cursor \
  --cursor-port 8080  # Optional: custom port
```

### Scenario 2: Using Claude Desktop (Local)

**Given** Claude Desktop is installed and configured  
**When** I run PR summarization with `--llm-provider claude-local`  
**Then** PR summaries are generated using Claude Desktop API  
**And** The tool automatically detects Claude Desktop endpoint  
**And** Summaries use Claude's superior code understanding

```bash
# Using Claude Desktop (auto-detected)
github-tools pr-summary-report \
  --start-date 1w \
  --end-date today \
  --llm-provider claude-local

# Or with explicit endpoint
github-tools pr-summary-report \
  --start-date 1w \
  --end-date today \
  --llm-provider claude-local \
  --claude-endpoint http://localhost:11434
```

### Scenario 3: Using Google Gemini (Cloud API)

**Given** Google Gemini API key is configured  
**When** I run PR summarization with `--llm-provider gemini`  
**Then** PR summaries are generated using Google's Gemini API  
**And** Summaries leverage Gemini's code understanding capabilities  
**And** Alternative to OpenAI for organizations preferring Google's ecosystem

```bash
# Using Gemini API
github-tools pr-summary-report \
  --start-date 1w \
  --end-date today \
  --llm-provider gemini \
  --gemini-api-key ${GOOGLE_API_KEY}

# Or via environment variable
export GOOGLE_API_KEY="your-api-key"
github-tools pr-summary-report \
  --start-date 1w \
  --end-date today \
  --llm-provider gemini
```

### Scenario 4: Auto-Detection (Enterprise Default)

**Given** Multiple local agents are available  
**When** I run PR summarization without specifying a provider  
**Then** The tool automatically detects available local agents  
**And** Uses the first available agent (priority: Claude Desktop > Cursor > Gemini > OpenAI)  
**And** If no providers are available, fails with a clear error message listing attempted providers and configuration hints

```bash
# Auto-detect (prefers local agents)
github-tools pr-summary-report \
  --start-date 1w \
  --end-date today
```

### Scenario 5: Configuration File

**Given** A configuration file with local agent settings  
**When** I run PR summarization  
**Then** Settings are loaded from configuration  
**And** No command-line flags are needed

```yaml
# config.yaml
llm:
  provider: claude-local
  endpoint: http://localhost:11434
  model: claude-3-5-sonnet
  timeout: 30
```

Or with Gemini:

```yaml
# config.yaml
llm:
  provider: gemini
  api_key: ${GOOGLE_API_KEY}
  model: gemini-pro
  timeout: 30
```

### Scenario 6: Mixed Environments

**Given** Some developers use local agents, others use OpenAI  
**When** Each developer runs PR summarization  
**Then** Each can use their preferred provider  
**And** All summaries are compatible and consistent

### Scenario 7: Provider Failure During Batch Processing

**Given** Multiple PRs are being processed and the selected provider fails mid-batch  
**When** A provider error occurs (e.g., connection timeout, rate limit)  
**Then** Processing continues with remaining PRs  
**And** Failed PRs are marked with an error indicator in the output  
**And** If auto-detection is enabled, failed PRs are automatically retried using the next available provider in priority order  
**And** The final report includes both successful summaries and error indicators for failed PRs

## Requirements

### Functional Requirements

1. **Provider Abstraction**
   - Support multiple LLM providers through a unified interface
   - Implement provider registry pattern for extensibility
   - Support provider auto-detection

2. **Local Agent Support**
   - **Cursor Agent**: Support Cursor's local API or command-line interface
   - **Claude Desktop**: Support Claude Desktop's local API endpoint
   - **Gemini (Google)**: Support Google's Gemini API (cloud-based) via Google AI Studio
   - **Generic HTTP API**: Support any OpenAI-compatible local API

3. **Configuration**
   - Provider selection via CLI (`--llm-provider`)
   - Provider settings in configuration files (JSON/TOML/YAML)
   - Environment variable overrides
   - Auto-detection with priority fallback chain

4. **Backward Compatibility**
   - Default behavior unchanged (OpenAI API)
   - Existing configurations continue to work
   - No breaking changes to CLI interface

### Non-Functional Requirements

1. **Performance**
   - **Latency Targets**:
     - Individual PR summary: ≤ 5 seconds per PR
     - Batch operations: Complete at least 10 PRs/minute per provider
   - Local agents should meet or exceed these targets (may be faster than cloud APIs)
   - **Default Timeouts**:
     - Local agents (Claude Desktop, Cursor): 30 seconds
     - Cloud providers (OpenAI, Gemini): 60 seconds
     - Configurable per provider via configuration files
   - **Retry Logic**:
     - Maximum 3 retries per request
     - Exponential backoff delays: 1s, 2s, 4s between retries
     - Retry on transient errors: timeouts, HTTP 5xx server errors, rate limits (429)
     - No retries on: authentication errors (401), client errors (4xx except 429), invalid requests
   - Graceful degradation if local agent unavailable
   - Batch processing: Continue processing remaining PRs when a provider fails mid-batch
   - Failed PRs marked with error indicator in output
   - Automatic retry of failed PRs using next available provider (if auto-detection enabled)

2. **Security & Privacy**
   - No external API calls when using local agents
   - Support for air-gapped environments
   - Credential handling for authenticated local APIs

3. **Usability**
   - Automatic detection of available agents
   - Clear error messages when agents unavailable, including:
     - List of providers that were attempted
     - Detection status for each provider (e.g., "Claude Desktop: not running", "OpenAI: API key missing")
     - Actionable configuration hints (e.g., "Set GOOGLE_API_KEY environment variable to enable Gemini")
   - Configuration examples in documentation

## Technical Design

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   PR Summary Report                      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              LLM Provider Registry                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  OpenAI  │  │  Claude  │  │  Cursor  │  │  Gemini  │ │
│  │ Provider │  │ Provider │  │ Provider │  │ Provider │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              LLM Provider Interface                      │
│  - summarize(prompt: str) -> str                        │
│  - is_available() -> bool                               │
│  - get_metadata() -> dict                               │
└─────────────────────────────────────────────────────────┘
```

### Provider Interface

```python
class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def summarize(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 150,
        temperature: float = 0.3,
    ) -> str:
        """Generate summary using LLM."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Get provider metadata (name, version, etc.)."""
        pass
```

### Provider Implementations

1. **OpenAIProvider** (existing, refactored)
   - Uses OpenAI API
   - Requires API key
   - External API calls

2. **ClaudeLocalProvider** (new)
   - Connects to Claude Desktop API
   - Default endpoint: `http://localhost:11434/api/v1/chat/completions`
   - Auto-detects running Claude Desktop
   - No API key required for local instance

3. **CursorProvider** (new)
   - Connects to Cursor Agent API (if available)
   - Default endpoint: `http://localhost:8080/api/v1/chat/completions`
   - Auto-detects running Cursor Agent
   - May support command-line interface as fallback

4. **GeminiProvider** (new)
   - Uses Google's Gemini API (cloud-based)
   - Requires Google API key (via GOOGLE_API_KEY env var or config)
   - Supports multiple Gemini models (gemini-pro, gemini-pro-vision, gemini-ultra)
   - Alternative to OpenAI for organizations using Google Cloud

5. **GenericHTTPProvider** (new, extensible)
   - Supports any OpenAI-compatible API
   - Configurable endpoint and API key
   - Useful for Ollama, LocalAI, etc.

### Configuration Schema

```yaml
llm:
  provider: claude-local  # openai | claude-local | cursor | gemini | auto
  auto_detect: true       # Auto-detect available providers
  
  # OpenAI settings (existing, cloud provider: 60s default)
  openai:
    api_key: ${OPENAI_API_KEY}
    model: gpt-3.5-turbo
    base_url: https://api.openai.com/v1
    timeout: 60  # default for cloud providers
  
  # Claude Desktop settings (local agent: 30s default)
  claude_local:
    endpoint: http://localhost:11434
    model: claude-3-5-sonnet
    timeout: 30  # default for local agents
    auto_detect: true
  
  # Cursor Agent settings (local agent: 30s default)
  cursor:
    endpoint: http://localhost:8080
    timeout: 30  # default for local agents
    auto_detect: true
  
  # Google Gemini settings (cloud provider: 60s default)
  gemini:
    api_key: ${GOOGLE_API_KEY}
    model: gemini-pro  # gemini-pro | gemini-pro-vision | gemini-ultra
    base_url: https://generativelanguage.googleapis.com/v1beta
    timeout: 60  # default for cloud providers
  
  # Generic HTTP provider (for custom LLMs)
  generic:
    endpoint: http://localhost:11434
    api_key: optional
    model: llama2
    headers:
      Authorization: Bearer ${API_KEY}
```

### Provider Detection

```python
def detect_available_providers() -> List[str]:
    """
    Detect available LLM providers in priority order.
    
    Priority:
    1. Claude Desktop (most capable for code, local)
    2. Cursor Agent (code-focused, local)
    3. Gemini (Google, cloud-based alternative)
    4. Generic local LLM (Ollama, LocalAI, etc.)
    5. OpenAI (fallback, requires API key)
    
    Returns:
        List of available provider names
    """
    available = []
    
    # Check Claude Desktop
    if _check_claude_desktop():
        available.append("claude-local")
    
    # Check Cursor Agent
    if _check_cursor_agent():
        available.append("cursor")
    
    # Check Gemini (Google API key present)
    if os.getenv("GOOGLE_API_KEY"):
        available.append("gemini")
    
    # Check generic local LLMs (Ollama, etc.)
    if _check_generic_local():
        available.append("generic")
    
    # OpenAI always available if API key present
    if os.getenv("OPENAI_API_KEY"):
        available.append("openai")
    
    return available
```

## Implementation Plan

### Phase 1: Provider Abstraction (Refactoring)

1. Extract OpenAI logic into `OpenAIProvider` class
2. Create `LLMProvider` abstract base class
3. Update `LLMSummarizer` to use provider interface
4. Add provider registry

### Phase 2: Local Agent Support

1. Implement `ClaudeLocalProvider`
2. Implement `CursorProvider`
3. Implement `GeminiProvider`
4. Implement `GenericHTTPProvider`
5. Add provider detection logic

### Phase 3: Configuration & Integration

1. Add LLM configuration to config files
2. Update CLI with `--llm-provider` option
3. Add auto-detection feature
4. Update documentation

### Phase 4: Testing & Validation

1. Unit tests for each provider
2. Integration tests for local agents
3. End-to-end tests for auto-detection
4. Documentation and examples

## Acceptance Criteria

1. ✅ PR summaries can be generated using Cursor Agent
2. ✅ PR summaries can be generated using Claude Desktop
3. ✅ PR summaries can be generated using Google Gemini API
4. ✅ Tool automatically detects available local agents and cloud providers
5. ✅ Configuration supports all provider settings (local and cloud)
6. ✅ Backward compatibility maintained (OpenAI still works)
7. ✅ Clear error messages when agents unavailable, listing attempted providers and configuration hints
8. ✅ Documentation includes setup guides for all providers
9. ✅ All existing tests pass after refactoring
10. ✅ New provider implementations are unit tested
11. ✅ Integration tests validate all provider workflows
12. ✅ Batch processing continues with remaining PRs when provider fails, with automatic retry using next available provider (if auto-detection enabled)
13. ✅ Performance targets met: individual PR summary ≤ 5 seconds, batch operations ≥ 10 PRs/minute per provider

## Dependencies

- User Story 4 (PR Summarization) must be complete
- Access to Cursor Agent, Claude Desktop, or Gemini API for testing
- Understanding of provider API interfaces:
  - OpenAI API (existing)
  - Claude Desktop API
  - Cursor Agent API
  - Google Gemini API

## Risks & Mitigations

1. **Risk**: Local agent APIs may change or be undocumented
   - **Mitigation**: Use abstraction layer; support fallback to OpenAI

2. **Risk**: Performance may be slower with local agents
   - **Mitigation**: Add timeout configuration; provide performance guidelines; implement retry logic with exponential backoff for transient failures

3. **Risk**: Auto-detection may be unreliable
   - **Mitigation**: Allow manual provider selection; provide detection logs

## Future Enhancements

- Support for additional local LLMs (Ollama, LocalAI, vLLM, etc.)
- Local Gemini implementations (Gemini via Vertex AI, on-premise deployments)
- Provider performance benchmarking
- Caching strategies for local and cloud agents
- Batch processing optimizations
- Multi-provider fallback chains
- Cost comparison and analytics across providers

## References

- [User Story 4: PR Summarization](./spec.md#user-story-4)
- [Claude Desktop API Documentation](https://docs.anthropic.com/claude/docs)
- [Cursor Agent Documentation](https://cursor.com/docs)
- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [OpenAI-Compatible API Specification](https://platform.openai.com/docs/api-reference)

