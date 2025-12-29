# GitHub API Usage Contract

**Feature**: GitHub Developer Contribution Analytics Tools  
**Date**: 2024-12-28  
**Phase**: 1 - Design

## Overview

This document defines how the tools interact with the GitHub API. It specifies which endpoints are used, how rate limiting is handled, and what data is collected.

## Authentication

### Token Requirements

- **Type**: Personal Access Token (PAT) or OAuth token
- **Scopes Required**:
  - `repo` (for private repositories)
  - `read:org` (for organization membership)
  - `read:user` (for user information)
- **Rate Limits**:
  - Authenticated: 5,000 requests/hour
  - Unauthenticated: 60 requests/hour (not supported)

### Token Storage

- Environment variable: `GITHUB_TOKEN`
- Configuration file: `github.token` field
- Command-line: `--token` option
- Priority: Command-line > Environment > Config file

## API Endpoints Used

### Repository Information

**Endpoint**: `GET /repos/{owner}/{repo}`

**Purpose**: Get repository metadata

**Response Fields Used**:
- `name`, `full_name`, `owner.login`
- `private`, `archived`
- `created_at`, `updated_at`
- `default_branch`

**Rate Limit Impact**: 1 request per repository

---

### Commits

**Endpoint**: `GET /repos/{owner}/{repo}/commits`

**Purpose**: Collect commit contributions

**Query Parameters**:
- `since`: ISO 8601 timestamp (start date)
- `until`: ISO 8601 timestamp (end date)
- `author`: Filter by author (optional)
- `per_page`: 100 (max)
- `page`: Pagination

**Response Fields Used**:
- `sha`, `commit.author.name`, `commit.author.email`, `commit.author.date`
- `commit.message`
- `author.login` (GitHub user)
- `stats.additions`, `stats.deletions`
- `files[].filename`

**Rate Limit Impact**: ~1 request per 100 commits (with pagination)

**Pagination**: Required for repositories with >100 commits

---

### Pull Requests

**Endpoint**: `GET /repos/{owner}/{repo}/pulls`

**Purpose**: Collect pull request contributions

**Query Parameters**:
- `state`: `all` (to get merged PRs)
- `base`: Branch name (e.g., `main`)
- `sort`: `updated`
- `direction`: `desc`
- `since`: ISO 8601 timestamp
- `per_page`: 100
- `page`: Pagination

**Response Fields Used**:
- `number`, `title`, `body`
- `user.login` (creator)
- `state`, `merged_at`, `merge_commit_sha`
- `base.ref`, `head.ref`
- `created_at`, `updated_at`, `closed_at`
- `additions`, `deletions`, `changed_files`

**Additional Endpoint**: `GET /repos/{owner}/{repo}/pulls/{pull_number}`

**Purpose**: Get detailed PR information (if not in list response)

**Rate Limit Impact**: ~1-2 requests per PR (list + detail if needed)

---

### Pull Request Reviews

**Endpoint**: `GET /repos/{owner}/{repo}/pulls/{pull_number}/reviews`

**Purpose**: Collect code review contributions

**Response Fields Used**:
- `id`, `user.login` (reviewer)
- `state`: `APPROVED`, `CHANGES_REQUESTED`, `COMMENTED`
- `submitted_at`
- `body` (review comment)

**Rate Limit Impact**: 1 request per PR

---

### Issues

**Endpoint**: `GET /repos/{owner}/{repo}/issues`

**Purpose**: Collect issue contributions

**Query Parameters**:
- `state`: `all`
- `since`: ISO 8601 timestamp
- `per_page`: 100
- `page`: Pagination

**Response Fields Used**:
- `number`, `title`, `body`
- `user.login` (creator)
- `state`, `closed_at`
- `labels[].name`
- `assignees[].login`

**Note**: PRs are also returned by this endpoint (PRs are issues). Filter by `pull_request` field.

**Rate Limit Impact**: ~1 request per 100 issues

---

### Comments

