<div align="center">

# ⚡ YNCLI

**Autonomous Polyglot AI Coding Agent & Interactive Terminal Workspace**

[![PyPI Version](https://img.shields.io/pypi/v/yncli.svg?color=blue&style=flat-square)](https://pypi.org/project/yncli/)
[![NPM Version](https://img.shields.io/npm/v/@yanzyuyu/yncli.svg?color=red&style=flat-square)](https://www.npmjs.com/package/@yanzyuyu/yncli)
[![Python Versions](https://img.shields.io/pypi/pyversions/yncli.svg?style=flat-square)](https://pypi.org/project/yncli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

*Langsung paham struktur workspace Anda, merancang rencana arsitektur di `plan.md`, dan mengeksekusi kode multi-bahasa tanpa basa-basi.*

[Dokumentasi Web](https://yanzyuyu.github.io/yncli/) • [Instalasi](#-instalasi--penggunaan) • [Fitur Utama](#-fitur-utama) • [Perintah Konsol](#️-perintah-di-dalam-konsol-slash-commands)

</div>

---

## 💡 Mengapa YNCLI?

Kebanyakan AI CLI hanya memberikan potongan kode di chat yang harus Anda copy-paste manual. **YNCLI adalah agen otonom sejati**:

- 🧠 **Zero-Setup Context Memory**: Otomatis memindai file kode dan konfigurasi proyek Anda ke dalam memori aktif saat dibuka.
- 🎯 **3 Mode Operasi Spesifik**:
  - `Plan Mode`: Merancang PRD, arsitektur sistem, dan menyimpan strategi ke `plan.md`.
  - `Build Mode`: Menulis, memodifikasi, dan memvalidasi kode di disk secara otonom.
  - `Ask Mode`: Konsultasi dan tanya jawab teknis tanpa risiko merusak file.
- 🌐 **Multi-Provider & BYOK (Bring Your Own Key)**:
  - Hubungkan langsung ke **Google Gemini AI Studio** via `/google <api_key>`
  - Hubungkan ke **OpenAI, OpenRouter, Groq, atau Local Ollama** via `/endpoint` & `/key`
  - Gunakan model server bawaan (`ag/claude-sonnet-4-6`, `ag/gemini-3.7-flash-high`) via `/default`.
- ⚡ **Polyglot Syntax Engine**: Validasi otomatis untuk PHP (Laravel), TypeScript/JavaScript, Python, Go, Rust, Java, C++, Ruby, dan C#.
- 📦 **Compact Paste & @Mention**: Paste log error ratusan baris otomatis diringkas menjadi `[ pasted N lines ]`, dan ketik `@nama_file` untuk menyematkan file tertentu.

---

## ⚡ Instalasi & Penggunaan

### 1. Menggunakan Node.js / NPX (Rekomendasi Cepat)
```bash
# Langsung jalankan tanpa instalasi:
npx @yanzyuyu/yncli

# Atau pasang secara global:
npm install -g @yanzyuyu/yncli
yncli
```

### 2. Menggunakan Python / Pip
```bash
# Pasang via pip:
pip install --upgrade yncli
yncli

# Atau via pipx:
pipx run yncli
```

### 3. Script Pasang Otomatis 1 Baris
- **Windows (PowerShell)**:
  ```powershell
  irm https://raw.githubusercontent.com/yanzyuyu/yncli/main/install.ps1 | iex
  ```
- **Linux / macOS (Bash)**:
  ```bash
  curl -fsSL https://raw.githubusercontent.com/yanzyuyu/yncli/main/install.sh | bash
  ```

---

## 🛠️ Contoh Penggunaan

```bash
# Masuk ke sesi interaktif:
yncli

# Eksekusi instruksi langsung 1 baris:
yncli "Buatkan auth controller Laravel dengan JWT token dan unit test"

# Pilih model AI tertentu:
yncli -m ag/claude-sonnet-4-6

# Mulai langsung di Plan Mode:
yncli --mode plan
```

---

## ⌨️ Perintah di Dalam Konsol (Slash Commands)

| Perintah | Fungsi |
| :--- | :--- |
| `/model` | Buka popup interaktif untuk memilih model AI (klik mouse / panah) |
| `/google <key>` | Hubungkan langsung ke Google AI Studio Gemini API Key Anda |
| `/default` | Kembalikan provider & model ke server bawaan (`ag/*`, `cx/*`) |
| `/endpoint <url>` | Ganti endpoint AI kustom (OpenAI, Ollama, OpenRouter, Groq, dll) |
| `/key <api_key>` | Masukkan API key kustom Anda |
| `/plan` | Masuk ke **Plan Mode** (Riset arsitektur & rancang `plan.md`) |
| `/build` | Masuk ke **Build Mode** (Eksekusi mandiri pembuatan & modifikasi kode) |
| `/ask` | Masuk ke **Ask Mode** (Tanya jawab murni tanpa modifikasi file) |
| `/cd <folder>` | Pindah folder kerja aktif & re-index memori proyek |
| `/skills` | Lihat & ganti spesialisasi (ultrabrain, architect, debugger, dll) |
| `/update` | Cek dan perbarui YNCLI ke versi terbaru secara otomatis |
| `/clear` | Bersihkan riwayat chat dan refresh memori workspace |
| `/save` | Simpan sesi percakapan ke file Markdown |
| `/exit` | Keluar dari YNCLI |

---

## 🤝 Kontribusi

Kontribusi selalu terbuka! Silakan fork repository ini, buat branch baru, dan kirimkan Pull Request (PR). Jangan lupa berikan ⭐ Star jika proyek ini bermanfaat!

---

## 📄 Lisensi
[MIT License](LICENSE) © 2026 [Yanzyuyu](https://github.com/yanzyuyu).
