# Data Model

**Feature**: GitHub Developer Contribution Analytics Tools  
**Date**: 2024-12-28  
**Phase**: 1 - Design

## Overview

This document defines the core data models for the GitHub contribution analytics tools. All models are designed to be serializable to JSON/CSV for machine-readable output and human-readable reports.

## Core Entities

### Developer

Represents an individual contributor identified by GitHub username.

**Attributes**:
- `username` (string, required): GitHub username (unique identifier)
- `display_name` (string, optional): Display name from GitHub profile
- `email` (string, optional): Email address (if available)
- `organization_member` (boolean, required): Whether user is a member of the organization
- `team_affiliations` (list[string], optional): List of team names this developer belongs to
- `external` (boolean, required): Whether contributor is external to organization

**Relationships**:
- One-to-many with `Contribution` (developer has many contributions)
- Many-to-many with `Team` (developer can belong to multiple teams)

**Validation Rules**:
- `username` must be non-empty and match GitHub username format
- `team_affiliations` must reference valid team names if provided

**State**: Immutable (developer identity doesn't change, but affiliations may)

---

### Repository

Represents a GitHub repository within the organization.

**Attributes**:
- `name` (string, required): Repository name
- `full_name` (string, required): Full repository name (org/repo)
- `owner` (string, required): Organization or user that owns the repository
- `visibility` (enum: "public" | "private", required): Repository visibility
- `created_at` (datetime, required): Repository creation timestamp
- `updated_at` (datetime, required): Last update timestamp
- `default_branch` (string, required): Default branch name (typically "main")
- `archived` (boolean, required): Whether repository is archived
- `description` (string, optional): Repository description

**Relationships**:
- One-to-many with `Contribution` (repository has many contributions)
- One-to-many with `PullRequestSummary` (repository has many PR summaries)

**Validation Rules**:
- `full_name` must match pattern `owner/name`
- `default_branch` must exist in repository
- `created_at` <= `updated_at`

**State**: Mutable (archived status, description can change)

---

### Contribution

Represents a single contribution event (commit, pull request, review, issue).

**Attributes**:
- `id` (string, required): Unique contribution identifier (GitHub ID or hash)
- `type` (enum: "commit" | "pull_request" | "review" | "issue" | "comment", required): Contribution type
- `timestamp` (datetime, required): When contribution occurred
- `repository` (string, required): Repository full name (reference to Repository)
- `developer` (string, required): Developer username (reference to Developer)
- `title` (string, optional): Title/description of contribution
- `state` (string, optional): State (e.g., "open", "closed", "merged" for PRs; "open", "closed" for issues)
- `metadata` (object, optional): Type-specific metadata:
  - For commits: `sha`, `message`, `files_changed`, `additions`, `deletions`
  - For PRs: `number`, `base_branch`, `head_branch`, `merged`, `review_count`, `comment_count`
  - For reviews: `review_id`, `state` ("approved", "changes_requested", "commented"), `pr_number`
  - For issues: `number`, `labels`, `assignees`

**Relationships**:
- Many-to-one with `Developer` (contribution belongs to one developer)
- Many-to-one with `Repository` (contribution belongs to one repository)

**Validation Rules**:
- `timestamp` must be valid datetime
- `type` must be one of allowed values
- `repository` must reference valid repository
- `developer` must reference valid developer
- For PRs: `state` must be "open", "closed", or "merged"
- For reviews: `state` must be "approved", "changes_requested", or "commented"

**State**: Immutable (contributions are historical records)

---

### Team

Represents a group of developers within the organization.

**Attributes**:
- `name` (string, required): Team name (unique identifier)
- `members` (list[string], required): List of developer usernames
- `department` (string, optional): Department name this team belongs to
- `description` (string, optional): Team description

**Relationships**:
- Many-to-many with `Developer` (team has many developers)
- Many-to-one with `Department` (team belongs to one department, optional)

**Validation Rules**:
- `name` must be non-empty
- `members` must contain valid developer usernames
- `members` list must not be empty

**State**: Mutable (members can be added/removed)

---

### Department

Represents an organizational unit containing multiple teams.

**Attributes**:
- `name` (string, required): Department name (unique identifier)
- `teams` (list[string], required): List of team names
- `description` (string, optional): Department description

**Relationships**:
- One-to-many with `Team` (department has many teams)

**Validation Rules**:
- `name` must be non-empty
- `teams` must contain valid team names
- `teams` list must not be empty

**State**: Mutable (teams can be added/removed)

---

### TimePeriod

Represents a date range for filtering and analyzing contributions.

**Attributes**:
- `start_date` (datetime, required): Start of time period (inclusive)
- `end_date` (datetime, required): End of time period (inclusive)
- `period_type` (enum: "daily" | "weekly" | "monthly" | "quarterly" | "yearly" | "custom", required): Period type
- `timezone` (string, optional): Timezone for date calculations (default: UTC)

**Relationships**:
- Used as filter criteria for `Contribution` queries

**Validation Rules**:
- `start_date` <= `end_date`
- `end_date` must not be in the future (for historical analysis)
- `period_type` must match date range (e.g., "daily" for 1-day range)

**State**: Immutable (time periods are fixed ranges)

---

### PullRequestSummary

Represents a concise summary of a pull request merged to main branch.

**Attributes**:
- `pr_id` (string, required): Pull request identifier (GitHub PR number)
- `repository` (string, required): Repository full name (reference to Repository)
- `title` (string, required): PR title
- `merge_date` (datetime, required): When PR was merged to main
- `author` (string, required): Developer username who created PR (reference to Developer)
- `summary` (string, required): Concise summary text (max 4 lines)
- `files_changed` (integer, optional): Number of files changed
- `additions` (integer, optional): Lines added
- `deletions` (integer, optional): Lines deleted
- `context_tags` (list[string], optional): Tags derived from repository context analysis (e.g., ["api", "frontend", "bugfix"])

**Relationships**:
- Many-to-one with `Repository` (PR summary belongs to one repository)
- Many-to-one with `Developer` (PR summary created by one developer)

**Validation Rules**:
- `summary` must be non-empty and contain no more than 4 lines when formatted
- `merge_date` must be valid datetime
- `repository` must reference valid repository
- `author` must reference valid developer
- `pr_id` must be unique within repository

**State**: Immutable (PR summaries are historical records)

---

## Aggregated Models

### DeveloperMetrics

Aggregated metrics for a developer over a time period.

**Attributes**:
- `developer` (string, required): Developer username
- `time_period` (TimePeriod, required): Time period for metrics
- `total_commits` (integer, required): Total commits
- `pull_requests_created` (integer, required): PRs created
- `pull_requests_reviewed` (integer, required): PRs reviewed
- `pull_requests_merged` (integer, required): PRs merged
- `issues_created` (integer, required): Issues created
- `issues_resolved` (integer, required): Issues resolved/resolved
- `code_review_participation` (integer, required): Number of reviews participated in
- `repositories_contributed` (list[string], required): List of repository names
- `per_repository_breakdown` (object, optional): Metrics broken down by repository

**Computed Fields**:
- `total_contributions`: Sum of all contribution types
- `average_contributions_per_day`: Total contributions / days in period

---

### RepositoryMetrics

Aggregated metrics for a repository over a time period.

**Attributes**:
- `repository` (string, required): Repository full name
- `time_period` (TimePeriod, required): Time period for metrics
- `total_contributions` (integer, required): Total contributions
- `active_contributors` (integer, required): Number of unique contributors
- `contributor_list` (list[string], required): List of contributor usernames
- `commits` (integer, required): Total commits
- `pull_requests` (integer, required): Total pull requests
- `issues` (integer, required): Total issues
- `reviews` (integer, required): Total reviews
- `trend` (enum: "increasing" | "decreasing" | "stable", optional): Activity trend compared to previous period
- `contribution_distribution` (object, optional): Distribution of contributions by developer

**Computed Fields**:
- `average_contributions_per_contributor`: Total contributions / active contributors
- `health_score`: Composite score based on activity, contributor diversity, trends

---

### TeamMetrics

Aggregated metrics for a team over a time period.

**Attributes**:
- `team` (string, required): Team name
- `time_period` (TimePeriod, required): Time period for metrics
- `total_activity` (integer, required): Total contributions from team members
- `member_count` (integer, required): Number of team members
- `average_per_person` (float, required): Average contributions per team member
- `top_contributors` (list[object], optional): Top contributors with their metrics
- `repositories_contributed` (list[string], required): List of repositories team contributed to

**Computed Fields**:
- `team_productivity_score`: Normalized score based on team size and activity

---

### DepartmentMetrics

Aggregated metrics for a department over a time period.

**Attributes**:
- `department` (string, required): Department name
- `time_period` (TimePeriod, required): Time period for metrics
- `total_activity` (integer, required): Total contributions from department teams
- `team_count` (integer, required): Number of teams in department
- `team_metrics` (list[TeamMetrics], required): Metrics for each team
- `average_per_team` (float, required): Average contributions per team

**Computed Fields**:
- `department_productivity_score`: Normalized score based on department size and activity

---

## Data Flow

### Collection Phase
1. Fetch raw data from GitHub API
2. Transform API responses to `Contribution` objects
3. Enrich with `Developer` and `Repository` information
4. Store in memory (DataFrame) or cache (JSON/SQLite)

### Analysis Phase
1. Filter contributions by time period, repository, team
2. Aggregate contributions into `DeveloperMetrics`, `RepositoryMetrics`, `TeamMetrics`, `DepartmentMetrics`
3. Detect anomalies and trends
4. Generate PR summaries

### Reporting Phase
1. Format aggregated metrics into report structures
2. Generate human-readable reports (Markdown/PDF)
3. Generate machine-readable reports (JSON/CSV)
4. Output to stdout or files

---

## Serialization Formats

### JSON Format
All models support JSON serialization using standard Python `json` module. Use camelCase for JSON keys to match common API conventions.

### CSV Format
Flat structures (DeveloperMetrics, RepositoryMetrics) can be serialized to CSV. Nested structures (TeamMetrics with per-repository breakdown) may require multiple CSV files or flattened representation.

### Markdown Format
Human-readable reports use Markdown tables and sections. Templates defined in `reports/templates/`.

---

## Validation & Error Handling

### Input Validation
- Validate all required fields are present
- Validate field types match expected types
- Validate relationships (references exist)
- Validate business rules (dates, enums, constraints)

### Error Handling
- Missing data: Use defaults (0 for counts, empty lists for collections)
- Invalid references: Log warning, exclude from aggregation
- API failures: Partial results, log errors, continue processing other repositories

---

## Caching Strategy

### Cache Keys
- Contributions: `contributions:{repository}:{start_date}:{end_date}`
- Developer metrics: `developer_metrics:{username}:{start_date}:{end_date}`
- Repository metrics: `repo_metrics:{repository}:{start_date}:{end_date}`
- PR summaries: `pr_summaries:{repository}:{period_type}:{period_value}`

### Cache Invalidation
- Time-based: Invalidate after TTL (default: 1 hour for recent data, 24 hours for historical)
- Event-based: Invalidate when new contributions detected
- Manual: User can force refresh with `--no-cache` flag

---

## Future Extensions

Potential additions (not in current scope):
- Contribution quality metrics (code review feedback, test coverage)
- Collaboration networks (developer interaction graphs)
- Technology stack analysis (languages, frameworks used)
- Code ownership metrics (file-level ownership)

