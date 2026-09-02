# yncli

A simple, fast AI coding assistant that lives in your terminal. It reads your project files, helps you plan features, and writes code directly to your disk so you don't have to copy-paste.

[![PyPI](https://img.shields.io/pypi/v/yncli?style=flat-square&color=blue)](https://pypi.org/project/yncli/)
[![npm](https://img.shields.io/npm/v/@yanzyuyu/yncli?style=flat-square&color=red)](https://www.npmjs.com/package/@yanzyuyu/yncli)
[![GitHub Stars](https://img.shields.io/github/stars/yanzyuyu/yncli?style=flat-square&color=yellow)](https://github.com/yanzyuyu/yncli/stargazers)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

```text
       █   █  yncli 1.2.3
       █   █  Autonomous AI Coding Agent
        █ █   ag/claude-sonnet-4-6 (Build Mode)
         █    ~/Projects/laravel-app
         █
Project: PHP / Laravel (10/193 files in active memory)

build > @UserController.php add rate limiting to login endpoint
[ - ] Modifying app/Http/Controllers/UserController.php...
[OK] Applied changes & syntax check passed!
```

---

## Quick Start

Run it instantly without installing anything:

```bash
npx @yanzyuyu/yncli
```

Or install it globally:

```bash
# Python
pip install yncli

# Node.js
npm install -g @yanzyuyu/yncli
```

Then just open any project folder and run:

```bash
yncli
```

---

## Why use this?

Most AI tools spit out markdown blocks and expect you to copy-paste every file by hand. `yncli` works directly with your codebase:

- **Zero-Setup Context**: Automatically indexes your project files into memory so you never have to explain your directory structure.
- **Plans Before It Codes (`/plan`)**: Writes clear architecture specs and task lists into `plan.md` before making changes.
- **Direct File Edits (`/build`)**: Modifies files directly on disk and runs syntax validation for PHP/Laravel, TypeScript, Python, Go, and more.
- **Bring Your Own Model**: Use your Google Gemini key (`/google <key>`), connect local Ollama (`/endpoint http://localhost:11434/v1`), or use OpenRouter/Groq.
- **Noise-Free Terminal**: Pasting long error logs (100+ lines) collapses into `[ pasted 100 lines ]` so your screen stays clean.

---

## Usage

```bash
# Interactive coding session
yncli

# Quick one-liner fix
yncli "Fix broken migration in database/migrations"

# Start directly in planning mode
yncli --mode plan
```

---

## Shortcuts

Inside the session:

| Command | Description |
| :--- | :--- |
| `@file` | Mention any file to inject its full content into context |
| `/model` | Open interactive model picker popup |
| `/google <key>` | Connect directly with your Google Gemini AI key |
| `/default` | Reset to default models (`ag/*`, `cx/*`) |
| `/endpoint <url>` | Connect to local Ollama, OpenRouter, or OpenAI |
| `/plan` | Plan architecture & save to `plan.md` |
| `/build` | Code & edit files autonomously |
| `/skills` | Switch persona (architect, debugger, ultrabrain) |
| `/update` | Auto-update yncli to latest release |

---

## License

[MIT](LICENSE) © 2026 Yanzyuyu
