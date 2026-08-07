# Sprint 1 — Log Pengerjaan (M0 Contract Layer + M1 Agent Core)

> Datasheet pengerjaan Sprint 1. Setiap kali ada update fitur/logika (kode, schema, struktur), tambahkan entry baru di bawah — jangan edit entry lama, supaya riwayat tetap utuh dan tidak ambigu soal apa yang sudah dikerjakan.

## Format Entry

```
## [YYYY-MM-DD] Judul singkat

- **Apa yang dikerjakan:** ...
- **File yang dibuat/diubah:** ...
- **Alasan/keputusan:** ... (kalau ada keputusan desain yang perlu diingat)
- **Belum dikerjakan / TODO lanjutan:** ...
```

---

## [2026-08-06] Setup environment awal

- **Apa yang dikerjakan:** Inisialisasi struktur proyek dasar untuk Sprint 1. Belum ada logic/kode fungsional.
- **File yang dibuat/diubah:**
  - `backend/` — root package, dengan sub-folder kosong (`.gitkeep`): `schemas/`, `agent_core/`, `agent_core/tools/`, `memory/`, `registry/`, `dal/`, `security/`, `orchestrator/`, `persona/`
  - `.venv/` — virtual environment Python 3.13.0
  - `requirements.txt` — kosong, akan diisi bertahap
  - `README.md` — deskripsi proyek + fungsi tiap folder
  - `.gitignore` — standar Python (venv/, __pycache__/, .env, dll)
  - git repo lokal diinisialisasi (belum ada commit)
- **Alasan/keputusan:** Struktur folder `backend/` dibuat lebih lengkap dari sekadar M0+M1 (termasuk `memory/`, `registry/`, `dal/`, `security/`, `orchestrator/`, `persona/`) supaya modul-modul sprint selanjutnya (M2 dst.) sudah punya tempat tanpa perlu restrukturisasi folder di tengah jalan.
- **Belum dikerjakan / TODO lanjutan:**
  - M0: belum ada file schema apa pun di `backend/schemas/`
  - M1: belum ada `agent_core/agent.py`, `agent_core/llm_client.py`, atau tool registry
  - Belum ada commit git pertama
  - Belum ada `.env` / `.env.example` untuk API key

## [2026-08-06] Riset paper Sprint 1 & seluruh roadmap

- **Apa yang dikerjakan:** Membaca dan meringkas ~96 paper/jurnal di `Paper & Journal/F.R.I.D.A.Y/` (bukan cuma yang wajib untuk Sprint 1, tapi seluruh koleksi lintas 12 sprint atas permintaan user), disusun jadi satu file referensi.
- **File yang dibuat/diubah:**
  - `Memory Think/PAPER_NOTES.md` — catatan per paper (kategori, sprint terkait, ide inti, relevansi ke F.R.I.D.A.Y, sumber informasi), plus tabel "File Bermasalah" untuk file yang isinya tidak cocok dengan nama filenya.
- **Alasan/keputusan:** File catatan paper ditaruh di `Memory Think/`, bukan di dalam `Paper & Journal/`, supaya folder paper tetap murni data (PDF) dan tidak tercampur catatan olahan — sama alasannya kenapa log ini juga dipindah ke sini.
- **Belum dikerjakan / TODO lanjutan:**
  - 5 file paper perlu dicari ulang (isinya salah/tertukar), terutama untuk kategori Proactive (#14) dan Persona (#15) yang jadi belum lengkap
  - 4 paper soal jailbreak/sandbox-escape belum dibaca (memicu safety filter otomatis berulang) — perlu ditinjau manual oleh user
  - Detail lengkap ada di `Memory Think/PAPER_NOTES.md`
