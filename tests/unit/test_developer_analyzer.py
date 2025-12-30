"""Unit tests for developer metric aggregation logic."""

from datetime import datetime, timedelta

import pytest

from github_tools.models.contribution import Contribution
from github_tools.models.developer import Developer
from github_tools.models.time_period import TimePeriod


@pytest.fixture
def sample_contributions():
    """Sample contributions for testing aggregation."""
    base_date = datetime(2024, 12, 1, 10, 0, 0)
    
    return [
        # Commits
        Contribution(
            id="c1",
            type="commit",
            timestamp=base_date,
            repository="myorg/repo1",
            developer="alice",
            metadata={"sha": "abc", "files_changed": 2},
        ),
        Contribution(
            id="c2",
            type="commit",
            timestamp=base_date + timedelta(hours=1),
            repository="myorg/repo1",
            developer="alice",
            metadata={"sha": "def", "files_changed": 1},
        ),
        Contribution(
            id="c3",
            type="commit",
            timestamp=base_date + timedelta(hours=2),
            repository="myorg/repo2",
            developer="alice",
            metadata={"sha": "ghi", "files_changed": 3},
        ),
        # Pull requests
        Contribution(
            id="pr1",
            type="pull_request",
            timestamp=base_date + timedelta(days=1),
            repository="myorg/repo1",
            developer="alice",
            title="Add feature",
            state="merged",
            metadata={"number": 1, "merged": True},
        ),
        Contribution(
            id="pr2",
            type="pull_request",
            timestamp=base_date + timedelta(days=2),
            repository="myorg/repo1",
            developer="alice",
            title="Fix bug",
            state="closed",
            metadata={"number": 2, "merged": False},
        ),
        # Reviews
        Contribution(
            id="r1",
            type="review",
            timestamp=base_date + timedelta(days=1, hours=2),
            repository="myorg/repo1",
            developer="bob",
            title="Review PR #1",
            state="approved",
            metadata={"review_id": 1, "pr_number": 1},
        ),
        # Issues
        Contribution(
            id="i1",
            type="issue",
            timestamp=base_date + timedelta(days=3),
            repository="myorg/repo1",
            developer="alice",
            title="Bug report",
            state="open",
            metadata={"number": 1},
        ),
        Contribution(
            id="i2",
            type="issue",
            timestamp=base_date + timedelta(days=4),
            repository="myorg/repo1",
            developer="alice",
            title="Feature request",
            state="closed",
            metadata={"number": 2},
        ),
    ]


class TestDeveloperMetricAggregation:
    """Tests for developer metric aggregation logic."""
    
    def test_count_commits_by_developer(self, sample_contributions):
        """Test counting commits per developer."""
        alice_commits = [
            c for c in sample_contributions
            if c.developer == "alice" and c.type == "commit"
        ]
        assert len(alice_commits) == 3
    
    def test_count_pull_requests_by_developer(self, sample_contributions):
        """Test counting pull requests per developer."""
        alice_prs = [
            c for c in sample_contributions
            if c.developer == "alice" and c.type == "pull_request"
        ]
        assert len(alice_prs) == 2
    
    def test_count_merged_pull_requests(self, sample_contributions):
        """Test counting merged pull requests."""
        merged_prs = [
            c for c in sample_contributions
            if c.type == "pull_request" and c.state == "merged"
        ]
        assert len(merged_prs) == 1
    
    def test_count_reviews_by_developer(self, sample_contributions):
        """Test counting reviews per developer."""
        bob_reviews = [
            c for c in sample_contributions
            if c.developer == "bob" and c.type == "review"
        ]
        assert len(bob_reviews) == 1
    
    def test_count_issues_by_developer(self, sample_contributions):
        """Test counting issues per developer."""
        alice_issues = [
            c for c in sample_contributions
            if c.developer == "alice" and c.type == "issue"
        ]
        assert len(alice_issues) == 2
    
    def test_count_resolved_issues(self, sample_contributions):
        """Test counting resolved issues."""
        resolved_issues = [
            c for c in sample_contributions
            if c.type == "issue" and c.state == "closed"
        ]
        assert len(resolved_issues) == 1
    
    def test_get_repositories_contributed(self, sample_contributions):
        """Test getting list of repositories a developer contributed to."""
        alice_contributions = [
            c for c in sample_contributions if c.developer == "alice"
        ]
        repos = {c.repository for c in alice_contributions}
        assert repos == {"myorg/repo1", "myorg/repo2"}
    
    def test_per_repository_breakdown(self, sample_contributions):
        """Test calculating per-repository breakdown."""
        alice_repo1 = [
            c for c in sample_contributions
            if c.developer == "alice" and c.repository == "myorg/repo1"
        ]
        alice_repo2 = [
            c for c in sample_contributions
            if c.developer == "alice" and c.repository == "myorg/repo2"
        ]
        
        assert len(alice_repo1) == 5  # 2 commits, 2 PRs, 1 issue
        assert len(alice_repo2) == 1  # 1 commit

