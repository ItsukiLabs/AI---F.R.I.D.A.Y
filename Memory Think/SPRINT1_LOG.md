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

## [2026-08-07] Commit pertama M0 Contract Layer

- **Apa yang dikerjakan:** Semua hasil kerja M0 (schema, test, catatan modul, update log) di-stage dan di-commit ke git lokal dengan pesan `feat(m0): add ToolContract schema for tool manifest`.
- **File yang dibuat/diubah:** 10 file masuk commit `46c7be7` — `backend/__init__.py`, `backend/schemas/__init__.py`, `backend/schemas/tool_contract.py`, `backend/schemas/versioning.py`, `backend/tests/__init__.py`, `backend/tests/test_tool_contract.py`, `Memory Think/M0_contract_layer.md`, `Memory Think/M1_agent_core.md`, `Memory Think/SPRINT1_LOG.md`, `requirements.txt`. File `backend/schemas/.gitkeep` terhapus (tergantikan isi asli).
- **Alasan/keputusan:** Commit dipisah per unit kerja logis (M0 selesai = satu commit), bukan digabung sekaligus sama commit besar berikutnya — supaya riwayat git gampang ditelusuri per modul.
- **Belum dikerjakan / TODO lanjutan:**
  - Commit ini **belum di-push** ke `origin/master` — masih 1 commit ahead secara lokal, menunggu instruksi push.
  - `.env`/`.env.example` untuk API key LLM masih belum ada.
  - M1 (agent loop ReAct) belum mulai coding.

## [2026-08-07] Push commit M0 + diskusi biaya LLM & keputusan cloud-dulu-lokal-nanti

- **Apa yang dikerjakan:**
  1. Push commit `46c7be7` ke `origin/master` (`ea92316..46c7be7`).
  2. User tanya: kalau pakai Anthropic/OpenAI apakah F.R.I.D.A.Y jadi berbayar, sementara dia mau F.R.I.D.A.Y bebas biaya/kontrol pihak luar dan cuma patuh ke dia + orang yang dia setujui, "tanpa batasan". Dijelaskan: (a) cloud API memang bayar per-token/usage, bukan gratis untuk pemakaian serius; (b) "bebas biaya & kontrol penuh" = soal *LLM engine*, sudah match sama rencana Sprint 8 (M12 Local Inference + M13 Hybrid Routing) — pakai model open-weight lokal (Llama/Mistral/Qwen/DeepSeek via llama.cpp/Ollama); (c) "cuma patuh ke aku & yang aku setujui" = soal **M11 Security/Permission**, independen dari LLM mana yang dipakai; (d) diklarifikasi ulang maksud "tanpa batasan" karena ambigu — bisa berarti bebas biaya/kontrol korporat (dicapai via model lokal) atau berarti model tanpa batasan konten/perilaku sama sekali (ditolak dibantu kalau maksudnya itu). User konfirmasi maksudnya opsi (a) — bebas biaya/kontrol korporat.
  3. Keputusan arsitektur M1: **mulai pakai cloud API dulu untuk Sprint 1 (prototyping cepat, kualitas tool-calling lebih reliable)**, tapi M1 didesain provider-agnostic supaya gampang di-swap ke local model pas Sprint 8 sesuai rencana awal — bukan langsung lompat ke local sekarang karena setup hosting+quantization akan menunda validasi logic loop ReAct itu sendiri.
  4. User pilih provider: **siapkan dua-duanya** (Anthropic Claude + OpenAI) di `.env.example`, walau default provider M1 nanti cuma satu (`anthropic`).
- **File yang dibuat/diubah:**
  - `.env.example` — baru, template variabel: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `LLM_PROVIDER` (default `anthropic`).
  - `.env` — baru, isi sama seperti template tapi key masih kosong (user perlu isi manual API key asli-nya sendiri). **Tidak masuk git** (sudah di-`.gitignore`, dicek `git status` cuma `.env.example` yang muncul).
- **Alasan/keputusan:**
  - `.env.example` sengaja dikecualikan dari `.gitignore` (pola `.env.*` + `!.env.example`) supaya template variabel ikut ke-commit tapi secret asli tidak pernah ke-push.
  - Nama variabel `LLM_PROVIDER` ditambahin (bukan cuma dua API key) supaya M1 nanti bisa baca satu switch simpel buat nentuin provider default, tanpa hardcode di kode.
- **Belum dikerjakan / TODO lanjutan:**
  - User perlu isi `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` asli di `.env` miliknya sendiri (bukan sesuatu yang saya isi/lihat).
  - `python-dotenv` (atau setara) belum ditambahkan ke `requirements.txt` — akan ditambah pas mulai coding M1 yang benar-benar konsumsi `.env` ini.
  - M1 (agent loop ReAct) belum mulai coding — sekarang jadi next step utama.

## [2026-08-12] Rombak struktur folder paper jadi per-modul (M0–M17)

