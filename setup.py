"""Setup configuration for Automated Calling"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = (this_directory / "requirements.txt").read_text(encoding="utf-8").splitlines()
requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]

setup(
    name="automated-calling",
    version="1.0.0",
    author="Arpit Patel",
    description="A production-ready local AI voice agent for automated calling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/delhiarpitpatel/automated-calling",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "automated-calling=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "src": ["models/voices/*.onnx", "models/voices/*.json"],
    },
)
