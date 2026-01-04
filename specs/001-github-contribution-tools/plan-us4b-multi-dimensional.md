# Implementation Plan: Multi-Dimensional PR Impact Analysis (User Story 4b)

**Branch**: `001-github-contribution-tools` | **Date**: 2024-12-28 | **Spec**: [user-story-4b-multi-dimensional-analysis.md](./user-story-4b-multi-dimensional-analysis.md)  
**Input**: Feature specification from `/specs/001-github-contribution-tools/user-story-4b-multi-dimensional-analysis.md`  
**Parent Story**: User Story 4 (PR Summarization)

**Note**: This plan extends the existing PR summarization feature (User Story 4) with multi-dimensional impact analysis across 7 critical dimensions. See [plan.md](./plan.md) for the main feature implementation plan.

## Summary

Enhancement to PR summarization feature that adds structured analysis across 7 critical dimensions: Security Impact, Cost/FinOps Impact, Operational Impact, Architectural Integrity, Mentorship Insights, Data Governance Impact, and AI Governance Impact (SAIF framework). Implements file pattern detection, dimension-specific analyzers, structured LLM prompts, and response parsing to produce comprehensive PR impact summaries. Maintains backward compatibility with existing PR summarization while extending output format.

## Technical Context

**Language/Version**: Python 3.11+ (inherited from parent feature)  
**Primary Dependencies** (in addition to existing):
- `PyGithub` (existing) for accessing PR file diffs via `pull_request.get_files()`
- LLM providers (existing provider abstraction from User Story 4a)
- `pydantic` (existing) for structured response validation
- `regex` or built-in `re` for file pattern matching
- Optional: `terraform-parser` or similar for IAC file analysis (future enhancement)

**Storage**: No changes - uses existing file-based caching and configuration system  
**Testing**: `pytest` with `pytest-mock` (existing) + LLM response mocking  
**Target Platform**: Linux/macOS/Windows (cross-platform, same as parent)  
**Project Type**: Enhancement to existing single project  
**Performance Goals**: 
- Multi-dimensional analysis adds ≤ 2 seconds to existing PR summary generation time
- Batch processing maintains ≥ 8 PRs/minute throughput
- File analysis completes in < 500ms per PR (cached when possible)
- LLM token usage optimized (structured prompts, efficient file summaries)

**Constraints**: 
- Must maintain backward compatibility with existing PR summarization
- No breaking changes to CLI interface (additive only)
- Must work with all LLM providers (OpenAI, Claude, Gemini, Generic)
- Analysis must handle PRs with 100+ changed files efficiently
- Must gracefully handle missing or incomplete file data

**Scale/Scope**: 
- Support all 7 dimensions for every PR (with N/A when not applicable)
- Handle PRs with up to 200 changed files
- Support same scale as parent feature (500 repos, 50 team members, 1 year periods)
- Process file patterns: IAC (Terraform, CloudFormation), AI/ML models, data files, config files

**Integration Points**:
- Extends existing `src/github_tools/summarizers/llm_summarizer.py`
- Integrates with existing `src/github_tools/collectors/pr_collector.py` (add file diff collection)
- Updates `src/github_tools/cli/pr_summary_report.py` (add dimensional format option)
- Uses existing LLM provider abstraction from User Story 4a
- Extends `src/github_tools/reports/generator.py` and templates

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Library-First ✅
- **Status**: COMPLIANT
- **Rationale**: Multi-dimensional analyzers are implemented as standalone library modules (`src/github_tools/summarizers/dimensions/`). File pattern detector is a reusable library component. Each dimension analyzer is independently testable. The orchestrator composes analyzers following library-first pattern.

### II. CLI Interface ✅
- **Status**: COMPLIANT
- **Rationale**: Adds optional `--dimensional-analysis` flag to existing CLI. No changes to text in/out protocol. Backward compatible - existing commands work unchanged. New format is additive only.

### III. Test-First (NON-NEGOTIABLE) ✅
- **Status**: COMPLIANT
- **Rationale**: All dimension analyzers will have unit tests written first. File pattern detector tests precede implementation. Integration tests for multi-dimensional analysis written before implementation. TDD cycle strictly enforced.

### IV. Integration Testing ✅
- **Status**: COMPLIANT
- **Rationale**: Integration tests required for:
  - Multi-dimensional analysis end-to-end flow
  - File pattern detection with real PR file data
  - LLM response parsing and validation
  - Accuracy validation with ground truth dataset (T103)
  - Performance benchmarking (T104)

### V. Observability & Versioning ✅
- **Status**: COMPLIANT
- **Rationale**: Structured logging for dimension analysis progress, file pattern detection, LLM token usage. Dimension analysis metadata logged for debugging. Error messages include actionable hints. Versioning: MINOR bump (new functionality, backward compatible).

**Gate Result**: ✅ PASS - All constitution principles satisfied. Proceed to Phase 0.