**Endpoint**: `GET /repos/{owner}/{repo}/issues/{issue_number}/comments`

**Purpose**: Collect issue/PR comments (optional, lower priority)

**Response Fields Used**:
- `id`, `user.login`
- `body`, `created_at`

**Rate Limit Impact**: 1 request per issue/PR

---

### Organization Members

**Endpoint**: `GET /orgs/{org}/members`

**Purpose**: Identify internal vs external contributors

**Query Parameters**:
- `per_page`: 100
- `page`: Pagination

**Response Fields Used**:
- `login` (username)

**Rate Limit Impact**: ~1 request per 100 members

---

### User Information

**Endpoint**: `GET /users/{username}`

**Purpose**: Get developer display name and profile info

**Response Fields Used**:
- `login`, `name`, `email`
- `type`: `User` vs `Bot`

**Rate Limit Impact**: 1 request per unique developer

**Caching**: Cache user info (changes infrequently)

---

### Repository Contents (for PR Context)

**Endpoint**: `GET /repos/{owner}/{repo}/contents/{path}`

**Purpose**: Analyze repository structure for PR summarization context

**Response Fields Used**:
- `name`, `type`, `path`
- `content` (base64 encoded, for files)
- `sha` (for trees)

**Rate Limit Impact**: Variable (depends on repository size)

**Note**: For large repositories, consider cloning instead of API calls.

---

## Rate Limiting Strategy

### Detection

Monitor `X-RateLimit-Remaining` header in responses:
- If < 100: Slow down requests
- If < 10: Pause and wait
- If = 0: Implement backoff

### Backoff Strategy

When rate limit hit:
1. Calculate wait time: `wait_time = (rate_limit_reset - now) + buffer`
2. Log warning: "Rate limit exceeded, waiting until {reset_time}"
3. Sleep until reset time
4. Retry request

### Request Throttling

- Default: 1 request per 100ms (10 req/sec)
- When approaching limit: 1 request per 500ms (2 req/sec)
- When limit hit: Exponential backoff

### Caching

Cache API responses to minimize requests:
- Repository metadata: 24 hours
- Commit/PR/Issue data: 1 hour (for recent data)
- User information: 24 hours
- Organization members: 1 hour

---

## Error Handling

### HTTP Status Codes

- `200 OK`: Success, process response
- `401 Unauthorized`: Invalid token, abort with error
- `403 Forbidden`: Rate limit exceeded or insufficient permissions
- `404 Not Found`: Repository doesn't exist or no access
- `422 Unprocessable Entity`: Invalid query parameters
- `500/502/503`: Server error, retry with backoff

### Retry Strategy

- **Retryable Errors**: 500, 502, 503, 429 (rate limit)
- **Non-Retryable**: 401, 403, 404, 422
- **Max Retries**: 3
- **Backoff**: Exponential (1s, 2s, 4s)

### Error Logging

Log all API errors with context:
- Endpoint called
- Status code
- Error message
- Repository/entity affected
- Timestamp

---

## Data Collection Order

For efficiency, collect data in this order:

1. **Repository List**: Get all repositories in organization
2. **Repository Metadata**: Get metadata for each repository (parallel, throttled)
3. **Contributions**: For each repository (sequential or batched):
   - Commits (paginated)
   - Pull Requests (paginated)
   - Issues (paginated)
   - Reviews (per PR)
4. **User Information**: Collect user info for unique developers (cached)
5. **Organization Members**: Get member list (cached)

## GitHub Enterprise Support

For GitHub Enterprise Server:
- Use `--base-url` option: `https://github.example.com/api/v3`
- Same endpoints, different base URL
- May have different rate limits (check instance settings)
- Authentication same (PAT or OAuth)

## GraphQL Alternative (Future Consideration)

GitHub GraphQL API could reduce requests:
- Single query for multiple data types
- More efficient for complex queries
- However, REST API is simpler and sufficient for current needs

**Decision**: Use REST API for Phase 1, consider GraphQL in future if performance becomes issue.

