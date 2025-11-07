"""Git operations handler for Auto Reviewer."""

import os
from git import Repo
from typing import List, Dict

class GitHandler:
    """Handler for Git operations."""
    
    def __init__(self, repo_path: str = None):
        """Initialize GitHandler with repository path."""
        self.repo_path = repo_path or os.getcwd()
        self._repo = None

    @property
    def repo(self) -> Repo:
        """Get the Git repository."""
        if not self._repo:
            self._repo = Repo(self.repo_path)
        return self._repo

    def is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        try:
            _ = self.repo
            return True
        except:
            return False

    def get_repo_root(self) -> str:
        """Get the root directory of the git repository."""
        return self.repo.git.rev_parse("--show-toplevel")

    def get_current_branch(self) -> str:
        """Get the name of the current branch."""
        return self.repo.active_branch.name

    def get_changed_files(self) -> List[str]:
        """Get list of files changed in the current working directory."""
        return [item.a_path for item in self.repo.index.diff(None)]

    def get_diff_for_file(self, file_path: str) -> str:
        """Get the diff for a specific file."""
        return self.repo.git.diff(file_path)

    def get_file_content(self, file_path: str, ref: str = 'HEAD') -> str:
        """Get content of a file at a specific reference."""
        try:
            return self.repo.git.show(f'{ref}:{file_path}')
        except:
            with open(file_path, 'r') as f:
                return f.read()

    def get_commit_history(self, file_path: str, max_count: int = 10) -> List[Dict]:
        """Get commit history for a specific file."""
        commits = []
        for commit in self.repo.iter_commits(paths=file_path, max_count=max_count):
            commits.append({
                'hash': commit.hexsha,
                'author': commit.author.name,
                'message': commit.message,
                'date': commit.committed_datetime.isoformat()
            })
        return commits