# Auto Reviewer

An AI-powered local code reviewer for pull requests. Get instant, intelligent feedback on your code changes before submitting them for review.

## Features

- AI-Powered Analysis: Leverages advanced language models for code review
- Pull Request Analysis: Examines changes, context, and potential impacts
- Code Quality Metrics: Tracks code quality, complexity, and best practices
- Local Processing: Reviews code locally before pushing to remote
- Customizable Rules: Define custom review rules and preferences
- Detailed Reports: Generate comprehensive review reports

## Installation

```bash
pip install auto-reviewer
```

## Quick Start

1. Set up your environment variables:
```bash
GITHUB_TOKEN=your_github_token
OPENAI_API_KEY=your_openai_api_key
```

2. Start Auto Reviewer:
```bash
auto-reviewer
```

3. Configure your repository:
```bash
auto-reviewer init
```

## Usage

Review a pull request:
```bash
auto-reviewer review <pr-number>
```

Review local changes:
```bash
auto-reviewer review-local
```

## Configuration

Create `.autoreviewerrc` in your project root:
```yaml
rules:
  max_file_changes: 50
  complexity_threshold: 15
  required_tests: true
ignore_patterns:
  - "*.md"
  - "*.json"
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
