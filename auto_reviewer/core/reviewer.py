"""Core code review functionality with advanced analysis capabilities."""

import os
import ast
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel

from auto_reviewer.core.git import GitHandler
from auto_reviewer.core.config import load_config

@dataclass
class CodeMetrics:
    """Code quality metrics."""
    cyclomatic_complexity: int
    maintainability_index: float
    cognitive_complexity: int
    lines_of_code: int
    comment_ratio: float

class ReviewComment(BaseModel):
    """Model for code review comments."""
    line_number: int
    severity: str
    category: str
    message: str
    suggestion: Optional[str] = None
    confidence: float
    context: str

class CodeReviewer:
    """Advanced code reviewer with static analysis and AI integration."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize CodeReviewer with configuration."""
        self.config = load_config(config_path)
        self.git = GitHandler()
        self.ai_client = OpenAI()
        self._setup_analysis_patterns()

    def _setup_analysis_patterns(self):
        """Setup patterns for code analysis."""
        self.patterns = {
            'security': [
                r'exec\s*\(',
                r'eval\s*\(',
                r'subprocess\.call',
                r'os\.system',
                r'input\s*\(',
            ],
            'performance': [
                r'for\s+\w+\s+in\s+range\(len\(',
                r'\.copy\(\)',
                r'while\s+True:',
            ],
            'best_practices': [
                r'global\s+',
                r'except:',
                r'print\s*\(',
            ]
        }

    async def review_pr(self, pr_number: int) -> Dict:
        """Review a GitHub pull request with detailed analysis."""
        try:
            pr_info = await self.git.get_pr_info(pr_number)
            changed_files = pr_info['changed_files']
            
            # Parallel review of changed files
            with ThreadPoolExecutor() as executor:
                review_tasks = [
                    executor.submit(self._analyze_file_changes, file)
                    for file in changed_files
                ]
                reviews = [task.result() for task in review_tasks]

            # Aggregate insights
            overall_analysis = self._aggregate_reviews(reviews)
            
            return {
                "status": "success",
                "pr_number": pr_number,
                "reviews": reviews,
                "summary": overall_analysis,
                "recommendations": self._generate_recommendations(overall_analysis)
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def review_local_changes(self) -> Dict:
        """Review local changes with comprehensive analysis."""
        try:
            changed_files = self.git.get_changed_files()
            if not changed_files:
                return {"status": "success", "message": "No changes to review"}

            reviews = []
            metrics = []
            
            for file_path in changed_files:
                if self._should_ignore_file(file_path):
                    continue
                
                # Get file changes and context
                diff = self.git.get_diff_for_file(file_path)
                current_content = self.git.get_file_content(file_path)
                
                # Comprehensive analysis
                file_metrics = self._calculate_metrics(current_content)
                static_analysis = self._perform_static_analysis(current_content)
                ai_review = self._get_ai_review(file_path, diff, current_content)
                
                review = {
                    "file": file_path,
                    "metrics": file_metrics,
                    "static_analysis": static_analysis,
                    "ai_review": ai_review,
                    "suggestions": self._generate_suggestions(static_analysis, file_metrics)
                }
                
                reviews.append(review)
                metrics.append(file_metrics)

            return {
                "status": "success",
                "files_reviewed": len(reviews),
                "results": reviews,
                "overall_metrics": self._aggregate_metrics(metrics),
                "summary": self._generate_review_summary(reviews)
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _calculate_metrics(self, content: str) -> CodeMetrics:
        """Calculate code quality metrics."""
        try:
            tree = ast.parse(content)
            
            # Calculate cyclomatic complexity
            complexity = self._calculate_cyclomatic_complexity(tree)
            
            # Calculate maintainability index
            maintainability = self._calculate_maintainability_index(content)
            
            # Calculate cognitive complexity
            cognitive = self._calculate_cognitive_complexity(tree)
            
            # Calculate lines of code and comment ratio
            loc, comment_ratio = self._calculate_loc_metrics(content)
            
            return CodeMetrics(
                cyclomatic_complexity=complexity,
                maintainability_index=maintainability,
                cognitive_complexity=cognitive,
                lines_of_code=loc,
                comment_ratio=comment_ratio
            )
        
        except Exception:
            return CodeMetrics(
                cyclomatic_complexity=-1,
                maintainability_index=-1,
                cognitive_complexity=-1,
                lines_of_code=-1,
                comment_ratio=-1
            )

    def _get_ai_review(self, file_path: str, diff: str, content: str) -> Dict:
        """Get AI-powered code review."""
        try:
            # Prepare context-aware prompt
            prompt = self._build_review_prompt(file_path, diff, content)
            
            # Get AI analysis
            response = self.ai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert code reviewer with deep knowledge of software engineering principles,
                        design patterns, and best practices. Focus on:
                        1. Code quality and maintainability
                        2. Security vulnerabilities
                        3. Performance optimizations
                        4. Design pattern improvements
                        5. Testing suggestions
                        Provide specific, actionable feedback with code examples where relevant."""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            review = response.choices[0].message.content
            
            # Structure the AI response
            return self._structure_ai_review(review)
        
        except Exception as e:
            return {"error": str(e)}

    def _build_review_prompt(self, file_path: str, diff: str, content: str) -> str:
        """Build a detailed prompt for AI review."""
        return f"""Please review the following code changes:

File: {file_path}

Diff:
{diff}

Current file content:
{content}

Please analyze the code for:
1. Code quality issues
2. Potential security vulnerabilities
3. Performance improvements
4. Design pattern violations
5. Testing gaps

For each issue found, provide:
- Specific location (line number)
- Severity (high/medium/low)
- Detailed explanation
- Concrete suggestion for improvement
- Code example if applicable

Focus on providing actionable, specific feedback that will help improve the code quality."""

    def _structure_ai_review(self, review: str) -> Dict:
        """Structure the AI review response."""
        # Extract and categorize feedback
        issues = []
        suggestions = []
        current_section = None
        
        for line in review.split('\n'):
            if line.strip().lower().startswith(('issue:', 'suggestion:')):
                current_section = 'issue' if 'issue:' in line.lower() else 'suggestion'
                issues.append(line) if current_section == 'issue' else suggestions.append(line)
            elif line.strip() and current_section:
                if current_section == 'issue':
                    issues[-1] += '\n' + line
                else:
                    suggestions[-1] += '\n' + line

        return {
            "issues": [self._parse_issue(issue) for issue in issues],
            "suggestions": [self._parse_suggestion(sugg) for sugg in suggestions],
            "review_score": self._calculate_review_score(issues, suggestions)
        }

    def _should_ignore_file(self, file_path: str) -> bool:
        """Check if file should be ignored based on configuration."""
        import fnmatch
        
        # Get patterns from config or use defaults
        patterns = self.config.get('ignore_patterns', [
            '*.md',
            '*.json',
            '*.yaml',
            '*.lock',
            '**/tests/*',
            '**/migrations/*',
            '**/node_modules/*'
        ])
        
        # Check if file matches any ignore pattern
        return any(fnmatch.fnmatch(file_path, pattern) for pattern in patterns)