- **Apa yang dikerjakan:**
  1. User mau kasih paper pengganti untuk 2 file bermasalah (M17: paper mismatch soal Context-Awareness; M11: 4 paper jailbreak/sandbox-escape yang sebelumnya DILEWATI). Awalnya disarankan taruh di folder lama (`Interaksi Manusia-Komputer.../` dan `2/`), tapi user minta sekalian folder papernya dirombak total jadi satu folder per modul (`M0/` s.d. `M17/`) biar lebih gampang dipahami paper mana untuk modul mana.
  2. Diklarifikasi dulu: banyak paper relevan ke >1 modul (MCP, Agent-OS, HearthNet, OSWorld 2.0, dll.) — user pilih opsi **satu folder modul utama per paper** (bukan folder "Lintas-Modul" terpisah, bukan juga digandakan fisik ke tiap folder relevan). Relevansi ke modul lain tetap dicatat sebagai teks di `PAPER_NOTES.md`, bukan lewat lokasi file.
  3. Enumerasi seluruh 96 file PDF nyata di folder lama (`1/`-`5/` + 3 folder tematik + 2 file di root), dipetakan satu-per-satu ke modul utamanya berdasarkan `sprint-paper-mapping.md` (kategori→modul) + isi entry masing-masing di `PAPER_NOTES.md`.
  4. Eksekusi lewat script (`mkdir` + `mv` per file, dijalankan dari Bash) — dipilih pendekatan script/mapping-list dibanding mv manual satu-satu karena skalanya besar (96 file, banyak nama file berkarakter spesial: apostrof, en-dash, titik dua, tanda kurung).
  5. Folder lama yang sudah kosong (`2/`, `3/`, `4/`, `5/`, `Implementasi Teknis & Pemrosesan Bahasa Alami/`) dihapus. Folder `1/` dan 2 folder tematik lain **tidak dihapus** karena masih menyisakan file yang belum bisa dikategorikan (3 file mismatch tanpa kategori jelas + 1 file `Nggak dulu` non-paper yang memang sudah dikecualikan sejak awal).
  6. `PAPER_NOTES.md` diupdate otomatis via script Python (replace literal path lama→baru) untuk 90 dari 93 referensi path di badan dokumen, plus tabel "File Bermasalah" diedit manual (formatnya kolom terpisah, tidak kena replace otomatis) supaya kolom Folder-nya juga mengikuti skema baru. Ditambah catatan penjelasan skema baru di bagian atas dokumen.
- **File yang dibuat/diubah:**
  - `Paper & Journal/F.R.I.D.A.Y/M0/` s.d. `M17/` — baru, isi total 93 PDF (lihat rincian di bawah).
  - `Paper & Journal/F.R.I.D.A.Y/2/`, `3/`, `4/`, `5/`, `Implementasi Teknis & Pemrosesan Bahasa Alami/` — dihapus (sudah kosong).
  - `Memory Think/PAPER_NOTES.md` — seluruh field `Lokasi file` diupdate ke path baru, tabel "File Bermasalah" diupdate (kolom Folder + catatan lokasi khusus untuk 2 paper pengganti M17/M15), ditambah catatan skema folder baru di bagian atas dokumen.
  - `Memory Think/SPRINT1_LOG.md` — entry ini.
- **Alasan/keputusan:**
  - Mapping "1 paper = 1 folder modul utama" dipilih user supaya tidak ada duplikat file besar (PDF) dan tidak ada folder "Lintas-Modul" yang jadi kategori aneh sendiri di luar skema M0-M17 — trade off-nya: kalau mau tahu paper itu relevan ke modul lain juga, harus buka `PAPER_NOTES.md`, bukan cukup lihat lokasi filenya.
  - 3 file mismatch yang isinya sama sekali belum jelas kategori aslinya (Recent Advances in Conversational AI, Voice Assistants in Everyday Life, Building Trust in Human-AI Collaboration) **sengaja tidak dipaksa masuk folder M manapun** — dibiarkan di folder tematik lama sampai paper aslinya ditemukan, supaya tidak salah taruh modul lalu harus dipindah lagi nanti.
  - **Lokasi paper pengganti (update dari jawaban sebelumnya di sesi ini):** karena foldernya sudah dirombak, paper pengganti untuk M17 (Context-Awareness) taruh langsung di `M17/`, dan untuk M11 (4 paper jailbreak/sandbox-escape) taruh langsung di `M11/` — bukan lagi di folder tematik/`2/` seperti disebut sebelumnya di percakapan ini, karena folder itu sudah tidak ada.
- **Belum dikerjakan / TODO lanjutan:**
  - User perlu cari ulang 3 paper mismatch yang belum ketahuan modulnya (lihat tabel File Bermasalah di `PAPER_NOTES.md`) sebelum bisa dipindah ke folder M yang tepat.
  - Paper pengganti M17 & M11 yang dijanjikan user belum ditaruh — begitu ditaruh di `M17/`/`M11/`, saya perlu baca dan update status entry terkait di `PAPER_NOTES.md` (dari MISMATCH/DILEWATI ke Teks penuh/Ekstraksi parsial).
  - M1 (agent loop ReAct) masih belum mulai coding — tetap next step utama untuk kode (independen dari beres-beres paper ini).

