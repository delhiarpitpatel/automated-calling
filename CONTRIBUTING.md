# Contributing to Automated Calling

Thank you for considering contributing to this project! Here are some guidelines to help you get started.

## How to Contribute

### Reporting Bugs
- Use the GitHub Issues page
- Describe the bug clearly
- Include steps to reproduce
- Mention your hardware specs (CPU/RAM) and Linux distro (e.g., EndeavourOS)

### Suggesting Enhancements
- Use GitHub Issues with the "enhancement" label
- Explain why this enhancement would be useful (e.g., adding a new STT engine)
- Provide examples if possible

### Pull Requests
1. Fork the repository
2. Create a feature branch (```git checkout -b feature/amazing-feature```)
3. Make your changes
4. Commit your changes (```git commit -m 'Add amazing feature'```)
5. Push to the branch (```git push origin feature/amazing-feature```)
6. Open a Pull Request

## Development Setup

1. Clone the repository
```bash
git clone https://github.com/delhiarpitpatel/automated-calling.git
cd automated-calling
```

2. Setup virtual environment and install dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Code Style
- Follow PEP 8 Python standards
- Use meaningful variable and function names
- Add docstrings for complex logic in models/ or core/
- Keep the main async loop efficient and non-blocking

## Questions?
Feel free to open an issue for any questions about contributing.
