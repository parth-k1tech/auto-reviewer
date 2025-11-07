"""Tests for static code analysis functionality."""

import pytest
from auto_reviewer.core.static_analysis import StaticAnalyzer

def test_static_analyzer_complexity():
    """Test cyclomatic complexity calculation."""
    analyzer = StaticAnalyzer()
    code = """
def complex_function(x):
    if x > 0:
        if x < 10:
            return True
        else:
            return False
    elif x < 0:
        return None
    else:
        for i in range(10):
            if i == 5:
                break
    return False
"""
    result = analyzer.analyze_code(code)
    assert result.complexity > 1  # Should have high complexity due to nested conditions

def test_static_analyzer_patterns():
    """Test pattern detection."""
    analyzer = StaticAnalyzer()
    code = """
import os
def unsafe_function():
    user_input = input()
    os.system(user_input)  # Security issue
    exec(user_input)      # Security issue
    
    # Performance issue
    data = [1, 2, 3, 4, 5]
    for i in range(len(data)):
        print(data[i])
"""
    result = analyzer.analyze_code(code)
    
    # Check for security issues
    security_findings = result.patterns_found.get('security', [])
    assert len(security_findings) >= 2  # Should find os.system and exec
    
    # Check for performance issues
    performance_findings = result.patterns_found.get('performance', [])
    assert len(performance_findings) >= 1  # Should find inefficient list iteration

def test_static_analyzer_invalid_syntax():
    """Test handling of invalid Python syntax."""
    analyzer = StaticAnalyzer()
    code = """
def invalid_function()
    this is not valid python
"""
    result = analyzer.analyze_code(code)
    assert result.complexity == -1  # Should indicate error
    assert len(result.issues) > 0  # Should have syntax error issue