# Contributing to Automated Calling# Contributing to Automated Calling



Thank you for your interest in contributing! We welcome contributions of all types.Thank you for considering contributing to this project! Here are some guidelines to help you get started.



## Getting Started## How to Contribute



1. **Fork** the repository### Reporting Bugs

2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/automated-calling.git`- Use the GitHub Issues page

3. **Create a branch**: `git checkout -b feature/your-feature-name`- Describe the bug clearly

4. **Make changes** and test them- Include steps to reproduce

5. **Commit** with clear messages: `git commit -m "Add feature: description"`- Mention your hardware specs (CPU/RAM) and Linux distro (e.g., EndeavourOS)

6. **Push** to your fork: `git push origin feature/your-feature-name`

7. **Open a Pull Request** with a clear title and description### Suggesting Enhancements

- Use GitHub Issues with the "enhancement" label

## Code Guidelines- Explain why this enhancement would be useful (e.g., adding a new STT engine)

- Provide examples if possible

### Python Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)### Pull Requests

- Use type hints for function signatures1. Fork the repository

- Write docstrings (Google style) for all functions and classes2. Create a feature branch (```git checkout -b feature/amazing-feature```)

- Use meaningful variable names3. Make your changes

4. Commit your changes (```git commit -m 'Add amazing feature'```)

### Format & Quality5. Push to the branch (```git push origin feature/amazing-feature```)

```bash6. Open a Pull Request

# Format code

black .## Development Setup



# Check style1. Clone the repository

flake8 .```bash

git clone https://github.com/delhiarpitpatel/automated-calling.git

# Type checkingcd automated-calling

mypy .```



# Run tests2. Setup virtual environment and install dependencies

pytest tests/```bash

```python -m venv venv

source venv/bin/activate

## Types of Contributionspip install -r requirements.txt

```

### Bug Reports

- Use GitHub Issues with the `bug` label## Code Style

- Provide steps to reproduce- Follow PEP 8 Python standards

- Include system info (OS, Python version, hardware)- Use meaningful variable and function names

- Attach logs if applicable- Add docstrings for complex logic in models/ or core/

- Keep the main async loop efficient and non-blocking

### Feature Requests

- Use GitHub Issues with the `enhancement` label## Questions?

- Describe the feature and its use caseFeel free to open an issue for any questions about contributing.

- Provide examples if possible

### Code Contributions
- Small fixes (docs, typos) are always welcome
- For larger features, open an issue first for discussion
- Write tests for new functionality
- Update documentation as needed

### Documentation
- Fix typos and improve clarity
- Add examples and use cases
- Improve installation instructions
- Document edge cases

## Areas We Need Help With

- 🔧 Raspberry Pi / ARM support
- 🪟 Windows GPU optimization
- 📱 Mobile app integration
- 🌍 Additional language support
- 📊 Performance benchmarking
- 🧪 Test coverage improvements

## Pull Request Process

1. Ensure all tests pass: `pytest tests/`
2. Update documentation if needed
3. Add yourself to the contributors list (if desired)
4. Respond to code review feedback
5. Squash commits before merging (if requested)

## Questions?

- Open a GitHub Discussion for questions
- Check existing issues before posting
- Join our community for real-time chat

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make Automated Calling better! 🎉
