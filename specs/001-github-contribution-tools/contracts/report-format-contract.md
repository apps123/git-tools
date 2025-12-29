# Report Format Contracts

**Feature**: GitHub Developer Contribution Analytics Tools  
**Date**: 2024-12-28  
**Phase**: 1 - Design

## Overview

This document defines the output format contracts for all report types. Formats must be consistent, parseable, and suitable for both human consumption and machine processing.

## Common Format Requirements

### Human-Readable Formats (Markdown, PDF)

- Must be readable without special tools
- Must include metadata (period, generation date, tool version)
- Must use consistent structure and styling
- Must support tables, lists, and sections

### Machine-Readable Formats (JSON, CSV)

- Must be valid JSON/CSV (parseable by standard tools)
- Must include schema/metadata for validation
- Must use consistent field names
- Must handle missing/null values gracefully

## Developer Report Formats

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "metadata": {
      "type": "object",
      "properties": {
        "generated_at": {"type": "string", "format": "date-time"},
        "tool_version": {"type": "string"},
        "period": {
          "type": "object",
          "properties": {
            "start_date": {"type": "string", "format": "date-time"},
            "end_date": {"type": "string", "format": "date-time"}
          },
          "required": ["start_date", "end_date"]
        }
      },
      "required": ["generated_at", "tool_version", "period"]
    },
    "summary": {
      "type": "object",
      "properties": {
        "total_developers": {"type": "integer"},
        "total_contributions": {"type": "integer"}
      }
    },
    "developers": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "username": {"type": "string"},
          "display_name": {"type": "string"},
          "total_commits": {"type": "integer"},
          "pull_requests_created": {"type": "integer"},
          "pull_requests_reviewed": {"type": "integer"},
          "pull_requests_merged": {"type": "integer"},
          "issues_created": {"type": "integer"},
          "issues_resolved": {"type": "integer"},
          "code_review_participation": {"type": "integer"},
          "repositories_contributed": {
            "type": "array",
            "items": {"type": "string"}
          },
          "per_repository_breakdown": {
            "type": "object",
            "additionalProperties": {
              "type": "object",
              "properties": {
                "commits": {"type": "integer"},
                "pull_requests_created": {"type": "integer"},
                "pull_requests_reviewed": {"type": "integer"}
              }
            }
          }
        },
        "required": ["username", "total_commits", "pull_requests_created", "pull_requests_reviewed", "pull_requests_merged", "issues_created", "issues_resolved", "code_review_participation", "repositories_contributed"]
      }
    }
  },
  "required": ["metadata", "summary", "developers"]
}
```

### CSV Schema

**File**: `developer-report-{start_date}-{end_date}.csv`

**Columns** (in order):
1. `username` (string)
2. `display_name` (string, nullable)
3. `total_commits` (integer)
4. `pull_requests_created` (integer)
5. `pull_requests_reviewed` (integer)
6. `pull_requests_merged` (integer)
7. `issues_created` (integer)
8. `issues_resolved` (integer)
9. `code_review_participation` (integer)
10. `repositories_contributed` (string, comma-separated list)

**Notes**:
- Header row required
- UTF-8 encoding
- Comma-separated, double-quote strings containing commas
- Null values represented as empty string

### Markdown Schema

```markdown
# Developer Activity Report

**Generated**: {ISO 8601 timestamp}
**Tool Version**: {version}
**Period**: {start_date} to {end_date}

## Summary

- Total Developers: {count}
- Total Contributions: {count}

## Developers

| Username | Display Name | Commits | PRs Created | PRs Reviewed | PRs Merged | Issues Created | Issues Resolved |
|----------|--------------|---------|-------------|--------------|------------|----------------|-----------------|
| {username} | {display_name} | {count} | {count} | {count} | {count} | {count} | {count} |

### {username}

**Repositories**: {comma-separated list}

#### Per-Repository Breakdown

| Repository | Commits | PRs Created | PRs Reviewed |
|------------|---------|-------------|--------------|
| {repo} | {count} | {count} | {count} |
```

---

## Repository Report Formats

### JSON Schema

```json
{
  "metadata": {...},
  "summary": {
    "total_repositories": {"type": "integer"},
    "total_contributions": {"type": "integer"}
  },
  "repositories": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "repository": {"type": "string"},
        "total_contributions": {"type": "integer"},
        "active_contributors": {"type": "integer"},
        "commits": {"type": "integer"},
        "pull_requests": {"type": "integer"},
        "issues": {"type": "integer"},
        "reviews": {"type": "integer"},
        "trend": {"type": "string", "enum": ["increasing", "decreasing", "stable"]},
        "contribution_distribution": {
          "type": "object",
          "additionalProperties": {"type": "integer"}
        }
      }
    }
  }
}
```

---

## PR Summary Report Formats

### JSON Schema

```json
{
  "metadata": {...},
  "period": {
    "type": {"type": "string", "enum": ["daily", "weekly", "monthly", "quarterly", "yearly"]},
    "value": {"type": "string"},
    "start_date": {"type": "string", "format": "date-time"},
    "end_date": {"type": "string", "format": "date-time"}
  },
  "repositories": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "repository": {"type": "string"},
        "pull_requests": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "pr_id": {"type": "string"},
              "title": {"type": "string"},
              "merge_date": {"type": "string", "format": "date-time"},
              "author": {"type": "string"},
              "summary": {"type": "string"},
              "files_changed": {"type": "integer"},
              "additions": {"type": "integer"},
              "deletions": {"type": "integer"},
              "context_tags": {
                "type": "array",
                "items": {"type": "string"}
              }
            },
            "required": ["pr_id", "title", "merge_date", "author", "summary"]
          }
        }
      }
    }
  }
}
```

### Markdown Schema

```markdown
# PR Summary Report

