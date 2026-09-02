import os
from pathlib import Path
from typing import Dict, List, Any


LANGUAGE_SIGNATURES = {
    "python": {
        "files": ["pyproject.toml", "requirements.txt", "setup.py", "Pipfile", "poetry.lock", "tox.ini", ".flake8", "ruff.toml"],
        "extensions": [".py", ".pyi", ".ipynb"],
        "name": "Python",
        "idioms": [
            "Use PEP 8 naming conventions and explicit type hints (typing / PEP 484).",
            "Prefer standard library and modern idioms (dataclasses, pydantic, path objects from pathlib).",
            "Use async/await with asyncio when doing I/O-bound operations.",
            "Write modular, testable functions with pytest docstrings and robust exception handling."
        ],
        "syntax_command": "python -m py_compile {file}"
    },
    "typescript": {
        "files": ["tsconfig.json", "package.json"],
        "extensions": [".ts", ".tsx"],
        "name": "TypeScript / JavaScript",
        "idioms": [
            "Use strict TypeScript types without implicit 'any'. Use type interfaces and generics where appropriate.",
            "Prefer ES modules (import/export) and modern ES2022+ features (optional chaining, nullish coalescing).",
            "Write clean functional or class-based components/services with comprehensive error boundaries.",
            "Ensure proper promise rejection handling and async/await."
        ],
        "syntax_command": "npx tsc --noEmit"
    },
    "javascript": {
        "files": ["package.json", "jsconfig.json"],
        "extensions": [".js", ".jsx", ".mjs", ".cjs"],
        "name": "JavaScript (Node/Browser)",
        "idioms": [
            "Write modern ES6+ JavaScript with const/let, arrow functions, and destructuring.",
            "Use modern async/await patterns and clean error handling.",
            "Maintain clean separation of concerns and avoid global state pollution."
        ],
        "syntax_command": "node --check {file}"
    },
    "rust": {
        "files": ["Cargo.toml", "Cargo.lock"],
        "extensions": [".rs"],
        "name": "Rust",
        "idioms": [
            "Respect Rust ownership, borrowing rules, and lifetimes. Minimize unnecessary cloning.",
            "Use idiomatic Result<T, E> and Option<T> pattern matching or the ? operator for error propagation.",
            "Leverage traits, zero-cost abstractions, and cargo clippy conventions.",
            "Write unit tests inside #[cfg(test)] modules."
        ],
        "syntax_command": "cargo check"
    },
    "golang": {
        "files": ["go.mod", "go.sum"],
        "extensions": [".go"],
        "name": "Go (Golang)",
        "idioms": [
            "Follow standard Go formatting (gofmt) and naming conventions (camelCase/PascalCase).",
            "Handle errors explicitly with 'if err != nil' right after calls.",
            "Use goroutines and channels carefully, preventing goroutine leaks with context.Context.",
            "Keep packages focused and interfaces small and composable."
        ],
        "syntax_command": "go vet ./..."
    },
    "cpp": {
        "files": ["CMakeLists.txt", "Makefile", ".clang-format"],
        "extensions": [".cpp", ".cc", ".cxx", ".hpp", ".h"],
        "name": "C / C++",
        "idioms": [
            "Use modern C++ (C++17/20/23) idioms: RAII, smart pointers (std::unique_ptr, std::shared_ptr).",
            "Avoid raw owning pointers and manual memory allocation (new/delete).",
            "Use const references for non-primitive function arguments and constexpr for compile-time evaluation."
        ],
        "syntax_command": "g++ -fsyntax-only {file}"
    },
    "csharp": {
        "files": ["*.csproj", "*.sln", "NuGet.Config"],
        "extensions": [".cs"],
        "name": "C# (.NET)",
        "idioms": [
            "Use modern C# (C# 11/12) features: top-level statements, record types, pattern matching, nullable reference types.",
            "Follow standard .NET PascalCase/camelCase naming conventions and Dependency Injection patterns.",
            "Leverage async/await with Task and LINQ for declarative data querying."
        ],
        "syntax_command": "dotnet build --no-incremental"
    },
    "java": {
        "files": ["pom.xml", "build.gradle", "build.gradle.kts"],
        "extensions": [".java", ".kt"],
        "name": "Java / Kotlin",
        "idioms": [
            "Use modern Java (17/21) records, sealed classes, pattern matching, and streams.",
            "Follow SOLID principles, clear package hierarchies, and Spring/Jakarta idioms if applicable.",
            "Use Lombok or record classes to reduce boilerplate."
        ],
        "syntax_command": "javac {file}"
    },
    "php": {
        "files": ["composer.json", "composer.lock", "artisan"],
        "extensions": [".php"],
        "name": "PHP",
        "idioms": [
            "Always declare strict types: `declare(strict_types=1);` at the top of PHP files.",
            "Use modern PHP 8.2+ features (enums, readonly properties, constructor property promotion, match expressions).",
            "Follow PSR-12 coding standard and PSR-4 autoloading conventions."
        ],
        "syntax_command": "php -l {file}"
    },
    "ruby": {
        "files": ["Gemfile", "Rakefile", ".rubocop.yml"],
        "extensions": [".rb", ".erb"],
        "name": "Ruby / Rails",
        "idioms": [
            "Follow Ruby style guide: 2 spaces indentation, snake_case for methods, CamelCase for classes.",
            "Use idiomatic blocks, iterators, and enumerable methods.",
            "Embrace DRY and convention over configuration."
        ],
        "syntax_command": "ruby -c {file}"
    },
    "dart": {
        "files": ["pubspec.yaml", "pubspec.lock"],
        "extensions": [".dart"],
        "name": "Dart / Flutter",
        "idioms": [
            "Follow sound null safety rules and effective Dart style guidelines.",
            "Structure Flutter widgets into clean, composable sub-widgets.",
            "Use proper state management patterns (Riverpod, Bloc, Provider)."
        ],
        "syntax_command": "dart analyze"
    },
    "shell": {
        "files": [],
        "extensions": [".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd"],
        "name": "Shell / PowerShell",
        "idioms": [
            "For bash: use `set -euo pipefail` and double quote all variable expansions.",
            "For PowerShell: use `$ErrorActionPreference = 'Stop'` and standard Verb-Noun cmdlet naming.",
            "Handle paths with spaces and check exit codes for all external tool invocations."
        ],
        "syntax_command": None
    }
}


