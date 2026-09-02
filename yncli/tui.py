import os
import sys
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text
from rich.syntax import Syntax
from rich.status import Status
from rich.columns import Columns

from yncli.agent import Agent
from yncli.config import save_config, CONFIG_DIR
from yncli.clean_text import clean_text_for_terminal
from yncli.version import __version__
from yncli.update_checker import check_for_updates_fast


class TerminalUI:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.console = Console(force_terminal=True, soft_wrap=True)
        self.session = None
        self._active_spinner: Optional[Status] = None
        self._pasted_blocks: Dict[str, str] = {}

    def _stop_spinner(self) -> None:
        if self._active_spinner:
            try:
                self._active_spinner.stop()
            except Exception:
                pass
            self._active_spinner = None

    def _start_spinner(self, text: str) -> None:
        self._stop_spinner()
        try:
            self._active_spinner = self.console.status(text, spinner="dots")
            self._active_spinner.start()
        except Exception:
            pass

    def _get_prompt_session(self):
        if self.session is None:
            try:
                from prompt_toolkit import PromptSession
                from prompt_toolkit.history import FileHistory
                from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
                from prompt_toolkit.styles import Style
                from prompt_toolkit.completion import Completer, Completion

                CONFIG_DIR.mkdir(parents=True, exist_ok=True)
                history_file = CONFIG_DIR / "history.txt"

                prompt_style = Style.from_dict({
                    "prompt": "#38bdf8",
                    "arrow": "#a855f7",
                    "completion-menu.completion": "bg:#1e1e2e #cdd6f4",
                    "completion-menu.completion.current": "bg:#313244 #89b4fa bold",
                    "completion-menu.meta": "bg:#181825 #a6adc8",
                })

                class MentionCompleter(Completer):
                    def __init__(self, workspace_memory):
                        self.workspace_memory = workspace_memory

                    def get_completions(self, document, complete_event):
                        text = document.text_before_cursor
                        # Check if user just typed '@' or is typing a path after '@'
                        if "@" in text:
                            last_at = text.rfind("@")
                            word = text[last_at + 1:]
                            # Offer completion for files in workspace tree
                            for fpath in self.workspace_memory.file_tree:
                                if fpath.lower().startswith(word.lower()) or word.lower() in fpath.lower():
                                    yield Completion(
                                        fpath,
                                        start_position=-len(word),
                                        display=f"@{fpath}",
                                        display_meta="file"
                                    )

                from prompt_toolkit.key_binding import KeyBindings
                from prompt_toolkit.keys import Keys

                completer = MentionCompleter(self.agent.workspace_memory)
                kb = KeyBindings()

                # Hidden paste store for current prompt session
                self._pasted_blocks = {}

                @kb.add(Keys.BracketedPaste)
                def _(event):
                    data = event.data
                    line_count = len(data.splitlines())
                    # If pasted text is multiline or long (>= 2 lines or > 120 chars)
                    if line_count >= 2 or len(data) > 150:
                        paste_id = f"PASTE_BLOCK_{len(self._pasted_blocks) + 1}"
                        self._pasted_blocks[paste_id] = {
                            "token": f"[ pasted {line_count} lines ]",
                            "data": data
                        }
                        event.current_buffer.insert_text(f"[ pasted {line_count} lines ]")
                    else:
                        event.current_buffer.insert_text(data)

                self.session = PromptSession(
                    history=FileHistory(str(history_file)),
                    auto_suggest=AutoSuggestFromHistory(),
                    completer=completer,
                    key_bindings=kb,
                    style=prompt_style
                )
            except Exception:
                self.session = False
        return self.session

    def print_banner(self) -> None:
        cwd = Path(self.agent.workspace_dir).resolve()
        folder_name = cwd.name or str(cwd)
        cwd_str = str(cwd).replace(str(Path.home()), "~")
        mode_title = self.agent.mode.capitalize()
        mode_color = "#38bdf8" if self.agent.mode == "plan" else ("#10b981" if self.agent.mode == "build" else "#f59e0b")

        # Top pill badge
        self.console.print()
        pill = Text()
        pill.append(f" {folder_name} ", style="bold black on #f59e0b")
        pill.append("  yncli", style="dim white")
        self.console.print(pill)
        self.console.print()

        # Rainbow pixel letter 'Y' logo
        logo = Text()
        logo.append("██       ██\n", style="bold #ef4444")
        logo.append(" ██     ██ \n", style="bold #f97316")
        logo.append("  ██   ██  \n", style="bold #eab308")
        logo.append("   ██ ██   \n", style="bold #22c55e")
        logo.append("    ███    \n", style="bold #06b6d4")
        logo.append("     █     \n", style="bold #3b82f6")
        logo.append("     █     ", style="bold #a855f7")

        # Info metadata
        info = Text()
        info.append(f"yncli {__version__}\n", style="bold #60a5fa")
        info.append("Autonomous Polyglot AI Coding Agent\n", style="dim white")
        info.append(f"{self.agent.model} ", style="white")
        info.append(f"({mode_title} Mode)\n", style=mode_color)
        info.append(f"{cwd_str}\n", style="dim")

        cols = Columns([logo, info], padding=(0, 3))
        self.console.print(cols)

        # Check for available update (Fast check & cache)
        update_info = check_for_updates_fast(timeout_sec=0.8)
        if update_info:
            update_panel = Panel(
                f"[bold yellow]🔔 Update Tersedia:[/] [dim]v{update_info['current']}[/] → [bold green]v{update_info['latest']}[/]\n"
                f"[dim]Ketik [bold cyan]/update[/bold cyan] untuk memperbarui & restart otomatis, atau jalankan:[reset]\n"
                f"• [cyan]yncli --update[/cyan]   • [cyan]npm i -g @yanzyuyu/yncli[/cyan]",
                border_style="yellow",
                padding=(0, 2)
            )
            self.console.print(update_panel)

        self.console.print("─" * 60, style="dim #334155")
        
        loaded_count = len(self.agent.workspace_memory.indexed_files)
        total_files = len(self.agent.workspace_memory.file_tree)
        self.console.print(f"[dim]Project: [cyan]{self.agent.workspace_memory.project_type}[/cyan] ({loaded_count}/{total_files} files loaded into active memory)[/dim]\n")

    def print_help(self) -> None:
        table = Table(title="Panduan Perintah", border_style="dim cyan", show_header=True)
        table.add_column("Perintah", style="yellow")
        table.add_column("Keterangan", style="white")
        
        table.add_row("/model, /models", "Buka popup interaktif untuk memilih model AI (klik mouse / panah)")
        table.add_row("/default, /reset", "Kembalikan provider & model ke bawaan (Model ag/*, cx/*)")
        table.add_row("/google <api_key>", "Hubungkan langsung ke Google AI Studio Gemini API Key Anda")
        table.add_row("/key <api_key>", "Ganti API Key kustom Anda")
        table.add_row("/endpoint <url>", "Ganti Endpoint API kustom (OpenAI, Ollama, OpenRouter, Groq, dll)")
        table.add_row("/plan", "Masuk ke Plan Mode (Riset & susun PRD plan.md otomatis)")
        table.add_row("/build", "Masuk ke Build Mode (Eksekusi autonomous pembuatan & editing kode)")
        table.add_row("/ask", "Masuk ke Ask Mode (Konsultasi murni tanpa modifikasi file)")
        table.add_row("/update, /upgrade", "Perbarui yncli ke versi terbaru & restart otomatis")
        table.add_row("/cd <folder>", "Pindah direktori kerja aktif")
        table.add_row("/pwd", "Lihat path direktori saat ini")
        table.add_row("/approval [on|off]", "Atur persetujuan tool (on = otomatis, off = tanya dulu)")
        table.add_row("/thinking [on|off]", "Tampilkan atau sembunyikan live reasoning")
        table.add_row("/skill <nama>", "Pilih skill (ultrabrain, system_architect, debug_oracle, dll)")
        table.add_row("/clear", "Bersihkan memori percakapan sesi ini")
        table.add_row("/save [file]", "Simpan percakapan ke file Markdown")
        table.add_row("/exit, /quit", "Keluar dari yncli")
        
        self.console.print(table)

    def open_model_popup_selector(self) -> None:
        self._start_spinner("[dim cyan]Mengambil daftar model dari server...[/dim cyan]")
        try:
            models = self.agent.client.list_models()
        finally:
            self._stop_spinner()

        if not models:
            self.console.print("[red]Gagal mengambil daftar model dari server.[/red]")
            return

        # Filter out dead / zero-quota prefixes from provider (e.g. 'guts/' which returns 402 Payment Required)
        # Prioritize top working models: 'ag/', 'cx/'
        def model_sort_key(m_dict):
            mid = m_dict.get("id", "")
            if mid.startswith("ag/"):
                return (0, mid)
            elif mid.startswith("cx/"):
                return (1, mid)
            elif mid.startswith("cbcn/"):
                return (3, mid)
            elif mid.startswith("guts/"):
                return (4, mid)
            return (2, mid)

        sorted_models = sorted(models, key=model_sort_key)
        
        values = []
        for m in sorted_models:
            mid = m.get("id", "")
            # Skip completely unpayable/broken models
            if mid.startswith("guts/"):
                continue
            
            badge = ""
            if mid.startswith("ag/"):
                badge = " ⭐ (Ultra Fast & Stable)"
            elif mid.startswith("cx/"):
                badge = " ⚡ (Active)"
            elif mid in ("gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3-flash-preview"):
                badge = " ⭐ (Google Official - Ultra Fast & Active)"
            elif "pro" in mid:
                badge = " ⚠️ (Tier Pro - Butuh Saldo/Billing)"
            
            label = f"{mid}{badge}"
            values.append((mid, label))

        try:
            from prompt_toolkit.shortcuts import radiolist_dialog
            from prompt_toolkit.styles import Style

            dialog_style = Style.from_dict({
                "dialog": "bg:#1e1e2e",
                "dialog.body": "bg:#181825 #cdd6f4",
                "dialog.title": "bg:#313244 #89b4fa bold",
                "dialog.border": "#89b4fa",
                "button.focused": "bg:#a6e3a1 #11111b bold",
                "radio-selected": "bold #a6e3a1",
            })

            result = radiolist_dialog(
                title="Pilih Model AI (Gunakan Panah / Klik Mouse)",
                text=f"Model aktif: {self.agent.model}\nPilih model di bawah lalu klik OK atau tekan Enter:",
                values=values,
                default=self.agent.model,
                style=dialog_style
            ).run()

            if result:
                self.agent.set_model(result)
                save_config({"model": result})
                self.console.print(f"[green]Model berhasil diubah ke: [cyan]{result}[/cyan][/green]")
                self.console.print(f"[dim]Memory refreshed: {len(self.agent.workspace_memory.indexed_files)} files active in memory[/dim]")
            else:
                self.console.print("[dim]Pemilihan model dibatalkan.[/dim]")

        except Exception:
            self.console.print("[cyan]Daftar Model Tersedia:[/cyan]")
            for idx, (mid, label) in enumerate(values, start=1):
                marker = "(*)" if mid == self.agent.model else "( )"
                self.console.print(f" {idx:2d}. {marker} [cyan]{mid}[/cyan]")
            self.console.print("\nMasukkan nomor model atau ID model: ", end="")
            try:
                choice = input().strip()
                if choice.isdigit() and 1 <= int(choice) <= len(values):
                    sel = values[int(choice) - 1][0]
                    self.agent.set_model(sel)
                    save_config({"model": sel})
                    self.console.print(f"[green]Model diubah ke: [cyan]{sel}[/cyan][/green]")
                elif choice in [v[0] for v in values]:
                    self.agent.set_model(choice)
                    save_config({"model": choice})
                    self.console.print(f"[green]Model diubah ke: [cyan]{choice}[/cyan][/green]")
            except Exception:
                pass

    def handle_slash_command(self, cmd_line: str) -> bool:
        parts = cmd_line.strip().split()
        if not parts:
            return True
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in ("/exit", "/quit", "exit", "quit"):
            self.console.print("\n[yellow]Sesi selesai. Sampai jumpa![/yellow]\n")
            sys.exit(0)

        elif cmd == "/help":
            self.print_help()
            return True

        elif cmd in ("/model", "/models"):
            if not args:
                self.open_model_popup_selector()
                return True
            new_model = args[0].strip()
            self.agent.set_model(new_model)
            save_config({"model": new_model})
            self.console.print(f"[green]Model berhasil diganti ke: [cyan]{new_model}[/cyan][/green]")
            return True

        elif cmd in ("/endpoint", "/baseurl"):
            if not args:
                self.console.print(f"Endpoint API saat ini: [cyan]{self.agent.client.base_url}[/cyan]")
                self.console.print("Gunakan: [yellow]/endpoint <url_base_api>[/yellow] (contoh: https://api.openai.com/v1 atau http://localhost:11434/v1)")
                return True
            new_url = args[0].strip().rstrip("/")
            self.agent.client.base_url = new_url
            save_config({"base_url": new_url})
            self.console.print(f"[green]Endpoint API berhasil diganti ke: [cyan]{new_url}[/cyan][/green]")
            return True

        elif cmd in ("/default", "/reset", "/reset-api"):
            from yncli.config import DEFAULT_BASE_URL, DEFAULT_API_KEY, DEFAULT_MODEL
            self.agent.client.base_url = DEFAULT_BASE_URL
            self.agent.client.api_key = DEFAULT_API_KEY
            self.agent.set_model(DEFAULT_MODEL)
            save_config({
                "base_url": DEFAULT_BASE_URL,
                "api_key": DEFAULT_API_KEY,
                "model": DEFAULT_MODEL
            })
            self.console.print("[bold green]Berhasil reset ke konfigurasi bawaan (Default Provider)![/bold green]")
            self.console.print(f"Endpoint: [cyan]{DEFAULT_BASE_URL}[/cyan]")
            self.console.print(f"Model aktif: [cyan]{DEFAULT_MODEL}[/cyan] (Daftar model ag/*, cx/* kembali tersedia via [yellow]/model[/yellow])")
            return True

        elif cmd in ("/key", "/apikey"):
            if not args:
                masked = self.agent.client.api_key[:6] + "..." + self.agent.client.api_key[-4:] if len(self.agent.client.api_key) > 10 else "***"
                self.console.print(f"API Key saat ini: [cyan]{masked}[/cyan]")
                self.console.print("Gunakan: [yellow]/key <api_key_anda>[/yellow]")
                return True
            new_key = args[0].strip()
            self.agent.client.api_key = new_key
            save_config({"api_key": new_key})
            self.console.print("[green]API Key berhasil disimpan dan diperbarui.[/green]")
            return True

        elif cmd in ("/google", "/gemini"):
            if not args:
                self.console.print("Gunakan: [yellow]/google <google_api_key>[/yellow]")
                self.console.print("Contoh: [cyan]/google AIzaSy...[/cyan] atau [cyan]/google AQ.Ab8...[/cyan]")
                return True
            g_key = args[0].strip()
            g_endpoint = "https://generativelanguage.googleapis.com/v1beta/openai"
            g_model = "gemini-3.6-flash"
            self.agent.client.base_url = g_endpoint
            self.agent.client.api_key = g_key
            self.agent.set_model(g_model)
            save_config({
                "base_url": g_endpoint,
                "api_key": g_key,
                "model": g_model
            })
            self.console.print("[bold green]Berhasil terhubung ke Google Gemini AI Studio![/bold green]")
            self.console.print(f"Endpoint: [cyan]{g_endpoint}[/cyan]")
            self.console.print(f"Model aktif: [cyan]{g_model}[/cyan] (Ketik [yellow]/model[/yellow] untuk memilih model Gemini lainnya)")
            return True

        elif cmd == "/plan":
            self.agent.set_mode("plan")
            save_config({"mode": "plan"})
            self.console.print("[green]Mode aktif: [cyan]Plan Mode[/cyan] (Riset arsitektur & susun PRD plan.md).[/green]")
            return True

        elif cmd == "/build":
            self.agent.set_mode("build")
            save_config({"mode": "build"})
            self.console.print("[green]Mode aktif: [cyan]Build Mode[/cyan] (Eksekusi autonomous pembuatan & editing kode).[/green]")
            return True

        elif cmd == "/ask":
            self.agent.set_mode("ask")
            save_config({"mode": "ask"})
            self.console.print("[green]Mode aktif: [cyan]Ask Mode[/cyan] (Konsultasi murni tanpa modifikasi file).[/green]")
            return True

        elif cmd in ("/mode", "/modes"):
            if not args:
                self.console.print(f"Mode saat ini: [cyan]{self.agent.mode.capitalize()} Mode[/cyan]")
                self.console.print("Pilihan mode: [yellow]/plan[/yellow], [yellow]/build[/yellow], [yellow]/ask[/yellow]")
                return True
            m = args[0].lower()
            if m in ("plan", "build", "ask"):
                self.agent.set_mode(m)
                save_config({"mode": m})
                self.console.print(f"[green]Mode diubah ke: [cyan]{m.capitalize()} Mode[/cyan][/green]")
            else:
                self.console.print("[red]Mode tidak valid. Pilihan: plan, build, ask[/red]")
            return True

        elif cmd == "/cd":
            if not args:
                self.console.print(f"Direktori saat ini: [cyan]{Path(self.agent.workspace_dir).resolve()}[/cyan]")
                self.console.print("Gunakan: [yellow]/cd <path_direktori>[/yellow]")
                return True
            target_path = " ".join(args).strip()
            from yncli.tools.system_tools import change_directory
            res = change_directory(target_path, current_cwd=self.agent.workspace_dir)
            if res.get("success"):
                self.agent.set_workspace_dir(res["new_cwd"])
                self.console.print(f"[green]Direktori dipindahkan ke: [cyan]{res['new_cwd']}[/cyan][/green]")
                self.console.print(f"[dim]Workspace re-indexed: {len(self.agent.workspace_memory.indexed_files)} files loaded[/dim]")
            else:
                self.console.print(f"[red]Gagal pindah direktori: {res.get('message')}[/red]")
            return True

        elif cmd == "/pwd":
            self.console.print(f"Direktori kerja: [cyan]{Path(self.agent.workspace_dir).resolve()}[/cyan]")
            return True

        elif cmd == "/thinking":
            if not args:
                cur = "Aktif" if self.agent.show_thinking else "Mati"
                self.console.print(f"Status Thinking: [cyan]{cur}[/cyan] (Gunakan: /thinking on | /thinking off)")
                return True
            val = args[0].lower() in ("on", "true", "1", "yes", "enable")
            self.agent.set_show_thinking(val)
            save_config({"show_thinking": val})
            status = "Diaktifkan" if val else "Dimatikan"
            self.console.print(f"[green]Thinking {status}.[/green]")
            return True

        elif cmd in ("/approval", "/auto"):
            if not args:
                cur = "Otomatis" if self.agent.auto_approve else "Tanya dulu"
                self.console.print(f"Persetujuan tool: [cyan]{cur}[/cyan] (Gunakan: /approval on | /approval off)")
                return True
            val = args[0].lower() in ("on", "auto", "true", "1", "yes", "otomatis")
            self.agent.set_auto_approve(val)
            save_config({"auto_approve": val})
            status = "Otomatis (Langsung eksekusi)" if val else "Tanya dulu (Konfirmasi manual)"
            self.console.print(f"[green]Persetujuan tool diubah ke: [cyan]{status}[/cyan][/green]")
            return True

        elif cmd == "/clear":
            self.agent.reset_history()
            self.agent.workspace_memory.refresh()
            self.console.print("[green]Riwayat percakapan telah dibersihkan & memori workspace diperbarui.[/green]")
            return True

        elif cmd == "/skills":
            skills = self.agent.skills_mgr.list_skills()
            current = self.agent.skills_mgr.active_skill
            self.console.print(f"Skill aktif: [green]{current}[/green]\nDaftar skill yang tersedia:")
            for s in skills:
                marker = "* " if s == current else "  "
                self.console.print(f"{marker}[cyan]{s}[/cyan]")
            return True

        elif cmd == "/skill":
            if not args:
                self.console.print("Gunakan: [yellow]/skill <nama_skill>[/yellow] (contoh: /skill ultrabrain)")
                return True
            skill_name = args[0].lower().strip()
            if self.agent.skills_mgr.set_active_skill(skill_name):
                self.console.print(f"[green]Skill aktif: [cyan]{skill_name}[/cyan][/green]")
            else:
                self.console.print(f"[red]Skill '{skill_name}' tidak ditemukan.[/red]")
            return True

        elif cmd == "/tools":
            from yncli.tools import AGENT_TOOLS
            table = Table(title="Daftar Alat (Tools)", border_style="dim magenta")
            table.add_column("Nama", style="yellow")
            table.add_column("Fungsi", style="white")
            for t in AGENT_TOOLS:
                fn = t.get("function", {})
                table.add_row(fn.get("name", ""), fn.get("description", ""))
            self.console.print(table)
            return True

        elif cmd in ("/update", "/upgrade"):
            from yncli.update_checker import perform_self_update
            success = perform_self_update()
            if success:
                self.console.print("\n[bold green]Pembaruan selesai! Silakan jalankan kembali:[/bold green] [bold cyan]yncli[/bold cyan]\n")
                sys.exit(0)
            return True

        elif cmd == "/save":
            fname = args[0] if args else f"chat_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            lines = [f"# yncli export - {datetime.datetime.now().isoformat()}\n\n"]
            for msg in self.agent.history:
                role = msg.get("role", "").capitalize()
                content = msg.get("content") or ""
                lines.append(f"### {role}\n\n{content}\n\n---\n")
            with open(fname, "w", encoding="utf-8") as f:
                f.writelines(lines)
            self.console.print(f"[green]Percakapan disimpan ke: [cyan]{fname}[/cyan][/green]")
            return True

        else:
            self.console.print(f"[red]Perintah tidak dikenal:[/red] '{cmd}'. Ketik [yellow]/help[/yellow] untuk bantuan.")
            return True

    def run_interactive_loop(self) -> None:
        self.print_banner()
        ps = self._get_prompt_session()

        while True:
            try:
                self.console.print()
                prompt_label = f"{self.agent.mode} > "
                if ps:
                    user_input = ps.prompt([
                        ("class:prompt", prompt_label),
                    ]).strip()
                else:
                    self.console.print(f"[cyan]{prompt_label}[/cyan]", end="")
                    user_input = input().strip()

                if not user_input:
                    continue

                if user_input.startswith("/"):
                    self.handle_slash_command(user_input)
                    continue

                if getattr(self, "_pasted_blocks", None):
                    for pid, pinfo in list(self._pasted_blocks.items()):
                        tok = pinfo.get("token", "")
                        raw_data = pinfo.get("data", "")
                        if tok and tok in user_input:
                            user_input = user_input.replace(tok, f"\n```\n{raw_data}\n```\n", 1)
                        else:
                            # Fallback if user edited whitespace around token
                            import re
                            def _repl(match):
                                return f"\n```\n{raw_data}\n```\n"
                            user_input = re.sub(r'\[\s*pasted\s+\d+\s+lines?\s*\]', _repl, user_input, count=1)
                    self._pasted_blocks.clear()

                self.execute_turn(user_input)

            except (KeyboardInterrupt, EOFError):
                self.console.print("\n[dim](Sesi dihentikan. Ketik /exit untuk keluar)[/dim]")
            except Exception as e:
                self.console.print(f"\n[red]Error: {str(e)}[/red]")

    def ask_tool_confirmation(self, name: str, args: Dict[str, Any]) -> bool:
        self._stop_spinner()
        self.console.print()
        
        target_path = args.get("file_path", args.get("path", args.get("command", "")))
        content = args.get("content", args.get("replacement_content", ""))

        if name in ("write_file", "edit_file_replace", "save_plan_document") and content:
            lines = content.strip().split("\n")
            line_count = len(lines)
            self.console.print(f"[bold white]{target_path}[/bold white]  [dim #38bdf8]+{line_count}[/dim #38bdf8]")
            
            preview_lines = lines[:12]
            for idx, line in enumerate(preview_lines, start=1):
                clean_l = clean_text_for_terminal(line[:80])
                self.console.print(f" [dim]{idx:2d}[/dim] [green]+[/green] [dim cyan]{clean_l}[/dim cyan]")
            
            if line_count > 12:
                self.console.print(f" [dim]... {line_count - 12} baris lainnya[/dim]")
            self.console.print("Reason: File modification in workspace\n", style="dim")
            prompt_title = f"Allow execution of {name} on this file?"
        else:
            args_summary = ", ".join(f"{k}={repr(v)[:50]}" for k, v in args.items())
            self.console.print(f"[bold white]{name}[/bold white]({args_summary})")
            self.console.print("Reason: Terminal / Tool execution\n", style="dim")
            prompt_title = f"Allow execution of {name}?"

        self.console.print(f"[bold white]{prompt_title}[/bold white]")
        self.console.print("  [bold #38bdf8]> 1. Yes, allow execution[/bold #38bdf8]")
        self.console.print("    2. Yes, and always allow (enable auto-approve)")
        self.console.print("    3. No, deny execution")
        self.console.print("\nPilih (1/2/3 atau y/a/n): ", end="")

        try:
            choice = input().strip().lower()
            if choice in ("2", "a", "all", "always"):
                self.agent.set_auto_approve(True)
                save_config({"auto_approve": True})
                self.console.print("[green]Auto-approve diaktifkan untuk aksi berikutnya.[/green]\n")
                return True
            elif choice in ("1", "y", "ya", "yes", ""):
                self.console.print()
                return True
            else:
                self.console.print("[dim red]Aksi dibatalkan.[/dim red]\n")
                return False
        except (KeyboardInterrupt, EOFError):
            self.console.print("\n[dim red]Aksi dibatalkan.[/dim red]\n")
            return False

    def execute_turn(self, user_prompt: str) -> None:
        content_chunks = []
        is_thinking = False
        step_history: List[str] = []

        from yncli.mention_resolver import resolve_file_mentions
        resolved_prompt, attached_files = resolve_file_mentions(user_prompt, workspace_dir=self.agent.workspace_dir)

        if attached_files:
            pills = []
            for af in attached_files:
                pills.append(f"[bold cyan]@{af['path']}[/bold cyan] [dim]({af['lines']} baris)[/dim]")
            self.console.print(f"[dim]📎 Menyertakan file:[/dim] {', '.join(pills)}")

        def _update_live_display(current_status: str) -> None:
            # Maintain max 3 recent steps
            display_lines = list(step_history[-2:]) + [f"[bold cyan]●[/bold cyan] {current_status}"]
            banner_text = "\n".join(display_lines)
            self._start_spinner(banner_text)

        def on_status_update(status_text: str) -> None:
            if not is_thinking:
                _update_live_display(f"[bold #38bdf8][ - ][/bold #38bdf8] {status_text}")

        def on_thinking(chunk: str) -> None:
            nonlocal is_thinking
            self._stop_spinner()
            clean_chunk = clean_text_for_terminal(chunk)
            if not is_thinking:
                self.console.print("[dim cyan]Thinking:[/dim cyan]\n", style="dim")
                is_thinking = True
            sys.stdout.write(clean_chunk)
            sys.stdout.flush()

        def on_content(chunk: str) -> None:
            nonlocal is_thinking
            clean_chunk = clean_text_for_terminal(chunk)
            if is_thinking:
                self.console.print("\n")
                is_thinking = False
            content_chunks.append(clean_chunk)

        def on_tool_start(name: str, args: Dict[str, Any]) -> None:
            nonlocal is_thinking
            if is_thinking:
                self.console.print("\n")
                is_thinking = False

            target = args.get("file_path", args.get("path", args.get("command", args.get("query", ""))))
            if len(str(target)) > 40:
                target = str(target)[:40] + "..."
            
            tool_stage_map = {
                "list_directory": f"Memeriksa struktur folder ({target})",
                "find_files": f"Mencari file ({target})",
                "grep_search": f"Mencari isi kode ({target})",
                "read_file": f"Membaca file ({target})",
                "write_file": f"Building & menulis file ({target})",
                "edit_file_replace": f"Memperbarui kode ({target})",
                "save_plan_document": f"Menyimpan rencana ({target})",
                "run_terminal_command": f"Menjalankan perintah terminal ({target})",
                "web_search": f"Riset web ({target})",
                "fetch_webpage": f"Mengambil referensi web ({target})",
                "change_directory": f"Berpindah direktori ({target})"
            }
            stage_desc = tool_stage_map.get(name, f"Eksekusi {name} ({target})")
            
            # Add previous action as completed step (max 3 sliding window)
            step_history.append(f"[dim green]✔[/dim green] [dim]{stage_desc}[/dim]")
            if len(step_history) > 3:
                step_history.pop(0)

            _update_live_display(f"[bold #f59e0b][ - ][/bold #f59e0b] [bold white]{stage_desc}[/bold white]")

        def on_tool_end(name: str, output: str) -> None:
            pass

        _update_live_display(f"[bold #38bdf8][ - ][/bold #38bdf8] Menganalisis instruksi ({self.agent.model})...")
        try:
            res = self.agent.run_turn(
                user_prompt=resolved_prompt,
                on_thinking=on_thinking,
                on_content=on_content,
                on_tool_start=on_tool_start,
                on_tool_end=on_tool_end,
                on_tool_confirm=self.ask_tool_confirmation,
                on_status_update=on_status_update
            )
        finally:
            self._stop_spinner()

        # Render full Markdown with Rich (renders **bold**, headers, syntax highlighting)
        final_text = clean_text_for_terminal("".join(content_chunks) or res.get("content", ""))
        if final_text:
            self.console.print()
            try:
                self.console.print(Markdown(final_text))
            except Exception:
                self.console.print(final_text)

        # Plan Mode transition workflow: Auto prompt to Build
        if self.agent.mode == "plan" and final_text:
            plan_file = Path(self.agent.workspace_dir).resolve() / "plan.md"
            if plan_file.exists():
                self.console.print(f"\n[green]• Dokumen PRD rencana implementasi telah dibuat di: [bold cyan]{plan_file}[/bold cyan][/green]")
            
            self.console.print("\n[bold white]Mau langsung dieksekusi / build sekarang?[/bold white]")
            self.console.print("  [bold #10b981]> 1. Ya, beralih ke Build Mode dan mulai bangun kode[/bold #10b981]")
            self.console.print("    2. Tidak, tetap di Plan Mode")
            self.console.print("\nPilih (1/2 atau y/n): ", end="")
            try:
                answer = input().strip().lower()
                if answer in ("1", "y", "ya", "yes", ""):
                    self.agent.set_mode("build")
                    save_config({"mode": "build"})
                    self.console.print("\n[green]Beralih ke Build Mode. Memulai eksekusi implementasi rencana...[/green]\n")
                    self.execute_turn("Rencana di plan.md telah disetujui. Buka plan.md dan mulai eksekusi pembuatan/pembaruan kode secara tuntas.")
                else:
                    self.console.print("[dim]Tetap berada dalam Plan Mode.[/dim]")
            except (KeyboardInterrupt, EOFError):
                pass
