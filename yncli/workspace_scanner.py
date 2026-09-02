import os
from pathlib import Path
from typing import Dict, Any, List


def scan_workspace_deep(workspace_dir: str = ".") -> Dict[str, Any]:
    """
    Performs deep background workspace inspection, analyzing project structure,
    key files, frameworks, and existing implementation state.
    """
    cwd = Path(workspace_dir).resolve()
    if not cwd.exists():
        return {"summary": "Workspace directory not found.", "key_files": {}, "tree": []}

    ignore_dirs = {
        "node_modules", "venv", ".venv", "__pycache__", "target", "vendor",
        "dist", "build", ".git", ".idea", ".vscode", "yncli.egg-info"
    }

    files_list: List[str] = []
    dirs_list: List[str] = []
    key_files_content: Dict[str, str] = {}

    priority_files = [
        "plan.md", "README.md", "package.json", "composer.json", "requirements.txt",
        "index.html", "index.php", "main.py", "app.py", "Cargo.toml", "go.mod",
        "style.css", "styles.css", "script.js", "app.js", "App.tsx", "App.jsx"
    ]

    try:
        for root, dirs, files in os.walk(cwd):
            dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
            rel_root = Path(root).relative_to(cwd)

            for d in dirs:
                rel_d = rel_root / d if str(rel_root) != "." else Path(d)
                dirs_list.append(f"{rel_d.as_posix()}/")

            for f in sorted(files):
                if f.startswith(".") and f not in (".env", ".gitignore"):
                    continue
                rel_f = rel_root / f if str(rel_root) != "." else Path(f)
                posix_path = rel_f.as_posix()
                files_list.append(posix_path)

                # Read key context files if small
                if f in priority_files and len(key_files_content) < 6:
                    full_p = cwd / rel_f
                    try:
                        if full_p.stat().st_size < 30000:
                            with open(full_p, "r", encoding="utf-8", errors="replace") as fp:
                                snippet = fp.read(4000)
                                key_files_content[posix_path] = snippet
                    except Exception:
                        pass
    except Exception as e:
        return {"summary": f"Error scanning workspace: {e}", "key_files": {}, "tree": []}

    return {
        "cwd": str(cwd),
        "total_files": len(files_list),
        "total_dirs": len(dirs_list),
        "files": files_list[:60],
        "key_files": key_files_content
    }


def format_workspace_context(scan_data: Dict[str, Any]) -> str:
    """
    Formats the deep scan data into an executive architectural context for LLM system prompt.
    """
    if not scan_data or "cwd" not in scan_data:
        return "No workspace data available."

    lines = []
    lines.append(f"### Current Workspace: {scan_data['cwd']}")
    lines.append(f"Total Detected Files: {scan_data.get('total_files', 0)} files")
    
    files = scan_data.get("files", [])
    if files:
        lines.append("### Project File Structure:")
        for f in files[:35]:
            lines.append(f"  - {f}")
        if len(files) > 35:
            lines.append(f"  - ... ({len(files) - 35} more files)")
    else:
        lines.append("### Project File Structure: (Empty workspace directory)")

    key_files = scan_data.get("key_files", {})
    if key_files:
        lines.append("\n### Key Project Files Overview:")
        for fname, content in key_files.items():
            lines.append(f"#### File: `{fname}`")
            lines.append("```")
            preview = "\n".join(content.splitlines()[:25])
            lines.append(preview)
            lines.append("```")

    return "\n".join(lines)
