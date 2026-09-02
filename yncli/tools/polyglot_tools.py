import os
import subprocess
import tempfile
import re
from pathlib import Path
from typing import Optional
from yncli.language_detector import detect_workspace_languages, LANGUAGE_SIGNATURES
from yncli.tools.system_tools import run_terminal_command


def validate_code_syntax(language: str, file_path: Optional[str] = None, code_snippet: Optional[str] = None) -> str:
    """
    Validates the syntax of a code file or code snippet across various languages (Python, JS/TS, Rust, Go, C/C++, PHP, Ruby, etc.)
    """
    lang_key = language.lower().strip()
    
    # Map common aliases
    alias_map = {
        "py": "python",
        "ts": "typescript",
        "js": "javascript",
        "rs": "rust",
        "golang": "golang",
        "go": "golang",
        "c++": "cpp",
        "c": "cpp",
        "cs": "csharp",
        "kt": "java",
        "rb": "ruby",
    }
    lang_key = alias_map.get(lang_key, lang_key)

    temp_file = None
    target_file = file_path

    if not target_file and code_snippet:
        ext_map = {
            "python": ".py",
            "typescript": ".ts",
            "javascript": ".js",
            "rust": ".rs",
            "golang": ".go",
            "cpp": ".cpp",
            "csharp": ".cs",
            "java": ".java",
            "php": ".php",
            "ruby": ".rb",
            "dart": ".dart",
            "shell": ".ps1"
        }
        ext = ext_map.get(lang_key, ".txt")
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=ext, mode="w", encoding="utf-8")
        temp.write(code_snippet)
        temp.close()
        temp_file = temp.name
        target_file = temp_file

    if not target_file or not Path(target_file).exists():
        return "[ERROR] No file or code snippet provided for validation."

    try:
        # 1. Python Syntax Validation
        if lang_key == "python":
            import py_compile
            try:
                py_compile.compile(target_file, doraise=True)
                return f"[PASS] Python Syntax Check: No syntax errors detected in {Path(target_file).name}."
            except py_compile.PyCompileError as e:
                return f"[FAIL] Python Syntax Error:\n{str(e)}"

        # 2. General compiler/linter check using system tools
        sig = LANGUAGE_SIGNATURES.get(lang_key)
        if sig and sig.get("syntax_command"):
            cmd = sig["syntax_command"].replace("{file}", f'"{target_file}"')
            result = run_terminal_command(cmd, timeout=15)
            
            # Check exit code
            is_exit_zero = "[Process exited with code 0]" in result
            res_lower = result.lower()

            # Special case for PHP: "no syntax errors detected"
            if "no syntax errors detected" in res_lower and is_exit_zero:
                return f"[PASS] PHP Syntax Check: No syntax errors detected in {Path(target_file).name}."

            # Determine failure
            has_explicit_error = any(kw in res_lower for kw in [
                "parse error", "syntax error", "fatal error", "compile error", 
                "error[e", "compilation failed", "unhandled exception"
            ])

            if (not is_exit_zero) or has_explicit_error:
                return f"[FAIL] {sig['name']} Syntax / Compiler Check Result:\n{result}"
            else:
                return f"[PASS] {sig['name']} Syntax / Compiler Check Passed:\n{result}"

        return f"[INFO] Syntax validator not configured or language toolchain not found for '{language}'. File saved."

    except Exception as e:
        return f"[ERROR] During syntax validation: {str(e)}"
    finally:
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass


def run_project_tests(test_filter: str = "", cwd: str = ".") -> str:
    """
    Automatically detects the project type and runs standard test suites (pytest, npm test, cargo test, go test, dotnet test).
    """
    workspace = Path(cwd).resolve()
    
    if (workspace / "pytest.ini").exists() or (workspace / "tests").exists() or (workspace / "pyproject.toml").exists():
        cmd = f"pytest {test_filter}" if test_filter else "pytest"
        return run_terminal_command(cmd, timeout=60, cwd=cwd)
    elif (workspace / "package.json").exists():
        cmd = f"npm test -- {test_filter}" if test_filter else "npm test"
        return run_terminal_command(cmd, timeout=60, cwd=cwd)
    elif (workspace / "Cargo.toml").exists():
        cmd = f"cargo test {test_filter}" if test_filter else "cargo test"
        return run_terminal_command(cmd, timeout=60, cwd=cwd)
    elif (workspace / "go.mod").exists():
        cmd = f"go test ./... -run {test_filter}" if test_filter else "go test ./..."
        return run_terminal_command(cmd, timeout=60, cwd=cwd)
    elif list(workspace.glob("*.csproj")) or list(workspace.glob("*.sln")):
        cmd = f"dotnet test --filter {test_filter}" if test_filter else "dotnet test"
        return run_terminal_command(cmd, timeout=60, cwd=cwd)
    elif (workspace / "composer.json").exists() and (workspace / "vendor" / "bin" / "phpunit").exists():
        cmd = f"./vendor/bin/phpunit --filter {test_filter}" if test_filter else "./vendor/bin/phpunit"
        return run_terminal_command(cmd, timeout=60, cwd=cwd)
    
    return "[INFO] No known test suite configuration detected in workspace. Use run_terminal_command for custom test scripts."
