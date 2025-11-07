"""Test configuration functionality."""

import os
import pytest
from auto_reviewer.core.config import load_config, get_default_config

def test_get_default_config():
    """Test getting default configuration."""
    config = get_default_config()
    assert isinstance(config, dict)
    assert 'rules' in config
    assert 'ignore_patterns' in config

def test_load_config_nonexistent():
    """Test loading configuration from nonexistent file."""
    config = load_config('nonexistent.yaml')
    assert config == get_default_config()

def test_load_config_custom(tmp_path):
    """Test loading custom configuration."""
    config_content = """
    rules:
      max_file_changes: 100
      complexity_threshold: 20
      required_tests: false
    ignore_patterns:
      - "*.txt"
    """
    config_path = tmp_path / '.autoreviewerrc'
    config_path.write_text(config_content)
    
    config = load_config(str(config_path))
    assert config['rules']['max_file_changes'] == 100
    assert config['rules']['complexity_threshold'] == 20
    assert config['rules']['required_tests'] is False
    assert '*.txt' in config['ignore_patterns']