**Period**: {period_type} {period_value} ({start_date} to {end_date})
**Generated**: {timestamp}

## {repository}

### PR #{pr_id}: {title}
**Author**: {author} | **Merged**: {merge_date}

{summary_line_1}
{summary_line_2}
{summary_line_3}
{summary_line_4}

**Stats**: {files_changed} files changed, +{additions}/-{deletions} lines

**Tags**: {context_tags}

---
```

**Summary Format Rules**:
- Exactly 4 lines (or fewer if PR is simple)
- Each line is a complete sentence
- Lines separated by newline (`\n`)
- No markdown formatting in summary (plain text)

### CSV Schema

**File**: `pr-summary-{period_type}-{period_value}.csv`

**Columns**:
1. `repository` (string)
2. `pr_id` (string)
3. `title` (string)
4. `merge_date` (ISO 8601 datetime)
5. `author` (string)
6. `summary` (string, newlines represented as `\n`)
7. `files_changed` (integer)
8. `additions` (integer)
9. `deletions` (integer)
10. `context_tags` (string, comma-separated)

---

## Team Report Formats

### JSON Schema

```json
{
  "metadata": {...},
  "teams": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "team": {"type": "string"},
        "total_activity": {"type": "integer"},
        "member_count": {"type": "integer"},
        "average_per_person": {"type": "number"},
        "top_contributors": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "username": {"type": "string"},
              "contributions": {"type": "integer"}
            }
          }
        },
        "repositories_contributed": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    }
  },
  "departments": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "department": {"type": "string"},
        "total_activity": {"type": "integer"},
        "team_count": {"type": "integer"},
        "average_per_team": {"type": "number"},
        "team_metrics": {
          "type": "array",
          "items": {"$ref": "#/definitions/team"}
        }
      }
    }
  }
}
```

---

## Trends Report Formats

### JSON Schema

```json
{
  "metadata": {...},
  "trends": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "entity_type": {"type": "string", "enum": ["developer", "repository", "team"]},
        "entity_id": {"type": "string"},
        "trend": {"type": "string", "enum": ["increasing", "decreasing", "stable"]},
        "change_percentage": {"type": "number"},
        "current_period": {
          "type": "object",
          "properties": {
            "contributions": {"type": "integer"}
          }
        },
        "previous_period": {
          "type": "object",
          "properties": {
            "contributions": {"type": "integer"}
          }
        }
      }
    }
  },
  "anomalies": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "entity_type": {"type": "string"},
        "entity_id": {"type": "string"},
        "type": {"type": "string", "enum": ["drop", "spike"]},
        "magnitude": {"type": "number"},
        "current_period": {...},
        "previous_period": {...},
        "duration_days": {"type": "integer"}
      }
    }
  }
}
```

---

## Format Validation

### JSON Validation

- Must be valid JSON (parseable by `json.loads()`)
- Must conform to JSON Schema (if schema provided)
- Must use UTF-8 encoding
- Must use ISO 8601 for dates/timestamps

### CSV Validation

- Must be valid CSV (parseable by standard CSV parser)
- Must have header row
- Must use UTF-8 encoding
- Must handle special characters (quotes, commas, newlines) correctly

### Markdown Validation

- Must be valid Markdown (renderable by common Markdown parsers)
- Must use consistent heading levels
- Must use consistent table formatting
- Must escape special characters in code blocks

---

## Versioning

Report formats are versioned:
- Version in `metadata.tool_version` field
- Breaking changes require major version bump
- Backward compatibility maintained for at least 2 major versions

---

## Error Reports

When errors occur during report generation:

### JSON Error Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional context",
    "timestamp": "2024-12-28T10:30:00Z"
  },
  "partial_results": {
    // Include any successfully generated data
  }
}
```

### Text Error Format

```
Error: {message}
Code: {code}
Details: {details}
Timestamp: {timestamp}
```

Errors always output to stderr, never mixed with report data.

