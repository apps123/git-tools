"""Performance tests for multi-dimensional analysis."""

import time
import pytest

from github_tools.summarizers.multi_dimensional_analyzer import MultiDimensionalAnalyzer
from github_tools.summarizers.file_pattern_detector import PRFile


@pytest.fixture
def analyzer():
    """Create analyzer instance."""
    return MultiDimensionalAnalyzer()


@pytest.fixture
def sample_pr_context():
    """Sample PR context for testing."""
    return {
        "title": "Test PR",
        "body": "Test description",
        "repository": "test/repo",
    }


@pytest.fixture
def small_file_list():
    """Small list of files (10 files)."""
    return [
        PRFile(f"file{i}.py", "modified", 10, 5)
        for i in range(10)
    ]


@pytest.fixture
def large_file_list():
    """Large list of files (200 files)."""
    return [
        PRFile(f"file{i}.py", "modified", 10, 5)
        for i in range(200)
    ]


@pytest.mark.performance
class TestDimensionalPerformance:
    """Performance tests for multi-dimensional analysis."""
    
    def test_analysis_time_small_pr(self, analyzer, sample_pr_context, small_file_list):
        """
        Test that analysis completes in ≤2 seconds for small PRs (≤20 files).
        
        Per NFR-4b-002: Analysis adds ≤2 seconds to existing PR summary generation time.
        """
        start_time = time.time()
        
        results = analyzer.analyze(sample_pr_context, small_file_list)
        
        elapsed = time.time() - start_time
        
        assert elapsed <= 2.0, f"Analysis took {elapsed:.2f}s, exceeds 2s threshold"
        assert len(results) == 7, "All dimensions should be analyzed"
    
    def test_analysis_time_large_pr(self, analyzer, sample_pr_context, large_file_list):
        """
        Test that analysis handles large PRs efficiently (200 files).
        
        Should still complete reasonably quickly even with many files.
        """
        start_time = time.time()
        
        results = analyzer.analyze(sample_pr_context, large_file_list)
        
        elapsed = time.time() - start_time
        
        # Allow more time for large PRs, but should still be reasonable (<10s)
        assert elapsed <= 10.0, f"Analysis took {elapsed:.2f}s, exceeds 10s threshold for large PR"
        assert len(results) == 7, "All dimensions should be analyzed"
    
    def test_batch_throughput(self, analyzer, sample_pr_context, small_file_list):
        """
        Test batch processing throughput ≥8 PRs/minute.
        
        Per NFR-4b-002: Batch processing maintains ≥8 PRs/minute throughput.
        """
        num_prs = 10
        pr_contexts = [
            {
                "title": f"PR {i}",
                "body": f"Description {i}",
                "repository": "test/repo",
            }
            for i in range(num_prs)
        ]
        
        start_time = time.time()
        
        for pr_context in pr_contexts:
            analyzer.analyze(pr_context, small_file_list)
        
        elapsed = time.time() - start_time
        
        # Calculate throughput (PRs per minute)
        throughput = (num_prs / elapsed) * 60
        
        assert throughput >= 8.0, (
            f"Throughput {throughput:.2f} PRs/min below threshold of 8 PRs/min. "
            f"Processed {num_prs} PRs in {elapsed:.2f}s"
        )
    
    def test_file_pattern_detection_performance(self, analyzer, large_file_list):
        """Test file pattern detection is efficient."""
        start_time = time.time()
        
        file_patterns = analyzer.pattern_detector.detect_patterns(large_file_list)
        
        elapsed = time.time() - start_time
        
        # Pattern detection should be very fast (<500ms per NFR)
        assert elapsed <= 0.5, (
            f"File pattern detection took {elapsed:.2f}s, exceeds 500ms threshold"
        )
        assert isinstance(file_patterns, dict)

