# CLI Command Contracts

**Feature**: GitHub Developer Contribution Analytics Tools  
**Date**: 2024-12-28  
**Phase**: 1 - Design

## Overview

This document defines the CLI command contracts for all tools in the collection. All commands follow Unix philosophy: text in/out, composable, scriptable.

## Common Options

All commands support these common options:

- `--format <format>`: Output format. Values: `json`, `markdown`, `csv`, `pdf` (default: `markdown`)
- `--output <file>`: Output file path (default: stdout)
- `--config <file>`: Configuration file path (default: `~/.github-tools/config.yaml`)
- `--token <token>`: GitHub API token (or use `GITHUB_TOKEN` env var)
- `--base-url <url>`: GitHub API base URL (for GitHub Enterprise, default: `https://api.github.com`)
- `--no-cache`: Disable caching, force fresh data collection
- `--verbose`: Enable verbose logging
- `--quiet`: Suppress non-error output
- `--version`: Show version and exit
- `--help`: Show help and exit

## Command: `developer-report`

Generate developer activity report.

### Usage

```bash
github-tools developer-report [OPTIONS] --start-date <date> --end-date <date> [--repository <repo>] [--developer <username>]
```

### Arguments

- `--start-date <date>` (required): Start date (ISO format: YYYY-MM-DD or relative: "2024-01-01", "30d", "1w", "1m")
- `--end-date <date>` (required): End date (ISO format: YYYY-MM-DD or relative: "2024-12-31", "today", "yesterday")
- `--repository <repo>` (optional): Filter by repository (can specify multiple times)
- `--developer <username>` (optional): Filter by developer (can specify multiple times)
- `--team <team>` (optional): Filter by team (can specify multiple times)
- `--include-external`: Include external contributors (default: false)

### Output Formats

#### JSON Format

```json
{
  "period": {
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-12-31T23:59:59Z"
  },
  "developers": [
    {
      "username": "alice",
      "display_name": "Alice Developer",
      "total_commits": 150,
      "pull_requests_created": 25,
      "pull_requests_reviewed": 40,
      "pull_requests_merged": 22,
      "issues_created": 10,
      "issues_resolved": 8,
      "code_review_participation": 40,
      "repositories_contributed": ["org/repo1", "org/repo2"],
      "per_repository_breakdown": {
        "org/repo1": {
          "commits": 100,
          "pull_requests_created": 15,
          "pull_requests_reviewed": 20
        }
      }
    }
  ]
}
```

#### Markdown Format

```markdown
# Developer Activity Report

**Period**: 2024-01-01 to 2024-12-31

## Summary

- Total Developers: 10
- Total Contributions: 1,250

## Developers

| Username | Commits | PRs Created | PRs Reviewed | PRs Merged | Issues Created | Issues Resolved |
|----------|---------|-------------|--------------|------------|----------------|-----------------|
| alice    | 150     | 25          | 40           | 22         | 10             | 8               |

...
```

#### CSV Format

```csv
username,display_name,total_commits,pull_requests_created,pull_requests_reviewed,pull_requests_merged,issues_created,issues_resolved,code_review_participation
alice,Alice Developer,150,25,40,22,10,8,40
bob,Bob Coder,120,20,35,18,8,6,35
```

### Exit Codes

- `0`: Success
- `1`: User error (invalid arguments, authentication failure)
- `2`: System error (API failure, network error)

---

## Command: `repository-report`

Analyze repository contribution patterns.

### Usage

```bash
github-tools repository-report [OPTIONS] --start-date <date> --end-date <date> [--repository <repo>]
```

### Arguments

- `--start-date <date>` (required): Start date
- `--end-date <date>` (required): End date
- `--repository <repo>` (optional): Filter by repository (can specify multiple times, default: all org repositories)
- `--compare-previous`: Compare with previous period
- `--include-archived`: Include archived repositories (default: false)

### Output Formats

#### JSON Format

```json
{
  "period": {
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-12-31T23:59:59Z"
  },
  "repositories": [
    {
      "repository": "org/repo1",
      "total_contributions": 500,
      "active_contributors": 15,
      "commits": 300,
      "pull_requests": 100,
      "issues": 80,
      "reviews": 120,
      "trend": "increasing",
      "contribution_distribution": {
        "alice": 150,
        "bob": 120
      }
    }
  ]
}
```

### Exit Codes

- `0`: Success
- `1`: User error
- `2`: System error

---

## Command: `team-report`

Generate team and department contribution metrics.

### Usage

```bash
github-tools team-report [OPTIONS] --start-date <date> --end-date <date> [--team <team>] [--department <dept>]
```

### Arguments

- `--start-date <date>` (required): Start date
- `--end-date <date>` (required): End date
- `--team <team>` (optional): Filter by team (can specify multiple times)
- `--department <dept>` (optional): Filter by department (can specify multiple times)
- `--compare-previous`: Compare with previous period
- `--attribution-mode <mode>`: How to handle multi-team developers. Values: `full` (count in all teams), `proportional` (divide by team count), `primary` (count in primary team only)

### Output Formats

#### JSON Format

```json
{
  "period": {
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-12-31T23:59:59Z"
  },
  "teams": [
    {
      "team": "backend-team",
      "total_activity": 1000,
      "member_count": 10,
      "average_per_person": 100.0,
      "top_contributors": [
        {"username": "alice", "contributions": 150}
      ],
      "repositories_contributed": ["org/api", "org/services"]
    }
  ],
  "departments": [
    {
      "department": "engineering",
      "total_activity": 5000,
      "team_count": 5,
      "average_per_team": 1000.0,
      "team_metrics": [...]
    }
  ]
}
```

