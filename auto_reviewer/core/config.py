"""Configuration handler for Auto Reviewer."""

import os
import yaml
from typing import Dict, Any, Optional

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from .autoreviewerrc file."""
    if not config_path:
        config_path = os.path.join(os.getcwd(), ".autoreviewerrc")
    
    if not os.path.exists(config_path):
        return get_default_config()
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_default_config() -> Dict[str, Any]:
    """Get default configuration."""
    return {
        "rules": {
            "max_file_changes": 50,
            "complexity_threshold": 15,
            "required_tests": True
        },
        "ignore_patterns": [
            "*.md",
            "*.json"
        ]
    }