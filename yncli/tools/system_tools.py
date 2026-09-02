import os
import platform
import subprocess
import datetime
from pathlib import Path
from typing import Dict, Any

from yncli.clean_text import clean_text_for_terminal


def get_current_datetime_str() -> str:
    now = datetime.datetime.now()
    return now.strftime("%A, %d %B %Y %H:%M:%S %Z")


def get_system_info(cwd: str = ".") -> Dict[str, Any]:
    now = datetime.datetime.now()
    os_name = platform.system()
    os_release = platform.release()
    shell = "powershell.exe" if os_name == "Windows" else os.getenv("SHELL", "/bin/bash")
    
    info = {
        "datetime": get_current_datetime_str(),
        "date_iso": now.isoformat(),
        "os": f"{os_name} {os_release} ({platform.machine()})",
        "shell": shell,
        "cwd": str(Path(cwd).resolve()),
        "user": os.getenv("USERNAME", os.getenv("USER", "developer")),
    }
    return info


def change_directory(path: str, current_cwd: str = ".") -> Dict[str, Any]:
    """
    Changes the active working directory for the agent.
    """
    target = Path(current_cwd) / Path(path) if not Path(path).is_absolute() else Path(path)
    target = target.resolve()

    if not target.exists():
        return {
            "success": False,
            "message": f"[ERROR] Directory tidak ditemukan: {target}",
            "new_cwd": str(Path(current_cwd).resolve())
        }
    if not target.is_dir():
        return {
            "success": False,
            "message": f"[ERROR] Path bukan direktori: {target}",
            "new_cwd": str(Path(current_cwd).resolve())
        }

    try:
        os.chdir(str(target))
        return {
            "success": True,
            "message": f"[SUCCESS] Berhasil pindah ke direktori: {target}",
            "new_cwd": str(target)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"[ERROR] Gagal berpindah direktori: {str(e)}",
            "new_cwd": str(Path(current_cwd).resolve())
        }


def save_plan_document(content: str, current_cwd: str = ".") -> str:
    """
    Saves the Technical Implementation Plan / PRD into plan.md in the current workspace.
    Sanitizes content to ensure clean UTF-8 formatting.
    """
    plan_path = Path(current_cwd).resolve() / "plan.md"
    try:
        cleaned_content = clean_text_for_terminal(content)
        with open(plan_path, "w", encoding="utf-8") as f:
            f.write(cleaned_content)
        return f"[SUCCESS] Dokumen PRD dan rencana implementasi berhasil disimpan ke: {plan_path}"
    except Exception as e:
        return f"[ERROR] Gagal menyimpan plan.md: {str(e)}"


def run_terminal_command(command: str, timeout: int = 60, cwd: str = ".") -> str:
    work_dir = Path(cwd).resolve()
    if not work_dir.exists():
        return f"[ERROR] Working directory does not exist: {work_dir}"

    is_windows = platform.system() == "Windows"
    
    try:
        if is_windows:
            process = subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace"
            )
        else:
            process = subprocess.run(
                command,
                shell=True,
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace"
            )

        stdout = process.stdout.strip()
        stderr = process.stderr.strip()
        exit_code = process.returncode

        output_parts = []
        if stdout:
            output_parts.append(f"STDOUT:\n{stdout}")
        if stderr:
            output_parts.append(f"STDERR:\n{stderr}")
        if not stdout and not stderr:
            output_parts.append("(Perintah selesai tanpa output)")

        output_parts.append(f"\n[Process exited with code {exit_code}]")
        return "\n".join(output_parts)

    except subprocess.TimeoutExpired:
        return f"[ERROR] Perintah melebihi batas waktu ({timeout} detik)."
    except Exception as e:
        return f"[ERROR] Gagal mengeksekusi perintah: {str(e)}"


def git_status(cwd: str = ".") -> str:
    return run_terminal_command("git status --short", timeout=15, cwd=cwd)


def git_diff(cwd: str = ".", staged: bool = False) -> str:
    cmd = "git diff --cached" if staged else "git diff"
    return run_terminal_command(cmd, timeout=20, cwd=cwd)
