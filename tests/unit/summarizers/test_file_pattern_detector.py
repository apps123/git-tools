"""Unit tests for file pattern detector."""

import pytest

from github_tools.summarizers.file_pattern_detector import (
    FilePatternDetector,
    FileCategory,
    PRFile,
)


class TestFilePatternDetector:
    """Tests for FilePatternDetector."""
    
    def test_detect_category_iac_terraform(self):
        """Test detection of Terraform files."""
        detector = FilePatternDetector()
        assert detector.detect_category("main.tf") == FileCategory.IAC
        assert detector.detect_category("variables.tfvars") == FileCategory.IAC
        assert detector.detect_category("terraform/modules/ec2.tf") == FileCategory.IAC
        assert detector.detect_category("infra/terraform/main.tf") == FileCategory.IAC
    
    def test_detect_category_iac_cloudformation(self):
        """Test detection of CloudFormation files."""
        detector = FilePatternDetector()
        assert detector.detect_category("template.yaml") == FileCategory.IAC
        assert detector.detect_category("cloudformation/stack.json") == FileCategory.IAC
    
    def test_detect_category_ai_model(self):
        """Test detection of AI/ML model files."""
        detector = FilePatternDetector()
        assert detector.detect_category("model.pkl") == FileCategory.AI_MODEL
        assert detector.detect_category("checkpoint.h5") == FileCategory.AI_MODEL
        assert detector.detect_category("model.onnx") == FileCategory.AI_MODEL
        assert detector.detect_category("models/bert.pt") == FileCategory.AI_MODEL
        assert detector.detect_category("models/checkpoints/model.ckpt") == FileCategory.AI_MODEL
    
    def test_detect_category_data_file(self):
        """Test detection of data files."""
        detector = FilePatternDetector()
        assert detector.detect_category("data.csv") == FileCategory.DATA_FILE
        assert detector.detect_category("dataset.parquet") == FileCategory.DATA_FILE
        assert detector.detect_category("data/training.json") == FileCategory.DATA_FILE
        assert detector.detect_category("datasets/test.avro") == FileCategory.DATA_FILE
    
    def test_detect_category_config(self):
        """Test detection of configuration files."""
        detector = FilePatternDetector()
        assert detector.detect_category(".env") == FileCategory.CONFIG
        assert detector.detect_category(".env.production") == FileCategory.CONFIG
        assert detector.detect_category("config.yaml") == FileCategory.CONFIG
        assert detector.detect_category("config/app.toml") == FileCategory.CONFIG
    
    def test_detect_category_security_config(self):
        """Test detection of security configuration files."""
        detector = FilePatternDetector()
        assert detector.detect_category("cert.pem") == FileCategory.SECURITY_CONFIG
        assert detector.detect_category("private.key") == FileCategory.SECURITY_CONFIG
        assert detector.detect_category("secrets/api.key") == FileCategory.SECURITY_CONFIG
        assert detector.detect_category("security/policy.json") == FileCategory.SECURITY_CONFIG
    
    def test_detect_category_infrastructure(self):
        """Test detection of infrastructure files."""
        detector = FilePatternDetector()
        assert detector.detect_category("Dockerfile") == FileCategory.INFRASTRUCTURE
        assert detector.detect_category("docker-compose.yml") == FileCategory.INFRASTRUCTURE
        assert detector.detect_category("kubernetes/deployment.yaml") == FileCategory.INFRASTRUCTURE
        assert detector.detect_category("k8s/service.yml") == FileCategory.INFRASTRUCTURE
    
    def test_detect_category_documentation(self):
        """Test detection of documentation files."""
        detector = FilePatternDetector()
        assert detector.detect_category("README.md") == FileCategory.DOCUMENTATION
        assert detector.detect_category("docs/api.rst") == FileCategory.DOCUMENTATION
        assert detector.detect_category("CHANGELOG.md") == FileCategory.DOCUMENTATION
    
    def test_detect_category_test(self):
        """Test detection of test files."""
        detector = FilePatternDetector()
        assert detector.detect_category("test_service.py") == FileCategory.TEST
        assert detector.detect_category("service_test.py") == FileCategory.TEST
        assert detector.detect_category("tests/unit/test_api.py") == FileCategory.TEST
    
    def test_detect_category_unknown(self):
        """Test detection of unknown files."""
        detector = FilePatternDetector()
        assert detector.detect_category("random_file.txt") == FileCategory.UNKNOWN
        assert detector.detect_category("unknown.xyz") == FileCategory.UNKNOWN
    
    def test_detect_patterns(self):
        """Test pattern detection for multiple files."""
        detector = FilePatternDetector()
        files = [
            PRFile("main.tf", "modified", 10, 5),
            PRFile("model.pkl", "added", 100, 0),
            PRFile("data.csv", "added", 50, 0),
            PRFile(".env", "modified", 2, 1),
            PRFile("app.py", "modified", 20, 10),
        ]
        
        patterns = detector.detect_patterns(files)
        
        assert "iac" in patterns
        assert "main.tf" in patterns["iac"]
        assert "ai_model" in patterns
        assert "model.pkl" in patterns["ai_model"]
        assert "data_file" in patterns
        assert "data.csv" in patterns["data_file"]
        assert "config" in patterns
        assert ".env" in patterns["config"]
    
    def test_get_iac_files(self):
        """Test filtering IAC files."""
        detector = FilePatternDetector()
        files = [
            PRFile("main.tf", "modified", 10, 5),
            PRFile("app.py", "modified", 20, 10),
            PRFile("variables.tfvars", "added", 5, 0),
        ]
        
        iac_files = detector.get_iac_files(files)
        assert len(iac_files) == 2
        assert all(f.filename.endswith((".tf", ".tfvars")) for f in iac_files)
    
    def test_get_ai_model_files(self):
        """Test filtering AI model files."""
        detector = FilePatternDetector()
        files = [
            PRFile("model.pkl", "added", 100, 0),
            PRFile("app.py", "modified", 20, 10),
            PRFile("models/bert.pt", "added", 200, 0),
        ]
        
        ai_files = detector.get_ai_model_files(files)
        assert len(ai_files) == 2
        assert any(f.filename == "model.pkl" for f in ai_files)
        assert any(f.filename == "models/bert.pt" for f in ai_files)
    
    def test_get_config_files(self):
        """Test filtering configuration files."""
        detector = FilePatternDetector()
        files = [
            PRFile(".env", "modified", 2, 1),
            PRFile("config.yaml", "added", 5, 0),
            PRFile("cert.pem", "added", 10, 0),
            PRFile("app.py", "modified", 20, 10),
        ]
        
        config_files = detector.get_config_files(files)
        assert len(config_files) >= 2  # .env and config.yaml, cert.pem may also match
        assert any(f.filename == ".env" for f in config_files)
        assert any(f.filename == "config.yaml" for f in config_files)
    
    def test_get_security_config_files(self):
        """Test filtering security configuration files."""
        detector = FilePatternDetector()
        files = [
            PRFile("cert.pem", "added", 10, 0),
            PRFile("private.key", "added", 5, 0),
            PRFile(".env", "modified", 2, 1),
        ]
        
        security_files = detector.get_security_config_files(files)
        assert len(security_files) == 2
        assert any(f.filename == "cert.pem" for f in security_files)
        assert any(f.filename == "private.key" for f in security_files)

