"""Unit tests for internal/external contributor classification."""

import pytest
from unittest.mock import Mock, patch

from github_tools.models.developer import Developer
from github_tools.utils.filters import classify_contributor, apply_contributor_classification
from github_tools.api.client import GitHubClient
from github_tools.utils.config import GitHubConfig


@pytest.fixture
def mock_github_client():
    """Create a mock GitHub client."""
    config = GitHubConfig(token="test-token", base_url="https://api.github.com")
    client = Mock(spec=GitHubClient)
    client.config = config
    return client


class TestClassifyContributor:
    """Tests for classify_contributor function."""
    
    def test_organization_member_is_internal(self, mock_github_client):
        """Test that organization members are classified as internal."""
        mock_github_client.is_organization_member.return_value = True
        
        is_internal, is_org_member = classify_contributor(
            mock_github_client,
            "alice",
            repository="myorg/my-repo",
        )
        
        assert is_internal is True
        assert is_org_member is True
        mock_github_client.is_organization_member.assert_called_once_with("alice")
    
    def test_outside_collaborator_is_external(self, mock_github_client):
        """Test that outside collaborators are classified as external."""
        mock_github_client.is_organization_member.return_value = False
        mock_github_client.is_repository_collaborator.return_value = True
        
        is_internal, is_org_member = classify_contributor(
            mock_github_client,
            "bob",
            repository="myorg/my-repo",
        )
        
        assert is_internal is False
        assert is_org_member is False
        mock_github_client.is_organization_member.assert_called_once_with("bob")
        mock_github_client.is_repository_collaborator.assert_called_once_with(
            "myorg/my-repo",
            "bob",
        )
    
    def test_non_member_non_collaborator_is_external(self, mock_github_client):
        """Test that users who are neither members nor collaborators are external."""
        mock_github_client.is_organization_member.return_value = False
        mock_github_client.is_repository_collaborator.return_value = False
        
        is_internal, is_org_member = classify_contributor(
            mock_github_client,
            "charlie",
            repository="myorg/my-repo",
        )
        
        assert is_internal is False
        assert is_org_member is False
    
    def test_classification_without_repository(self, mock_github_client):
        """Test classification when repository is not provided."""
        mock_github_client.is_organization_member.return_value = False
        
        is_internal, is_org_member = classify_contributor(
            mock_github_client,
            "diana",
            repository=None,
        )
        
        assert is_internal is False
        assert is_org_member is False
        mock_github_client.is_organization_member.assert_called_once_with("diana")
        # Should not check collaborator status without repository
        mock_github_client.is_repository_collaborator.assert_not_called()


class TestApplyContributorClassification:
    """Tests for apply_contributor_classification function."""
    
    def test_classify_multiple_developers(self, mock_github_client):
        """Test classifying multiple developers."""
        mock_github_client.is_organization_member.side_effect = lambda u: u == "alice"
        mock_github_client.is_repository_collaborator.return_value = False
        
        developers = [
            Developer(
                username="alice",
                display_name="Alice",
                organization_member=False,
                is_internal=False,
            ),
            Developer(
                username="bob",
                display_name="Bob",
                organization_member=False,
                is_internal=False,
            ),
        ]
        
        classified = apply_contributor_classification(
            developers,
            mock_github_client,
            repository="myorg/my-repo",
        )
        
        assert len(classified) == 2
        assert classified[0].is_internal is True
        assert classified[0].organization_member is True
        assert classified[1].is_internal is False
        assert classified[1].organization_member is False
    
    def test_preserves_other_developer_fields(self, mock_github_client):
        """Test that classification preserves other developer fields."""
        mock_github_client.is_organization_member.return_value = True
        mock_github_client.is_repository_collaborator.return_value = False
        
        developers = [
            Developer(
                username="alice",
                display_name="Alice Developer",
                email="alice@example.com",
                organization_member=False,
                team_affiliations=["backend-team"],
                is_internal=False,
            ),
        ]
        
        classified = apply_contributor_classification(
            developers,
            mock_github_client,
            repository="myorg/my-repo",
        )
        
        assert len(classified) == 1
        assert classified[0].username == "alice"
        assert classified[0].display_name == "Alice Developer"
        assert classified[0].email == "alice@example.com"
        assert classified[0].team_affiliations == ["backend-team"]
        assert classified[0].is_internal is True
        assert classified[0].organization_member is True

