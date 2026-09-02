import json
from typing import List, Dict, Any

from yncli.tools.system_tools import run_terminal_command, git_status, git_diff, get_system_info, change_directory, save_plan_document
from yncli.tools.file_tools import read_file, write_file, edit_file_replace, list_directory, find_files, grep_search
from yncli.tools.search_tools import web_search, fetch_webpage
from yncli.tools.polyglot_tools import validate_code_syntax, run_project_tests

AGENT_TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "change_directory",
            "description": "Changes the current active working directory of the workspace (e.g. 'cd laravelcrud' or 'cd ..' or entering a project folder).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative or absolute directory path to switch to"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_plan_document",
            "description": "Saves the complete PRD (Product Requirements Document) with ASCII mockups, database schemas, stack specs, and implementation roadmap into plan.md in the current workspace directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The full Markdown content of the PRD to save into plan.md"}
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Searches the web in real-time via DuckDuckGo for the latest information, documentation, news, or solutions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query keywords"},
                    "max_results": {"type": "integer", "description": "Number of results to return (default: 5)"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_webpage",
            "description": "Fetches a URL and converts its content into clean, readable text/markdown.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The complete HTTP/HTTPS URL"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads file contents with line numbers. Can view entire file or specific line range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Relative or absolute path to the file"},
                    "start_line": {"type": "integer", "description": "Optional 1-indexed start line"},
                    "end_line": {"type": "integer", "description": "Optional 1-indexed end line"}
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Creates or completely overwrites a file with new content. Automatically creates parent directories.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Relative or absolute path to the file"},
                    "content": {"type": "string", "description": "The full code/text content to write"}
                },
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file_replace",
            "description": "Performs surgical search-and-replace edit on an existing file. target_content must uniquely match the section being modified.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Relative or absolute path to the file"},
                    "target_content": {"type": "string", "description": "Exact text or lines in the file to replace"},
                    "replacement_content": {"type": "string", "description": "New replacement text"}
                },
                "required": ["file_path", "target_content", "replacement_content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "Lists contents of a directory, showing files and subdirectories.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dir_path": {"type": "string", "description": "Directory path (default: current directory '.')"},
                    "recursive": {"type": "boolean", "description": "If true, lists recursively up to max_depth"},
                    "max_depth": {"type": "integer", "description": "Maximum depth for recursive listing (default: 2)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_files",
            "description": "Finds files matching a glob pattern (e.g. '*.py', '*.ts', 'config*') in the project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Glob pattern (e.g. '*.rs', '*.go')"},
                    "search_dir": {"type": "string", "description": "Starting directory (default: '.')"}
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "grep_search",
            "description": "Fast text and regex search across all files in the directory tree.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keyword or regex pattern"},
                    "search_path": {"type": "string", "description": "Path to search within (default: '.')"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_terminal_command",
            "description": "Runs a terminal command (PowerShell on Windows, Bash on Unix) in the workspace and returns stdout, stderr, and exit code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Command line string to execute"},
                    "timeout": {"type": "integer", "description": "Timeout in seconds (default: 60)"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "validate_code_syntax",
            "description": "Validates syntax of a file or code snippet using the appropriate language compiler or linter (Python, TypeScript, Rust, Go, C++, PHP, etc.).",
            "parameters": {
                "type": "object",
                "properties": {
                    "language": {"type": "string", "description": "Programming language (e.g. 'python', 'typescript', 'rust', 'go', 'cpp', 'php')"},
                    "file_path": {"type": "string", "description": "Optional path to existing file"},
                    "code_snippet": {"type": "string", "description": "Optional code string to validate directly"}
                },
                "required": ["language"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_project_tests",
            "description": "Auto-detects and runs project unit tests (pytest, npm test, cargo test, go test, dotnet test).",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_filter": {"type": "string", "description": "Optional filter keyword for test cases"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_status",
            "description": "Gets current git repository status (branch, changed files).",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


def execute_tool(name: str, arguments: Dict[str, Any], current_cwd: str = ".") -> Any:
    try:
        if name == "change_directory":
            return change_directory(path=arguments.get("path", "."), current_cwd=current_cwd)
        elif name == "save_plan_document":
            return save_plan_document(content=arguments.get("content", ""), current_cwd=current_cwd)
        elif name == "web_search":
            return web_search(query=arguments.get("query", ""), max_results=arguments.get("max_results", 5))
        elif name == "fetch_webpage":
            return fetch_webpage(url=arguments.get("url", ""))
        elif name == "read_file":
            return read_file(
                file_path=arguments.get("file_path", ""),
                start_line=arguments.get("start_line"),
                end_line=arguments.get("end_line")
            )
        elif name == "write_file":
            return write_file(file_path=arguments.get("file_path", ""), content=arguments.get("content", ""))
        elif name == "edit_file_replace":
            return edit_file_replace(
                file_path=arguments.get("file_path", ""),
                target_content=arguments.get("target_content", ""),
                replacement_content=arguments.get("replacement_content", "")
            )
        elif name == "list_directory":
            return list_directory(
                dir_path=arguments.get("dir_path", "."),
                recursive=arguments.get("recursive", False),
                max_depth=arguments.get("max_depth", 2)
            )
        elif name == "find_files":
            return find_files(pattern=arguments.get("pattern", "*"), search_dir=arguments.get("search_dir", "."))
        elif name == "grep_search":
            return grep_search(query=arguments.get("query", ""), search_path=arguments.get("search_path", "."))
        elif name == "run_terminal_command":
            return run_terminal_command(command=arguments.get("command", ""), timeout=arguments.get("timeout", 60), cwd=current_cwd)
        elif name == "validate_code_syntax":
            return validate_code_syntax(
                language=arguments.get("language", ""),
                file_path=arguments.get("file_path"),
                code_snippet=arguments.get("code_snippet")
            )
        elif name == "run_project_tests":
            return run_project_tests(test_filter=arguments.get("test_filter", ""), cwd=current_cwd)
        elif name == "git_status":
            return git_status(cwd=current_cwd)
        else:
            return f"[ERROR] Unknown tool: {name}"
    except Exception as e:
        return f"[ERROR] Gagal mengeksekusi tool '{name}': {str(e)}"
