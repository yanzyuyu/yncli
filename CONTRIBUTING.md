# Contributing to YNCLI

Thank you for your interest in contributing to **YNCLI**! We welcome bug reports, feature requests, documentation improvements, and code contributions from developers around the world.

---

## 🛠️ Local Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/yncli.git
   cd yncli
   ```

2. **Set up Python virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies in editable mode:**
   ```bash
   pip install -e .
   pip install -r requirements.txt
   ```

4. **Run YNCLI locally:**
   ```bash
   yncli
   ```

---

## 🌿 Contribution Guidelines

1. **Create a branch for your feature/fix:**
   ```bash
   git checkout -b feat/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```
2. **Follow coding standards:**
   - Keep code clean, modular, and type-annotated (`typing`).
   - Test changes thoroughly across platforms (Windows, Linux, macOS) if modifying CLI/TUI logic.
3. **Commit your changes:**
   - Use conventional commit messages: `feat: ...`, `fix: ...`, `docs: ...`, `ci: ...`
4. **Open a Pull Request (PR):**
   - Provide a clear description of what was changed and why.
   - Attach terminal screenshots or recordings for UI/TUI modifications.

---

## 📜 Code of Conduct
Please be respectful, constructive, and welcoming to all community members and contributors.

Thank you for helping make YNCLI better! 🚀
