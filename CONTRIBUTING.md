# Contributing to Kuwait Social AI - DigitalOcean Hosting

Thank you for your interest in contributing to this project! This document provides guidelines for contributions.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Issues

1. Check existing issues to avoid duplicates
2. Use clear, descriptive titles
3. Provide detailed information about the problem
4. Include steps to reproduce if applicable

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Run tests (`./test-scripts.sh`)
5. Commit with clear messages
6. Push to your fork
7. Create a Pull Request

### Coding Standards

#### Bash Scripts
- Use `set -euo pipefail` for error handling
- Follow shellcheck recommendations
- Add comments for complex logic
- Use meaningful variable names
- Validate all user inputs

#### Security
- Never commit secrets or credentials
- Use environment variables for sensitive data
- Follow principle of least privilege
- Implement proper access controls

### Testing

All changes must pass:
- Script syntax validation
- Functional tests
- Security checks
- GitHub Actions CI

Run tests locally:
```bash
./test-scripts.sh
./validate-environment.sh
```

### Documentation

- Update README.md for user-facing changes
- Update inline comments for code changes
- Include examples where helpful
- Keep documentation concise and clear

## Review Process

1. All PRs are automatically reviewed by CodeRabbit
2. Address any issues raised by automated checks
3. Human review for final approval
4. Merge after all checks pass

## Questions?

Feel free to open an issue for any questions about contributing.