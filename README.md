# F.R.I.D.A.Y

Asisten AI personal — agentic AI assistant dengan kemampuan tool-use, kontrol IoT/OS, memori jangka panjang, dan voice interaction, terinspirasi oleh F.R.I.D.A.Y dari fiksi.

Target proyek ini realistis: mencapai kira-kira 80–85% dari fungsionalitas yang *terlihat* (tool-use, kontrol perangkat, memori, percakapan suara), bukan mereplikasi reasoning superhuman. Dibangun bertahap mengikuti roadmap 12 sprint (`Memory Think/sprint-paper-mapping.md`).

**Posisi terkini:** lihat [`STATUS.md`](STATUS.md) (satu halaman, diperbarui tiap tahap selesai).

## Yang sudah bisa

- **Agent loop** (M1): ReAct dengan native tool-calling Claude, validasi argumen tool, kegagalan tool jadi observasi (bukan crash).
- **Memori 3 lapis** (M2): sesi (ringkasan otomatis saat panjang), profil (fakta yang sengaja disimpan), arsip (semua percakapan, dicari dengan `recall_memory`).
- **Katalog tool** (M4): model mencari tool yang dibutuhkan (`find_tools`), tidak semua tool disuntik ke prompt.
- **Perangkat** (M5): rumah simulasi (lampu, AC) dengan kontrak device, status perintah, perangkat lambat, dan simulasi kegagalan. Belum ada perangkat nyata.
- **CLI** terminal untuk mengobrol dengan F.R.I.D.A.Y memakai LLM asli.

Belum ada: gerbang izin/keamanan (Sprint 4), suara (Sprint 5), perangkat nyata, model lokal (Sprint 8).

## Menjalankan

Butuh Python 3.13.

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt   # Windows
cp .env.example .env    # lalu isi ANTHROPIC_API_KEY; opsional FRIDAY_TIMEZONE=Asia/Jakarta
```

**CLI** (memakai kredit API Anthropic setiap pesan):

```bash
.venv/Scripts/python.exe -m backend.cli                 # rumah standar
.venv/Scripts/python.exe -m backend.cli --home dua-lampu # 2 lampu di ruang tamu
```

Perintah di dalam CLI: `/state`, `/fail <device> offline|lost_ack`, `/slow <device> <reads>`, `/journal`, `/journal ack`, `/trace on|off`, `/new`, `/session`, `/help`, `/quit`.

**Izin (Sprint 4):** setiap tool harus terdaftar di `config/permissions.json` (`read_only` / `standard` / `critical`, plus `"confirm": true` untuk `standard` yang ingin ditanyakan dulu). Tool yang tidak terdaftar tidak pernah dijalankan. Aksi yang perlu konfirmasi ditanyakan langsung di terminal (y/n), bukan lewat AI. Setiap perintah perangkat dicatat di jurnal aksi (`backend/journal/data/actions.db`).

**Test** (LLM palsu, gratis, tanpa API key):

```bash
.venv/Scripts/python.exe -m pytest backend/tests -q
```

CI (GitHub Actions, `.github/workflows/tests.yml`) menjalankan test yang sama di Linux dan Windows setiap push.

## Struktur Folder (`backend/`)

| Folder | Modul | Isi |
|---|---|---|
| `schemas/` | M0 | Kontrak data: `ToolContract`, kontrak Device, format sesi/profil/arsip. |
| `agent_core/` | M1 | Loop agent, klien LLM, registry tool per turn, konfigurasi, tool dasar (`tools/`). |
| `memory/` | M2 | Sesi + kompaksi, profil, arsip SQLite FTS5, beserta store-nya. |
| `orchestrator/` | M2 v2 | `Orchestrator.run_turn()` — satu pintu per turn, urutan simpan profil → sesi → arsip. |
| `registry/` | M4 | Katalog tool, `find_tools`, auto-load, retensi tool lintas turn. |
| `devices/` | M5 | Driver rumah simulasi, `DeviceService` (shadow desired/reported, status perintah), pembuat tool perangkat. |
| `dal/` | — | Helper pencarian FTS5 bersama. |
| `cli.py` | — | CLI terminal. |
| `tests/` | — | Seluruh test (pytest). |
| `security/` | M11 | Versi mini: daftar izin pemilik, gerbang izin, slot konfirmasi (`TerminalConfirmer`). |
| `journal/` | M11 | Jurnal aksi SQLite (setiap perintah perangkat dicatat sebelum dan sesudah dikirim). |
| `persona/` | M15 | Belum ada (Sprint 10). |

## Dokumentasi

- `STATUS.md` — posisi sekarang.
- `Memory Think/SPRINT{N}_LOG.md` — log kerja per sprint (append-only, termasuk diskusi dan keputusan).
- `Memory Think/M*_*.md` — catatan per modul (kegunaan, pendekatan, ringkasan teknis, bahasa awam).
- `Memory Think/PAPER_NOTES.md`, `sprint-paper-mapping.md` — riset paper dan peta sprint.
- `FRIDAY_PROJECT_REVIEW.md` + `Memory Think/feedback_another_ai/` — tinjauan proyek dan feedback dari 4 model AI (2026-10-25).