## [2026-08-12] Audit & update PAPER_NOTES.md — 9 paper baru M11/M17 dibaca, ketemu `pdftotext` tersedia

- **Apa yang dikerjakan:**
  1. User diam-diam sudah taruh paper baru di `M11/` dan `M17/` (menjawab TODO sesi sebelumnya), lalu minta saya cek & update `PAPER_NOTES.md`, sampaikan kalau ada yang kurang/kurang cocok/perlu sesuatu.
  2. Audit terstruktur (script Python): bandingkan isi fisik tiap folder `M0`-`M17` vs semua path yang direferensikan di `PAPER_NOTES.md`, supaya nemu file yang belum tercatat tanpa perlu baca ulang seluruh dokumen. Ketemu 9 file baru asli (bukan false-positive dari keterbatasan regex terhadap format tabel 2-kolom): 5 di `M11/` (termasuk 1 salinan tambahan paper "Not What You've Signed Up For" yang sudah ada), 4 di `M17/`.
  3. Coba baca 9 PDF baru pakai Read tool → gagal (`pdftoppm`/poppler tidak terpasang). Dicoba fallback: ternyata **`pdftotext` (poppler CLI, versi lain) tersedia** di environment ini — sebelumnya di sesi 2026-08-06 disimpulkan "tool render PDF tidak tersedia" untuk banyak paper, ternyata itu spesifik ke `pdftoppm`/Read-tool, bukan ke poppler secara keseluruhan.
  4. Ekstrak & baca abstract+intro (kadang lebih) dari 9 paper baru pakai `pdftotext`, tulis entry baru di `PAPER_NOTES.md` kategori #6 (4 entry: LASM survey, AgentDojo, InjecAgent, Toward Secure LLM Agents) dan kategori #14 (3 entry: Personalization Survey, ContextAgent, Enabling Personalized Long-term Interactions, Proactive Agent — total 4, salah satu penomoran di atas keliru, lihat file untuk hitungan pasti 4 entry M17).
  5. Sekalian coba `pdftotext` ke paper LAMA yang berstatus "Gagal dibaca" (Proactive Conversational Agents with Inner Thoughts, 22MB) — berhasil, jadi diupgrade dari "Gagal dibaca" ke entry lengkap terverifikasi.
  6. Update tabel "File Bermasalah" dan catatan kategori #14 di `PAPER_NOTES.md` supaya tidak lagi menganggap kategori itu "kekurangan 1 paper" — sudah diperkuat signifikan meski file mismatch aslinya belum diganti.
  7. Ketemu bagian **basi** di `sprint-paper-mapping.md` — tabel "Kategori yang BELUM Punya Paper" (ditulis 2025-07-14) menyebut 6 kategori (#6-#12) masih butuh paper, padahal per audit hari ini semua sudah terisi (paper-nya sudah diriset sejak sesi 2026-08-06, tabel itu memang tidak pernah diupdate). Diperbaiki jadi tabel status "sudah terisi" + daftar TODO yang genuinely masih terbuka (4 DILEWATI, 3 mismatch tanpa kategori, 1 mismatch M15).
- **File yang dibuat/diubah:**
  - `Memory Think/PAPER_NOTES.md` — 8 entry baru (4 di kategori #6, 4 di kategori #14), 1 entry lama di-upgrade penuh (Inner Thoughts), 1 entry lama ditambah catatan salinan ke-3 (Not What You've Signed Up For), tabel File Bermasalah + catatan kategori #14 diupdate, ringkasan total di akhir dokumen diupdate.
  - `Memory Think/sprint-paper-mapping.md` — tabel "Kategori yang BELUM Punya Paper" diperbarui dari basi jadi cerminan status nyata.
  - `Memory Think/SPRINT1_LOG.md` — entry ini.
- **Alasan/keputusan:**
  - Tidak baca ulang seluruh 96 PDF lama dari nol untuk audit ini — scope dibatasi ke: (a) file yang genuinely baru (ketahuan lewat diff disk-vs-notes, bukan tebakan), (b) 1 paper lama yang statusnya "gagal total" dan sekarang bisa diperbaiki dengan tool yang baru ketahuan tersedia. Membaca ulang semua paper lama di luar scope permintaan user turn ini.
  - Ekstraksi pakai `pdftotext` (bukan Read tool) dicatat jujur di field "Sumber informasi" sebagai "Ekstraksi mendalam" (bukan "Teks penuh") karena yang dibaca baru abstract+intro (kadang metodologi), bukan keseluruhan paper — konsisten sama konvensi sourcing-transparency yang sudah ada dari sesi awal.
- **Belum dikerjakan / TODO lanjutan (saat itu):**
  - 14 entry "Pengetahuan umum" berpotensi diupgrade pakai `pdftotext`.
  - 4 paper DILEWATI di M11 belum dicoba dibaca ulang.
  - 3 file mismatch tanpa kategori jelas + 1 file mismatch M15 masih menunggu paper pengganti dari user.
  - M1 (agent loop ReAct) masih belum mulai coding.

## [2026-08-12] Eksekusi 2 rekomendasi: upgrade 12 entry "Pengetahuan umum" + baca 4 paper DILEWATI

- **Apa yang dikerjakan:** User menyetujui dua rekomendasi dari entry sebelumnya, dikerjakan berurutan dalam satu turn.
  1. **Upgrade status sumber 12 entry lama** (kategori #7-#10 + 1 di #14): diekstrak via `pdftotext`, dibaca abstract/intro/related-work, entry ditulis ulang dengan detail teknis akurat (penulis, metode, angka hasil) dan status "Sumber informasi" naik dari "Pengetahuan umum" ke "Ekstraksi mendalam". 11 dari 12 berhasil diupgrade penuh. 1 (AutoAgents) dikonfirmasi ulang tetap mismatch — filenya memang salah unduh (isi paper fisika kuantum "Quantum Codes from Twisted Unitary t-groups"), bukan masalah tool, jadi tetap "Pengetahuan umum".
  2. **Ditemukan 2 koreksi faktual** saat proses upgrade (bukan cuma nambah detail, tapi membetulkan kesalahan lama): (a) entry "ASVspoof (2017)" — deskripsi lama soal "replay attack, corpus RedDots" ternyata salah paper; file fisiknya adalah laporan ASVspoof **2015** (fokus TTS/voice-conversion spoofing, bukan replay) — deskripsi lama itu sebenarnya menggambarkan edisi ASVspoof 2017 yang berbeda. (b) entry "Building Accurate Low Latency ASR" — dugaan lama "two-pass decoding" ternyata bukan itu; paper aslinya pakai hierarchical CTC + joint end-of-speech detection.
  3. **Baca 4 paper DILEWATI di M11** (jailbreak code agent, MCP protocol security, sandbox escape, safety alignment) — semua berhasil diekstrak & dibaca via `pdftotext` tanpa hambatan sama sekali, mengonfirmasi dugaan bahwa masalah DILEWATI dulu adalah tool render PDF (`pdftoppm`/Read tool), bukan filter konten. Dibaca dengan fokus ke metodologi/temuan agregat (kerangka evaluasi & pertahanan), bukan detail teknik eksploitasi/payload — sesuai prinsip riset keamanan defensif. Salah satunya ("Breaking the Protocol... MCP") ditandai KRITIS karena analisis formal pertama terhadap spesifikasi MCP itu sendiri, langsung relevan ke keputusan M0 pakai MCP sebagai format kontrak.
  4. Update pendukung: tabel "File Bermasalah" (4 baris DILEWATI dihapus, sudah tidak relevan), ringkasan total paper di akhir dokumen, dan tabel status di `sprint-paper-mapping.md`.
- **File yang dibuat/diubah:**
  - `Memory Think/PAPER_NOTES.md` — 12 entry lama diupgrade/dikoreksi, 4 entry baru menggantikan bagian "Paper yang DILEWATI", tabel File Bermasalah + ringkasan akhir diupdate.
  - `Memory Think/sprint-paper-mapping.md` — tabel status kategori #6 & daftar TODO diupdate (4 DILEWATI dicoret, selesai).
  - `Memory Think/SPRINT1_LOG.md` — entry ini.
- **Alasan/keputusan:**
  - Koreksi ASVspoof & Building Accurate Low Latency ASR sengaja ditulis eksplisit sebagai "koreksi" (bukan diam-diam diganti) — supaya kalau ada keputusan kode yang sudah sempat dibuat berdasarkan catatan lama yang salah, ketahuan perlu ditinjau ulang.
  - 4 paper DILEWATI dibaca dengan sengaja membatasi diri ke metodologi/temuan, bukan meniru/mengutip detail teknik serangan — konsisten dengan prinsip dual-use security research (pelajari untuk bertahan, bukan untuk menyerang).
- **Belum dikerjakan / TODO lanjutan:**
  - 3 file mismatch tanpa kategori jelas + 1 file mismatch M15 masih menunggu paper pengganti dari user.
  - Status sumber di `PAPER_NOTES.md` sekarang: 106/109 entry punya sumber terverifikasi (Teks penuh/Ekstraksi mendalam/Ekstraksi parsial), cuma AutoAgents yang masih "Pengetahuan umum" (genuinely tidak bisa diperbaiki tanpa file baru).
  - M1 (agent loop ReAct) masih belum mulai coding — tetap next step utama.

## [2026-08-13] Verifikasi & perbaikan file paper pengganti (M7/M14/M15/M17) — 3 berhasil, 1 ternyata duplikat bukan paper baru

- **Apa yang dikerjakan:**
  1. User menambahkan beberapa file paper baru ke folder `M7/`, `M14/`, `M17/` sebagai kandidat pengganti file mismatch yang tercatat di TODO sesi sebelumnya. Saya diminta cek apakah file-file itu valid.
  2. Verifikasi satu-per-satu pakai `pdftotext` (bukan cuma cek nama file): **M14 (AutoAgents)** dan **M17 (Context-Awareness)** — isi cocok dengan judul, berhasil. **"Form Follows Function"** — isinya benar (paper anthropomorphism LLM asli), tapi ditemukan **salah taruh folder**: user taruh di `M17/`, padahal isinya untuk `M15/` (Persona). **M7 (Depthwise CNN 2022)** — file yang ditambahkan ternyata **duplikat 100% dari paper 2020 yang sudah ada** (dikonfirmasi via `diff` full-text, hasilnya kosong sama sekali, plus MD5 hash identik) — bukan paper baru yang beda.
  3. User sendiri sempat menelusuri ulang mencari paper "Depthwise CNN 2022" yang genuinely berbeda dan tidak menemukan — mengonfirmasi kesimpulan bahwa file itu memang tidak ada sebagai paper terpisah, "2022" di nama file lama cuma penamaan keliru.
  4. User setuju eksekusi rencana: pindah "Form Follows Function" ke folder yang benar, hapus file-file lama yang sudah tergantikan, hapus duplikat M7 yang salah nama.
  5. Eksekusi file: hapus `M7/A Depthwise Separable CNN for Keyword Spotting on an Embedded System (2022).pdf` (mismatch asli, isi Sub-mW) — sempat juga hapus 1 file duplikat tambahan (`A Depthwise Separable CNN for Keyword Spotting (2022).pdf`, tanpa "on an Embedded System") yang sempat "hilang lalu muncul lagi" di listing folder (kemungkinan delay sinkronisasi OneDrive, bukan tindakan saya) — dicek ulang hash-nya tetap identik ke paper 2020, aman dihapus. Hapus `M14/AutoAgents...(2024).pdf` (mismatch lama, fisika kuantum) dan `M17/Context-Awareness...and Large Language Models.pdf` (mismatch lama, kriptografi medis). Pindahkan `Form Follows Function...pdf` dari `M17/` ke `M15/`.
  6. Update `PAPER_NOTES.md`: tulis ulang entry AutoAgents (M14), tambah entry baru untuk Context-Awareness survey (M17, arXiv:2402.01968) dan Humanizing Machines (M15, arXiv:2508.17573), update catatan Sub-mW (M7) menghapus referensi ke file yang sudah dihapus, bersihkan 4 baris tabel "File Bermasalah" yang sudah resolved + 1 baris "Inner Thoughts — Gagal dibaca" yang sudah basi (sudah terverifikasi sejak 2026-08-12 tapi tabel tidak sempat disinkron saat itu), update ringkasan total paper.
  7. Update `sprint-paper-mapping.md`: tandai selesai untuk mismatch M14/M15/M17 di catatan TODO kategori.
- **File yang dibuat/diubah:**
  - `Paper & Journal/F.R.I.D.A.Y/M7/`, `M14/`, `M17/`, `M15/` — operasi hapus/pindah file seperti dijelaskan di atas.
  - `Memory Think/PAPER_NOTES.md` — 3 entry ditulis ulang/baru (AutoAgents, Context-Awareness survey, Humanizing Machines), 1 entry diperbarui (Sub-mW), tabel File Bermasalah dikurangi dari 10 baris jadi 5 baris, ringkasan total diupdate.
  - `Memory Think/sprint-paper-mapping.md` — catatan TODO kategori diupdate, mismatch M14/M15/M17 ditandai selesai.
  - `Memory Think/SPRINT1_LOG.md` — entry ini.
- **Alasan/keputusan:**
  - Verifikasi pakai ekstraksi teks langsung (bukan cuma percaya nama file/klaim user) tetap dipertahankan sebagai standar — terbukti berguna lagi di sesi ini karena menemukan file M7 yang di-upload user ternyata bukan paper baru (kalau langsung dipercaya nama filenya, kategori #7 akan tampak "selesai" padahal isinya duplikat).
  - File "Form Follows Function" tidak dihapus lalu diminta unggah ulang — cukup dipindah foldernya, karena isinya sudah benar, cuma lokasinya yang salah.
  - Delay muncul-hilang file di M7 (kemungkinan OneDrive sync) dilaporkan apa adanya ke user, bukan didiamkan, supaya user tahu ini bukan tindakan saya yang tidak disengaja.
- **Belum dikerjakan / TODO lanjutan:**
  - 3 file mismatch tanpa kategori jelas (Recent Advances, Voice Assistants in Everyday Life, Building Trust) masih menunggu paper pengganti — belum ada progres dari user untuk ini.
  - Commit git untuk semua perubahan `Memory Think/*.md` sesi ini + sesi sebelumnya (2026-08-12) masih menumpuk, belum di-push.
  - M1 (agent loop ReAct) masih belum mulai coding — tetap next step utama untuk kode.

## [2026-08-13] M1 Agent Core — implementasi awal loop ReAct

- **Apa yang dikerjakan:**
  1. User tanya soal budget $5 credit Anthropic buat development/testing M1 — dijawab pakai harga resmi terbaru (Haiku 4.5 $1/$5 per 1M token, Sonnet 5 $2/$10 intro, Opus 5 $5/$25): estimasi ~550 test run di Haiku, ~275 di Sonnet, ~110 di Opus untuk $5, cukup nyaman untuk beberapa minggu development kalau dominan pakai Haiku. Disepakati model default development = `claude-haiku-4-5`, gampang di-override lewat env var.
  2. Masuk plan mode untuk desain implementasi M1 sebelum coding — riset struktur `backend/` yang sudah ada (M0 schema, requirements.txt, `.env.example`), keputusan desain kunci: **native tool-calling Claude** (bukan text-parsing manual ala paper ReAct 2022 asli, karena sekarang ada tool-calling API — teks sebelum `tool_use` block = Thought, `tool_use` block = Action, tool result = Observation), validasi input tool pakai library `jsonschema` (bukan hand-rolled), Reflexion di-scope minimal (refleksi cuma hidup dalam satu sesi run, persistensi lintas-sesi itu M2), 1 tool contoh (`get_current_time`, read-only) untuk uji loop end-to-end tanpa butuh IoT/OS (M4/M5) yang belum ada. Plan disetujui user setelah update kecil (tambah `ANTHROPIC_MODEL` default).
  3. Eksekusi implementasi sesuai plan — lihat daftar file di bawah.
  4. Jalankan `python -m pytest backend/tests/ -v` — sempat 1 test gagal (`test_invalid_tool_args_trigger_reflection_then_retry`), ternyata bug di test double (`FakeLLMClient` menyimpan referensi list `messages` yang sama, bukan snapshot — karena `run_agent` mutasi list itu dengan `.append()` di setiap iterasi, semua entry `llm.calls` akhirnya menunjuk ke state akhir yang sama). Diperbaiki dengan `list(messages)` (shallow copy) saat mencatat tiap call. Bukan bug di `loop.py` sendiri. Setelah fix: **19/19 test lulus** (11 lama M0 + 8 baru M1).
- **File yang dibuat/diubah:**
  - `.env.example`, `.env` — tambah `ANTHROPIC_MODEL=claude-haiku-4-5`.
  - `requirements.txt` — tambah `anthropic>=0.40,<1`, `python-dotenv>=1.0,<2`, `jsonschema>=4.23,<5` (terinstall ke `.venv`).
  - `backend/agent_core/__init__.py`, `config.py` — baru.
  - `backend/agent_core/llm_client.py` — baru: `LLMClient` (Protocol), `ToolCallRequest`/`LLMResponse` (dataclass), `AnthropicLLMClient`, `tool_contract_to_anthropic_tool()`, `get_llm_client()` factory (`"openai"` → `NotImplementedError` disengaja).
  - `backend/agent_core/tool_registry.py` — baru: `ToolRegistry` (register/get/to_llm_tools).
  - `backend/agent_core/loop.py` — baru: `run_agent()` — loop ReAct inti dengan validasi jsonschema, reflexion-on-error, guard `max_iterations`.
  - `backend/agent_core/tools/__init__.py`, `time_tool.py` — baru: tool contoh `get_current_time` + `ALL_TOOLS` registration list.
  - `backend/agent_core/.gitkeep`, `backend/agent_core/tools/.gitkeep` — dihapus (folder sudah tidak kosong).
  - `backend/tests/test_tool_registry.py`, `test_agent_loop.py` — baru: 8 test (4 tool_registry, 4 agent_loop pakai `FakeLLMClient`).
  - `Memory Think/M1_agent_core.md` — status diupdate jadi "Implementasi awal selesai", bagian Ringkasan Teknis ditulis ulang sesuai kode nyata.
  - `Memory Think/SPRINT1_LOG.md` — entry ini.
- **Alasan/keputusan:**
  - `messages: list[dict]` dipakai sebagai format riwayat percakapan bersama (bukan tipe khusus per-provider) — `loop.py` yang merekonstruksi assistant message dari `LLMResponse` (provider-agnostic) balik ke bentuk yang diterima Anthropic API, supaya `LLMClient` interface tetap bersih tanpa bocorin raw SDK objects ke loop.
  - Tool call gagal (validasi atau exception) selalu ditangkap jadi `tool_result` dengan `is_error: true` dan pesan verbal — tidak pernah membiarkan exception menjalar ke atas loop — supaya prinsip Reflexion (LLM lihat kegagalan, coba lagi dengan info itu) benar-benar terjadi, bukan cuma niat.
  - Registrasi tool manual eksplisit (`ALL_TOOLS` list), bukan auto-discovery — untuk jumlah tool sekecil ini (1 tool) auto-discovery cuma nambah kompleksitas tanpa manfaat nyata.
- **Belum dikerjakan / TODO lanjutan:**
  - Provider `"openai"` di `get_llm_client()` sengaja belum diimplementasi (Sprint 8/M12-M13).
  - Belum ada tool nyata untuk kontrol IoT/OS (M4/M5 belum digarap) — `get_current_time` cuma contoh minimal untuk uji loop.
  - Reflexion belum persisten lintas sesi — itu ranah M2 (Memory), belum dimulai.
  - Perubahan sesi ini **belum di-commit/push** ke git.

## [2026-08-13] Verifikasi smoke test manual M1 dengan API key asli

- **Apa yang dikerjakan:** User mengisi `ANTHROPIC_API_KEY` asli di `.env` (dibuat dari Anthropic Console, key baru). Dijelaskan alur pengambilan key (console.anthropic.com → Settings → API Keys → Create Key) dan bagaimana key itu mengalir ke kode (`.env` → `config.py` baca via `load_dotenv()` → `AnthropicLLMClient` pakai buat inisialisasi SDK `anthropic`). Setelah key terisi, dijalankan smoke test manual: `run_agent("jam berapa sekarang?", registry, get_llm_client("anthropic"))` dengan tool `get_current_time` terdaftar.
- **Hasil:** **Berhasil** — API call asli ke `claude-haiku-4-5` sukses, model manggil tool `get_current_time` di iterasi 1, jawab final pakai hasilnya di iterasi 2 ("Waktu sekarang adalah 08:42:06 UTC, Kamis 13 Agustus 2026"). `exceeded_max_iterations=False`. Ini pertama kalinya loop M1 diverifikasi jalan end-to-end lewat API asli, bukan cuma lulus test dengan `FakeLLMClient`.
- **File yang dibuat/diubah:**
  - `.env` — `ANTHROPIC_API_KEY` diisi user (tidak masuk git, sudah di-`.gitignore`).
  - `Memory Think/M1_agent_core.md` — tambah catatan "Verifikasi nyata", hapus item TODO smoke test (sudah selesai).
  - `Memory Think/SPRINT1_LOG.md` — entry ini.
- **Alasan/keputusan:** Tidak menampilkan isi API key asli di percakapan/log manapun — cukup konfirmasi baris `ANTHROPIC_API_KEY=` terisi via `grep -c`, bukan `cat` isi filenya, supaya key tidak pernah muncul di transcript.
- **Belum dikerjakan / TODO lanjutan:** Sama seperti entry sebelumnya (provider OpenAI, tool IoT/OS nyata, Reflexion persisten M2) — commit/push sesi ini masih menunggu instruksi user.

## [2026-08-13] Commit & push paper fixes M7/M14/M15/M17; cari & verifikasi 3 paper pengganti terakhir

- **Apa yang dikerjakan:**
  1. Commit git untuk semua perubahan sesi ini (hapus/pindah file paper M7/M14/M15/M17 + update `PAPER_NOTES.md`/`sprint-paper-mapping.md`/`SPRINT1_LOG.md`) sebagai satu unit kerja logis, langsung di-push ke `origin/master` (`4c452f5..0c05301`).
  2. User tanya detail 3 file mismatch tanpa kategori jelas yang masih PR (folder mana, isi apa, kenapa mismatch) — dijelaskan satu-satu: 2 file di `Arsitektur & Evaluasi Sistem Asisten AI (Teknik & Komputasi)/` (Recent Advances in Conversational AI → isi asli paper matematika Willmore energy; Voice Assistants in Everyday Life → isi asli paper computer vision land cover classification), 1 file di `Interaksi Manusia-Komputer & Psikologi AI (Human-Computer Interaction)/` (Building Trust in Human-AI Collaboration → isi asli paper virtual try-on diffusion model).
  3. User minta bantuan cari kandidat pengganti. Dicoba `WebSearch` judul persis ketiga file — **tidak ditemukan paper dengan judul itu di manapun**, mengonfirmasi dugaan bahwa judul-judul itu bukan judul paper asli persis (kemungkinan parafrase dari daftar bacaan lama). Diputuskan cari paper pengganti tematik terdekat: "A Survey of Large Language Models" (Zhao et al., arXiv:2303.18223), "A Mixed-Methods Approach to Understanding User Trust after Voice Assistant Failures" (Baughan et al., CHI'23, arXiv:2303.00164), "A Systematic Review on Fostering Appropriate Trust in Human-AI Interaction" (Mehrotra et al., arXiv:2311.06305).
  4. User mengunduh & menaruh ketiga kandidat di folder tematik lama (nama file asli dari judul paper, bukan menimpa nama file lama). Diverifikasi isi via `pdftotext` — ketiganya cocok 100% dengan judul/penulis/arXiv ID yang diharapkan.
  5. Ditentukan modul tujuan berdasarkan isi (bukan cuma ikut nama folder lama): Survey of LLM → `M1/` (fondasi agent core, kategori #1), Mixed-Methods Trust → `M15/` (persona/trust voice assistant, kategori #15, melengkapi paper trust yang sudah ada di sana), Systematic Review Trust → `M16/` (evaluasi/benchmarking, kategori #16, karena isinya taksonomi metode pengukuran trust bukan studi UX spesifik voice assistant).
  6. Eksekusi file: pindahkan 3 file baru ke folder M yang ditentukan (rename tambah tahun biar konsisten pola penamaan), hapus 3 file mismatch lama, folder `Arsitektur & Evaluasi.../` dan `Interaksi Manusia-Komputer.../` jadi kosong total → dihapus (migrasi ke skema `M0`-`M17` sekarang 100%, kecuali `1/Nggak dulu/` yang memang sengaja dikecualikan).
  7. Update `PAPER_NOTES.md`: 3 entry baru ditulis lengkap (kategori #1/#15/#16), tabel "File Bermasalah" dikosongkan dari baris mismatch (tersisa cuma 2 baris duplikat/versi-lain yang bukan masalah), ringkasan total diupdate jadi "0 mismatch tersisa, migrasi folder 100%".
  8. Update `sprint-paper-mapping.md`: TODO section diganti jadi "status selesai semua", 3 mismatch terakhir ditandai selesai dengan detail pengganti.
- **File yang dibuat/diubah:**
  - `Paper & Journal/F.R.I.D.A.Y/M1/A Survey of Large Language Models (2023).pdf`, `M15/A Mixed-Methods Approach to Understanding User Trust after Voice Assistant Failures (2023).pdf`, `M16/A Systematic Review on Fostering Appropriate Trust in Human-AI Interaction (2023).pdf` — baru (dipindah dari folder tematik lama).
  - `Paper & Journal/F.R.I.D.A.Y/Arsitektur & Evaluasi Sistem Asisten AI (Teknik & Komputasi)/`, `Interaksi Manusia-Komputer & Psikologi AI (Human-Computer Interaction)/` — dihapus (kosong).
  - `Memory Think/PAPER_NOTES.md` — 3 entry baru, tabel File Bermasalah & ringkasan diupdate.
  - `Memory Think/sprint-paper-mapping.md` — TODO section diupdate jadi selesai semua.
  - `Memory Think/SPRINT1_LOG.md` — entry ini.
- **Alasan/keputusan:**
  - Modul tujuan ditentukan dari isi paper yang sebenarnya, bukan otomatis ikut nama folder tematik lamanya — supaya konsisten dengan prinsip "1 paper = 1 folder modul utama" yang dipakai sejak rombak folder 2026-08-12.
  - Nama file baru ditambah "(2023)" mengikuti pola penamaan file lain di folder yang sama (tahun publikasi di akhir nama), bukan dipertahankan sama seperti nama file lama yang mismatch — beda dengan kasus M15 sebelumnya (Form Follows Function) yang nama filenya sengaja dipertahankan karena warisan; di sini tidak ada alasan mempertahankan nama lama karena filenya benar-benar baru dan berbeda topiknya dari nama file mismatch sebelumnya.
- **Belum dikerjakan / TODO lanjutan:**
  - Perubahan sesi ini **belum di-commit/push** — menunggu instruksi user.
  - M1 (agent loop ReAct) masih belum mulai coding — tetap next step utama untuk kode. Seluruh backlog riset paper sekarang sudah tuntas (0 mismatch tersisa), jadi tidak ada lagi alasan menunda mulai coding M1.

## [2026-08-13] Penutup hari: rekap status commit/push + koreksi 2 TODO basi

- **Apa yang dikerjakan:** User tanya apakah seluruh hasil kerja hari ini sudah tercatat. Dicek ulang urutan kronologis vs urutan entry di file ini (`grep` commit hash) — ketemu **2 baris TODO yang sudah basi**: entry "M1 Agent Core" (di atas, TODO poin terakhir) dan entry "Commit & push paper fixes..." (TODO di atasnya) sama-sama bilang "belum di-commit/push", padahal keduanya **sudah** di-push di turn-turn setelahnya. Entry lama sengaja tidak diedit langsung (konvensi append-only project ini — riwayat harus tetap utuh), jadi dikoreksi lewat entry penutup ini.
- **Rekap status commit/push hari ini (2026-08-13), urut kronologis nyata:**
  1. `0c05301` — fix M7/M14/M15/M17 mismatch pertama (dicatat entry "Verifikasi & perbaikan file paper pengganti..." di atas)
  2. `552496e` — fix 3 mismatch terakhir + migrasi folder 100% (dicatat entry "Commit & push paper fixes..." di atas — TODO "belum di-commit"-nya sudah tidak berlaku, sudah di-push sebagai commit ini)
  3. `f12d10a` — implementasi M1 Agent Core lengkap (dicatat entry "M1 Agent Core — implementasi awal loop ReAct" di atas — TODO "belum di-commit/push"-nya juga sudah tidak berlaku, sudah di-push sebagai commit ini)
- **File yang dibuat/diubah:** `Memory Think/SPRINT1_LOG.md` — entry ini saja (tidak ada perubahan kode/paper baru).
- **Alasan/keputusan:** Catatan chronological order di file ini sempat tidak pas dengan urutan waktu tulis sebenarnya (entry "Commit & push paper fixes..." ditulis sebelum entry M1, tapi posisinya di file muncul setelah) — bukan salah data, cuma urutan append yang meleset satu langkah. Diputuskan tidak reorder entry lama (berisiko dianggap mengubah riwayat), cukup diberi rekap eksplisit di sini supaya pembaca berikutnya tidak salah asumsi urutan kejadian.
- **Belum dikerjakan / TODO lanjutan:** Tidak ada tambahan baru — semua pekerjaan hari ini (paper fixes 2x commit + M1 implementation) sudah ter-push ke `origin/master`. Next step: mulai Sprint 2 (M2 Memory) atau perkuat M1 (tool IoT/OS nyata nunggu M4/M5, Reflexion persisten nunggu M2) — keputusan di tangan user.
