import re
import os
from pathlib import Path
from typing import Tuple, List, Dict


def resolve_file_mentions(prompt: str, workspace_dir: str = ".") -> Tuple[str, List[Dict[str, str]]]:
    """
    Scans the prompt for @file or @folder mentions (e.g. @app/Http/Controllers/UserController.php or @index.html).
    Loads the contents of referenced files and appends them as explicit contextual attachments.
    
    Returns:
        (cleaned_prompt, list_of_attached_files)
    """
    cwd = Path(workspace_dir).resolve()
    
    # Matches patterns like @filename.ext or @"path with spaces/file.ext" or @path/to/file
    mention_pattern = re.compile(r'@(?:"([^"]+)"|([a-zA-Z0-9_\-\.\/\\]+))')
    
    matches = mention_pattern.findall(prompt)
    if not matches:
        return prompt, []

    attached_files = []
    seen_paths = set()

    for m_quoted, m_unquoted in matches:
        rel_path = (m_quoted or m_unquoted).strip()
        if not rel_path:
            continue

        clean_path = rel_path.replace("\\", "/")
        if clean_path in seen_paths:
            continue
        seen_paths.add(clean_path)

        target_file = cwd / rel_path
        if target_file.exists() and target_file.is_file():
            try:
                # Read content up to 100KB
                size = target_file.stat().st_size
                if size < 150000:
                    with open(target_file, "r", encoding="utf-8", errors="replace") as fp:
                        content = fp.read()
                    attached_files.append({
                        "path": clean_path,
                        "content": content,
                        "lines": len(content.splitlines()),
                        "size_bytes": size
                    })
            except Exception:
                pass
        elif not target_file.exists():
            # Try searching in subdirectories
            for root, _, files in os.walk(cwd):
                for f in files:
                    if f.lower() == Path(rel_path).name.lower():
                        found = Path(root) / f
                        try:
                            rel_found = found.relative_to(cwd).as_posix()
                            if rel_found not in seen_paths and found.stat().st_size < 150000:
                                seen_paths.add(rel_found)
                                with open(found, "r", encoding="utf-8", errors="replace") as fp:
                                    content = fp.read()
                                attached_files.append({
                                    "path": rel_found,
                                    "content": content,
                                    "lines": len(content.splitlines()),
                                    "size_bytes": found.stat().st_size
                                })
                        except Exception:
                            pass
                        break

    if not attached_files:
        return prompt, []

    # Build enriched context block
    enrichment_blocks = ["\n\n### [USER ATTACHED @FILES CONTEXT]:"]
    for item in attached_files:
        enrichment_blocks.append(
            f"\n--- ATTACHED FILE: @{item['path']} ({item['lines']} lines) ---\n"
            f"{item['content']}\n"
            f"--- END OF @{item['path']} ---"
        )

    enriched_prompt = prompt + "\n" + "\n".join(enrichment_blocks)
    return enriched_prompt, attached_files
