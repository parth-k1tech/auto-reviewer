"""CLI interface for Auto Reviewer."""

import os
import sys
import typer
from typing import Optional

from auto_reviewer.core.config import load_config
from auto_reviewer.core.reviewer import CodeReviewer
from auto_reviewer.core.git import GitHandler

app = typer.Typer()

@app.command()
def review(pr_number: int):
    """Review a specific pull request."""
    try:
        reviewer = CodeReviewer()
        result = reviewer.review_pr(pr_number)
        typer.echo(result)
    except Exception as e:
        typer.echo(f"Error reviewing PR {pr_number}: {str(e)}", err=True)
        sys.exit(1)

@app.command()
def review_local():
    """Review local changes."""
    try:
        reviewer = CodeReviewer()
        result = reviewer.review_local_changes()
        typer.echo(result)
    except Exception as e:
        typer.echo(f"Error reviewing local changes: {str(e)}", err=True)
        sys.exit(1)

@app.command()
def init():
    """Initialize Auto Reviewer in the current repository."""
    try:
        git = GitHandler()
        if not git.is_git_repo():
            typer.echo("Not a git repository. Please run this command in a git repository.")
            sys.exit(1)
        
        config_path = os.path.join(git.get_repo_root(), ".autoreviewerrc")
        if os.path.exists(config_path):
            overwrite = typer.confirm("Configuration file already exists. Overwrite?")
            if not overwrite:
                typer.echo("Initialization cancelled.")
                return

        # Create default configuration
        config = {
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
        
        with open(config_path, "w") as f:
            import yaml
            yaml.dump(config, f)
        
        typer.echo("Auto Reviewer initialized successfully!")
        
    except Exception as e:
        typer.echo(f"Error initializing Auto Reviewer: {str(e)}", err=True)
        sys.exit(1)

def main():
    """Main entry point for the CLI."""
    app()