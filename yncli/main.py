import sys
import os
import argparse
from pathlib import Path

# Ensure UTF-8 output encoding across Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from yncli.config import load_config, save_config
from yncli.client import LLMClient
from yncli.agent import Agent
from yncli.tui import TerminalUI


def main():
    parser = argparse.ArgumentParser(
        prog="yncli",
        description="[YNCLI] Autonomous Polyglot AI Coding Agent & TUI"
    )
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Optional prompt to execute in quick one-shot mode. If omitted, starts interactive TUI."
    )
    parser.add_argument(
        "-m", "--model",
        type=str,
        help="Specify the AI model to use (e.g. ag/gemini-3.7-flash-high, ag/claude-sonnet-4-6)"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["plan", "build", "ask"],
        help="Set operating mode: 'plan' (architect/planner), 'build' (autonomous coding), 'ask' (Q&A/consult)"
    )
    parser.add_argument(
        "-s", "--skill",
        type=str,
        help="Activate a specialized skill mode (ultrabrain, system_architect, debug_oracle, security_auditor, refactor_master, polyglot)"
    )
    parser.add_argument(
        "-w", "--workspace",
        type=str,
        default=".",
        help="Workspace directory path (default: current directory)"
    )
    parser.add_argument(
        "--show-thinking",
        action="store_true",
        help="Display live thinking/reasoning stream"
    )
    parser.add_argument(
        "--hide-thinking",
        action="store_true",
        help="Hide live thinking/reasoning stream"
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Automatically approve and execute all tool actions without asking"
    )
    parser.add_argument(
        "--ask-approve",
        action="store_true",
        help="Ask user confirmation before executing any tool action"
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available models and exit"
    )
    parser.add_argument(
        "--update", "-u",
        action="store_true",
        help="Check and automatically update yncli to the latest version"
    )

    args = parser.parse_args()

    if args.update:
        from yncli.update_checker import perform_self_update
        perform_self_update()
        sys.exit(0)

    config = load_config()

    base_url = config.get("base_url")
    api_key = config.get("api_key")
    model = args.model or config.get("model")
    mode = args.mode or config.get("mode", "build")

    client = LLMClient(base_url=base_url, api_key=api_key)

    if args.list_models:
        print(f"[INFO] Connecting to {base_url}...")
        models = client.list_models()
        if not models:
            print("[ERROR] Failed to fetch models or no models returned.")
        else:
            print(f"[INFO] Available Models ({len(models)}):")
            for m in models:
                print(f" - {m.get('id')} ({m.get('owned_by')})")
        sys.exit(0)

    # Determine thinking visibility
    show_thinking = config.get("show_thinking", False)
    if args.show_thinking:
        show_thinking = True
    elif args.hide_thinking:
        show_thinking = False

    # Determine approval mode
    auto_approve = config.get("auto_approve", False)
    if args.auto_approve:
        auto_approve = True
    elif args.ask_approve:
        auto_approve = False

    agent = Agent(
        client=client,
        model=model,
        workspace_dir=args.workspace,
        mode=mode,
        auto_approve=auto_approve,
        show_thinking=show_thinking
    )

    if args.skill:
        agent.skills_mgr.set_active_skill(args.skill)
    else:
        agent.skills_mgr.set_active_skill("ultrabrain")

    tui = TerminalUI(agent=agent)

    if args.prompt:
        query = " ".join(args.prompt).strip()
        tui.execute_turn(query)
    else:
        tui.run_interactive_loop()


if __name__ == "__main__":
    main()
