# yncli

A simple, fast AI coding assistant that lives in your terminal. It reads your project files, helps you plan features, and writes code directly to your disk so you don't have to copy-paste.

[![PyPI](https://img.shields.io/pypi/v/yncli?style=flat-square&color=blue)](https://pypi.org/project/yncli/)
[![npm](https://img.shields.io/npm/v/@yanzyuyu/yncli?style=flat-square&color=red)](https://www.npmjs.com/package/@yanzyuyu/yncli)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

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

Then just navigate to your project folder and run:

```bash
yncli
```

---

## Why use this?

Most AI tools spit out markdown blocks and expect you to copy-paste every file by hand. `yncli` works directly with your codebase:

- **Understands your workspace**: It automatically maps the files in your current directory so you don't have to explain your folder structure.
- **Plans before coding (`/plan`)**: Generates clear architecture notes and task lists in `plan.md` before touching your code.
- **Direct file edits (`/build`)**: Writes and updates files directly on your disk, running syntax checks across PHP, TypeScript, Python, Go, and more.
- **Bring your own model**: Connect your Google Gemini API key (`/google <key>`), point to local Ollama (`/endpoint http://localhost:11434/v1`), or use OpenRouter/Groq.
- **Clean terminal**: Pasting 100+ lines of error logs automatically shrinks to `[ pasted 100 lines ]` so your screen stays readable.

---

## Usage

### Interactive Mode
```bash
# Open interactive session in current folder
yncli

# Start in planning mode
yncli --mode plan

# Use a specific model
yncli -m ag/claude-sonnet-4-6
```

### One-shot Command
```bash
yncli "Fix the authentication middleware in app/Http/Middleware/Auth.php"
```

---

## Useful Commands

Once inside the session, you can use these shortcuts:

| Command | What it does |
| :--- | :--- |
| `/model` | Open the interactive model picker popup |
| `/google <key>` | Connect directly with your Google Gemini AI key |
| `/default` | Reset provider back to default models (`ag/*`, `cx/*`) |
| `/endpoint <url>` | Set a custom OpenAI-compatible API endpoint |
| `/key <key>` | Set your custom API key |
| `/plan` | Switch to **Plan Mode** (saves architecture to `plan.md`) |
| `/build` | Switch to **Build Mode** (writes and modifies files) |
| `/ask` | Switch to **Ask Mode** (answers questions without editing files) |
| `/cd <dir>` | Change active project folder |
| `/skills` | Switch agent persona (architect, debugger, ultrabrain) |
| `/update` | Auto-update to the latest version |
| `/clear` | Clear chat history & refresh file memory |
| `/save` | Export conversation to a Markdown file |
| `/exit` | Exit yncli |

---

## License

[MIT](LICENSE) © 2026 Yanzyuyu
