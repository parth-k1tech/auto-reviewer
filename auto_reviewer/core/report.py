"""Report generation utilities for code reviews."""

import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class ReportGenerator:
    """Generates formatted reports from code review results."""

    def __init__(self, output_dir: Optional[str] = None):
        """Initialize report generator."""
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(self, review_results: Dict, format: str = "markdown") -> str:
        """Generate a formatted report from review results."""
        if format == "markdown":
            return self._generate_markdown_report(review_results)
        elif format == "html":
            return self._generate_html_report(review_results)
        elif format == "json":
            return self._generate_json_report(review_results)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def save_report(self, report: str, format: str = "markdown") -> Path:
        """Save the report to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"code_review_{timestamp}.{format}"
        report_path = self.output_dir / filename
        
        report_path.write_text(report)
        return report_path

    def _generate_markdown_report(self, results: Dict) -> str:
        """Generate a markdown format report."""
        report = ["# Code Review Report\n"]
        report.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Overall summary
        report.append("## Summary\n")
        report.append(f"- Files reviewed: {results.get('files_reviewed', 0)}")
        report.append(f"- Status: {results.get('status', 'unknown')}\n")
        
        # Metrics summary if available
        if 'overall_metrics' in results:
            report.append("## Overall Metrics\n")
            metrics = results['overall_metrics']
            report.append("```")
            for key, value in metrics.items():
                report.append(f"{key}: {value}")
            report.append("```\n")
        
        # Detailed results
        if 'results' in results:
            report.append("## Detailed Review\n")
            for file_review in results['results']:
                report.append(f"### {file_review['file']}\n")
                
                # File metrics
                if 'metrics' in file_review:
                    report.append("#### Metrics\n")
                    report.append("```")
                    for key, value in file_review['metrics'].__dict__.items():
                        report.append(f"{key}: {value}")
                    report.append("```\n")
                
                # Static analysis results
                if 'static_analysis' in file_review:
                    report.append("#### Static Analysis\n")
                    for issue in file_review['static_analysis'].get('issues', []):
                        report.append(f"- [{issue['severity']}] Line {issue.get('line', 'N/A')}: {issue['message']}\n")
                
                # AI review
                if 'ai_review' in file_review:
                    report.append("#### AI Review\n")
                    ai_review = file_review['ai_review']
                    
                    if 'issues' in ai_review:
                        report.append("##### Issues\n")
                        for issue in ai_review['issues']:
                            report.append(f"- {issue}\n")
                    
                    if 'suggestions' in ai_review:
                        report.append("##### Suggestions\n")
                        for suggestion in ai_review['suggestions']:
                            report.append(f"- {suggestion}\n")
        
        return "\n".join(report)

    def _generate_html_report(self, results: Dict) -> str:
        """Generate an HTML format report."""
        # Convert markdown to HTML
        markdown_content = self._generate_markdown_report(results)
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Code Review Report</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; }
                h1 { color: #2c3e50; border-bottom: 2px solid #eee; }
                h2 { color: #34495e; margin-top: 30px; }
                h3 { color: #7f8c8d; }
                .metrics { background: #f8f9fa; padding: 15px; border-radius: 5px; }
                .issue { margin: 10px 0; padding: 10px; border-left: 4px solid #e74c3c; }
                .suggestion { margin: 10px 0; padding: 10px; border-left: 4px solid #2ecc71; }
                code { background: #f8f9fa; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            {content}
        </body>
        </html>
        """
        
        # Basic markdown to HTML conversion
        html_content = markdown_content.replace("\n\n", "<br><br>")
        html_content = html_content.replace("```", "<code>")
        
        return html_template.format(content=html_content)

    def _generate_json_report(self, results: Dict) -> str:
        """Generate a JSON format report."""
        # Convert any non-serializable objects to strings
        def serialize(obj):
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            return str(obj)
        
        return json.dumps(results, default=serialize, indent=2)