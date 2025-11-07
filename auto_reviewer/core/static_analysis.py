"""Static code analysis utilities."""

import ast
import re
import math
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

@dataclass
class StaticAnalysisResult:
    """Results of static code analysis."""
    complexity: int
    maintainability: float
    cognitive_complexity: int
    issues: List[Dict]
    patterns_found: Dict[str, List[Tuple[int, str]]]

class StaticAnalyzer:
    """Static code analyzer for Python code."""

    def __init__(self):
        """Initialize the static analyzer."""
        self._setup_patterns()

    def _setup_patterns(self):
        """Setup analysis patterns."""
        self.patterns = {
            'security': {
                'eval_exec': (r'(eval|exec)\s*\(', 'Use of eval() or exec()'),
                'shell_injection': (r'(os\.system|subprocess\.call)', 'Potential shell injection'),
                'sql_injection': (r'execute\s*\(\s*[\'"][^\']*%[^\']*[\'"]\s*%', 'Potential SQL injection'),
            },
            'performance': {
                'list_in_loop': (r'for\s+\w+\s+in\s+range\(len\(', 'Inefficient list iteration'),
                'nested_loops': (r'for.*:\s*\n\s*for.*:', 'Nested loops detected'),
            },
            'maintainability': {
                'long_function': (r'def\s+\w+[^}]*\}', 'Long function definition'),
                'complex_condition': (r'if.*and.*or.*:', 'Complex conditional'),
            }
        }

    def analyze_code(self, code: str) -> StaticAnalysisResult:
        """Perform static analysis on code."""
        try:
            tree = ast.parse(code)
            
            # Calculate metrics
            complexity = self._calculate_complexity(tree)
            maintainability = self._calculate_maintainability(code)
            cognitive = self._calculate_cognitive_complexity(tree)
            
            # Find patterns
            patterns_found = self._find_patterns(code)
            
            # Collect issues
            issues = self._collect_issues(tree, patterns_found)
            
            return StaticAnalysisResult(
                complexity=complexity,
                maintainability=maintainability,
                cognitive_complexity=cognitive,
                issues=issues,
                patterns_found=patterns_found
            )
            
        except SyntaxError:
            return StaticAnalysisResult(
                complexity=-1,
                maintainability=-1,
                cognitive_complexity=-1,
                issues=[{"severity": "error", "message": "Invalid Python syntax"}],
                patterns_found={}
            )

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try,
                              ast.ExceptHandler, ast.With, ast.Assert,
                              ast.AsyncFor, ast.AsyncWith)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity

    def _calculate_maintainability(self, code: str) -> float:
        """Calculate maintainability index."""
        lines = code.split('\n')
        loc = len([line for line in lines if line.strip()])
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        
        # Halstead volume approximation
        unique_operators = len(set(re.findall(r'[+\-*/%=<>!&|^~]', code)))
        unique_operands = len(set(re.findall(r'\b[a-zA-Z_]\w*\b', code)))
        
        # Basic maintainability index calculation
        volume = (unique_operators + unique_operands) * math.log(loc if loc > 0 else 1)
        maintainability = 171 - 5.2 * math.log(volume) - 0.23 * self._calculate_complexity(ast.parse(code))
        
        # Adjust based on comment ratio
        comment_ratio = comment_lines / loc if loc > 0 else 0
        maintainability += 50 * comment_ratio
        
        return max(0, min(100, maintainability))

    def _calculate_cognitive_complexity(self, tree: ast.AST) -> int:
        """Calculate cognitive complexity."""
        class CognitiveComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.complexity = 0
                self.nesting = 0

            def visit_If(self, node):
                self.complexity += (1 + self.nesting)
                self.nesting += 1
                self.generic_visit(node)
                self.nesting -= 1

            def visit_While(self, node):
                self.complexity += (1 + self.nesting)
                self.nesting += 1
                self.generic_visit(node)
                self.nesting -= 1

            def visit_For(self, node):
                self.complexity += (1 + self.nesting)
                self.nesting += 1
                self.generic_visit(node)
                self.nesting -= 1

            def visit_Try(self, node):
                self.complexity += (1 + self.nesting)
                self.nesting += 1
                self.generic_visit(node)
                self.nesting -= 1

        visitor = CognitiveComplexityVisitor()
        visitor.visit(tree)
        return visitor.complexity

    def _find_patterns(self, code: str) -> Dict[str, List[Tuple[int, str]]]:
        """Find pattern matches in code."""
        results = {}
        
        for category, patterns in self.patterns.items():
            category_results = []
            for name, (pattern, description) in patterns.items():
                for match in re.finditer(pattern, code):
                    line_no = code.count('\n', 0, match.start()) + 1
                    category_results.append((line_no, description))
            if category_results:
                results[category] = category_results
                
        return results

    def _collect_issues(self, tree: ast.AST, patterns_found: Dict[str, List[Tuple[int, str]]]) -> List[Dict]:
        """Collect all identified issues."""
        issues = []
        
        # Add pattern-based issues
        for category, findings in patterns_found.items():
            for line_no, description in findings:
                issues.append({
                    "line": line_no,
                    "category": category,
                    "severity": "high" if category == "security" else "medium",
                    "message": description
                })
        
        # Add complexity-based issues
        complexity = self._calculate_complexity(tree)
        if complexity > 10:
            issues.append({
                "line": None,
                "category": "maintainability",
                "severity": "medium",
                "message": f"High cyclomatic complexity: {complexity}"
            })
        
        return issues