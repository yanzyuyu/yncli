import os
import json
from pathlib import Path
from typing import Dict, Any, List


class WorkspaceMemory:
    """
    Maintains real-time in-depth memory and indexed source code of the active workspace.
    """
    def __init__(self, workspace_dir: str = "."):
        self.workspace_dir = str(Path(workspace_dir).resolve())
        self.indexed_files: Dict[str, str] = {}
        self.file_tree: List[str] = []
        self.project_type: str = "general"
        self.refresh()

    def refresh(self) -> None:
        cwd = Path(self.workspace_dir)
        if not cwd.exists():
            return

        ignore_dirs = {
            "node_modules", "venv", ".venv", "__pycache__", "target", "vendor",
            "dist", "build", ".git", ".idea", ".vscode", "yncli.egg-info"
        }

        source_exts = {
            ".html", ".htm", ".css", ".js", ".jsx", ".ts", ".tsx", ".php",
            ".py", ".json", ".md", ".sql", ".yaml", ".yml", ".toml", ".rs", ".go"
        }

        self.indexed_files = {}
        self.file_tree = []

        try:
            for root, dirs, files in os.walk(cwd):
                dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
                rel_root = Path(root).relative_to(cwd)

                for f in sorted(files):
                    if f.startswith(".") and f not in (".env", ".gitignore"):
                        continue
                    rel_f = rel_root / f if str(rel_root) != "." else Path(f)
                    posix_path = rel_f.as_posix()
                    self.file_tree.append(posix_path)

                    full_path = cwd / rel_f
                    ext = full_path.suffix.lower()
                    
                    # Pre-load core config and entry source files (up to 10 key files, max 15KB each)
                    # For deeper files, AI uses read_file tool or user @mention to prevent huge payload timeouts
                    if (ext in source_exts or f in ("Dockerfile", "Makefile")) and len(self.indexed_files) < 10:
                        try:
                            size = full_path.stat().st_size
                            if 0 < size < 15000:
                                with open(full_path, "r", encoding="utf-8", errors="replace") as fp:
                                    self.indexed_files[posix_path] = fp.read()
                        except Exception:
                            pass
        except Exception:
            pass

        # Detect primary project type
        fset = set(self.file_tree)
        if "index.html" in fset or any(f.endswith(".html") for f in fset):
            self.project_type = "Web Frontend (HTML/CSS/JS)"
        elif "composer.json" in fset or "artisan" in fset or any(f.endswith(".php") for f in fset):
            self.project_type = "PHP / Laravel"
        elif "package.json" in fset:
            self.project_type = "Node.js / JavaScript"
        elif "requirements.txt" in fset or "pyproject.toml" in fset or any(f.endswith(".py") for f in fset):
            self.project_type = "Python"

    def get_context_for_prompt(self) -> str:
        """
        Builds an exhaustive source code snapshot for the AI so it never needs to ask where files are.
        """
        lines = []
        lines.append(f"### WORKSPACE LOCATION: {self.workspace_dir}")
        lines.append(f"### DETECTED PROJECT TYPE: {self.project_type}")
        lines.append(f"### TOTAL WORKSPACE FILES ({len(self.file_tree)}):")
        for f in self.file_tree[:30]:
            lines.append(f"  - {f}")
        if len(self.file_tree) > 30:
            lines.append(f"  - ... ({len(self.file_tree) - 30} other files)")

        if self.indexed_files:
            lines.append("\n### COMPLETE PRE-LOADED PROJECT SOURCE FILES:")
            for fname, content in self.indexed_files.items():
                lines.append(f"\n========================================")
                lines.append(f"FILE: `{fname}` ({len(content.splitlines())} lines)")
                lines.append(f"========================================")
                lines.append(content)
        else:
            lines.append("\n(No existing project source files found in workspace directory)")

        return "\n".join(lines)
