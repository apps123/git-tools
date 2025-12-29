# Research & Technology Decisions

**Feature**: GitHub Developer Contribution Analytics Tools  
**Date**: 2024-12-28  
**Phase**: 0 - Research & Technology Selection

## Technology Choices

### GitHub API Client Library

**Decision**: Use `PyGithub` library  
**Rationale**: 
- Mature, well-maintained library with comprehensive GitHub API coverage
- Handles authentication, rate limiting, and pagination automatically
- Supports both GitHub.com and GitHub Enterprise
- Active community and good documentation
- Provides Pythonic interface that simplifies API interactions

**Alternatives Considered**:
- `github3.py`: More lightweight but less feature-complete
- Direct REST API calls with `requests`: Too low-level, requires manual rate limiting and pagination
- `octokit.py`: Less mature and smaller community

**Implementation Notes**: Use `PyGithub.Github` class with token authentication. Implement custom rate limit handling wrapper to respect API limits and provide retry/backoff logic.

---

### CLI Framework

**Decision**: Use `click` library  
**Rationale**:
- Clean, composable command structure aligns with Unix philosophy
- Built-in support for multiple output formats (JSON, text)
- Excellent help text generation
- Easy to test (click.testing.CliRunner)
- Supports command groups for organizing multiple tools

**Alternatives Considered**:
- `argparse`: Standard library but more verbose, less composable
- `typer`: Modern but adds async complexity not needed here
- `docopt`: Declarative but less flexible for complex CLIs

**Implementation Notes**: Use `click.group()` for main command, `click.command()` for subcommands. Use `click.option()` with `--format` flag supporting 'json', 'markdown', 'csv' values.

---

### Data Processing & Analysis

**Decision**: Use `pandas` for data aggregation and analysis  
**Rationale**:
- Powerful data manipulation for aggregating contributions by developer, repository, team, time period
- Efficient handling of large datasets (100K+ commits)
- Built-in time series analysis for trend detection
- Easy conversion to CSV/JSON for machine-readable output
- Well-integrated with other Python data science tools

**Alternatives Considered**:
- Pure Python dictionaries/lists: Too slow for large datasets
- `polars`: Faster but less mature ecosystem
- `dask`: Overkill for single-machine processing

**Implementation Notes**: Use pandas DataFrames for in-memory data processing. Convert GitHub API responses to DataFrames early in pipeline. Use groupby operations for aggregation.

---

### PR Summarization

**Decision**: Use OpenAI API (GPT-4 or GPT-3.5-turbo) via `openai` library  
**Rationale**:
- High-quality summarization with context understanding
- Can analyze repository code context effectively
- Supports structured output for consistent formatting
- Well-documented API with good Python SDK
- Cost-effective for batch processing (can use cheaper models for simple PRs)

**Alternatives Considered**:
- Local LLM (llama.cpp, etc.): Requires significant infrastructure, lower quality
- Anthropic Claude API: Similar quality but less established Python SDK
- Rule-based summarization: Insufficient for contextual understanding
- GitHub Copilot API: Not designed for batch summarization

**Implementation Notes**: 
- Use GPT-3.5-turbo for cost efficiency (can upgrade to GPT-4 for complex PRs)
- Implement prompt engineering to ensure 4-line limit
- Cache repository context analysis to reduce API calls
- Handle API rate limits and errors gracefully

---

### Repository Context Analysis

**Decision**: Use `GitPython` library for repository code analysis  
**Rationale**:
- Pure Python library for git operations
- Can clone/analyze repository structure without external git binary dependency
- Supports reading file contents, commit history, branch information
- Good for programmatic repository analysis

**Alternatives Considered**:
- `subprocess` with git commands: Less reliable, platform-dependent
- `dulwich`: Pure Python but less feature-complete
- GitHub API file contents endpoint: Limited to individual files, inefficient for full context

**Implementation Notes**: 
- Clone repositories to temporary directory for analysis
- Analyze repository structure (file tree, README, recent commits) to build context
- Clean up temporary clones after analysis
- Handle large repositories efficiently (analyze only relevant files)

---

### Report Generation

**Decision**: Use `jinja2` for template-based report generation  
**Rationale**:
- Flexible templating for human-readable reports (Markdown, HTML)
- Separates data from presentation
- Supports multiple output formats from same template
- Well-established, widely used library

**Alternatives Considered**:
- `string.Template`: Too limited for complex reports
- `markdown` library: Only generates Markdown, need more flexibility
- Direct string formatting: Hard to maintain, not reusable

**Implementation Notes**: 
- Create Jinja2 templates for Markdown reports
- Use separate formatters for JSON/CSV (structured data, no templating needed)
- Support PDF generation via `weasyprint` or `reportlab` (optional, lower priority)

---

### Testing Framework

**Decision**: Use `pytest` with `pytest-mock` and `pytest-cov`  
**Rationale**:
- Industry standard for Python testing
- Excellent fixture system for test data
- Easy mocking of external APIs
- Good integration with coverage tools
- Supports parametrized tests for multiple scenarios

**Alternatives Considered**:
- `unittest`: Standard library but more verbose
- `nose2`: Less actively maintained
- `hypothesis`: Property-based testing, good for edge cases but not primary framework

**Implementation Notes**:
- Use `pytest.fixture` for GitHub API mocks
- Use `pytest.mark.parametrize` for testing multiple time periods, repositories
- Mock external API calls in unit tests
- Use real git operations in isolated test repositories for integration tests

---

### Configuration Management

**Decision**: Use `pydantic` for configuration validation and `pyyaml`/`toml` for config files  
**Rationale**:
- Type-safe configuration with validation
- Clear error messages for invalid config
- Supports environment variables and config files
- Well-integrated with modern Python practices

