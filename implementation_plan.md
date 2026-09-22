# YNCLI Phase 3: SOTA AI Agent Architecture

Berdasarkan riset terbaru (Aider, SWE-Agent, Devin), untuk membuat yncli menjadi AI Coding Agent terbaik (State-of-the-Art), kita harus beralih dari sekadar 'chat dengan file' menjadi **Autonomous System dengan Context Awareness**.

## Proposed Architecture Upgrades

### 1. The 'Repo Map' Engine (Aider Style)
- **Masalah:** AI sering kehabisan konteks (Token Limit) jika membaca seluruh file, atau buta struktur jika hanya mengandalkan regex search.
- **Solusi (Anti-Overengineering):** Membuat workspace_scanner.py yang menggunakan modul bawaan Python st (Abstract Syntax Tree) untuk melakukan ekstraksi. 
- **Hasil:** AI akan mendapatkan 'Peta Kode' ringan yang berisi daftar *Class*, *Function signatures*, dan relasinya tanpa isi logika di dalamnya. Ini membuat AI paham seluruh arsitektur proyek dalam hitungan detik.

### 2. Native MCP (Model Context Protocol) Client
- **Masalah:** Saat ini tools yncli di-hardcode di dalam 	ools/__init__.py. Jika user ingin konek ke Figma, Database SQL, atau GitHub, harus coding manual.
- **Solusi:** Membuat mcp_client.py yang menggunakan JSON-RPC over stdio.
- **Hasil:** yncli bisa langsung menggunakan ribuan server MCP open-source yang ada di pasaran (seperti konektor ke Postgres, Google Drive, Slack, dll) secara otomatis tanpa ubah kode inti!

### 3. Agent-Computer Interface (ACI) & Auto-Self Correction (SWE-Agent Style)
- **Masalah:** Terkadang AI mengubah kode, lalu langsung berhenti tanpa tahu kodenya error atau tidak.
- **Solusi:** Di dalam gent.py (Agentic Loop), kita tambahkan gerbang verifikasi **Linter/Syntax Check otomatis**. 
- **Workflow:** Setelah AI memanggil tool edit_file_replace, yncli akan otomatis menjalankan linter (misal: python -m py_compile atau 	sc). Jika ada error, hasilnya langsung di-*feed* kembali ke AI dalam loop yang sama agar AI melakukan revisi (Self-Correction) *sebelum* membalas ke pengguna.

## Verification Plan
1. **Repo Map Test:** Menjalankan yncli pada folder proyek besar dan memastikan AI tahu fungsi yang ada di file lain tanpa harus membacanya.
2. **MCP Test:** Mencoba menyambungkan yncli dengan server MCP open-source sederhana (misal SQLite MCP) dan memastikan AI bisa memanggil fungsi SQL.
3. **Self-Correction Test:** Meminta AI membuat syntax error yang disengaja, dan melihat apakah loop mendeteksinya dan membetulkannya otomatis.