## Phase 0: Research & Design Decisions

### Research Areas

1. **GitHub API PR File Access**
   - PyGithub `pull_request.get_files()` method details and limitations
   - Handling large PRs with 100+ files (pagination, summarization strategies)
   - Accessing file patch/diff content efficiently
   - Rate limit considerations for file access

2. **File Pattern Detection**
   - IAC file patterns (Terraform `.tf`, CloudFormation `.yaml/.json`, Pulumi, etc.)
   - AI/ML model file patterns (`.pkl`, `.h5`, `.onnx`, `.pb`, model directories)
   - Data file patterns (`.csv`, `.parquet`, database schemas, data pipeline configs)
   - Configuration file patterns (`.env`, `.config`, security configs)

3. **LLM Prompt Engineering**
   - Structured prompt templates for dimensional analysis
   - Token-efficient file content summarization
   - Response format consistency across providers
   - Handling N/A cases in prompts

4. **Response Parsing & Validation**
   - Structured output parsing (JSON-like format from LLM)
   - Validation of impact levels (High/Medium/Low, etc.)
   - Error handling for malformed LLM responses
   - Fallback strategies when parsing fails

5. **SAIF Framework Integration**
   - Google SAIF framework principles and requirements
   - AI governance checklist items
   - Model lifecycle considerations
   - Ethical guidelines compliance indicators

### Technical Decisions Needed

- [ ] File access strategy: Load all files vs. sample-based for large PRs
- [ ] File content summarization: Full diff vs. file-level summary vs. pattern-based extraction
- [ ] LLM prompt structure: Single comprehensive prompt vs. dimension-specific prompts
- [ ] Response format: Structured JSON vs. free-form text with parsing
- [ ] Caching strategy: Cache file analysis results, dimension analysis results
- [ ] Performance optimization: Parallel dimension analysis vs. sequential

## Phase 1: Design Artifacts

### Data Model Extensions

Extend existing data models:

**New Entity: PRFileAnalysis**
- Fields: `filename`, `file_type`, `pattern_category`, `additions`, `deletions`, `is_iac`, `is_ai_model`, `is_data_file`, `is_config`, `summary`
- Relationships: Belongs to `PullRequest`

**New Entity: DimensionalAnalysis**
- Fields: `security_impact`, `cost_impact`, `operational_impact`, `architectural_integrity`, `mentorship_insights`, `data_governance_impact`, `ai_governance_impact`
- Each dimension: `level` (High/Medium/Low/etc.), `description`, `is_applicable` (boolean)
- Relationships: Belongs to `PullRequestSummary`

### API Contracts

**File Pattern Detector Contract** (`contracts/file-pattern-detector-contract.md`):
- `detect_patterns(files: List[PRFile]) -> Dict[str, List[str]]`
- Returns pattern categories mapped to file lists
- Pattern categories: `iac`, `ai_model`, `data_file`, `config`, `security_config`, `infrastructure`

**Dimension Analyzer Contract** (`contracts/dimension-analyzer-contract.md`):
- `analyze(pr_context: PRContext, file_analysis: PRFileAnalysis) -> DimensionResult`
- Each analyzer implements this interface
- Returns structured result with level and description

**LLM Dimensional Prompt Contract** (`contracts/dimensional-prompt-contract.md`):
- Input: PR metadata, file analysis summary, dimension-specific context
- Output: Structured response with all 7 dimensions
- Format: JSON-like structure parseable by `dimensional_parser.py`

### Configuration Schema

Extend `src/github_tools/utils/config.py` with dimensional analysis configuration:

```python
class DimensionalAnalysisConfig(BaseModel):
    """Dimensional analysis configuration."""
    enabled: bool = True
    file_analysis_cache_ttl: int = 3600  # 1 hour
    max_files_per_pr: int = 200  # Summarize if exceeded
    emoji_enabled: bool = True
    dimensions: Dict[str, bool] = {
        "security": True,
        "cost": True,
        "operational": True,
        "architectural": True,
        "mentorship": True,
        "data_governance": True,
        "ai_governance": True,
    }
```

## Phase 2: Implementation Structure

### New Source Files

```
src/github_tools/summarizers/
├── file_pattern_detector.py      # Detect IAC, AI/ML, data file patterns
├── multi_dimensional_analyzer.py # Orchestrator for all dimensions
├── dimensions/
│   ├── __init__.py
│   ├── security_analyzer.py      # Security impact analysis
│   ├── cost_analyzer.py          # Cost/FinOps impact analysis
│   ├── operational_analyzer.py   # Operational impact analysis
│   ├── architectural_analyzer.py # Architectural integrity analysis
│   ├── mentorship_analyzer.py    # Mentorship insights analysis
│   ├── data_governance_analyzer.py # Data governance impact analysis
│   └── ai_governance_analyzer.py # AI governance impact (SAIF)
├── prompts/
│   ├── __init__.py
│   └── dimensional_prompts.py    # Structured prompt templates
└── parsers/
    ├── __init__.py
    └── dimensional_parser.py     # Parse LLM structured responses
```

