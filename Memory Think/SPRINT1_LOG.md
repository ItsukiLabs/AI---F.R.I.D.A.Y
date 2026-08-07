# Sprint 1 — Log Pengerjaan (M0 Contract Layer + M1 Agent Core)

> Datasheet pengerjaan Sprint 1. Setiap kali ada update fitur/logika (kode, schema, struktur), tambahkan entry baru di bawah — jangan edit entry lama, supaya riwayat tetap utuh dan tidak ambigu soal apa yang sudah dikerjakan.
>
> Selain kode, **diskusi/pembahasan penting** (pertanyaan konsep, keputusan arsitektur yang muncul dari obrolan, penjelasan yang mengubah pemahaman) juga dicatat di sini sebagai entry tersendiri — supaya ada jejak "kenapa" di balik keputusan, bukan cuma "apa" yang berubah di kode.

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

## [2026-08-07] M0 Contract Layer — Tool Contract schema

- **Apa yang dikerjakan:** Implementasi kontrak pertama di M0: `ToolContract` — manifest yang mendeskripsikan setiap tool/skill yang bisa dipanggil agent. Bentuknya mengikuti primitif Tool dari MCP (name, description, input/output JSON Schema, annotation hints) digabung model versioning ala Agent-OS (`contract_version` terpisah dari `version` tool itu sendiri, supaya bentuk kontrak bisa berevolusi tanpa memutus tool lama). Ditulis pakai Pydantic v2.
- **File yang dibuat/diubah:**
  - `requirements.txt` — isi pertama kali: `pydantic>=2.9,<3`, `pytest>=8.3,<9`
  - `backend/__init__.py` — baru, supaya `backend` jadi package yang bisa di-import
  - `backend/schemas/versioning.py` — `CONTRACT_VERSION` (versi bentuk schema, bukan versi tool)
  - `backend/schemas/tool_contract.py` — `ToolAnnotations` (read_only_hint, destructive_hint, idempotent_hint, open_world_hint — mirror MCP), `PermissionTier` enum (read_only/standard/critical — label mentah untuk M11, bukan logic otorisasi), `ToolContract` (model utama + validator: name harus snake_case, version & contract_version harus semver, description tidak boleh kosong)
  - `backend/schemas/__init__.py` — re-export symbol utama
  - `backend/tests/__init__.py`, `backend/tests/test_tool_contract.py` — 11 test (default value, validasi name/version/description, serialisasi permission_tier)
  - `backend/schemas/.gitkeep` dihapus (folder sudah tidak kosong)
- **Alasan/keputusan:**
  - Scope M0 sengaja dipersempit ke Tool Contract dulu (paling kritis menurut sprint-paper-mapping.md), bukan sekaligus Task/Event/Memory/Device contract yang disebut di README — supaya tidak mendesain kontrak untuk modul yang belum digarap (Task contract nanti pas M3, Device contract pas M4/M5, dst).
  - `permission_tier` dimasukkan ke kontrak sekarang (bukan ditunda ke M11) karena PAPER_NOTES.md eksplisit bilang butuh dipetakan dari awal ("least privilege per tool") — tapi hanya sebagai label 3-tier di kontrak, logic enforcement penuh menyusul di Sprint 4/M11.
  - Pydantic v2 dipilih karena jadi standar de-facto untuk schema Python beranotasi tipe, dan dipakai juga oleh MCP SDK resmi.
- **Belum dikerjakan / TODO lanjutan:**
  - M0: belum ada kontrak untuk Task/Event/Memory/Device (ditunda ke sprint masing-masing)
  - M1: agent loop (ReAct Thought→Action→Observation) belum dimulai — ini pakai `ToolContract` sebagai fondasi manifest tool
  - Belum ada `.env`/`.env.example` untuk API key LLM
  - Belum commit ke git untuk perubahan ini

## [2026-08-07] Diskusi: verifikasi test M0 + konsep "tool vs pengetahuan umum" + catatan per-modul

