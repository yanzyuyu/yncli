from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8") if (this_directory / "README.md").exists() else ""

setup(
    name="yncli",
    version="1.2.3",
    description="Autonomous Polyglot AI Coding Agent & TUI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Yanzyuyu",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "yncli": ["built_in_skills/*.md"],
    },
    install_requires=[
        "rich>=13.7.0",
        "prompt_toolkit>=3.0.40",
        "requests>=2.31.0",
        "pygments>=2.17.0",
        "beautifulsoup4>=4.12.0",
    ],
    entry_points={
        "console_scripts": [
            "yncli=yncli.main:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Code Generators",
    ],
)
