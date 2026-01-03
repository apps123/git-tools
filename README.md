# GitHub Developer Contribution Analytics Tools

A comprehensive collection of Python command-line tools for analyzing developer contributions across GitHub organization repositories. These tools help engineering managers, team leads, and project managers understand team productivity, identify trends, and make data-driven decisions about resource allocation and team composition.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Commands](#cli-commands)
- [Configuration](#configuration)
- [Code Organization](#code-organization)
- [Data Models & Schema](#data-models--schema)
- [Caching & Storage](#caching--storage)
- [Architecture](#architecture)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Overview

This toolset provides comprehensive analytics for GitHub organizations, enabling stakeholders to:

- **Track Individual Contributions**: Understand how developers contribute across repositories with detailed metrics (commits, PRs, reviews, issues)
- **Analyze Repository Health**: Identify active repositories, detect maintenance gaps, and assess project health
- **Monitor Team Performance**: Aggregate contributions at team and department levels for organizational insights
- **Summarize Pull Requests**: Generate concise, contextual summaries of merged PRs using LLM technology
- **Detect Anomalies**: Identify significant changes in contribution patterns (drops/spikes >50%) for proactive management

### Use Cases

1. **Performance Reviews**: Generate developer activity reports for performance evaluations
2. **Resource Allocation**: Identify which repositories need more attention or are becoming deprecated
3. **Team Planning**: Understand team composition and contribution distribution
4. **Project Health Monitoring**: Track repository trends and detect declining activity
5. **Stakeholder Reporting**: Create periodic summaries of development activity for leadership
6. **Anomaly Detection**: Proactively identify significant changes in contribution patterns

## Features

### Core Capabilities

- ✅ **Developer Activity Reports**: Comprehensive metrics per developer (commits, PRs, reviews, issues)
- ✅ **Repository Analysis**: Contribution patterns, trends, and health indicators per repository
- ✅ **Team & Department Metrics**: Aggregated metrics at organizational levels
- ✅ **PR Summarization**: LLM-powered summaries of merged pull requests
- ✅ **Anomaly Detection**: Automatic detection of significant contribution pattern changes
- ✅ **Multiple Output Formats**: JSON, Markdown, and CSV for all reports
- ✅ **Flexible Filtering**: Filter by repository, developer, team, department, and time period
- ✅ **Rate Limiting**: Automatic handling of GitHub API rate limits with exponential backoff
- ✅ **Caching**: File-based caching to minimize API calls and improve performance
- ✅ **Internal/External Classification**: Distinguishes organization members from outside collaborators

### Quality Metrics

- **Attribution Accuracy**: ≥95% accuracy in correctly attributing contributions to developers
- **Anomaly Detection Recall**: ≥80% recall in detecting significant contribution pattern changes

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git (for cloning the repository)
- GitHub Personal Access Token (PAT) with appropriate scopes
- (Optional) OpenAI API key for PR summarization features

### System Dependencies

The following system-level dependencies may be required depending on your platform:

**Linux/Unix:**
- `git` - For GitPython operations (usually pre-installed)
- `build-essential` or equivalent - For compiling Python packages (if needed)

**macOS:**
- Xcode Command Line Tools - For compiling Python packages
  ```bash
  xcode-select --install
  ```

**Windows:**
- Git for Windows - For GitPython operations
- Visual C++ Build Tools - For compiling Python packages (if needed)

### Python Dependencies

The project requires the following Python packages (automatically installed with `pip install -r requirements.txt`):

#### Core Dependencies

- **PyGithub** (>=2.0.0) - GitHub API client library
- **click** (>=8.0.0) - Command-line interface framework
- **pandas** (>=2.0.0) - Data manipulation and analysis
- **pydantic** (>=2.0.0) - Data validation and settings management
- **pydantic-settings** (>=2.0.0) - Settings management for Pydantic
- **openai** (>=1.0.0) - OpenAI API client for PR summarization
- **GitPython** (>=3.1.0) - Git repository analysis
- **jinja2** (>=3.0.0) - Template engine for report generation

#### Optional Dependencies

- **pyyaml** - YAML configuration file support
- **toml** - TOML configuration file support

#### Development Dependencies

- **pytest** (>=7.0.0) - Testing framework
- **pytest-mock** (>=3.0.0) - Mocking utilities for tests
- **pytest-cov** (>=4.0.0) - Code coverage plugin
- **ruff** (>=0.1.0) - Fast Python linter
- **black** (>=23.0.0) - Code formatter
- **mypy** (>=1.0.0) - Static type checker

### Install from Source

```bash
# Clone the repository
git clone <repository-url>
cd git-tools

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install the package in development mode
pip install -e .

# Verify installation
github-tools --version
```

### Install with Development Dependencies

For development work, install additional development dependencies:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Or install everything at once
pip install -e ".[dev]"
```

### Dependency Versions

The project is tested with the following Python and package versions:

- **Python**: 3.11, 3.12
- **PyGithub**: 2.0.0+
- **click**: 8.0.0+
- **pandas**: 2.0.0+
- **pydantic**: 2.0.0+
- **openai**: 1.0.0+
- **GitPython**: 3.1.0+
- **jinja2**: 3.0.0+

For the complete list of dependencies with version constraints, see `requirements.txt` and `pyproject.toml`.

### Complete Dependency List

#### Runtime Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| PyGithub | >=2.0.0 | GitHub API client library |
| click | >=8.0.0 | Command-line interface framework |
| pandas | >=2.0.0 | Data manipulation and analysis |
| pydantic | >=2.0.0 | Data validation and settings management |
| pydantic-settings | >=2.0.0 | Settings management for Pydantic |
| openai | >=1.0.0 | OpenAI API client for PR summarization |
| GitPython | >=3.1.0 | Git repository analysis |
| jinja2 | >=3.0.0 | Template engine for report generation |

#### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | >=7.0.0 | Testing framework |
| pytest-mock | >=3.0.0 | Mocking utilities for tests |
| pytest-cov | >=4.0.0 | Code coverage plugin |
| ruff | >=0.1.0 | Fast Python linter |
| black | >=23.0.0 | Code formatter |
| mypy | >=1.0.0 | Static type checker |

#### Build Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| setuptools | >=61.0 | Package building and distribution |
| wheel | - | Built package format |

### Dependency Installation Methods

**Method 1: Using requirements.txt (Recommended)**
```bash
pip install -r requirements.txt
```

**Method 2: Using pyproject.toml**
```bash
pip install -e .
```

**Method 3: Install with development dependencies**
```bash
pip install -e ".[dev]"
```

**Method 4: Manual installation**
```bash
pip install PyGithub click pandas pydantic pydantic-settings openai GitPython jinja2
```

### GitHub Token Setup

Create a GitHub Personal Access Token with the following scopes:
- `repo` - Full control of private repositories
- `read:org` - Read organization membership
- `read:user` - Read user profile information

Set the token as an environment variable:

```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

Or add it to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.zshrc
source ~/.zshrc
```

### OpenAI API Key (Optional)

For PR summarization features, set your OpenAI API key:

```bash
export OPENAI_API_KEY="sk-your_key_here"
```

## Quick Start

### Step 1: Configure Your Environment

**Option A: Environment Variables (Quick Setup)**
```bash
# Set your GitHub token (required)
export GITHUB_TOKEN="ghp_your_token_here"

# Optional: Set organization for organization-wide reports
export GITHUB_TOOLS_GITHUB_ORGANIZATION="myorg"
```

**Option B: Configuration File (Recommended for Teams)**

Create a configuration file in JSON, TOML, or YAML format:

**`config.json` (JSON):**
```json
{
  "github": {
    "token": "${GITHUB_TOKEN}",
    "organization": "myorg",
    "base_url": "https://api.github.com"
  },
  "cache": {
    "directory": "~/.github-tools/cache",
    "ttl_hours": 24,
    "use_sqlite": false
  }
}
```

**`config.toml` (TOML):**
```toml
[github]
token = "${GITHUB_TOKEN}"  # Can use env var or actual token
organization = "myorg"
base_url = "https://api.github.com"

[cache]
directory = "~/.github-tools/cache"
ttl_hours = 24
use_sqlite = false
```

**`config.yaml` (YAML):**
```yaml
github:
  token: ${GITHUB_TOKEN}  # Can use env var or actual token
  organization: myorg
  base_url: https://api.github.com

cache:
  directory: ~/.github-tools/cache
  ttl_hours: 24
  use_sqlite: false
```

**Note**: For security, prefer using environment variables for tokens. The `${GITHUB_TOKEN}` syntax in config files is a placeholder - you should set the actual token via environment variable.

**Using the config file:**
```bash
# Use config file with any command
github-tools --config config.json developer-report --start-date 30d --end-date today
```

### Step 2: Generate Reports

#### Basic Developer Report

```bash
# Generate a developer activity report for the last 30 days
# Using environment variables
github-tools developer-report \
  --start-date 30d \
  --end-date today \
  --format markdown

# Or using a config file
github-tools --config config.json developer-report \
  --start-date 30d \
  --end-date today \
  --format markdown
```

#### Repository Analysis

```bash
# Analyze repository contributions for a specific period
github-tools repository-report \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --format json \
  --output repo-analysis.json
```

#### Team Report

**First, create a team configuration file:**

`teams.json`:
```json
{
  "teams": [
    {
      "name": "backend-team",
      "display_name": "Backend Team",
      "department": "engineering",
      "members": ["alice", "bob", "charlie"]
    },
    {
      "name": "frontend-team",
      "display_name": "Frontend Team",
      "department": "engineering",
      "members": ["diana", "eve"]
    }
  ]
}
```

**Then generate the team report:**
```bash
github-tools team-report \
  --start-date 1m \
  --end-date today \
  --team-config teams.json \
  --format markdown
```

### Complete Example with Configuration File

```bash
# 1. Create config.json (see Step 1, Option B above)
# 2. Set GITHUB_TOKEN environment variable
export GITHUB_TOKEN="ghp_your_token_here"

# 3. Run any command with config file
github-tools --config config.json developer-report \
  --start-date 30d \
  --end-date today \
  --format markdown \
  --output report.md
```

## CLI Commands

### `developer-report`

Generate developer activity reports showing individual contributions across repositories.

**Usage:**
```bash
github-tools developer-report [OPTIONS]
```

**Options:**
- `--start-date <date>` (required): Start date (ISO format: YYYY-MM-DD or relative: '30d', '1w', '1m', 'today', 'yesterday')
- `--end-date <date>` (required): End date (ISO format: YYYY-MM-DD or relative: 'today', 'yesterday')
- `--repository, -r <repo>`: Filter by repository (can specify multiple times)
- `--developer, -d <username>`: Filter by developer (can specify multiple times)
- `--team, -t <team>`: Filter by team (can specify multiple times)
- `--include-external`: Include external contributors (default: false)
- `--format, -f <format>`: Output format (json, markdown, csv) (default: markdown)
- `--output, -o <path>`: Output file path (default: stdout)
- `--no-cache`: Disable caching, force fresh data collection
- `--verbose, -v`: Enable verbose logging
- `--quiet, -q`: Suppress non-error output

**Examples:**
```bash
# Last 30 days, all developers
github-tools developer-report --start-date 30d --end-date today

# Specific repository, JSON output
github-tools developer-report \
  --start-date 2024-12-01 \
  --end-date 2024-12-31 \
  --repository myorg/my-repo \
  --format json \
  --output dev-report.json

# Specific developer, include external contributors
github-tools developer-report \
  --start-date 1w \
  --end-date today \
  --developer alice \
  --include-external
```

**Output Format:**
- **Markdown**: Human-readable report with tables and summaries
- **JSON**: Machine-readable structured data
- **CSV**: Spreadsheet-compatible format

### `repository-report`

Analyze repository contribution patterns, trends, and health indicators.

**Usage:**
```bash
github-tools repository-report [OPTIONS]
```

**Options:**
- `--start-date <date>` (required): Start date
- `--end-date <date>` (required): End date
- `--repository, -r <repo>`: Filter by repository (can specify multiple times)
- `--include-external`: Include external contributors
- `--format, -f <format>`: Output format (default: markdown)
- `--output, -o <path>`: Output file path
- `--no-cache`: Disable caching

**Examples:**
```bash
# Analyze all repositories for Q4 2024
github-tools repository-report \
  --start-date 2024-10-01 \
  --end-date 2024-12-31 \
  --format markdown

# Specific repository with trend analysis
github-tools repository-report \
  --start-date 1m \
  --end-date today \
  --repository myorg/backend-service
```

### `team-report`

Generate team and department-level contribution metrics.

**Usage:**
```bash
github-tools team-report [OPTIONS]
```

**Options:**
- `--start-date <date>` (required): Start date
- `--end-date <date>` (required): End date
- `--team-config <path>`: Path to team configuration file (JSON or YAML)
- `--team, -t <team>`: Filter by team name (can specify multiple times)
- `--department, -d <dept>`: Filter by department (can specify multiple times)
- `--include-external`: Include external contributors
- `--format, -f <format>`: Output format (default: markdown)
- `--output, -o <path>`: Output file path
- `--no-cache`: Disable caching

**Team Configuration File Format:**

`teams.json`:
```json
{
  "teams": [
    {
      "name": "backend-team",
      "display_name": "Backend Team",
      "department": "engineering",
      "members": ["alice", "bob", "charlie"]
    },
    {
      "name": "frontend-team",
      "display_name": "Frontend Team",
      "department": "engineering",
      "members": ["diana", "eve"]
    },
    {
      "name": "data-team",
      "display_name": "Data Team",
      "department": "data-science",
      "members": ["frank", "grace"]
    }
  ]
}
```

**Examples:**
```bash
# Team report with configuration file
github-tools team-report \
  --start-date 1m \
  --end-date today \
  --team-config teams.json \
  --format markdown

# Filter by department
github-tools team-report \
  --start-date 2024-12-01 \
  --end-date 2024-12-31 \
  --team-config teams.json \
  --department engineering
```

### `pr-summary-report`

Generate concise summaries of pull requests merged to main branches.

**Usage:**
```bash
github-tools pr-summary-report [OPTIONS]
```

**Options:**
- `--start-date <date>` (required): Start date
- `--end-date <date>` (required): End date
- `--repository, -r <repo>`: Filter by repository (can specify multiple times)
- `--base-branch <branch>`: Base branch to filter PRs (default: main)
- `--llm-provider <provider>`: LLM provider for summarization (openai, claude-local, cursor, auto). Default: auto (detects available)
- `--openai-api-key <key>`: OpenAI API key (or set OPENAI_API_KEY env var, required for OpenAI provider)
- `--format, -f <format>`: Output format (default: markdown)
- `--output, -o <path>`: Output file path
- `--no-cache`: Disable caching

**Note**: PR summarization supports multiple LLM providers:
- **OpenAI API** (default, requires API key): Cloud-based summarization
- **Claude Desktop** (`--llm-provider claude-local`): Local Claude agent for enterprise use
- **Cursor Agent** (`--llm-provider cursor`): Local Cursor agent support
- **Google Gemini** (`--llm-provider gemini`): Google's Gemini API (requires GOOGLE_API_KEY)
- **Auto-detect** (`--llm-provider auto` or omit): Automatically detects and uses available providers

**Examples:**
```bash
# Weekly PR summary (auto-detects local agents if available)
github-tools pr-summary-report \
  --start-date 1w \
  --end-date today \
  --format markdown

# Using Claude Desktop (local, enterprise-friendly)
github-tools pr-summary-report \
  --start-date 1w \
  --end-date today \
  --llm-provider claude-local \
  --format markdown

# Using Cursor Agent (local)
github-tools pr-summary-report \
  --start-date 1w \
  --end-date today \
  --llm-provider cursor \
  --format markdown

# Using Google Gemini API
github-tools pr-summary-report \
  --start-date 1w \
  --end-date today \
  --llm-provider gemini \
  --gemini-api-key ${GOOGLE_API_KEY} \
  --format markdown

# Explicitly use OpenAI API
github-tools pr-summary-report \
  --start-date 1w \
  --end-date today \
  --llm-provider openai \
  --openai-api-key sk-... \
  --format markdown

# Specific repository, custom base branch
github-tools pr-summary-report \
  --start-date 2024-12-01 \
  --end-date 2024-12-31 \
  --repository myorg/api-service \
  --base-branch develop
```

### `anomaly-report`

Detect significant changes in contribution patterns (drops/spikes >50%).

**Usage:**
```bash
github-tools anomaly-report [OPTIONS]
```

**Options:**
- `--current-start-date <date>` (required): Current period start date
- `--current-end-date <date>` (required): Current period end date
- `--previous-start-date <date>`: Previous period start date (default: same duration before current start)
- `--previous-end-date <date>`: Previous period end date (default: same as current start date)
- `--repository, -r <repo>`: Filter by repository (can specify multiple times)
- `--entity-type <type>`: Entity type to analyze (developer, repository, team) (default: developer)
- `--threshold <float>`: Anomaly detection threshold percentage (default: 50.0)
- `--format, -f <format>`: Output format (default: markdown)
- `--output, -o <path>`: Output file path
- `--no-cache`: Disable caching

**Examples:**
```bash
# Compare last week vs previous week
github-tools anomaly-report \
  --current-start-date 7d \
  --current-end-date today \
  --threshold 50.0

# Compare months, repository-level analysis
github-tools anomaly-report \
  --current-start-date 2024-12-01 \
  --current-end-date 2024-12-31 \
  --previous-start-date 2024-11-01 \
  --previous-end-date 2024-11-30 \
  --entity-type repository \
  --threshold 60.0
```

### Common Options

All commands support these common options:

- `--config <path>`: Path to configuration file
- `--token <token>`: GitHub token (overrides GITHUB_TOKEN env var)
- `--base-url <url>`: GitHub API base URL (default: https://api.github.com)
- `--verbose, -v`: Enable verbose logging
- `--quiet, -q`: Suppress non-error output
- `--version`: Show version information
- `--help`: Show command help

## Configuration

The tools support multiple ways to configure settings: environment variables, `.env` files, and command-line options. Configuration follows a priority order: command-line options > environment variables > `.env` file > defaults.

### Minimum Required Configuration

At minimum, you need a **GitHub Personal Access Token** to run any of the tools:

```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

For PR summarization features, you also need an OpenAI API key:

```bash
export OPENAI_API_KEY="sk-your_key_here"
```

### Configuration Methods

#### Method 1: Environment Variables (Recommended)

Set environment variables in your shell profile or session:

**Required:**
```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

**Optional:**
```bash
# Organization name (can also be specified per command)
export GITHUB_TOOLS_GITHUB_ORGANIZATION="myorg"

# For GitHub Enterprise
export GITHUB_TOOLS_GITHUB_BASE_URL="https://github.company.com/api/v3"

# Cache settings
export GITHUB_TOOLS_CACHE_DIR="$HOME/.github-tools/cache"
export GITHUB_TOOLS_CACHE_TTL_HOURS=24
export GITHUB_TOOLS_USE_SQLITE=false

# OpenAI API key (only for PR summarization)
export OPENAI_API_KEY="sk-your_key_here"
```

**Add to shell profile** (`~/.bashrc`, `~/.zshrc`, etc.) for persistence:
```bash
# GitHub Tools Configuration
export GITHUB_TOKEN="ghp_your_token_here"
export GITHUB_TOOLS_GITHUB_ORGANIZATION="myorg"
export OPENAI_API_KEY="sk-your_key_here"  # Optional
```

#### Method 2: `.env` File

Create a `.env` file in your project root or home directory:

`.env`:
```bash
# Required
GITHUB_TOKEN=ghp_your_token_here

# Optional - GitHub configuration
GITHUB_TOOLS_GITHUB_ORGANIZATION=myorg
GITHUB_TOOLS_GITHUB_BASE_URL=https://api.github.com

# Optional - Cache configuration
GITHUB_TOOLS_CACHE_DIR=~/.github-tools/cache
GITHUB_TOOLS_CACHE_TTL_HOURS=24
GITHUB_TOOLS_CACHE_TTL_HOURS_HISTORICAL=24
GITHUB_TOOLS_USE_SQLITE=false

# Optional - OpenAI API key (for PR summarization)
OPENAI_API_KEY=sk-your_key_here
```

The tools automatically load `.env` files from the current directory or your home directory.

#### Method 3: Configuration Files (JSON/TOML/YAML)

Create a configuration file in JSON, TOML, or YAML format. Supports both nested and flat structures.

**JSON Configuration (`config.json`):**

Nested structure:
```json
{
  "github": {
    "token": "${GITHUB_TOKEN}",
    "organization": "myorg",
    "base_url": "https://api.github.com"
  },
  "cache": {
    "directory": "~/.github-tools/cache",
    "ttl_hours": 24,
    "ttl_hours_historical": 24,
    "use_sqlite": false
  }
}
```

Flat structure (also supported):
```json
{
  "github_token": "${GITHUB_TOKEN}",
  "github_organization": "myorg",
  "github_base_url": "https://api.github.com",
  "cache_dir": "~/.github-tools/cache",
  "cache_ttl_hours": 24,
  "use_sqlite": false
}
```

**TOML Configuration (`config.toml`):**

```toml
[github]
token = "${GITHUB_TOKEN}"  # Or use actual token (not recommended)
organization = "myorg"
base_url = "https://api.github.com"

[cache]
directory = "~/.github-tools/cache"
ttl_hours = 24
ttl_hours_historical = 24
use_sqlite = false
```

**YAML Configuration (`config.yaml`):**

```yaml
github:
  token: ${GITHUB_TOKEN}  # Or use actual token (not recommended)
  organization: myorg
  base_url: https://api.github.com

cache:
  directory: ~/.github-tools/cache
  ttl_hours: 24
  ttl_hours_historical: 24
  use_sqlite: false
```

**Using configuration files:**
```bash
# Use config file with any command
github-tools --config config.json developer-report --start-date 30d --end-date today

# Config file settings can be overridden by environment variables
GITHUB_TOKEN="different_token" github-tools --config config.json developer-report ...
```

**Note**: 
- JSON support is built-in (no additional dependencies)
- TOML support uses Python's built-in `tomllib` (Python 3.11+) - no additional dependencies needed
- YAML support requires `pyyaml`: `pip install pyyaml` (optional dependency)

#### Method 4: Command-Line Options

Most settings can be overridden via command-line options:

```bash
# Override token
github-tools --token ghp_another_token developer-report --start-date 30d --end-date today

# Override base URL for GitHub Enterprise
github-tools --base-url https://github.company.com/api/v3 developer-report --start-date 30d --end-date today
```

**Configuration Priority** (highest to lowest):
1. Command-line options (`--token`, `--base-url`, etc.)
2. Environment variables (`GITHUB_TOKEN`, `GITHUB_TOOLS_*`)
3. Configuration file (`--config`)
4. Default values

### Configuration Examples by Use Case

#### Example 1: Basic Setup (GitHub.com)

**Minimum configuration:**
```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

**Run commands:**
```bash
# Must specify repository if organization not configured
github-tools developer-report \
  --start-date 30d \
  --end-date today \
  --repository myorg/my-repo

# Or specify organization via environment variable
export GITHUB_TOOLS_GITHUB_ORGANIZATION="myorg"
github-tools developer-report --start-date 30d --end-date today
```

#### Example 2: Complete Setup with Organization

**Configuration:**
```bash
export GITHUB_TOKEN="ghp_your_token_here"
export GITHUB_TOOLS_GITHUB_ORGANIZATION="myorg"
export GITHUB_TOOLS_CACHE_DIR="$HOME/.github-tools/cache"
export GITHUB_TOOLS_CACHE_TTL_HOURS=24
```

**Run commands:**
```bash
# Works across all organization repositories
github-tools developer-report --start-date 30d --end-date today
github-tools repository-report --start-date 1m --end-date today
```

#### Example 3: GitHub Enterprise Setup

**Configuration:**
```bash
export GITHUB_TOKEN="ghp_your_enterprise_token"
export GITHUB_TOOLS_GITHUB_ORGANIZATION="company-org"
export GITHUB_TOOLS_GITHUB_BASE_URL="https://github.company.com/api/v3"
```

**Run commands:**
```bash
github-tools developer-report --start-date 30d --end-date today
```

#### Example 4: With PR Summarization

**Configuration:**
```bash
export GITHUB_TOKEN="ghp_your_token_here"
export GITHUB_TOOLS_GITHUB_ORGANIZATION="myorg"
export OPENAI_API_KEY="sk-your_openai_key_here"
```

**Run commands:**
```bash
# PR summaries will use OpenAI API
github-tools pr-summary-report \
  --start-date 1w \
  --end-date today \
  --format markdown
```

#### Example 5: Team Reports Setup

Team reports require an additional team configuration file. Create `teams.json`:

`teams.json`:
```json
{
  "teams": [
    {
      "name": "backend-team",
      "display_name": "Backend Team",
      "department": "engineering",
      "members": ["alice", "bob", "charlie"]
    },
    {
      "name": "frontend-team",
      "display_name": "Frontend Team",
      "department": "engineering",
      "members": ["diana", "eve"]
    },
    {
      "name": "data-team",
      "display_name": "Data Team",
      "department": "data-science",
      "members": ["frank", "grace"]
    }
  ]
}
```

**Run team report:**
```bash
export GITHUB_TOKEN="ghp_your_token_here"
export GITHUB_TOOLS_GITHUB_ORGANIZATION="myorg"

github-tools team-report \
  --start-date 1m \
  --end-date today \
  --team-config teams.json \
  --format markdown
```

### Configuration Reference

#### Required Settings

| Setting | Environment Variable | Description |
|---------|---------------------|-------------|
| GitHub Token | `GITHUB_TOKEN` | GitHub Personal Access Token with `repo`, `read:org`, `read:user` scopes |

#### Optional Settings

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| Organization | `GITHUB_TOOLS_GITHUB_ORGANIZATION` | None | Default GitHub organization name |
| Base URL | `GITHUB_TOOLS_GITHUB_BASE_URL` | `https://api.github.com` | GitHub API base URL (for Enterprise) |
| Cache Directory | `GITHUB_TOOLS_CACHE_DIR` | `~/.github-tools/cache` | Directory for cached data |
| Cache TTL (Recent) | `GITHUB_TOOLS_CACHE_TTL_HOURS` | `1` | Cache TTL in hours for recent data |
| Cache TTL (Historical) | `GITHUB_TOOLS_CACHE_TTL_HOURS_HISTORICAL` | `24` | Cache TTL in hours for historical data |
| Use SQLite | `GITHUB_TOOLS_USE_SQLITE` | `false` | Use SQLite for caching (for large datasets) |
| OpenAI API Key | `OPENAI_API_KEY` | None | OpenAI API key for PR summarization |

#### Special Purpose Settings

| Setting | Environment Variable | Description |
|---------|---------------------|-------------|
| OpenAI API Key | `OPENAI_API_KEY` | Required only for `pr-summary-report` command |

### GitHub Token Scopes

Your GitHub Personal Access Token must have the following scopes:

- **`repo`**: Full control of private repositories (required for accessing private repos)
- **`read:org`**: Read organization membership (required for organization-level reports)
- **`read:user`**: Read user profile information (required for user attribution)

**Creating a GitHub Token:**
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `read:org`, `read:user`
4. Generate and copy the token
5. Set it as `GITHUB_TOKEN` environment variable

### Verifying Configuration

Test your configuration:

```bash
# Verify GitHub token is set
echo $GITHUB_TOKEN

# Test with a simple command
github-tools developer-report \
  --start-date 7d \
  --end-date today \
  --repository myorg/my-repo \
  --format json
```

If configuration is incorrect, you'll see an error message indicating what's missing.

## Code Organization

```
git-tools/
├── src/
│   └── github_tools/
│       ├── __init__.py
│       ├── api/                    # GitHub API integration
│       │   ├── __init__.py
│       │   ├── client.py           # GitHub API client wrapper
│       │   └── rate_limiter.py     # Rate limiting and retry logic
│       ├── models/                 # Data models
│       │   ├── __init__.py
│       │   ├── developer.py        # Developer model
│       │   ├── repository.py       # Repository model
│       │   ├── contribution.py     # Contribution model
│       │   ├── team.py             # Team model
│       │   └── time_period.py     # TimePeriod model
│       ├── collectors/             # Data collection
│       │   ├── __init__.py
│       │   ├── contribution_collector.py  # Collect contributions from GitHub
│       │   └── pr_summary_collector.py     # Collect and summarize PRs
│       ├── analyzers/              # Data analysis
│       │   ├── __init__.py
│       │   ├── developer_analyzer.py       # Developer metrics
│       │   ├── repository_analyzer.py      # Repository metrics
│       │   ├── team_analyzer.py            # Team/department metrics
│       │   └── anomaly_detector.py         # Anomaly detection
│       ├── summarizers/            # PR summarization
│       │   ├── __init__.py
│       │   ├── llm_summarizer.py          # LLM-based summarization
│       │   └── context_analyzer.py         # Repository context analysis
│       ├── reports/                # Report generation
│       │   ├── __init__.py
│       │   ├── generator.py               # Report generator
│       │   ├── formatters/                # Output formatters
│       │   │   ├── __init__.py
│       │   │   ├── json.py                # JSON formatter
│       │   │   ├── markdown.py            # Markdown formatter
│       │   │   └── csv.py                # CSV formatter
│       │   └── templates/                 # Report templates
│       │       └── developer_report.md.j2
│       ├── cli/                    # CLI commands
│       │   ├── __init__.py
│       │   ├── developer_report.py
│       │   ├── repository_report.py
│       │   ├── team_report.py
│       │   ├── pr_summary_report.py
│       │   └── anomaly_report.py
│       └── utils/                  # Utilities
│           ├── __init__.py
│           ├── config.py           # Configuration management
│           ├── cache.py             # Caching utilities
│           ├── filters.py          # Filtering helpers
│           └── logging.py           # Logging configuration
├── tests/
│   ├── __init__.py
│   ├── unit/                       # Unit tests
│   ├── integration/                # Integration tests
│   │   └── fixtures/               # Test fixtures
│   └── contract/                   # Contract tests
├── specs/                          # Specifications
│   └── 001-github-contribution-tools/
│       ├── spec.md
│       ├── plan.md
│       ├── tasks.md
│       └── contracts/
├── pyproject.toml                  # Project configuration
├── requirements.txt                # Dependencies
└── README.md                       # This file
```

### Key Components

1. **API Layer** (`api/`): Handles GitHub API interactions with rate limiting and error handling
2. **Models** (`models/`): Core data structures representing developers, repositories, contributions, etc.
3. **Collectors** (`collectors/`): Fetch and transform data from GitHub API
4. **Analyzers** (`analyzers/`): Compute metrics and detect patterns
5. **Summarizers** (`summarizers/`): Generate PR summaries using LLM
6. **Reports** (`reports/`): Format and generate reports in multiple formats
7. **CLI** (`cli/`): Command-line interface for all tools
8. **Utils** (`utils/`): Shared utilities for configuration, caching, filtering, etc.

## Data Models & Schema

### Core Models

#### Developer
```python
{
    "username": str,              # GitHub username
    "display_name": str,          # Display name
    "email": str,                 # Email address
    "organization_member": bool,  # Is organization member
    "is_internal": bool,          # Internal vs external contributor
    "team_affiliations": List[str] # Team memberships
}
```

#### Repository
```python
{
    "name": str,                  # Repository name
    "full_name": str,             # owner/repo
    "owner": str,                 # Organization/owner
    "visibility": str,            # public, private, internal
    "created_at": datetime,       # Creation date
    "updated_at": datetime,       # Last update
    "default_branch": str,        # Default branch
    "archived": bool,             # Is archived
    "description": str            # Repository description
}
```

#### Contribution
```python
{
    "id": str,                    # Unique identifier
    "type": str,                  # commit, pull_request, review, issue
    "timestamp": datetime,        # When contribution occurred
    "repository": str,            # Repository full name
    "developer": str,             # Developer username
    "title": str,                 # Title/description
    "state": str,                 # open, closed, merged, etc.
    "metadata": dict              # Type-specific metadata
}
```

#### TimePeriod
```python
{
    "start_date": datetime,       # Period start
    "end_date": datetime,         # Period end
    "period_type": str           # daily, weekly, monthly, custom
}
```

### Aggregated Models

#### DeveloperMetrics
```python
{
    "developer": str,
    "time_period": TimePeriod,
    "total_commits": int,
    "pull_requests_created": int,
    "pull_requests_reviewed": int,
    "pull_requests_merged": int,
    "issues_created": int,
    "issues_resolved": int,
    "code_review_participation": int,
    "repositories_contributed": List[str],
    "per_repository_breakdown": dict
}
```

#### RepositoryMetrics
```python
{
    "repository": str,
    "time_period": TimePeriod,
    "total_contributions": int,
    "active_contributors": int,
    "contributor_list": List[str],
    "commits": int,
    "pull_requests": int,
    "issues": int,
    "reviews": int,
    "trend": str,                 # increasing, decreasing, stable
    "contribution_distribution": dict
}
```

#### TeamMetrics
```python
{
    "team_name": str,
    "time_period": TimePeriod,
    "total_contributions": int,
    "active_members": int,
    "member_list": List[str],
    "commits": int,
    "pull_requests": int,
    "issues": int,
    "reviews": int,
    "repositories_contributed": List[str]
}
```

#### Anomaly
```python
{
    "type": str,                  # contribution_drop, contribution_spike
    "entity": str,                # Entity identifier
    "entity_type": str,           # developer, repository, team
    "severity": str,              # low, medium, high, critical
    "description": str,           # Human-readable description
    "detected_at": datetime,      # When detected
    "previous_value": float,      # Previous period value
    "current_value": float,       # Current period value
    "change_percent": float       # Percentage change
}
```

## Caching & Storage

### File-Based Cache (Default)

The tool uses a file-based JSON cache to store collected data and minimize API calls.

**Cache Structure:**
```
~/.github-tools/
├── cache/
│   ├── contributions/
│   │   ├── contributions_myorg_repo1_20241201_20241231.json
│   │   └── contributions_myorg_repo2_20241201_20241231.json
│   └── repositories/
│       └── repos_myorg.json
└── checkpoints/
    ├── commits_myorg_repo1_2024-12-01.json
    └── prs_myorg_repo1_2024-12-01.json
```

**Cache Configuration:**
- **Location**: `~/.github-tools/cache/` (configurable)
- **TTL**: 24 hours (configurable)
- **Format**: JSON files
- **Naming**: `{type}_{repository}_{start_date}_{end_date}.json`

### SQLite Support (Optional)

For large-scale deployments, SQLite caching can be enabled:

```python
# In cache.py, SQLite backend can be used for:
# - Faster queries on large datasets
# - Better performance for historical analysis
# - Reduced file system overhead
```

**SQLite Schema** (when enabled):

The SQLite backend uses a simple key-value cache structure:

```sql
-- Cache entries table (generic key-value store)
CREATE TABLE IF NOT EXISTS cache_entries (
    key TEXT PRIMARY KEY,              -- Cache key (e.g., "contributions_myorg_repo1_20241201_20241231")
    value TEXT NOT NULL,               -- JSON-serialized cached data
    created_at TIMESTAMP NOT NULL,     -- When cache entry was created
    expires_at TIMESTAMP NOT NULL      -- When cache entry expires
);

-- Index for efficient expiration checks
CREATE INDEX IF NOT EXISTS idx_expires_at ON cache_entries(expires_at);
```

**Cache Key Format:**
- Contributions: `contributions_{repository}_{start_date}_{end_date}`
- Example: `contributions_myorg_repo1_20241201_20241231`

**Note**: The SQLite backend stores all cached data as JSON strings in the `value` column. The actual data models (contributions, developers, repositories) are serialized/deserialized as needed. This provides flexibility while maintaining a simple schema.

### Checkpoint System

For long-running data collection operations, checkpoints are saved to enable resumption:

```
~/.github-tools/checkpoints/
├── commits_myorg_repo1_2024-12-01.json
└── prs_myorg_repo1_2024-12-01.json
```

Checkpoint format:
```json
{
    "operation_id": "collect_commits_myorg_repo1",
    "retry_count": 3,
    "timestamp": "2024-12-28T10:30:00Z"
}
```

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI Commands                           │
│  developer-report | repository-report | team-report | ...   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Report Generator                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   JSON       │  │  Markdown    │  │     CSV      │       │
│  │  Formatter   │  │  Formatter   │  │  Formatter   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Analyzers                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Developer   │  │ Repository   │  │    Team     │        │
│  │   Analyzer   │  │  Analyzer    │  │  Analyzer   │        │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │   Anomaly    │  │   PR Summary │                         │
│  │   Detector   │  │  Collector   │                         │
│  └──────────────┘  └──────────────┘                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     Collectors                              │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │ Contribution│  │  PR Summary  │                          │
│  │  Collector   │  │  Collector   │                         │
│  └──────────────┘  └──────────────┘                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              GitHub API Client + Rate Limiter               │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │   GitHub     │  │    Rate      │                         │
│  │   Client     │  │   Limiter    │                         │
│  └──────────────┘  └──────────────┘                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                    GitHub API
```

### Data Flow

```
1. User Request
   │
   ├─> CLI Command
   │
   ├─> Configuration Load
   │
   ├─> Check Cache
   │   ├─> Cache Hit → Use Cached Data
   │   └─> Cache Miss → Fetch from API
   │
   ├─> GitHub API Calls
   │   ├─> Rate Limiting
   │   ├─> Retry Logic
   │   └─> Checkpointing
   │
   ├─> Data Collection
   │   ├─> Commits
   │   ├─> Pull Requests
   │   ├─> Reviews
   │   └─> Issues
   │
   ├─> Data Transformation
   │   ├─> Contribution Models
   │   ├─> Developer Classification
   │   └─> Filtering
   │
   ├─> Analysis
   │   ├─> Metric Calculation
   │   ├─> Aggregation
   │   └─> Anomaly Detection
   │
   ├─> Report Generation
   │   ├─> Format Selection
   │   ├─> Template Rendering
   │   └─> Output
   │
   └─> Cache Update
```

### Component Interactions

```
┌─────────────┐
│   CLI       │
└──────┬──────┘
       │
       ├─────────────────────────────────┐
       │                                 │
       ▼                                 ▼
┌─────────────┐                  ┌─────────────┐
│   Config    │                  │    Cache    │
│  Manager    │                  │   Manager   │
└─────────────┘                  └─────────────┘
       │                                 │
       └─────────────┬──────────────────┘
                     │
                     ▼
            ┌─────────────┐
            │   GitHub    │
            │ API Client  │
            └─────────────┘
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│Collector │  │Analyzer  │  │Summarizer│
└──────────┘  └──────────┘  └──────────┘
       │             │             │
       └─────────────┼─────────────┘
                     │
                     ▼
            ┌─────────────┐
            │   Report    │
            │  Generator  │
            └─────────────┘
```

## Usage Examples

### Example 1: Monthly Developer Performance Review

```bash
# Generate comprehensive developer report for December 2024
github-tools developer-report \
  --start-date 2024-12-01 \
  --end-date 2024-12-31 \
  --format markdown \
  --output december-2024-dev-report.md

# Generate JSON version for further processing
github-tools developer-report \
  --start-date 2024-12-01 \
  --end-date 2024-12-31 \
  --format json \
  --output december-2024-dev-report.json
```

### Example 2: Repository Health Check

```bash
# Identify repositories with declining activity
github-tools repository-report \
  --start-date 3m \
  --end-date today \
  --format markdown \
  --output repo-health-check.md

# Filter to specific repositories
github-tools repository-report \
  --start-date 1m \
  --end-date today \
  --repository myorg/legacy-service \
  --repository myorg/new-service
```

### Example 3: Team Sprint Retrospective

```bash
# Generate team metrics for sprint period
github-tools team-report \
  --start-date 2024-12-15 \
  --end-date 2024-12-29 \
  --team-config teams.json \
  --department engineering \
  --format markdown \
  --output sprint-retro.md
```

### Example 4: Weekly PR Summary for Stakeholders

```bash
# Generate weekly PR summary
github-tools pr-summary-report \
  --start-date 1w \
  --end-date today \
  --format markdown \
  --output weekly-pr-summary.md

# Email-friendly version
github-tools pr-summary-report \
  --start-date 1w \
  --end-date today \
  --format markdown | \
  mail -s "Weekly PR Summary" stakeholders@company.com
```

### Example 5: Anomaly Detection Alert

```bash
# Detect anomalies comparing this week to last week
github-tools anomaly-report \
  --current-start-date 7d \
  --current-end-date today \
  --threshold 50.0 \
  --format json \
  --output anomalies.json

# Check for critical anomalies only
github-tools anomaly-report \
  --current-start-date 1m \
  --current-end-date today \
  --threshold 80.0 \
  --entity-type repository
```

### Example 6: Automated Reporting Script

```bash
#!/bin/bash
# daily-report.sh

DATE=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)

# Generate daily developer report
github-tools developer-report \
  --start-date "$YESTERDAY" \
  --end-date "$DATE" \
  --format markdown \
  --output "reports/daily-dev-report-$DATE.md"

# Generate daily PR summary
github-tools pr-summary-report \
  --start-date "$YESTERDAY" \
  --end-date "$DATE" \
  --format markdown \
  --output "reports/daily-pr-summary-$DATE.md"

# Check for anomalies
github-tools anomaly-report \
  --current-start-date "$YESTERDAY" \
  --current-end-date "$DATE" \
  --threshold 50.0 \
  --format json \
  --output "reports/anomalies-$DATE.json"
```

## Troubleshooting

### Common Issues

#### 1. Rate Limit Exceeded

**Error**: `403: rate limit exceeded`

**Solution**:
- The tool automatically handles rate limits with exponential backoff
- Checkpoints are saved to resume collection
- Wait for the rate limit to reset (usually 1 hour)
- Use `--no-cache` to avoid cache issues

#### 2. Authentication Failed

**Error**: `401: Bad credentials`

**Solution**:
- Verify `GITHUB_TOKEN` is set: `echo $GITHUB_TOKEN`
- Ensure token has required scopes: `repo`, `read:org`, `read:user`
- Regenerate token if expired

#### 3. Organization Not Found

**Error**: `404: Not Found`

**Solution**:
- Verify organization name is correct
- Ensure token has access to the organization
- Use `--repository` to specify repositories directly

#### 4. OpenAI API Errors

**Error**: `OpenAI API error`

**Solution**:
- Verify `OPENAI_API_KEY` is set
- Check API key is valid and has credits
- PR summaries will fall back to simple summaries if API fails

#### 5. Cache Issues

**Error**: Stale or incorrect data

**Solution**:
- Use `--no-cache` to force fresh data
- Clear cache: `rm -rf ~/.github-tools/cache/*`
- Check cache TTL in configuration

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
github-tools --verbose developer-report --start-date 30d --end-date today
```

### Performance Optimization

1. **Use Caching**: Cache is enabled by default, don't disable unless necessary
2. **Filter Early**: Use `--repository` and `--developer` filters to reduce data collection
3. **Batch Operations**: Collect data once, generate multiple reports from cache
4. **Parallel Processing**: For large organizations, consider running multiple instances for different repositories

### Dependency Management

#### Updating Dependencies

```bash
# Update all dependencies to latest compatible versions
pip install --upgrade -r requirements.txt

# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade <package-name>
```

#### Dependency Conflicts

If you encounter dependency conflicts:

1. **Use a virtual environment** - Isolates project dependencies
2. **Check version constraints** - See `requirements.txt` for minimum versions
3. **Update pip** - Ensure pip is up to date: `pip install --upgrade pip`
4. **Check Python version** - Ensure Python 3.11+ is installed

#### Known Compatibility Issues

- **pandas 2.0+**: Requires Python 3.8+ (project requires 3.11+)
- **pydantic 2.0+**: Breaking changes from v1.x (project uses v2.x)
- **openai 1.0+**: API changes from v0.x (project uses v1.x)

## Contributing

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd git-tools

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install development dependencies
pip install -r requirements-dev.txt
pip install -e .

# Run tests
pytest

# Run linting
ruff check src/
black --check src/

# Run type checking
mypy src/
```

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for all public functions
- Follow TDD approach (tests first)

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/github_tools --cov-report=html

# Run specific test file
pytest tests/unit/test_developer_analyzer.py

# Run integration tests
pytest tests/integration/ -m integration
```

## License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2024 GitHub Developer Contribution Analytics Tools

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Support

For issues, questions, or contributions, please open an issue on the repository.

---

**Last Updated**: 2024-12-28
