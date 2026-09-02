import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

from yncli.client import LLMClient
from yncli.system_prompt import build_system_prompt
from yncli.skills_manager import SkillsManager
from yncli.workspace_memory import WorkspaceMemory
from yncli.tools import AGENT_TOOLS, execute_tool
from yncli.tools.polyglot_tools import validate_code_syntax
from yncli.clean_text import clean_text_for_terminal


class Agent:
    def __init__(
        self,
        client: LLMClient,
        model: str,
        workspace_dir: str = ".",
        mode: str = "build",
        max_tool_iterations: int = 50,
        auto_approve: bool = False,
        show_thinking: bool = False
    ):
        self.client = client
        self.model = model
        self.workspace_dir = workspace_dir
        self.mode = mode.lower()
        self.max_tool_iterations = max_tool_iterations
        self.auto_approve = auto_approve
        self.show_thinking = show_thinking
        self.skills_mgr = SkillsManager(workspace_dir=workspace_dir)
        self.workspace_memory = WorkspaceMemory(workspace_dir=workspace_dir)
        self.history: List[Dict[str, Any]] = []

    def reset_history(self) -> None:
        self.history = []

    def set_model(self, model: str) -> None:
        self.model = model
        self.workspace_memory.refresh()

    def set_mode(self, mode: str) -> None:
        self.mode = mode.lower()

    def set_auto_approve(self, auto_approve: bool) -> None:
        self.auto_approve = auto_approve

    def set_show_thinking(self, show_thinking: bool) -> None:
        self.show_thinking = show_thinking

    def set_workspace_dir(self, new_dir: str) -> None:
        self.workspace_dir = new_dir
        self.skills_mgr = SkillsManager(workspace_dir=new_dir)
        self.workspace_memory = WorkspaceMemory(workspace_dir=new_dir)

    def _get_active_tools(self) -> List[Dict[str, Any]]:
        """
        Enforces strict tool allowlists based on operating mode.
        """
        if self.mode == "ask":
            allowed_names = {"web_search", "fetch_webpage", "read_file"}
            return [t for t in AGENT_TOOLS if t.get("function", {}).get("name") in allowed_names]
        elif self.mode == "plan":
            allowed_names = {
                "read_file", "list_directory", "find_files", "grep_search",
                "web_search", "fetch_webpage", "change_directory", "git_status",
                "save_plan_document"
            }
            return [t for t in AGENT_TOOLS if t.get("function", {}).get("name") in allowed_names]
        else:
            return AGENT_TOOLS

    def run_turn(
        self,
        user_prompt: str,
        on_thinking: Optional[Callable[[str], None]] = None,
        on_content: Optional[Callable[[str], None]] = None,
        on_tool_start: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        on_tool_end: Optional[Callable[[str, str], None]] = None,
        on_tool_confirm: Optional[Callable[[str, Dict[str, Any]], bool]] = None,
        on_status_update: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Executes a multi-turn agentic cycle (ReAct: Reason -> Act -> Observe).
        """
        # Always refresh workspace memory on each turn to capture file updates
        self.workspace_memory.refresh()

        self.history.append({"role": "user", "content": user_prompt})

        total_thinking = []
        final_answer = ""
        iterations = 0
        plan_doc_saved = False
        action_keywords = ["benerin", "upgrade", "perbaiki", "ubah", "tambah", "buat", "fix", "update", "bikin", "desain"]
        is_action_prompt = any(k in user_prompt.lower() for k in action_keywords)
        stalling_detected_and_retried = False

        while iterations < self.max_tool_iterations:
            iterations += 1

            if on_status_update:
                on_status_update(f"Menghubungi AI ({self.model}) [{self.mode.capitalize()} Mode]...")

            # Trim history to avoid huge multi-megabyte payloads causing socket write timeout
            # Keep last 12 messages, truncating large tool outputs
            trimmed_history = []
            for msg in self.history[-12:]:
                m_copy = dict(msg)
                content = m_copy.get("content")
                if content and isinstance(content, str) and len(content) > 15000:
                    m_copy["content"] = content[:15000] + "\n... [Output truncated to preserve context]"
                trimmed_history.append(m_copy)

            system_prompt = build_system_prompt(self.workspace_dir, self.skills_mgr, self.mode, self.workspace_memory)
            messages = [{"role": "system", "content": system_prompt}] + trimmed_history

            thinking_cb = on_thinking if self.show_thinking else None
            tools = self._get_active_tools()

            try:
                response = self.client.stream_chat(
                    messages=messages,
                    model=self.model,
                    tools=tools if tools else None,
                    on_thinking=thinking_cb,
                    on_content=on_content
                )
            except Exception as e:
                raw_err = str(e)
                if "429" in raw_err or "quota" in raw_err.lower() or "14018" in raw_err or "额度" in raw_err:
                    err_msg = f"Kuota token API untuk model '{self.model}' telah habis (Error 429: Quota Exceeded).\nSilakan beralih ke model lain dengan mengetik: /model (contoh: /model ag/claude-sonnet-4-6 atau ag/gemini-3.7-flash-high)"
                else:
                    err_msg = f"Koneksi ke AI terganggu: {raw_err}"
                if on_content:
                    on_content(f"\n[ERROR] {err_msg}\n")
                return {"thinking": "".join(total_thinking), "content": err_msg}

            if response.get("thinking"):
                total_thinking.append(response["thinking"])

            tool_calls = response.get("tool_calls")
            resp_content = response.get("content", "")

            # Stalling & Lazy-Snippet Detection: In BUILD mode, if user asked for fixes/actions and AI only replied with text/markdown snippet without calling write_file/edit_file_replace
            has_markdown_code_block = "```" in resp_content and any(kw in user_prompt.lower() for kw in ["benerin", "fix", "update", "tambah", "error", "buat", "ubah", "atuh", "tolong"])
            is_stalling_text = any(phrase in resp_content.lower() for phrase in ["di mana web", "boleh saya tahu", "apakah proyeknya sudah ada", "bisa anda jelaskan", "butuh beberapa informasi"])
            
            if (
                self.mode == "build"
                and not tool_calls
                and not stalling_detected_and_retried
                and (is_stalling_text or has_markdown_code_block)
            ):
                stalling_detected_and_retried = True
                self.history.append({"role": "assistant", "content": resp_content})
                self.history.append({
                    "role": "user",
                    "content": "[Instruksi Sistem: Anda berada dalam BUILD MODE. Dilarang hanya menampilkan potongan kode di chat! Gunakan fungsi 'edit_file_replace' atau 'write_file' SEKARANG untuk langsung menulis perbaikan ke dalam file fisik yang dituju, lalu jalankan testing/verifikasi jika perlu!]"
                })
                continue

            assistant_msg: Dict[str, Any] = {"role": "assistant"}
            if resp_content:
                assistant_msg["content"] = resp_content
                final_answer = resp_content
            else:
                assistant_msg["content"] = None

            if tool_calls:
                assistant_msg["tool_calls"] = tool_calls
                self.history.append(assistant_msg)

                for tc in tool_calls:
                    fn_name = tc.get("function", {}).get("name", "")
                    raw_args = tc.get("function", {}).get("arguments", "{}")
                    call_id = tc.get("id", f"call_{fn_name}")

                    try:
                        parsed_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                    except Exception:
                        parsed_args = {"raw": raw_args}

                    # Hard Gatekeeper
                    if self.mode == "ask" and fn_name not in ("web_search", "fetch_webpage", "read_file"):
                        tool_output_str = f"[Ditolak] Mode saat ini adalah Ask Mode. Tindakan '{fn_name}' tidak diizinkan. Gunakan /build untuk eksekusi kode atau /plan untuk perencanaan."
                        if on_tool_end:
                            on_tool_end(fn_name, tool_output_str)
                        self.history.append({
                            "role": "tool",
                            "tool_call_id": call_id,
                            "name": fn_name,
                            "content": tool_output_str
                        })
                        continue

                    if self.mode == "plan" and fn_name in ("write_file", "edit_file_replace", "run_terminal_command"):
                        tool_output_str = f"[Ditolak] Mode saat ini adalah Plan Mode. Tindakan memodifikasi file '{fn_name}' hanya diizinkan pada Build Mode. Rencana disimpan via 'save_plan_document'."
                        if on_tool_end:
                            on_tool_end(fn_name, tool_output_str)
                        self.history.append({
                            "role": "tool",
                            "tool_call_id": call_id,
                            "name": fn_name,
                            "content": tool_output_str
                        })
                        continue

                    if on_tool_start:
                        on_tool_start(fn_name, parsed_args)

                    approved = True
                    if not self.auto_approve and on_tool_confirm:
                        approved = on_tool_confirm(fn_name, parsed_args)

                    if not approved:
                        tool_output_str = f"[Dibatalkan] Tindakan '{fn_name}' dibatalkan oleh pengguna."
                    else:
                        if on_status_update:
                            on_status_update(f"Menjalankan: {fn_name}...")

                        tool_res = execute_tool(fn_name, parsed_args, current_cwd=self.workspace_dir)

                        if fn_name == "change_directory" and isinstance(tool_res, dict):
                            if tool_res.get("success"):
                                self.set_workspace_dir(tool_res["new_cwd"])
                            tool_output_str = tool_res["message"]
                        elif fn_name == "save_plan_document":
                            plan_doc_saved = True
                            tool_output_str = str(tool_res)
                        else:
                            tool_output_str = str(tool_res)

                        if fn_name in ("write_file", "edit_file_replace") and "Successfully" in tool_output_str:
                            fpath = parsed_args.get("file_path", "")
                            ext = fpath.split(".")[-1].lower() if "." in fpath else ""
                            ext_to_lang = {
                                "py": "python", "ts": "typescript", "js": "javascript",
                                "rs": "rust", "go": "golang", "cpp": "cpp", "c": "cpp",
                                "php": "php", "rb": "ruby", "cs": "csharp", "java": "java"
                            }
                            if ext in ext_to_lang:
                                check_result = validate_code_syntax(ext_to_lang[ext], file_path=fpath)
                                if check_result.startswith("[FAIL]") or "[FAIL]" in check_result:
                                    tool_output_str += f"\n\n[Peringatan Sintaks]\n{check_result}\nHarap perbaiki error sintaks tersebut."

                    if on_tool_end:
                        on_tool_end(fn_name, tool_output_str)

                    self.history.append({
                        "role": "tool",
                        "tool_call_id": call_id,
                        "name": fn_name,
                        "content": tool_output_str
                    })

                continue
            else:
                self.history.append(assistant_msg)
                break

        if not final_answer:
            summary_messages = [
                {"role": "system", "content": build_system_prompt(self.workspace_dir, self.skills_mgr, self.mode, self.workspace_memory)}
            ] + self.history + [
                {"role": "user", "content": "Tindakan telah selesai. Berikan ringkasan dan jawaban akhir sekarang."}
            ]
            try:
                resp = self.client.stream_chat(
                    messages=summary_messages,
                    model=self.model,
                    on_content=on_content
                )
                final_answer = resp.get("content", "")
                self.history.append({"role": "assistant", "content": final_answer})
            except Exception:
                pass

        # Guarantee plan.md is saved in Plan Mode if AI generated a plan in text
        if self.mode == "plan" and final_answer and not plan_doc_saved:
            plan_file = Path(self.workspace_dir).resolve() / "plan.md"
            try:
                with open(plan_file, "w", encoding="utf-8") as f:
                    f.write(final_answer)
            except Exception:
                pass

        return {
            "thinking": "".join(total_thinking),
            "content": final_answer
        }
