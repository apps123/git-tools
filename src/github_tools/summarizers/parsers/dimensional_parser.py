"""Parser for structured dimensional analysis responses from LLM."""

import json
import re
from typing import Dict, Optional, Any

from github_tools.summarizers.dimensions.base import DimensionResult
from github_tools.utils.logging import get_logger

logger = get_logger(__name__)


class DimensionalParser:
    """
    Parses structured LLM responses for dimensional analysis.
    
    Handles JSON responses and fallback parsing from text responses.
    """
    
    @staticmethod
    def parse_response(response_text: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured dimensional analysis.
        
        Args:
            response_text: Raw LLM response text
        
        Returns:
            Dictionary with 'summary' and 'dimensions' keys
        """
        # Try to extract JSON from response
        json_data = DimensionalParser._extract_json(response_text)
        
        if json_data:
            return DimensionalParser._validate_and_normalize(json_data)
        else:
            # Fallback: parse from text format
            logger.warning("Could not extract JSON, attempting text parsing")
            return DimensionalParser._parse_text_format(response_text)
    
    @staticmethod
    def _extract_json(text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON object from response text."""
        # Try to find JSON block
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Try parsing entire text as JSON
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        
        return None
    
    @staticmethod
    def _validate_and_normalize(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize parsed JSON data.
        
        Args:
            data: Parsed JSON data
        
        Returns:
            Normalized dictionary with required structure
        """
        result = {
            "summary": data.get("summary", ""),
            "dimensions": {},
        }
        
        # Expected dimension names
        dimension_names = [
            "security",
            "cost",
            "operational",
            "architectural",
            "mentorship",
            "data_governance",
            "ai_governance",
        ]
        
        dimensions = data.get("dimensions", {})
        
        for dim_name in dimension_names:
            dim_data = dimensions.get(dim_name, {})
            
            if isinstance(dim_data, dict):
                level = dim_data.get("level", "N/A")
                description = dim_data.get("description", "")
            elif isinstance(dim_data, str):
                # Handle case where dimension is just a string
                level = "N/A"
                description = dim_data
            else:
                level = "N/A"
                description = ""
            
            result["dimensions"][dim_name] = {
                "level": level,
                "description": description or "Not specified",
            }
        
        return result
    
    @staticmethod
    def _parse_text_format(text: str) -> Dict[str, Any]:
        """
        Fallback: Parse from text format when JSON extraction fails.
        
        Args:
            text: Response text
        
        Returns:
            Parsed structure
        """
        result = {
            "summary": "",
            "dimensions": {},
        }
        
        # Extract summary
        summary_match = re.search(r'(?:summary|Summary):\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        if summary_match:
            result["summary"] = summary_match.group(1).strip()
        
        # Dimension mapping for text parsing
        dimension_patterns = {
            "security": r'(?:Security|⚠️)[\s\S]*?(?:level|impact)[\s\S]*?:\s*([^\n]+)',
            "cost": r'(?:Cost|💰)[\s\S]*?(?:level|impact)[\s\S]*?:\s*([^\n]+)',
            "operational": r'(?:Operational|📈)[\s\S]*?:\s*([^\n]+)',
            "architectural": r'(?:Architectural|🏗️)[\s\S]*?:\s*([^\n]+)',
            "mentorship": r'(?:Mentorship|🤝)[\s\S]*?:\s*([^\n]+)',
            "data_governance": r'(?:Data Governance|🏛️)[\s\S]*?:\s*([^\n]+)',
            "ai_governance": r'(?:AI Governance|🤖)[\s\S]*?:\s*([^\n]+)',
        }
        
        for dim_name, pattern in dimension_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                description = match.group(1).strip()
                # Try to extract level from description
                level_match = re.search(r'\b(High|Medium|Low|Positive|Negative|Neutral|Strong|Moderate|Weak|Impact|No Impact|N/A)\b', description, re.IGNORECASE)
                level = level_match.group(1) if level_match else "N/A"
                result["dimensions"][dim_name] = {
                    "level": level,
                    "description": description,
                }
            else:
                result["dimensions"][dim_name] = {
                    "level": "N/A",
                    "description": "Analysis unavailable",
                }
        
        return result
    
    @staticmethod
    def to_dimension_results(parsed_data: Dict[str, Any]) -> Dict[str, DimensionResult]:
        """
        Convert parsed data to DimensionResult objects.
        
        Args:
            parsed_data: Parsed dimensional analysis data
        
        Returns:
            Dictionary mapping dimension names to DimensionResult objects
        """
        results = {}
        
        dimensions = parsed_data.get("dimensions", {})
        
        dimension_mapping = {
            "security": "security",
            "cost": "cost",
            "operational": "operational",
            "architectural": "architectural",
            "mentorship": "mentorship",
            "data_governance": "data_governance",
            "ai_governance": "ai_governance",
        }
        
        for key, dim_name in dimension_mapping.items():
            dim_data = dimensions.get(key, {})
            
            if isinstance(dim_data, dict):
                level = dim_data.get("level", "N/A")
                description = dim_data.get("description", "")
            else:
                level = "N/A"
                description = str(dim_data) if dim_data else ""
            
            is_applicable = level.upper() != "N/A" and description.lower() != "not specified"
            
            results[dim_name] = DimensionResult(
                level=level,
                description=description or "Not specified",
                is_applicable=is_applicable,
            )
        
        return results

