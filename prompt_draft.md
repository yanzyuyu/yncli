# YNCLI Development Blueprint

## 1. Feature Specifications

### 1.1 Secure API Configuration (Zero-Trust)
- Remove hardcoded default API keys from client.py or config files.
- Create a ~/.yncli/config.json configuration file manager.
- Support loading API keys from .env via process.loadEnvFile() (if JS) or os.environ (in Python) before falling back to config.json.
- Do not repeatedly prompt if the key exists.

### 1.2 Local Router Detection
- Probing feature (HTTP GET /v1/models or similar) to detect local LLMs on common ports (11434, 1234, 4000).
- If a local router responds, prompt user: 'Terdeteksi local router di port XXXX. Gunakan ini? (y/n)'.

### 1.3 Context-Aware Skill Loader & Global Instructions
- Implement Global Instructions: Always read a GEMINI.md or SYSTEM.md file globally if it exists and inject it into the base system prompt.
- Implement Lazy-Loading for Skills: Instead of loading all SKILL.md files (which wastes tokens), implement a lightweight keyword or regex matching on the user's prompt to determine which specific skill(s) to load.

### 1.4 MCP (Model Context Protocol) & Agent Tools
- Add lightweight JSON-RPC MCP integration to allow yncli to communicate with standard MCP servers.
- Audit existing 	ools/ and ensure AI coding standards are met (YAGNI, diff-based replacement).

## 2. QA & Acceptance Criteria
- Must adhere strictly to human-coding standards (No AI Slop comments, no overly polite strings).
- Must adhere strictly to nti-overengineering (Zero unneeded external dependencies, utilize Python native standard libraries).
- Pass adversarial checks by enterprise_security_tester.
- Pass final review by enterprise_master_auditor (Zero-slop verification).

### 1.5 Autonomous Agentic Loop (Opencode-style)
- The AI must autonomously execute tools in a continuous loop without waiting for user intervention for every single step.
- It feeds the output of execute_tool() back into the conversation context as a 	ool_response / unction_call result and recursively calls the LLM until the task is logically complete.
- Adhere to nti-overengineering: Keep the loop logic flat and native (while loop), avoid pulling in massive agent frameworks like LangChain or AutoGen. Use pure Python arrays for chat history and native function calling API.
