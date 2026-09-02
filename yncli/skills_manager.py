import os
from pathlib import Path
from typing import Dict, List, Optional

PACKAGE_SKILLS_DIR = Path(__file__).parent / "built_in_skills"
ROOT_SKILLS_DIR = Path(__file__).parent.parent / "built_in_skills"


class SkillsManager:
    def __init__(self, workspace_dir: str = "."):
        self.workspace_dir = Path(workspace_dir).resolve()
        self.user_skills_dir = self.workspace_dir / ".skills"
        self.active_skill: Optional[str] = "ultrabrain"
        self._skills_cache: Dict[str, str] = {}
        self.load_skills()

    def load_skills(self) -> None:
        self._skills_cache.clear()
        
        # 1. Load built-in skills from package directory or root
        skills_dirs = [PACKAGE_SKILLS_DIR, ROOT_SKILLS_DIR]
        for sdir in skills_dirs:
            if sdir.exists():
                for file in sdir.glob("*.md"):
                    skill_name = file.stem.lower()
                    if skill_name not in self._skills_cache:
                        try:
                            with open(file, "r", encoding="utf-8") as f:
                                self._skills_cache[skill_name] = f.read().strip()
                        except Exception:
                            pass

        # 2. Load user workspace custom skills (.skills/*.md)
        if self.user_skills_dir.exists():
            for file in self.user_skills_dir.glob("*.md"):
                skill_name = file.stem.lower()
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        self._skills_cache[skill_name] = f.read().strip()
                except Exception:
                    pass

    def list_skills(self) -> List[str]:
        return sorted(list(self._skills_cache.keys()))

    def get_skill_content(self, skill_name: str) -> Optional[str]:
        return self._skills_cache.get(skill_name.lower())

    def set_active_skill(self, skill_name: str) -> bool:
        if skill_name.lower() in self._skills_cache:
            self.active_skill = skill_name.lower()
            return True
        return False

    def get_active_skill_prompt(self) -> str:
        if not self.active_skill:
            return ""
        content = self._skills_cache.get(self.active_skill, "")
        if content:
            return f"\n\n--- ACTIVE SKILL MODE: [{self.active_skill.upper()}] ---\n{content}\n"
        return ""