def detect_workspace_languages(workspace_dir: str = ".") -> Dict[str, Any]:
    """
    Scans the workspace directory and identifies detected languages, frameworks, and manifests.
    """
    workspace_path = Path(workspace_dir).resolve()
    detected = []
    file_counts = {}
    found_manifests = []

    try:
        # Check files in root and first depth
        for root, dirs, files in os.walk(workspace_path):
            # Skip hidden, node_modules, git, venv, cache dirs
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "venv", "__pycache__", "target", "vendor", "dist", "build", ".git")]
            
            for file in files:
                ext = Path(file).suffix.lower()
                file_counts[ext] = file_counts.get(ext, 0) + 1
                
                # Check root manifests
                if Path(root) == workspace_path:
                    for lang_key, data in LANGUAGE_SIGNATURES.items():
                        for manifest in data["files"]:
                            if manifest.startswith("*") and file.endswith(manifest[1:]):
                                found_manifests.append((lang_key, file))
                            elif file.lower() == manifest.lower():
                                found_manifests.append((lang_key, file))

    except Exception:
        pass

    # Score languages
    scored_languages = {}
    for lang_key, data in LANGUAGE_SIGNATURES.items():
        score = 0
        # Manifest matches have high score
        for m_lang, m_file in found_manifests:
            if m_lang == lang_key:
                score += 50
        
        # File extension matches
        for ext in data["extensions"]:
            count = file_counts.get(ext, 0)
            score += count * 5

        if score > 0:
            scored_languages[lang_key] = {
                "name": data["name"],
                "score": score,
                "idioms": data["idioms"],
                "syntax_command": data["syntax_command"]
            }

    sorted_langs = sorted(scored_languages.items(), key=lambda x: x[1]["score"], reverse=True)

    return {
        "primary_language": sorted_langs[0][0] if sorted_langs else "general",
        "detected_languages": [item[1]["name"] for item in sorted_langs],
        "details": scored_languages,
        "manifests": [f"{m[1]} ({m[0]})" for m in found_manifests]
    }
