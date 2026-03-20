# Proposed Repository Structure for Automated Calling

## Current vs. Proposed Structure

### Current Structure
```
automated-calling/
├── core/                          ← Source code mixed with docs
├── models/
├── integrations/
├── main.py
├── README.md                      ← Root-level documentation
├── CONTRIBUTING.md
├── QUICKSTART.md
├── requirements.txt
└── [Other doc files]
```

### Proposed Structure (Following large-mysql-migrator pattern)
```
automated-calling/
├── src/                           ← All source code
│   ├── core/
│   │   ├── __init__.py
│   │   ├── audio_io.py
│   │   ├── config.py
│   │   └── state_manager.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── vad.py
│   │   ├── stt.py
│   │   ├── llm.py
│   │   └── tts.py
│   ├── integrations/
│   │   ├── __init__.py
│   │   └── n8n_client.py
│   └── main.py
│
├── docs/                          ← All documentation
│   ├── _config.yml                ← Jekyll configuration
│   ├── _layouts/
│   │   ├── default.html
│   │   └── with-sidebar.html
│   ├── _includes/
│   │   ├── sidebar.html
│   │   └── head-custom.html
│   ├── assets/
│   │   └── css/
│   │       └── custom.css
│   ├── index.md                   ← Main docs landing page
│   ├── quickstart.md              ← Setup guide
│   ├── architecture.md            ← Technical architecture
│   ├── hardware.md                ← Hardware requirements
│   ├── configuration.md           ← Configuration guide
│   ├── models/
│   │   ├── overview.md
│   │   ├── vad.md                 ← VAD deep dive
│   │   ├── stt.md
│   │   ├── llm.md
│   │   └── tts.md
│   ├── engineering/
│   │   ├── fd2-hijacking.md       ← Glue engineering docs
│   │   ├── bluetooth-audio.md
│   │   ├── greedy-decoding.md
│   │   ├── context-pruning.md
│   │   └── thread-safety.md
│   ├── integration/
│   │   ├── n8n.md
│   │   └── webhooks.md
│   ├── api/
│   │   └── reference.md
│   ├── troubleshooting.md
│   └── examples.md
│
├── tests/                         ← Test suite
│   ├── __init__.py
│   ├── test_vad.py
│   ├── test_stt.py
│   ├── test_llm.py
│   ├── test_tts.py
│   ├── test_audio_io.py
│   └── fixtures/
│       └── sample_audio.wav
│
├── examples/                      ← Example usage
│   ├── basic_agent.py
│   ├── with_n8n.py
│   └── custom_llm.py
│
├── .github/workflows/             ← GitHub Actions
│   ├── tests.yml
│   ├── docs.yml
│   └── lint.yml
│
├── .env.example
├── .gitignore
├── LICENSE
├── README.md                      ← Root-level README (links to docs)
├── CONTRIBUTING.md                ← Contributing guidelines
├── requirements.txt               ← Production deps
├── requirements-dev.txt           ← Development deps
├── pyproject.toml                 ← Python project metadata
└── setup.py                       ← Package installation
```

---

## Advantages of This Structure

### ✅ **Separation of Concerns**
- `src/` contains ONLY executable code
- `docs/` contains ONLY documentation
- Clean git history (easy to track code changes)
- Easy to generate docs separately

### ✅ **Professional Organization**
- Matches industry standards (large-mysql-migrator, Django, FastAPI, etc.)
- GitHub automatically builds Jekyll docs from `/docs` folder
- Easier for contributors to find code vs. documentation

### ✅ **Scalability**
- As project grows, documentation doesn't clutter source
- Easy to add test suite without mixing with source
- Examples can be in separate folder

### ✅ **GitHub Pages Compatibility**
- GitHub automatically deploys `/docs` as website
- Jekyll configuration in `docs/_config.yml`
- Free hosting, automatic HTTPS, custom domain support

### ✅ **CI/CD Ready**
- Separate workflows for tests, docs, linting
- Tests run against `/src` only
- Docs build independently
- Package builds from clean source

---

## Should We Keep Docs and Src in Same Repo?

### **YES ✅ - Recommended**

**Reasons**:
1. **Single Source of Truth** - Code and docs stay in sync
2. **Easier Maintenance** - One PR updates code + docs together
3. **GitHub Pages** - Free docs hosting from `/docs` folder
4. **Discoverability** - Users find docs and code together
5. **CI/CD** - Validate docs build with every code change
6. **Community** - Contributors fix docs + code in same PR

**Real-world Examples**:
- Django ✅ (docs/ in main repo)
- FastAPI ✅ (docs/ in main repo)
- SQLAlchemy ✅ (docs/ in main repo)
- large-mysql-migrator ✅ (docs/ in main repo)
- Kubernetes ✅ (docs/ in main repo)

### What About Separate Repos?

**ONLY if**:
- Documentation is MASSIVE (500+ pages)
- Separate team manages docs
- Documentation versioning is complex
- Docs need different build tools

**For your project**: Single repo is perfect ✅

---

## Migration Path

### Step 1: Create new directory structure (No code moves yet)
```bash
mkdir -p src/core src/models src/integrations
mkdir -p docs/{_layouts,_includes,assets/css,models,engineering,integration,api}
mkdir -p tests/fixtures
mkdir -p examples
```