### Exit Codes

- `0`: Success
- `1`: User error
- `2`: System error

---

## Command: `pr-summary-report`

Generate periodic PR summary reports.

### Usage

```bash
github-tools pr-summary-report [OPTIONS] --period <period> --period-value <value> [--repository <repo>]
```

### Arguments

- `--period <period>` (required): Period type. Values: `daily`, `weekly`, `monthly`, `quarterly`, `yearly`
- `--period-value <value>` (required): Period value (date or identifier). Examples: `2024-12-28` (daily), `2024-W52` (weekly), `2024-12` (monthly), `2024-Q4` (quarterly), `2024` (yearly)
- `--repository <repo>` (optional): Filter by repository (can specify multiple times, default: all org repositories)
- `--main-branch <branch>`: Main branch name (default: `main`)
- `--include-context`: Include repository context analysis (default: true)
- `--max-summary-lines <n>`: Maximum lines per PR summary (default: 4)

### Output Formats

#### JSON Format

```json
{
  "period": {
    "type": "weekly",
    "value": "2024-W52",
    "start_date": "2024-12-23T00:00:00Z",
    "end_date": "2024-12-29T23:59:59Z"
  },
  "repositories": [
    {
      "repository": "org/repo1",
      "pull_requests": [
        {
          "pr_id": "123",
          "title": "Add user authentication",
          "merge_date": "2024-12-25T10:30:00Z",
          "author": "alice",
          "summary": "Implemented OAuth2 authentication flow.\nAdded login/logout endpoints.\nUpdated user model with auth fields.\nAdded integration tests.",
          "files_changed": 15,
          "additions": 200,
          "deletions": 50,
          "context_tags": ["api", "authentication", "backend"]
        }
      ]
    }
  ]
}
```

#### Markdown Format

```markdown
# PR Summary Report

**Period**: Week 52, 2024 (2024-12-23 to 2024-12-29)

## org/repo1

### PR #123: Add user authentication
**Author**: alice | **Merged**: 2024-12-25

Implemented OAuth2 authentication flow.
Added login/logout endpoints.
Updated user model with auth fields.
Added integration tests.

**Stats**: 15 files changed, +200/-50 lines

---
```

#### CSV Format

```csv
repository,pr_id,title,merge_date,author,summary,files_changed,additions,deletions
org/repo1,123,Add user authentication,2024-12-25T10:30:00Z,alice,"Implemented OAuth2 authentication flow. Added login/logout endpoints. Updated user model with auth fields. Added integration tests.",15,200,50
```

### Exit Codes

- `0`: Success
- `1`: User error
- `2`: System error

---

## Command: `trends`

Identify contribution trends and anomalies.

### Usage

```bash
github-tools trends [OPTIONS] --start-date <date> --end-date <date> [--repository <repo>] [--developer <username>]
```

### Arguments

- `--start-date <date>` (required): Start date
- `--end-date <date>` (required): End date
- `--repository <repo>` (optional): Filter by repository
- `--developer <username>` (optional): Filter by developer
- `--compare-periods <n>`: Number of previous periods to compare (default: 1)
- `--anomaly-threshold <percent>`: Threshold for anomaly detection (default: 50%)

### Output Formats

#### JSON Format

```json
{
  "period": {
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-12-31T23:59:59Z"
  },
  "trends": [
    {
      "entity_type": "developer",
      "entity_id": "alice",
      "trend": "increasing",
      "change_percentage": 25.5,
      "current_period": {"contributions": 150},
      "previous_period": {"contributions": 120}
    }
  ],
  "anomalies": [
    {
      "entity_type": "developer",
      "entity_id": "bob",
      "type": "drop",
      "magnitude": 75.0,
      "current_period": {"contributions": 10},
      "previous_period": {"contributions": 40},
      "duration_days": 30
    }
  ]
}
```

### Exit Codes

- `0`: Success
- `1`: User error
- `2`: System error

---

## Error Output Format

All commands output errors to stderr in consistent format:

### JSON Format (when `--format json`)

```json
{
  "error": {
    "code": "AUTHENTICATION_FAILED",
    "message": "Invalid GitHub token",
    "details": "Token expired or invalid"
  }
}
```

### Text Format (default)

```
Error: Invalid GitHub token
Details: Token expired or invalid
```

---

## Configuration File Format

Configuration file (YAML format):

```yaml
github:
  token: ${GITHUB_TOKEN}  # Can use env var
  base_url: https://api.github.com  # For GitHub Enterprise

organization:
  name: myorg
  repositories:
    - org/repo1
    - org/repo2
  # Or use GitHub API to discover

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

cache:
  enabled: true
  ttl_hours: 1
  directory: ~/.github-tools/cache

pr_summarization:
  provider: openai
  model: gpt-3.5-turbo
  max_lines: 4
  include_context: true
```

---

## Standard Input/Output

- **stdin**: Not used (all input via command-line arguments)
- **stdout**: Report output (JSON, Markdown, CSV, PDF)
- **stderr**: Logs, errors, warnings

## Composing Commands

Commands are designed to be composable:

```bash
# Pipe JSON output to jq for filtering
github-tools developer-report --format json --start-date 2024-01-01 --end-date 2024-12-31 | jq '.developers[] | select(.total_commits > 100)'

# Generate report and save to file
github-tools pr-summary-report --period monthly --period-value 2024-12 --output pr-summary-dec-2024.md

# Chain commands
github-tools repository-report --format json | github-tools trends --input -
```

