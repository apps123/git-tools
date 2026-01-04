# Quick Start Guide

**Feature**: GitHub Developer Contribution Analytics Tools  
**Date**: 2024-12-28

## Installation

### Prerequisites

- Python 3.11 or higher
- GitHub Personal Access Token (PAT) with appropriate scopes
- Access to organization repositories

### Install from Source

```bash
git clone <repository-url>
cd git-tools
pip install -e .
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Set GitHub Token

**Option A: Environment Variable** (Recommended)

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

**Option B: Configuration File**

Create `~/.github-tools/config.yaml`:

```yaml
github:
  token: ghp_your_token_here
  base_url: https://api.github.com  # Use https://github.example.com/api/v3 for GitHub Enterprise

organization:
  name: myorg
```

**Option C: Command-Line**

```bash
github-tools --token ghp_your_token_here <command>
```

### 2. Configure Teams (Optional)

Create or update `~/.github-tools/config.yaml`:

```yaml
teams:
  - name: backend-team
    members:
      - alice
      - bob
    department: engineering
  - name: frontend-team
    members:
      - charlie
      - diana
    department: engineering

departments:
  - name: engineering
    teams:
      - backend-team
      - frontend-team
```

## Basic Usage

### Generate Developer Activity Report

```bash
# Last 30 days, JSON output
github-tools developer-report \
  --start-date 30d \
  --end-date today \
  --format json

# Specific date range, Markdown output
github-tools developer-report \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --format markdown \
  --output developer-report-2024.md

# Filter by repository
github-tools developer-report \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --repository org/repo1 \
  --repository org/repo2
```

### Generate Repository Contribution Analysis

```bash
# Analyze all repositories
github-tools repository-report \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --format json

# Compare with previous period
github-tools repository-report \
  --start-date 2024-12-01 \
  --end-date 2024-12-31 \
  --compare-previous \
  --format markdown
```

### Generate Team Metrics

```bash
# Team-level metrics
github-tools team-report \
  --start-date 2024-Q4 \
  --end-date 2024-Q4 \
  --team backend-team \
  --format json

# Department-level metrics
github-tools team-report \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --department engineering \
  --format markdown
```

### Generate PR Summary Report

```bash
# Weekly PR summary
github-tools pr-summary-report \
  --start-date 1w \
  --end-date today \
  --format markdown \
  --output pr-summary-week-52.md

# Weekly PR summary with multi-dimensional analysis
github-tools pr-summary-report \
  --start-date 1w \
  --end-date today \
  --dimensional-analysis \
  --format markdown \
  --output pr-analysis-week-52.md

# Monthly PR summary for specific repository
github-tools pr-summary-report \
  --start-date 2024-12-01 \
  --end-date 2024-12-31 \
  --repository org/repo1 \
  --format json

# PR summary with local LLM (Claude Desktop)
github-tools pr-summary-report \
  --start-date 1w \
  --end-date today \
  --llm-provider claude-local \
  --format markdown

# PR summary with Google Gemini
github-tools pr-summary-report \
  --start-date 1w \
  --end-date today \
  --llm-provider gemini \
  --gemini-api-key ${GOOGLE_API_KEY} \
  --format markdown
```

### Identify Trends and Anomalies

```bash
# Developer trends
github-tools trends \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --developer alice \
  --format json

# Repository trends with anomaly detection
github-tools trends \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --repository org/repo1 \
  --anomaly-threshold 50 \
  --format markdown
```

## Common Workflows

### Weekly Team Report

```bash
#!/bin/bash
# Generate weekly reports for all teams

WEEK=$(date +%Y-W%V)
START=$(date -d "last monday" +%Y-%m-%d)
END=$(date -d "last sunday" +%Y-%m-%d)

# Developer report
github-tools developer-report \
  --start-date "$START" \
  --end-date "$END" \
  --format markdown \
  --output "reports/developer-report-$WEEK.md"

# PR summary
github-tools pr-summary-report \
  --period weekly \
  --period-value "$WEEK" \
  --format markdown \
  --output "reports/pr-summary-$WEEK.md"

# Team metrics
github-tools team-report \
  --start-date "$START" \
  --end-date "$END" \
  --format json \
  --output "reports/team-metrics-$WEEK.json"
```

### Monthly Executive Summary

```bash
#!/bin/bash
# Generate monthly summary for leadership