- **Apa yang dikerjakan:** Bukan penambahan kode, tapi tiga pembahasan yang mempengaruhi pemahaman & cara kerja proyek ke depan:
  1. **Verifikasi test M0** — user minta bukti konkret test benar-benar dijalankan (bukan diklaim doang). Test `backend/tests/test_tool_contract.py` dijalankan ulang dan outputnya ditampilkan mentah (11 passed). Lalu tiap test dijelasin satu-satu dalam bahasa awam: apa yang dicek dan kenapa itu penting (nama tool harus snake_case, versi harus semver, deskripsi nggak boleh kosong karena itu yang dibaca LLM buat mutusin manggil tool atau nggak, permission_tier harus bisa diserialize ke JSON).
  2. **Pertanyaan konsep: "kalau F.R.I.D.A.Y mau paham hal baru kayak dunia Art, harus bikin tool baru?"** — Jawaban: tergantung kebutuhannya, dipisah jadi 3 kategori:
     - Reasoning/diskusi umum (sejarah lukisan, teori warna) → sudah bisa dari pengetahuan bawaan LLM, **tidak butuh tool**.
     - Data spesifik/real-time dari sumber luar (cari lukisan di museum API, identifikasi gaya dari foto) → **butuh Tool baru** (M1), didaftarkan pakai `ToolContract` dari M0.
     - "Belajar" preferensi/fakta dari interaksi lalu diingat jangka panjang → itu ranah **Memory (M2)**, bukan Tool.
     - Kesimpulan prinsip: Tool = aksi manggil dunia luar; Memory = nambah pengetahuan/ingatan jangka panjang. Dua hal ini sering ketuker kalau nggak dipisah jelas dari awal.
  3. **Permintaan catatan per-modul** — user minta setiap modul "M" (M0, M1, dst.) punya file `.md` sendiri-sendiri di `Memory Think/`, isinya: kegunaan, pendekatan, ringkasan teknis, dan penjelasan bahasa awam — supaya bisa dipahami tanpa campur modul lain.
- **File yang dibuat/diubah:**
  - `Memory Think/M0_contract_layer.md` — baru. Catatan lengkap M0 (status: sedang digarap).
  - `Memory Think/M1_agent_core.md` — baru. Catatan lengkap M1 (status: belum digarap, masih rencana berbasis riset ReAct/Toolformer/Reflexion).
  - `Memory Think/SPRINT1_LOG.md` — entry ini + catatan konvensi baru bahwa diskusi juga dicatat, tidak cuma kode.
- **Alasan/keputusan:**
  - Log ini sengaja mulai mencakup pembahasan/diskusi (bukan cuma diff kode) atas permintaan eksplisit user — supaya ada data historis yang bisa dirujuk balik dan mengurangi risiko salah ingat ("halu") baik dari sisi user maupun asisten di sesi-sesi berikutnya.
  - File per-modul (`M0_*.md`, `M1_*.md`, dst.) dipisah dari `SPRINT1_LOG.md`: log ini isinya kronologis "apa yang terjadi kapan", sedangkan file per-modul isinya "pemahaman konsep yang sudah settled" tentang modul itu — dua jenis catatan beda fungsi, sengaja tidak digabung.
- **Belum dikerjakan / TODO lanjutan:**
  - M1: agent loop belum mulai coding, masih tahap catatan konsep di `M1_agent_core.md`
  - Belum ada file `M2_*.md` dst. — akan dibuat begitu sprint/modul terkait mulai dibahas
  - TODO dari entry sebelumnya masih berlaku: `.env`/`.env.example`, commit git untuk perubahan M0

## [2026-08-07] Penegasan aturan: log setiap instruksi, bukan cuma kode

- **Apa yang dikerjakan:** User menegaskan aturan standing untuk proyek ini: **setiap kali user menyuruh sesuatu**, entry baru harus ditambahkan ke `SPRINT1_LOG.md` — bukan cuma saat kode berubah, tapi juga diskusi/pertanyaan/keputusan. Ini penguatan dari entry sebelumnya ("Diskusi: verifikasi test M0..."), sekarang eksplisit dijadikan default tanpa perlu diminta ulang tiap kali.
- **File yang dibuat/diubah:**
  - `SPRINT1_LOG.md` — entry ini.
  - Memory eksternal (`friday_progress_tracking.md` di sistem memori Claude, bukan bagian dari repo ini) — diupdate supaya aturan ini terbawa otomatis ke sesi-sesi berikutnya, tidak perlu user ulang instruksi ini lagi.
- **Alasan/keputusan:** Tujuannya dua arah — (1) jadi data rujukan/"training" buat asisten supaya nggak salah asumsi soal apa yang sudah dibahas, (2) jadi pengingat buat user sendiri biar nggak lupa progres/keputusan yang sudah diambil.
- **Belum dikerjakan / TODO lanjutan:** Tidak ada perubahan teknis — murni penegasan konvensi kerja. TODO teknis sebelumnya (`.env`, commit git M0, mulai coding M1) masih berlaku.
