import os
import re
import fnmatch
from pathlib import Path
from typing import Optional, List, Dict, Any

from yncli.clean_text import clean_text_for_terminal


def read_file(file_path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
    """
    Reads file content with optional line number range (1-indexed).
    """
    path = Path(file_path).resolve()
    if not path.exists():
        return f"Error: File not found: {file_path}"
    if path.is_dir():
        return f"Error: Path is a directory, not a file: {file_path}"

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        total_lines = len(lines)
        if total_lines == 0:
            return f"(File {path.name} is empty)"

        s_line = max(1, start_line) if start_line is not None else 1
        e_line = min(total_lines, end_line) if end_line is not None else total_lines

        if s_line > e_line:
            return f"Error: start_line ({s_line}) cannot be greater than end_line ({e_line}). Total lines: {total_lines}"

        output = []
        output.append(f"File: {path.name} (Lines {s_line}-{e_line} of {total_lines})")
        output.append("-" * 50)
        for i in range(s_line - 1, e_line):
            output.append(f"{i + 1:4d} | {lines[i].rstrip()}")

        return "\n".join(output)
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"


def write_file(file_path: str, content: str) -> str:
    """
    Writes or overwrites content to a file, automatically creating parent directories.
    Sanitizes content to ensure clean UTF-8 without mojibake.
    """
    try:
        path = Path(file_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        cleaned_content = clean_text_for_terminal(content)
        with open(path, "w", encoding="utf-8") as f:
            f.write(cleaned_content)
        return f"Successfully written {len(cleaned_content.splitlines())} lines to {path}"
    except Exception as e:
        return f"Error writing file {file_path}: {str(e)}"


def edit_file_replace(file_path: str, target_content: str, replacement_content: str) -> str:
    """
    Performs precise surgical search-and-replace edit on an existing file.
    """
    path = Path(file_path).resolve()
    if not path.exists():
        return f"Error: File not found: {file_path}"

    try:
        with open(path, "r", encoding="utf-8") as f:
            original = f.read()

        target_norm = clean_text_for_terminal(target_content).replace("\r\n", "\n")
        orig_norm = original.replace("\r\n", "\n")
        repl_norm = clean_text_for_terminal(replacement_content).replace("\r\n", "\n")

        if target_norm in orig_norm:
            count = orig_norm.count(target_norm)
            if count > 1:
                return f"Error: target_content occurs {count} times in {file_path}. Please provide more unique surrounding lines."
            
            new_text = orig_norm.replace(target_norm, repl_norm, 1)
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_text)
            return f"Successfully updated {file_path} with search-and-replace edit."

        # Fallback: line-by-line whitespace-stripped match
        target_lines = [l.strip() for l in target_norm.strip().split("\n") if l.strip()]
        file_lines = orig_norm.split("\n")
        
        match_idx = -1
        for i in range(len(file_lines) - len(target_lines) + 1):
            subset = [file_lines[i + j].strip() for j in range(len(target_lines))]
            if subset == target_lines:
                match_idx = i
                break

        if match_idx != -1:
            end_match = match_idx + len(target_lines)
            new_file_lines = file_lines[:match_idx] + repl_norm.split("\n") + file_lines[end_match:]
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(new_file_lines))
            return f"Successfully updated {file_path} (matched with whitespace tolerance)."

        return f"Error: target_content was not found in {file_path}. Please check the exact lines."
    except Exception as e:
        return f"Error editing file {file_path}: {str(e)}"


def list_directory(dir_path: str = ".", recursive: bool = False, max_depth: int = 2) -> str:
    path = Path(dir_path).resolve()
    if not path.exists():
        return f"Error: Directory not found: {dir_path}"
    if not path.is_dir():
        return f"Error: Path is not a directory: {dir_path}"

    lines = [f"Directory listing for: {path}"]
    lines.append("-" * 50)

    try:
        if not recursive:
            entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
            for e in entries:
                if e.name.startswith(".") and e.name not in (".env", ".gitignore", ".skills"):
                    continue
                if e.is_dir():
                    lines.append(f"[DIR]  {e.name}/")
                else:
                    size = e.stat().st_size
                    lines.append(f"[FILE] {e.name:<30} ({size:,} bytes)")
        else:
            base_depth = len(path.parts)
            for root, dirs, files in os.walk(path):
                cur_path = Path(root)
                depth = len(cur_path.parts) - base_depth
                if depth > max_depth:
                    dirs[:] = []
                    continue

                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "venv", "__pycache__", "target", "vendor", "dist", "build", ".git")]
                
                indent = "  " * depth
                if depth > 0:
                    lines.append(f"{indent}[DIR] {cur_path.name}/")
                for f in sorted(files):
                    if not f.startswith("."):
                        fpath = cur_path / f
                        size = fpath.stat().st_size
                        lines.append(f"{indent}  [FILE] {f} ({size:,} bytes)")

        return "\n".join(lines)
    except Exception as e:
        return f"Error listing directory {dir_path}: {str(e)}"


def find_files(pattern: str, search_dir: str = ".") -> str:
    root_path = Path(search_dir).resolve()
    matches = []
    try:
        for root, dirs, files in os.walk(root_path):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "venv", "__pycache__", "target", "vendor", ".git")]
            for f in files:
                if fnmatch.fnmatch(f, pattern):
                    rel = Path(root, f).relative_to(root_path)
                    matches.append(str(rel))
        if not matches:
            return f"No files matching pattern '{pattern}' found in {search_dir}"
        return f"Found {len(matches)} files matching '{pattern}':\n" + "\n".join(f"- {m}" for m in matches[:50])
    except Exception as e:
        return f"Error finding files: {str(e)}"


def grep_search(query: str, search_path: str = ".", case_sensitive: bool = False) -> str:
    path = Path(search_path).resolve()
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        pattern = re.compile(query, flags)
    except Exception as e:
        return f"Invalid regex pattern: {str(e)}"

    matches = []
    try:
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "venv", "__pycache__", "target", "vendor", ".git")]
            for f in files:
                fpath = Path(root, f)
                if fpath.suffix.lower() in (".png", ".jpg", ".exe", ".dll", ".zip", ".tar", ".gz", ".pyc", ".pdf"):
                    continue
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as file_obj:
                        for line_idx, line in enumerate(file_obj, start=1):
                            if pattern.search(line):
                                rel = fpath.relative_to(path)
                                matches.append(f"{rel}:{line_idx}: {line.strip()}")
                                if len(matches) >= 50:
                                    break
                except Exception:
                    continue
            if len(matches) >= 50:
                break

        if not matches:
            return f"No matches found for query '{query}' in {search_path}"
        return f"Found {len(matches)} matches for '{query}':\n" + "\n".join(matches)
    except Exception as e:
        return f"Error running grep search: {str(e)}"