### Step 2: Move source code to `src/`
```bash
mv core/* src/core/
mv models/* src/models/
mv integrations/* src/integrations/
mv main.py src/
```

### Step 3: Reorganize documentation to `docs/`
```bash
# Create index structure
docs/index.md              ← Main landing page
docs/quickstart.md         ← From QUICKSTART.md
docs/configuration.md      ← From .env.example
docs/architecture.md       ← From README_refactored.md (architecture section)

# Create model-specific docs
docs/models/vad.md         ← From models/vad.py docstring
docs/models/stt.md         ← From models/stt.py docstring
docs/models/llm.md         ← From models/llm.py docstring
docs/models/tts.md         ← From models/tts.py docstring

# Create engineering docs
docs/engineering/fd2-hijacking.md          ← From models/vad.py
docs/engineering/bluetooth-audio.md        ← From models/tts.py
docs/engineering/greedy-decoding.md        ← From models/stt.py
docs/engineering/context-pruning.md        ← From models/llm.py
```

### Step 4: Create Jekyll configuration
```yaml
# docs/_config.yml
title: Automated Calling
description: Local AI Voice Agent for AMD APU
theme: minima
plugins:
  - jekyll-seo-tag
  - jekyll-sitemap
```

### Step 5: Update imports in code
```python
# OLD
from src.core.config import config

# NEW (if installing as package)
from automated_calling.core.config import config

# OR (if running from root with src in PYTHONPATH)
from src.core.config import config
```

### Step 6: Create `pyproject.toml` for packaging
```toml
[project]
name = "automated-calling"
version = "1.0.0"
description = "Local AI Voice Agent for AMD APU"
requires-python = ">=3.10"
dependencies = [
    "sounddevice==0.4.6",
    "numpy==2.4.2",
    # ... etc
]
```

---

## Updated Root-Level Files

### `README.md` (at project root)
```markdown
# Automated Calling: Local AI Voice Agent

> A high-performance, end-to-end AI voice agent designed to run entirely on local hardware (optimized for AMD APU / 8GB RAM).

## Quick Links

- **📚 [Full Documentation](docs/index.md)**
- **🚀 [Quick Start](docs/quickstart.md)**
- **🏗️ [Architecture](docs/architecture.md)**
- **🤖 [Models Overview](docs/models/overview.md)**
- **📖 [Contributing](CONTRIBUTING.md)**

## Features

- Full Local Execution
- CPU Optimized
- Low Latency (<2 seconds)
- n8n Integration

## Installation

```bash
pip install -r requirements.txt
python src/main.py
```

See [Quick Start Guide](docs/quickstart.md) for detailed setup.

## License

MIT - See [LICENSE](LICENSE)
```

---

## File Mapping (What Gets Moved Where)

| Current File | New Location | Purpose |
|---|---|---|
| `main.py` | `src/main.py` | Source code |
| `core/*.py` | `src/core/*.py` | Source code |
| `models/*.py` | `src/models/*.py` | Source code |
| `integrations/*.py` | `src/integrations/*.py` | Source code |
| `QUICKSTART.md` | `docs/quickstart.md` | User guide |
| `README_refactored.md` | `docs/index.md` + `docs/architecture.md` | Main docs |
| `CONTRIBUTING_refactored.md` | `CONTRIBUTING.md` | Contributing |
| `.env.example` | `docs/configuration.md` | Config reference |
| `models/vad.py` docstring | `docs/models/vad.md` | Model docs |
| `REFACTORING_SUMMARY.md` | Deprecated (archived) | Historical |

---

## GitHub Pages Setup

After reorganizing:

1. Go to repo Settings → Pages
2. Set source to `/docs` folder
3. Choose Jekyll theme (minima recommended)
4. Site auto-publishes at `https://delhiarpitpatel.github.io/automated-calling`

---

## Benefits Summary

| Aspect | Current | Proposed |
|--------|---------|----------|
| Code Location | Mixed | Organized in `src/` |
| Documentation | Mixed | Organized in `docs/` |
| GitHub Pages | Not set up | Ready to enable |
| Testing | None | Can add to `tests/` |
| Examples | None | Can add to `examples/` |
| Professionalism | Good | Excellent |
| Contributor UX | Good | Better |
| Scalability | OK | Excellent |

---

## My Recommendation

✅ **YES**, reorganize to follow the `large-mysql-migrator` structure:

1. **Cleaner codebase** - No documentation clutter in source
2. **Professional appearance** - Matches industry standards
3. **GitHub Pages ready** - Free automatic documentation hosting
4. **Easier contributions** - Clear separation helps new contributors
5. **Better maintainability** - Different tools for docs vs. code
6. **Scalable** - Easy to add tests, examples, multiple versions

The migration is straightforward since you don't have production dependencies to worry about. You can do it all at once or gradually.

**Would you like me to proceed with creating the reorganized structure?** I can:

1. Create the new directory structure
2. Move files to appropriate locations
3. Update all imports
4. Create Jekyll configuration
5. Generate organized documentation
6. Create `setup.py` and `pyproject.toml`

Let me know if you'd like to go ahead! 🚀
