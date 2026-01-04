"""File pattern detector for identifying file types and categories."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set

from github_tools.utils.logging import get_logger

logger = get_logger(__name__)


class FileCategory(Enum):
    """File category classifications."""
    IAC = "iac"  # Infrastructure as Code
    AI_MODEL = "ai_model"  # AI/ML model files
    DATA_FILE = "data_file"  # Data files
    CONFIG = "config"  # Configuration files
    SECURITY_CONFIG = "security_config"  # Security configuration
    INFRASTRUCTURE = "infrastructure"  # Infrastructure-related
    CODE = "code"  # Application code
    DOCUMENTATION = "documentation"  # Documentation files
    TEST = "test"  # Test files
    UNKNOWN = "unknown"  # Unknown/unclassified


@dataclass
class FilePattern:
    """File pattern for classification."""
    pattern: str  # Glob pattern or regex
    category: FileCategory
    extensions: Optional[List[str]] = None  # File extensions
    path_patterns: Optional[List[str]] = None  # Path patterns (e.g., "terraform/*", "**/models/**")


@dataclass
class PRFile:
    """Represents a file changed in a PR."""
    filename: str
    status: str  # "added", "modified", "removed"
    additions: int
    deletions: int
    patch: Optional[str] = None  # Diff content
    sha: Optional[str] = None


class FilePatternDetector:
    """
    Detects file patterns and categorizes files for dimensional analysis.
    
    Identifies IAC files, AI/ML models, data files, configuration files,
    and other patterns relevant to impact analysis.
    """
    
    # IAC file patterns
    IAC_PATTERNS = [
        FilePattern("*.tf", FileCategory.IAC, extensions=[".tf", ".tfvars", ".tf.json"]),
        FilePattern("*.tf.json", FileCategory.IAC),
        FilePattern("*.tfvars", FileCategory.IAC),
        FilePattern("terraform/**", FileCategory.IAC, path_patterns=["terraform/**"]),
        FilePattern("**/terraform/**", FileCategory.IAC, path_patterns=["**/terraform/**"]),
        FilePattern("*.tfstate", FileCategory.IAC),
        FilePattern("*.tfstate.backup", FileCategory.IAC),
        FilePattern("cloudformation/**", FileCategory.IAC, path_patterns=["cloudformation/**"]),
        FilePattern("**/*.yaml", FileCategory.IAC, extensions=[".yaml", ".yml"]),  # CloudFormation templates
        FilePattern("**/*.json", FileCategory.IAC, extensions=[".json"]),  # CloudFormation templates
        FilePattern("Pulumi.*", FileCategory.IAC, path_patterns=["Pulumi.*"]),
        FilePattern("*.pulumi.yaml", FileCategory.IAC),
        FilePattern("*.pulumi.yaml", FileCategory.IAC),
    ]
    
    # AI/ML model file patterns
    AI_MODEL_PATTERNS = [
        FilePattern("*.pkl", FileCategory.AI_MODEL, extensions=[".pkl", ".pickle"]),
        FilePattern("*.h5", FileCategory.AI_MODEL, extensions=[".h5", ".hdf5"]),
        FilePattern("*.onnx", FileCategory.AI_MODEL, extensions=[".onnx"]),
        FilePattern("*.pb", FileCategory.AI_MODEL, extensions=[".pb"]),  # TensorFlow protobuf
        FilePattern("*.pt", FileCategory.AI_MODEL, extensions=[".pt", ".pth"]),  # PyTorch
        FilePattern("*.ckpt", FileCategory.AI_MODEL, extensions=[".ckpt"]),  # Checkpoints
        FilePattern("*.safetensors", FileCategory.AI_MODEL, extensions=[".safetensors"]),
        FilePattern("models/**", FileCategory.AI_MODEL, path_patterns=["models/**", "**/models/**"]),
        FilePattern("checkpoints/**", FileCategory.AI_MODEL, path_patterns=["checkpoints/**", "**/checkpoints/**"]),
        FilePattern("*.joblib", FileCategory.AI_MODEL, extensions=[".joblib"]),
    ]
    
    # Data file patterns
    DATA_FILE_PATTERNS = [
        FilePattern("*.csv", FileCategory.DATA_FILE, extensions=[".csv"]),
        FilePattern("*.parquet", FileCategory.DATA_FILE, extensions=[".parquet"]),
        FilePattern("*.json", FileCategory.DATA_FILE, extensions=[".json"]),  # May overlap with IAC
        FilePattern("*.avro", FileCategory.DATA_FILE, extensions=[".avro"]),
        FilePattern("*.orc", FileCategory.DATA_FILE, extensions=[".orc"]),
        FilePattern("data/**", FileCategory.DATA_FILE, path_patterns=["data/**", "**/data/**"]),
        FilePattern("datasets/**", FileCategory.DATA_FILE, path_patterns=["datasets/**", "**/datasets/**"]),
        FilePattern("*.db", FileCategory.DATA_FILE, extensions=[".db", ".sqlite", ".sqlite3"]),
        FilePattern("*.sql", FileCategory.DATA_FILE, extensions=[".sql"]),
    ]
    
    # Configuration file patterns
    CONFIG_PATTERNS = [
        FilePattern(".env*", FileCategory.CONFIG, path_patterns=[".env*", "**/.env*"]),
        FilePattern("*.env", FileCategory.CONFIG, extensions=[".env"]),
        FilePattern("*.config", FileCategory.CONFIG, extensions=[".config"]),
        FilePattern("*.conf", FileCategory.CONFIG, extensions=[".conf"]),
        FilePattern("*.yaml", FileCategory.CONFIG, extensions=[".yaml", ".yml"]),  # May overlap with IAC
        FilePattern("*.toml", FileCategory.CONFIG, extensions=[".toml"]),
        FilePattern("*.ini", FileCategory.CONFIG, extensions=[".ini"]),
        FilePattern("config/**", FileCategory.CONFIG, path_patterns=["config/**", "**/config/**"]),
        FilePattern("*.properties", FileCategory.CONFIG, extensions=[".properties"]),
    ]
    
    # Security configuration patterns
    SECURITY_CONFIG_PATTERNS = [
        FilePattern("*.pem", FileCategory.SECURITY_CONFIG, extensions=[".pem", ".key", ".cert", ".crt"]),
        FilePattern("*.key", FileCategory.SECURITY_CONFIG),
        FilePattern("*.cert", FileCategory.SECURITY_CONFIG),
        FilePattern("*.crt", FileCategory.SECURITY_CONFIG),
        FilePattern("secrets/**", FileCategory.SECURITY_CONFIG, path_patterns=["secrets/**", "**/secrets/**"]),
        FilePattern("*.secret", FileCategory.SECURITY_CONFIG, extensions=[".secret"]),
        FilePattern("security/**", FileCategory.SECURITY_CONFIG, path_patterns=["security/**", "**/security/**"]),
        FilePattern("*.policy", FileCategory.SECURITY_CONFIG, extensions=[".policy"]),
    ]
    
    # Infrastructure patterns
    INFRASTRUCTURE_PATTERNS = [
        FilePattern("docker-compose*.yml", FileCategory.INFRASTRUCTURE, path_patterns=["docker-compose*.yml", "**/docker-compose*.yml"]),
        FilePattern("Dockerfile*", FileCategory.INFRASTRUCTURE, path_patterns=["Dockerfile*", "**/Dockerfile*"]),
        FilePattern("*.dockerfile", FileCategory.INFRASTRUCTURE, extensions=[".dockerfile"]),
        FilePattern("kubernetes/**", FileCategory.INFRASTRUCTURE, path_patterns=["kubernetes/**", "k8s/**", "**/kubernetes/**"]),
        FilePattern("k8s/**", FileCategory.INFRASTRUCTURE),
        FilePattern("*.yaml", FileCategory.INFRASTRUCTURE),  # K8s manifests
        FilePattern("*.yml", FileCategory.INFRASTRUCTURE),  # K8s manifests
        FilePattern("helm/**", FileCategory.INFRASTRUCTURE, path_patterns=["helm/**", "**/helm/**"]),
    ]
    
    # Documentation patterns
    DOCUMENTATION_PATTERNS = [
        FilePattern("*.md", FileCategory.DOCUMENTATION, extensions=[".md", ".markdown"]),
        FilePattern("*.rst", FileCategory.DOCUMENTATION, extensions=[".rst"]),
        FilePattern("docs/**", FileCategory.DOCUMENTATION, path_patterns=["docs/**", "**/docs/**"]),
        FilePattern("README*", FileCategory.DOCUMENTATION, path_patterns=["README*", "**/README*"]),
    ]
    
    # Test patterns
    TEST_PATTERNS = [
        FilePattern("test_*.py", FileCategory.TEST, path_patterns=["**/test_*.py"]),
        FilePattern("*_test.py", FileCategory.TEST, path_patterns=["**/*_test.py"]),
        FilePattern("tests/**", FileCategory.TEST, path_patterns=["tests/**", "**/tests/**"]),
        FilePattern("spec/**", FileCategory.TEST, path_patterns=["spec/**", "**/spec/**"]),
    ]
    
    def __init__(self):
        """Initialize file pattern detector with all patterns."""
        self.all_patterns: List[FilePattern] = (
            self.IAC_PATTERNS +
            self.AI_MODEL_PATTERNS +
            self.DATA_FILE_PATTERNS +
            self.CONFIG_PATTERNS +
            self.SECURITY_CONFIG_PATTERNS +
            self.INFRASTRUCTURE_PATTERNS +
            self.DOCUMENTATION_PATTERNS +
            self.TEST_PATTERNS
        )
    
    def detect_category(self, filename: str) -> FileCategory:
        """
        Detect file category from filename.
        
        Args:
            filename: File path/name
        
        Returns:
            FileCategory enum value
        """
        import os
        
        # Get file extension
        _, ext = os.path.splitext(filename)
        ext_lower = ext.lower()
        
        # Check extension-based patterns first (fastest)
        for pattern in self.all_patterns:
            if pattern.extensions and ext_lower in [e.lower() for e in pattern.extensions]:
                # Double-check path patterns if specified
                if pattern.path_patterns:
                    if any(self._match_path_pattern(filename, pp) for pp in pattern.path_patterns):
                        return pattern.category
                else:
                    return pattern.category
        
        # Check path-based patterns
        for pattern in self.all_patterns:
            if pattern.path_patterns:
                if any(self._match_path_pattern(filename, pp) for pp in pattern.path_patterns):
                    return pattern.category
        
        # Check glob-like patterns
        for pattern in self.all_patterns:
            if self._match_pattern(filename, pattern.pattern):
                return pattern.category
        
        return FileCategory.UNKNOWN
    
    def _match_path_pattern(self, filename: str, pattern: str) -> bool:
        """Match filename against path pattern."""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(filename, f"**/{pattern}")
    
    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """Match filename against glob pattern."""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)
    
    def detect_patterns(self, files: List[PRFile]) -> Dict[str, List[str]]:
        """
        Detect file patterns and categorize files.
        
        Args:
            files: List of PRFile objects
        
        Returns:
            Dictionary mapping category names to lists of filenames
        """
        categorized: Dict[str, List[str]] = {}
        
        for file in files:
            category = self.detect_category(file.filename)
            category_key = category.value
            
            if category_key not in categorized:
                categorized[category_key] = []
            
            categorized[category_key].append(file.filename)
        
        logger.debug(f"Detected patterns: {len(categorized)} categories, {sum(len(files) for files in categorized.values())} files")
        
        return categorized
    
    def get_iac_files(self, files: List[PRFile]) -> List[PRFile]:
        """Get all IAC files from file list."""
        return [f for f in files if self.detect_category(f.filename) == FileCategory.IAC]
    
    def get_ai_model_files(self, files: List[PRFile]) -> List[PRFile]:
        """Get all AI/ML model files from file list."""
        return [f for f in files if self.detect_category(f.filename) == FileCategory.AI_MODEL]
    
    def get_data_files(self, files: List[PRFile]) -> List[PRFile]:
        """Get all data files from file list."""
        return [f for f in files if self.detect_category(f.filename) == FileCategory.DATA_FILE]
    
    def get_config_files(self, files: List[PRFile]) -> List[PRFile]:
        """Get all configuration files from file list."""
        return [f for f in files if self.detect_category(f.filename) in [FileCategory.CONFIG, FileCategory.SECURITY_CONFIG]]
    
    def get_security_config_files(self, files: List[PRFile]) -> List[PRFile]:
        """Get all security configuration files from file list."""
        return [f for f in files if self.detect_category(f.filename) == FileCategory.SECURITY_CONFIG]