MONTH=$(date +%Y-%m)
START=$(date -d "$(date +%Y-%m-01)" +%Y-%m-%d)
END=$(date -d "$(date +%Y-%m-01) +1 month -1 day" +%Y-%m-%d)

# Department-level metrics
github-tools team-report \
  --start-date "$START" \
  --end-date "$END" \
  --format markdown \
  --output "reports/department-summary-$MONTH.md"

# Repository health
github-tools repository-report \
  --start-date "$START" \
  --end-date "$END" \
  --compare-previous \
  --format markdown \
  --output "reports/repository-health-$MONTH.md"

# PR summary
github-tools pr-summary-report \
  --period monthly \
  --period-value "$MONTH" \
  --format markdown \
  --output "reports/pr-summary-$MONTH.md"
```

### Find Top Contributors

```bash
# Get top 10 contributors by commits
github-tools developer-report \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --format json | \
  jq '.developers | sort_by(.total_commits) | reverse | .[0:10]'
```

### Identify Declining Repositories

```bash
# Find repositories with decreasing activity
github-tools repository-report \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --compare-previous \
  --format json | \
  jq '.repositories[] | select(.trend == "decreasing")'
```

## Output Formats

### JSON Format

Machine-readable, suitable for further processing:

```bash
github-tools developer-report --format json | jq '.developers[0]'
```

### Markdown Format

Human-readable, suitable for documentation:

```bash
github-tools developer-report --format markdown > report.md
```

### CSV Format

Suitable for spreadsheet analysis:

```bash
github-tools developer-report --format csv > report.csv
```

### PDF Format (Optional)

Requires additional dependencies:

```bash
pip install weasyprint
github-tools developer-report --format pdf > report.pdf
```

## Caching

### Enable Caching (Default)

Caching is enabled by default. Data is cached for 1 hour (recent data) or 24 hours (historical data).

Cache location: `~/.github-tools/cache/`

### Disable Caching

```bash
github-tools developer-report --no-cache ...
```

### Clear Cache

```bash
rm -rf ~/.github-tools/cache/*
```

## Troubleshooting

### Authentication Errors

**Error**: `401 Unauthorized`

**Solution**: 
- Verify token is valid: `curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user`
- Check token has required scopes: `repo`, `read:org`, `read:user`
- Regenerate token if expired

### Rate Limit Errors

**Error**: `403 Forbidden` with rate limit message

**Solution**:
- Wait for rate limit reset (check `X-RateLimit-Reset` header)
- Use `--no-cache` sparingly (caching reduces API calls)
- Process repositories sequentially (not in parallel)

### Repository Not Found

**Error**: `404 Not Found`

**Solution**:
- Verify repository name is correct: `org/repo-name`
- Check token has access to private repositories
- Verify repository exists and is not archived

### PR Summarization Failures

**Error**: PR summary generation fails

**Solution**:
- Check OpenAI API key is set: `export OPENAI_API_KEY=sk-...`
- Verify sufficient API credits
- Check repository is accessible (for context analysis)
- Use `--no-context` to skip repository context analysis

## Advanced Usage

### Custom Time Periods

```bash
# Relative dates
github-tools developer-report --start-date 30d --end-date today
github-tools developer-report --start-date 1w --end-date yesterday
github-tools developer-report --start-date 1m --end-date today

# Absolute dates
github-tools developer-report --start-date 2024-01-01 --end-date 2024-12-31
```

### Filtering

```bash
# Multiple repositories
github-tools developer-report \
  --repository org/repo1 \
  --repository org/repo2 \
  --repository org/repo3

# Multiple developers
github-tools developer-report \
  --developer alice \
  --developer bob

# Multiple teams
github-tools team-report \
  --team backend-team \
  --team frontend-team
```

### Composing Commands

```bash
# Pipe JSON to jq for filtering
github-tools developer-report --format json | \
  jq '.developers[] | select(.total_commits > 100)'

# Generate report and process
github-tools repository-report --format json | \
  python process_report.py

# Chain commands
github-tools repository-report --format json | \
  github-tools trends --input -
```

## Next Steps

- Read [Data Model](./data-model.md) for entity definitions
- Read [CLI Contracts](./contracts/cli-contracts.md) for detailed command reference
- Read [GitHub API Contract](./contracts/github-api-contract.md) for API usage details
- Read [Report Format Contract](./contracts/report-format-contract.md) for output format specifications

## Getting Help

```bash
# Command help
github-tools --help
github-tools developer-report --help

# Version
github-tools --version

# Verbose logging
github-tools developer-report --verbose ...
```