### Modified Source Files

- `src/github_tools/collectors/pr_collector.py` - Add PR file collection via `get_files()`
- `src/github_tools/summarizers/llm_summarizer.py` - Integrate multi-dimensional analysis
- `src/github_tools/cli/pr_summary_report.py` - Add `--dimensional-analysis` flag
- `src/github_tools/reports/generator.py` - Add multi-dimensional format support
- `src/github_tools/reports/templates/pr_summary_multidimensional.md` - New template

### Test Files

```
tests/unit/summarizers/
├── test_file_pattern_detector.py
├── test_multi_dimensional_analyzer.py
└── dimensions/
    ├── test_security_analyzer.py
    ├── test_cost_analyzer.py
    ├── test_operational_analyzer.py
    ├── test_architectural_analyzer.py
    ├── test_mentorship_analyzer.py
    ├── test_data_governance_analyzer.py
    └── test_ai_governance_analyzer.py

tests/integration/
├── test_pr_summary_multi_dimensional.py
├── test_dimensional_accuracy.py          # T103: Accuracy validation
└── fixtures/
    └── dimensional_ground_truth.json    # Ground truth PR annotations

tests/performance/
└── test_dimensional_performance.py     # T104: Performance benchmarking

tests/contract/
└── test_pr_summary_multidimensional_contract.py
```

## Complexity Tracking

No constitution violations. Enhancement follows library-first pattern, maintains CLI compatibility, and adheres to test-first development. Multi-dimensional analysis adds moderate complexity but improves PR understanding and organizational impact assessment. Complexity is justified by the value provided to security, FinOps, operations, and governance teams.

## Dependencies

- User Story 4 (PR Summarization) must be complete and tested
- User Story 4a (Multi-Provider LLM Support) should be complete (uses provider abstraction)
- Access to PR file diffs via GitHub API (PyGithub `get_files()` method)
- Understanding of SAIF framework for AI governance analysis
- Domain expertise for ground truth dataset creation (security, FinOps, architecture teams)

## Risks & Mitigations

1. **Risk**: LLM may not consistently produce structured dimensional analysis
   - **Mitigation**: Structured prompts with explicit format requirements, response validation, fallback to dimension-by-dimension analysis if needed

2. **Risk**: File analysis for large PRs may be slow or hit rate limits
   - **Mitigation**: Implement file summarization for PRs with >200 files, cache file analysis results, batch API calls efficiently

3. **Risk**: Analysis accuracy may not meet 90% target
   - **Mitigation**: Iterative prompt refinement, ground truth validation (T103), human review samples, accuracy monitoring

4. **Risk**: Performance degradation from additional analysis
   - **Mitigation**: Efficient file pattern detection, optimized prompts, caching strategies, performance benchmarking (T104)

5. **Risk**: Token costs increase significantly with file content
   - **Mitigation**: File content summarization, structured prompts, token optimization (T105), caching of analysis results

6. **Risk**: SAIF framework understanding may be incomplete
   - **Mitigation**: Reference official SAIF documentation, consult with AI governance team, iterative refinement based on feedback

## Performance Considerations

### File Analysis Optimization
- Cache file pattern detection results (file types don't change)
- Summarize large PRs: For PRs with >200 files, analyze top 50 by lines changed + sample of each pattern category
- Batch GitHub API calls for file access

### LLM Token Optimization
- Summarize file diffs before sending to LLM (extract key changes, not full patches)
- Use structured prompts with placeholders (avoid repeating context)
- Cache dimension analysis results for identical PR contexts

### Parallel Processing
- File pattern detection can run in parallel for multiple files
- Dimension analyzers can run in parallel (independent analysis)
- LLM calls can be batched or parallelized if provider supports

## Next Steps

1. Complete Phase 0 research on GitHub API file access patterns
2. Design structured prompt templates for dimensional analysis
3. Create ground truth dataset for accuracy validation
4. Generate detailed task breakdown (already in tasks.md T077-T105)
5. Begin test-first implementation following TDD principles

## Implementation Phases Summary

1. **Phase 1**: File Pattern Detector (T088) - Foundation for all dimensions
2. **Phase 2**: Dimension Analyzers (T089-T095) - Implement all 7 analyzers in parallel
3. **Phase 3**: Multi-Dimensional Orchestrator (T096) - Compose analyzers
4. **Phase 4**: LLM Integration (T097, T098, T101) - Prompts, summarizer integration, parsing
5. **Phase 5**: Report Generation (T099, T100, T102) - File collection, templates, CLI
6. **Phase 6**: Validation & Performance (T103, T104, T105) - Accuracy tests, benchmarking, optimization