**Alternatives Considered**:
- `configparser`: Standard library but limited type safety
- `python-dotenv`: Only handles environment variables
- `attrs`/`dataclasses`: Less validation features

**Implementation Notes**:
- Define Pydantic models for configuration (GitHub credentials, team mappings, etc.)
- Support YAML config files for team/department structure
- Use environment variables for sensitive credentials (GITHUB_TOKEN)

---

### Caching Strategy

**Decision**: File-based caching (JSON) with optional SQLite for large datasets  
**Rationale**:
- Simple file-based caching sufficient for most use cases
- JSON format is human-readable and debuggable
- SQLite option for organizations with 500+ repositories
- No external dependencies for basic caching
- Easy to invalidate and manage

**Alternatives Considered**:
- Redis: Overkill, adds infrastructure complexity
- In-memory only: Loses data between runs, inefficient for large datasets
- PostgreSQL: Too heavy for CLI tool

**Implementation Notes**:
- Cache GitHub API responses as JSON files (keyed by repository + time period)
- Implement cache invalidation based on time-to-live (e.g., 1 hour for recent data)
- Optional SQLite database for organizations with many repositories
- Cache repository context analysis (expensive operation)

---

## Integration Patterns

### GitHub API Rate Limiting

**Pattern**: Exponential backoff with jitter  
**Implementation**:
- Respect `X-RateLimit-Remaining` header
- When rate limit hit, wait with exponential backoff: `wait_time = base_delay * (2 ** retry_count) + random_jitter`
- Log rate limit events for observability
- Allow user to configure retry behavior

### Data Collection Pipeline

**Pattern**: Collect → Transform → Aggregate → Report  
**Flow**:
1. Collect raw data from GitHub API (commits, PRs, reviews, issues)
2. Transform to internal data models (Developer, Contribution, etc.)
3. Aggregate by developer/repository/team/time period
4. Generate reports in requested format

### PR Summarization Pipeline

**Pattern**: Collect PRs → Analyze Repository Context → Generate Summary  
**Flow**:
1. Collect PRs merged to main branch in time period
2. For each PR, analyze repository context (clone if needed, analyze codebase)
3. Generate summary using LLM with PR details + repository context
4. Format summary (ensure 4-line limit)
5. Generate report in requested formats

---

## Best Practices Research

### GitHub API Best Practices
- Use authenticated requests (higher rate limits: 5000/hour vs 60/hour)
- Implement pagination for all list endpoints
- Cache responses to reduce API calls
- Use GraphQL API for complex queries (if needed, but REST is simpler for this use case)

### CLI Best Practices
- Follow GNU style for long options (`--format` not `-format`)
- Support both short and long options
- Provide `--help` for all commands
- Use exit codes: 0 for success, 1 for user error, 2 for system error
- Support `--version` flag

### Error Handling Best Practices
- Distinguish between user errors (invalid input) and system errors (API failures)
- Provide actionable error messages
- Log errors with context (repository, time period, operation)
- Handle partial failures gracefully (some repositories fail, others succeed)

---

## Open Questions Resolved

### Q: How to handle GitHub Enterprise vs GitHub.com?
**A**: Use PyGithub's `Github(base_url=...)` parameter. Detect from configuration or allow user to specify.

### Q: How to handle very large repositories (100K+ commits)?
**A**: Use pagination and streaming. Process commits in batches. Consider date range filtering to reduce data volume.

### Q: How to ensure PR summaries are exactly 4 lines?
**A**: Use prompt engineering with explicit line limit. Post-process LLM output to enforce limit (truncate or reformat if needed).

### Q: How to handle team membership data?
**A**: Support multiple input formats: YAML config file, GitHub Teams API, CSV import. Allow manual override.

---

## Dependencies Summary

**Core Dependencies**:
- `PyGithub>=2.0.0` - GitHub API client
- `click>=8.0.0` - CLI framework
- `pandas>=2.0.0` - Data processing
- `openai>=1.0.0` - LLM API for summarization
- `GitPython>=3.1.0` - Git repository operations
- `jinja2>=3.0.0` - Report templating
- `pydantic>=2.0.0` - Configuration validation
- `pytest>=7.0.0` - Testing framework
- `pytest-mock>=3.0.0` - Mocking for tests
- `pytest-cov>=4.0.0` - Coverage reporting

**Optional Dependencies**:
- `weasyprint` or `reportlab` - PDF generation (optional)
- `pyyaml` or `toml` - Config file parsing

**Development Dependencies**:
- `black` - Code formatting
- `ruff` or `flake8` - Linting
- `mypy` - Type checking

---

## Performance Considerations

### API Rate Limiting
- Authenticated requests: 5000 requests/hour
- Need to batch operations to stay within limits
- Cache aggressively to minimize API calls
- Process repositories sequentially or with controlled concurrency

### Memory Management
- Stream large datasets rather than loading all into memory
- Use pandas chunking for very large DataFrames
- Clear intermediate data structures when done

### Repository Analysis
- Clone repositories to temporary directories
- Analyze only necessary files (README, recent commits, file structure)
- Clean up temporary clones immediately after use
- Consider shallow clones for large repositories

---

## Security Considerations

### Credential Management
- Never commit tokens or credentials to repository
- Use environment variables for sensitive data
- Support credential files with restricted permissions (600)
- Provide clear documentation on credential setup

### Repository Access
- Respect repository visibility (private vs public)
- Handle authentication failures gracefully
- Log access attempts for audit purposes
- Support read-only tokens (minimum permissions)

---

## Next Steps

All technology decisions resolved. Proceed to Phase 1: Design & Contracts.

