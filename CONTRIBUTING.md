# 🤝 Contributing Guide

First off, thank you for considering contributing to **Autonomous AI Agent**! 🎉

Whether you're fixing a bug, improving documentation, optimizing performance, or proposing a new feature, your contributions are greatly appreciated.

Please take a few minutes to read this guide before submitting your contribution.

---

# 📚 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Ways to Contribute](#-ways-to-contribute)
- [Development Setup](#-development-setup)
- [Branch Naming](#-branch-naming)
- [Coding Standards](#-coding-standards)
- [Testing](#-testing)
- [Commit Messages](#-commit-messages)
- [Pull Requests](#-pull-requests)
- [Documentation](#-documentation)
- [Reporting Bugs](#-reporting-bugs)
- [Suggesting Features](#-suggesting-features)

---

# 📜 Code of Conduct

By participating in this project, you agree to be respectful, constructive, and collaborative.

Please:

- Be respectful.
- Welcome new contributors.
- Give constructive feedback.
- Focus on improving the project.

---

# 🚀 Ways to Contribute

There are many ways to contribute, including:

- Fixing bugs
- Improving documentation
- Refactoring existing code
- Improving performance
- Writing tests
- Suggesting new features
- Improving prompts
- Optimizing AI workflows
- Enhancing Docker support
- Improving API documentation

Every contribution is valuable.

---

# 🛠️ Development Setup

## 1. Fork the Repository

Click the **Fork** button on GitHub.

---

## 2. Clone Your Fork

```bash
git clone https://github.com/<your-username>/autonomous-ai-agent.git
cd autonomous-ai-agent
```

---

## 3. Create a Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Configure Environment Variables

```bash
cp .env.example .env
```

Add your Google Gemini API key to the `.env` file before running the application.

---

## 6. Run the Application

```bash
uvicorn app:app --reload
```

---

# 🌿 Branch Naming

Please create a dedicated branch for every contribution.

Examples:

```text
feature/add-pdf-export
feature/improve-reflection

bugfix/fix-docx-generation
bugfix/fix-validation

docs/update-readme

refactor/executor

test/add-planner-tests
```

Avoid committing directly to the `main` branch.

---

# 💻 Coding Standards

Please follow these guidelines:

- Follow the existing project structure.
- Keep functions focused on a single responsibility.
- Use meaningful variable and function names.
- Write clear docstrings where appropriate.
- Prefer readability over clever code.
- Keep code modular and maintainable.
- Remove unused imports and dead code.

---

# 🧪 Testing

Before submitting your contribution, ensure all tests pass.

Run:

```bash
pytest
```

If you're adding a new feature:

- Add corresponding unit tests.
- Ensure existing tests continue to pass.
- Do not introduce breaking changes without discussion.

---

# 📝 Commit Messages

This project follows the **Conventional Commits** specification.

Examples:

```text
feat: add PDF document export

fix: resolve reflection loop issue

docs: improve API documentation

refactor: simplify execution pipeline

test: add planner unit tests

ci: add GitHub Actions workflow
```

Write clear and descriptive commit messages.

---

# 🔀 Pull Requests

Before opening a Pull Request, please ensure:

- The project builds successfully.
- All tests pass.
- Documentation is updated if needed.
- Your branch is up to date with `main`.
- The Pull Request has a clear description.

Small, focused Pull Requests are preferred over large changes.

---

# 📚 Documentation

If your contribution changes project behavior, please update:

- README.md
- API documentation
- Code comments (if necessary)
- Relevant documentation files

Keeping documentation up to date is an important part of every contribution.

---

# 🐞 Reporting Bugs

When reporting a bug, please include:

- Operating system
- Python version
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages or logs
- Screenshots (if applicable)

Providing detailed information helps reproduce and resolve issues more quickly.

---

# 💡 Suggesting Features

Feature requests are welcome.

When proposing a feature, please explain:

- The problem you're trying to solve
- Your proposed solution
- Why it would benefit the project
- Any alternative approaches you considered

---

# ❤️ Thank You

Thank you for helping improve **Autonomous AI Agent**.

Every contribution—whether it's code, documentation, testing, or feedback—helps make the project better for everyone.

Happy coding! 🚀
