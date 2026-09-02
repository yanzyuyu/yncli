# YNCLI One-Line Installer for Windows PowerShell
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Installing YNCLI Autonomous AI Agent... " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Check Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command py -ErrorAction SilentlyContinue
}

if (-not $pythonCmd) {
    Write-Host "[ERROR] Python 3 tidak ditemukan di sistem Anda." -ForegroundColor Red
    Write-Host "Silakan download dan install Python 3 dari https://www.python.org/downloads/ (centang 'Add Python to PATH')" -ForegroundColor Yellow
    exit 1
}

# 2. Install from PyPI
Write-Host "Installing yncli from PyPI via pip..." -ForegroundColor Cyan
& $pythonCmd.Source -m pip install --upgrade yncli

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] YNCLI berhasil diinstal!" -ForegroundColor Green
    Write-Host "Ketik 'yncli' di terminal mana saja untuk memulai." -ForegroundColor Yellow
} else {
    Write-Host "[ERROR] Gagal menginstal YNCLI." -ForegroundColor Red
}
