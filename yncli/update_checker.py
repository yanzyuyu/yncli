import json
import time
import sys
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

from yncli.version import __version__
from yncli.config import CONFIG_DIR

CACHE_FILE = CONFIG_DIR / "update_cache.json"


def parse_version_tuple(v: str):
    """Parse version string into tuple of ints for accurate semver comparison."""
    try:
        clean = v.strip().lstrip("v").split("-")[0]
        return tuple(int(x) for x in clean.split(".") if x.isdigit())
    except Exception:
        return (0, 0, 0)


def fetch_latest_version_live(timeout_sec: float = 1.2) -> Optional[str]:
    """Queries PyPI directly to get the absolute latest published version."""
    try:
        import requests
        resp = requests.get("https://pypi.org/pypi/yncli/json", timeout=timeout_sec)
        if resp.status_code == 200:
            data = resp.json()
            latest = data.get("info", {}).get("version")
            if latest:
                CONFIG_DIR.mkdir(parents=True, exist_ok=True)
                CACHE_FILE.write_text(json.dumps({
                    "last_checked": time.time(),
                    "latest_version": latest
                }, indent=2), encoding="utf-8")
                return latest
    except Exception:
        pass
    return None


def get_cached_update() -> Optional[Dict[str, Any]]:
    """Returns update info from cache if available."""
    try:
        if CACHE_FILE.exists():
            data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            latest_str = data.get("latest_version")
            if latest_str:
                curr_tuple = parse_version_tuple(__version__)
                latest_tuple = parse_version_tuple(latest_str)
                if latest_tuple > curr_tuple:
                    return {
                        "current": __version__,
                        "latest": latest_str
                    }
    except Exception:
        pass
    return None


def check_for_updates_fast(timeout_sec: float = 1.2) -> Optional[Dict[str, Any]]:
    """
    Checks for updates immediately on every startup with a fast 1.2s timeout.
    Falls back to cached update if offline or timeout.
    """
    # 1. Try fast live fetch
    latest_live = fetch_latest_version_live(timeout_sec=timeout_sec)
    if latest_live:
        curr_tuple = parse_version_tuple(__version__)
        latest_tuple = parse_version_tuple(latest_live)
        if latest_tuple > curr_tuple:
            return {
                "current": __version__,
                "latest": latest_live
            }

    # 2. Fallback to cache if network is slow/offline
    return get_cached_update()


def perform_self_update() -> bool:
    """
    Direct self-updater: Runs pip install --upgrade --no-cache-dir yncli
    and optionally npm install -g @yanzyuyu/yncli
    """
    print(f"\n[YNCLI] Memeriksa versi terbaru dari PyPI...")
    latest = fetch_latest_version_live(timeout_sec=5.0)
    curr_tuple = parse_version_tuple(__version__)
    latest_tuple = parse_version_tuple(latest) if latest else curr_tuple

    print(f"[YNCLI] Versi saat ini: v{__version__}")
    if latest:
        print(f"[YNCLI] Versi terbaru: v{latest}")

    if latest and latest_tuple <= curr_tuple:
        print("\n[OK] YNCLI Anda sudah menggunakan versi paling baru!")
        return True

    print("\n[YNCLI] Mengunduh dan menginstal pembaruan...")
    
    # 1. Update Python module via pip with retry (handling PyPI index propagation delay)
    pip_cmd = [
        sys.executable, "-m", "pip", "install",
        "--upgrade", "--no-cache-dir",
        "--disable-pip-version-check",
        f"yncli=={latest}" if latest else "yncli"
    ]
    
    res = subprocess.run(pip_cmd)
    
    # Retry once after short sleep if specific tag failed due to index propagation
    if res.returncode != 0:
        time.sleep(2)
        # Fallback to general --upgrade
        fallback_cmd = [
            sys.executable, "-m", "pip", "install",
            "--upgrade", "--no-cache-dir",
            "--disable-pip-version-check",
            "yncli"
        ]
        res = subprocess.run(fallback_cmd)

    if res.returncode == 0:
        print("\n[SUCCESS] YNCLI berhasil diperbarui ke versi terbaru!")
        print("[YNCLI] Memulai ulang sesi baru...\n")
        # Clear update cache
        CACHE_FILE.unlink(missing_ok=True)
        return True
    else:
        print("\n[ERROR] Gagal memperbarui via pip. Coba jalankan manual:")
        print(f"pip install --upgrade --no-cache-dir yncli\n")
        return False
