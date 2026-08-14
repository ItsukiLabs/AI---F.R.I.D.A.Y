# Sprint 2 — Log Pengerjaan (M2 Memory System)

> Datasheet pengerjaan Sprint 2. Setiap kali ada update fitur/logika (kode, schema, struktur), tambahkan entry baru di bawah — jangan edit entry lama, supaya riwayat tetap utuh dan tidak ambigu soal apa yang sudah dikerjakan.
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

## [2026-08-13] Setup log Sprint 2

- **Apa yang dikerjakan:** Sprint 1 (M0 Contract Layer + M1 Agent Core) selesai dan sudah di-push (commit `0c05301`, `552496e`, `f12d10a` — detail lengkap di `SPRINT1_LOG.md`). User konfirmasi lanjut ke Sprint 2 (M2 Memory System), diminta bikin file log terpisah mengikuti format `SPRINT1_LOG.md` — sesuai konvensi standing proyek ini bahwa tiap sprint punya file log sendiri di `Memory Think/`.
- **File yang dibuat/diubah:**
  - `Memory Think/SPRINT2_LOG.md` — baru (file ini).
- **Alasan/keputusan:**
  - Format & aturan sama persis dengan `SPRINT1_LOG.md` (append-only, catat diskusi bukan cuma kode) — supaya konsisten dan gampang dibandingkan lintas sprint.
  - M2 dipecah 3 sub-modul per `sprint-paper-mapping.md`: **M2a** (short-term/konteks aktif), **M2b** (long-term/retrieval-embedding), **M2c** (profile/hierarki memori & paging). 4 paper dasar sudah diriset dari sesi-sesi sebelumnya (lihat `PAPER_NOTES.md` kategori #2): **MemGPT** (⭐ Wajib — cetak biru hierarki memori ala virtual memory OS), **Generative Agents/Smallville** (memory stream + reflection berkala), **Lost in the Middle** (peringatan penempatan hasil retrieval dalam prompt), **RAG Survey 2023** (peta pola retrieval Naive→Advanced→Modular).
  - Ada overlap kecil dengan TODO tersisa M1: Reflexion di M1 saat ini cuma hidup satu sesi run — begitu M2 ada infrastruktur memori, refleksi kegagalan tool-call bisa dipersistenkan lintas sesi.
- **Belum dikerjakan / TODO lanjutan:**
  - Desain/implementasi M2 itu sendiri belum mulai — baru tahap setup log, belum ada plan mode atau kode.
  - `Memory Think/M2_memory.md` (catatan per-modul, ikut konvensi `M0_contract_layer.md`/`M1_agent_core.md`) belum dibuat — akan dibuat begitu diskusi/implementasi M2 mulai.

## [2026-08-13] Penegasan aturan: log setiap instruksi, bukan cuma kode

- **Apa yang dikerjakan:** User minta aturan standing yang sama seperti di Sprint 1 (lihat `SPRINT1_LOG.md`, entry "[2026-08-07] Penegasan aturan...") ditulis eksplisit juga di file log Sprint 2 ini — **setiap kali user menyuruh sesuatu**, entry baru ditambahkan ke `SPRINT2_LOG.md`, bukan cuma saat kode berubah, tapi juga diskusi/pertanyaan/keputusan konsep. Ini bukan aturan baru, cuma ditegaskan ulang supaya berlaku jelas per-file, tidak diasumsikan otomatis "nempel" dari Sprint 1.
- **File yang dibuat/diubah:**
  - `Memory Think/SPRINT2_LOG.md` — entry ini.
- **Alasan/keputusan:** Sama seperti alasan aslinya di Sprint 1 — jadi rujukan/"training" biar asisten nggak salah asumsi soal apa yang sudah dibahas, dan pengingat buat user sendiri biar nggak lupa progres/keputusan yang sudah diambil. Konvensi ini sudah tercatat juga di memori eksternal (`friday_progress_tracking.md`), tapi user tetap minta ditulis eksplisit di file log tiap sprint supaya jelas dari sisi dokumen proyek sendiri, tidak bergantung ke memori asisten di luar repo.
- **Belum dikerjakan / TODO lanjutan:** Tidak ada perubahan teknis — murni penegasan konvensi kerja, sama seperti TODO entry sebelumnya (desain/implementasi M2 belum mulai).

## [2026-08-14] Audit kecukupan paper M2 + verifikasi & perbaikan 10 file baru

- **Apa yang dikerjakan:**
  1. User tanya apakah paper M2 yang ada (4 paper: MemGPT, Generative Agents, Lost in the Middle, RAG Survey) sudah cukup untuk mulai desain M2. Dianalisis per sub-modul: M2c (hirarki) & M2a (konteks aktif) & M2b (retrieval) sudah tercover, tapi ada **gap nyata**: tidak ada paper soal mekanisme *forgetting/consolidation* untuk memori jangka panjang — penting karena F.R.I.D.A.Y jalan terus-menerus lintas sesi (beda dari Smallville yang cuma simulasi terbatas), tanpa strategi forgetting storage akan tumbuh tanpa batas.
  2. User diminta cek ulang isi folder `M2/` secara langsung (bukan cuma percaya catatan lama) — ternyata folder sudah berisi **15 file**, bukan 5 seperti di `PAPER_NOTES.md` (10 file baru sudah ditambahkan user tapi belum diverifikasi/dicatat), termasuk beberapa yang persis menjawab gap forgetting yang baru disebut (MemoryBank, FSFM, Survey on Memory Mechanism of LLM Agents, dkk).
  3. Verifikasi isi vs judul via `pdftotext` untuk semua 15 file (termasuk 5 lama, dicek ulang) — pola yang sama dipakai sejak Sprint 1 untuk kasus M7/M14/M15/M17. Hasil: **13 cocok**, **2 masalah**:
     - Duplikat 100% (md5 identik): `Generative Agents...(2023).pdf` (lama, tracked git) vs `Generative Agents...— Park et al. (2023), UIST.pdf` (baru, untracked)
     - Mismatch: `The Memory Function of Sleep — Diekelmann & Born (2010), Nature Reviews Neuroscience.pdf` isinya bukan paper itu — isi asli "About Sleep's Role in Memory" oleh Rasch & Born (2013), *Physiological Reviews*
     - Bonus: 1 salah atribusi nama file (bukan mismatch konten) — "Recursively Summarizing...— Qian et al." seharusnya "— Wang et al." (penulis asli tidak ada nama Qian)
  4. Eksekusi perbaikan: hapus file duplikat yang untracked (bukan yang tracked, biar tidak ada churn git tidak perlu), rename file sleep menyesuaikan isi asli (bukan cari paper pengganti, karena isinya tetap relevan buat topik consolidation), rename file Recursively Summarizing dengan atribusi benar. Hasil akhir folder `M2/`: **14 file**, semua cocok isi vs judul, 0 duplikat, 0 mismatch.
  5. Tulis 9 entry baru lengkap di `PAPER_NOTES.md` kategori #2 (ringkasan ide inti dari abstract masing-masing via `pdftotext`, relevansi ke sub-modul M2a/b/c, catatan koreksi nama file), update ringkasan total paper (108→117) dan tambah update log ke-4. Update `sprint-paper-mapping.md`: tabel Kategori #2 diperluas dari 3 jadi 14 baris paper, jumlah di tabel induk diupdate.
- **File yang dibuat/diubah:**
  - `Paper & Journal/F.R.I.D.A.Y/M2/` — 1 file duplikat dihapus, 2 file di-rename (sleep paper, Recursively Summarizing).
  - `Memory Think/PAPER_NOTES.md` — 9 entry baru di kategori #2, update ringkasan total & update log.
  - `Memory Think/sprint-paper-mapping.md` — tabel kategori #2 diperluas 3→14 paper, tabel induk diupdate.
  - `Memory Think/SPRINT2_LOG.md` — entry ini.
- **Alasan/keputusan:**
  - Standar verifikasi "cek isi PDF asli, jangan percaya nama file" tetap dipertahankan sebagai kebiasaan proyek — kembali terbukti berguna, menemukan 1 mismatch nyata dan 1 duplikat yang kalau tidak dicek akan tercatat sebagai "sudah lengkap" padahal salah.
  - File sleep yang mismatch **tidak** diganti dengan mencari paper "The Memory Function of Sleep" yang benar — cukup rename menyesuaikan isi asli, karena paper yang ada (Rasch & Born 2013) topiknya tetap relevan langsung untuk consolidation, jadi tidak ada alasan kuat membuang isi yang sudah bagus hanya karena nama filenya salah (sama prinsipnya dengan kasus "Form Follows Function" di Sprint 1).
  - Duplikat dihapus dari sisi yang untracked di git supaya tidak ada delete+re-add churn yang tidak perlu di riwayat commit.
- **Belum dikerjakan / TODO lanjutan:**
  - Perubahan sesi ini (file paper + 2 markdown notes) **belum di-commit/push** — menunggu instruksi user, sama seperti 2 perubahan `SPRINT1_LOG.md`/`SPRINT2_LOG.md` sebelumnya yang juga masih pending commit.
  - Riset paper M2 sekarang dianggap cukup kuat untuk mulai desain — termasuk sub-topik forgetting/consolidation M2c yang sebelumnya jadi gap. Next step: mulai plan mode untuk arsitektur M2 (M2a/M2b/M2c), belum ada kode maupun `M2_memory.md` sama sekali.

## [2026-08-14] M2a — desain arsitektur + implementasi lengkap short-term/active-context memory

- **Apa yang dikerjakan:**
  1. User minta mulai desain arsitektur M2a. Sebelum masuk plan mode, dijelaskan dulu (diskusi konsep, bukan kode): apa itu M2 secara keseluruhan, kenapa dipecah M2a/M2b/M2c (analogi working memory vs long-term archive vs hierarki-organisasi ala manusia), scope M2a spesifik (cuma konteks aktif satu sesi, bukan cross-session recall), dan klarifikasi bahwa voice recognition (M7-M10) **bukan** bagian M2 sama sekali — cuma modul input terpisah yang hasil transkripnya masuk ke pipeline M1/M2 yang sama seperti teks biasa.
  2. Masuk plan mode. Eksplorasi kode M1 (`loop.py`, `llm_client.py`) + paper M2a (MemGPT, Lost in the Middle, Recursively Summarizing) dilakukan langsung (bukan re-derive lewat subagent karena codebase masih kecil), lalu didelegasikan ke 1 agent Plan (dengan full context di-paste) untuk desain file-level.
  3. 3 keputusan desain dikonfirmasi user lewat `AskUserQuestion`: (a) persistensi ke **file JSON per sesi** (bukan SQLite — ditunda ke M2b), (b) sinyal "memory pressure" pakai **token asli dari respons API Anthropic** (`usage.input_tokens`, bukan estimasi karakter), (c) kompaksi pakai **recursive LLM summarization** sesuai paper (bukan sliding-window truncation).
  4. Muncul pertanyaan susulan dari user: siapa yang manggil `save()` — nunggu modul `orchestrator/` atau di-wire sekarang? Dicek `git`/`SPRINT1_LOG.md`: folder `backend/orchestrator/` ternyata **kosong sejak Sprint 1** (dibuat sebagai placeholder umum, bukan tied ke sprint/M-nomor manapun — beda dari M14 "Multi-Agent Orchestration" yang scope-nya spesifik koordinasi banyak agent). Karena tidak ada kepastian kapan folder itu terisi, diputuskan tambah **wrapper tipis `run_with_memory()`** yang auto-save tiap giliran, supaya fitur "inget lintas restart" beneran aktif sekarang, bukan cuma scaffolding. Ditambah 1 keputusan lagi: gap token overflow di tengah satu panggilan (`run_agent()` dengan banyak iterasi tool) **diterima** untuk versi pertama (`max_iterations` sudah membatasi risikonya), tidak ditambah hard-truncate darurat.
  5. Plan final ditulis, di-approve user, lalu dieksekusi penuh — lihat daftar file di bawah.
  6. `python -m pytest backend/tests/ -v` — sempat 1 test gagal (`test_run_with_memory_creates_and_persists_a_new_session`), ternyata bug di assertion test-nya sendiri (assert `content` sebagai string polos, padahal `_assistant_message()` selalu bungkus jadi content-block list `[{"type":"text",...}]`) — bukan bug di `runner.py`/`loop.py`. Diperbaiki assertion-nya. Setelah fix: **43/43 test lulus** (19 lama M0/M1 + 24 baru M2a).
  7. Smoke test manual dengan `ANTHROPIC_API_KEY` asli: 2 panggilan `run_with_memory()` terpisah, `session_id` sama — "My name is Ernold and I like cats." lalu "What is my name, and what do I like?". Giliran kedua benar jawab nama & preferensi dari giliran pertama, dibaca ulang dari file JSON di disk (bukan dari state proses) — bukti continuity beneran jalan end-to-end, bukan cuma lulus test dengan `FakeLLMClient`. File smoke test dihapus setelah verifikasi (tidak masuk git — `backend/memory/sessions/*.json` sudah di-gitignore).
- **File yang dibuat/diubah:**
  - `backend/schemas/memory_contract.py` — baru: `MessageRecord`, `SessionRecord` (Pydantic), `MEMORY_SCHEMA_VERSION`.
  - `backend/schemas/__init__.py` — re-export simbol memory_contract baru.
  - `backend/memory/__init__.py`, `session.py`, `compaction.py`, `store.py`, `runner.py` — baru: `Session`, `compact()`, `SessionStore`, `run_with_memory()`. `runner.py` sengaja **tidak** di-re-export dari `__init__.py` (dia impor `agent_core/loop.py`, yang mana `loop.py` impor `memory/session.py` — re-export dari `__init__` bakal jadi circular import).
  - `backend/memory/sessions/.gitkeep` — baru: placeholder folder data (isi `*.json` di-gitignore).
  - `backend/agent_core/llm_client.py` — `LLMResponse` dapat field baru `input_tokens`/`output_tokens` (default `None`, tidak breaking), diisi dari `response.usage` SDK Anthropic yang sebelumnya dibuang.
  - `backend/agent_core/loop.py` — `run_agent()` dapat parameter baru `session: Session | None = None`, additive murni (perilaku `session=None` identik 100% ke sebelum M2a). `messages.append(_assistant_message(response))` dipindah ke atas early-return supaya turn jawaban final juga masuk riwayat sesi.
  - `backend/agent_core/config.py` — `get_memory_compaction_threshold_tokens()` (default 6000), `get_memory_keep_recent_messages()` (default 6).
  - `.env.example` — dokumentasi 2 var baru `MEMORY_COMPACTION_THRESHOLD_TOKENS`, `MEMORY_KEEP_RECENT_MESSAGES`.
  - `.gitignore` — tambah `backend/memory/sessions/*.json`.
  - `backend/tests/test_memory_session.py`, `test_memory_compaction.py`, `test_memory_store.py`, `test_memory_runner.py`, `test_agent_loop_session.py` — baru: 24 test, semua pakai `FakeLLMClient` (pola sama seperti `test_agent_loop.py`), tidak ada panggilan API asli. `test_agent_loop.py` lama **tidak diubah sama sekali** (regression guard untuk `session=None`).
  - `Memory Think/M2_memory.md` — baru, mengikuti konvensi `M0_contract_layer.md`/`M1_agent_core.md` (Kegunaan/Pendekatan/Ringkasan Teknis/Bahasa Awam).
  - `Memory Think/SPRINT2_LOG.md` — entry ini.
- **Alasan/keputusan:**
  - Kompaksi cuma dicek di **awal** `run_agent()` (bukan di tengah loop) karena Anthropic API menolak riwayat yang motong pasangan `tool_use`/`tool_result` — satu-satunya titik potong yang selalu aman adalah tepat sebelum turn user baru, dan itu cuma muncul di awal panggilan.
  - `session.messages` (durable, dipersist apa adanya) dan `session.to_llm_messages()` (presentasi, dihitung ulang tiap panggilan, nyisipin summary di depan + ack sintetis + turn terbaru di belakang) sengaja dipisah — jawaban konkret untuk Lost-in-the-Middle tanpa bikin persistensi ribet.
  - `SessionRecord` cuma punya 1 field versi (`schema_version`), **tidak** meniru split `contract_version`/`version` ala M0 — sesi cuma punya 1 sumbu perubahan (bentuk file), beda dari `ToolContract` yang punya 2 sumbu independen (bentuk kontrak vs versi tiap tool).
  - `run_with_memory()` dipisah dari `run_agent()` supaya loop inti tetap bebas efek samping I/O (gampang di-test, tidak ada tulis-disk tersembunyi), tapi fitur "inget lintas restart" tetap beneran aktif sekarang tanpa nunggu modul `orchestrator/` yang belum punya jadwal pasti.
- **Belum dikerjakan / TODO lanjutan:**
  - Perubahan sesi ini **belum di-commit/push** — menunggu instruksi user.
  - Mid-call token overflow belum ada pengaman darurat (diterima sebagai gap v1, lihat `M2_memory.md`).
  - M2b (long-term/retrieval) dan M2c (profile/hierarki/forgetting) belum digarap — `session.archived_turns` sudah jadi seam/hook untuk M2b tapi belum ada yang membacanya.
  - Default threshold kompaksi (6000 token / 6 pesan) masih tebakan awal, belum divalidasi pemakaian nyata jangka panjang.

## [2026-08-14] Review arsitektur M2a sebelum commit — validasi terhadap prinsip "context ≠ memory"

- **Apa yang dikerjakan:** Sebelum commit, user minta review ulang M2a terhadap prinsip eksplisit: **"F.R.I.D.A.Y must never confuse conversation context with memory"** dan **"summarization compresses context; it must not invent or promote unspoken assumptions into user facts or preferences."** User kasih 8 poin review + taksonomi memori yang diinginkan (`Session` vs `Memory` terpisah; `Memory` = Working/Long-Term/Profile/Task-State). Diminta diskusi dulu (bukan langsung eksekusi/laporan formal) dan disela kalau ada bagian yang kurang tepat.
  1. Dibahas 1-per-1: 5 dari 8 poin dikonfirmasi **sudah benar tanpa perlu tindakan** (Session bukan Memory; atomic tool-call safety via `_find_safe_cut_index`, tidak perlu refactor jadi class `Turn`; persistence boundary `run_with_memory()`; tidak ada M2b/M2c yang menyelinap masuk; `current_task` tidak dihalangi struktur `Session` sekarang).
  2. 2 poin disela dengan reasoning teknis: **poin 5** (ganti `last_input_tokens` jadi estimasi context saat ini) — ditolak, karena (a) estimasi tanpa tokenizer asli itu balik ke heuristik karakter yang sudah ditolak di awal Sprint 2, menurunkan akurasi bukan menaikkan, dan (b) celah mid-call overflow itu **struktural** (soal di mana boleh potong — constraint tool_use/tool_result — bukan soal akurasi pengukuran token), jadi estimator lebih baik pun tidak menutup celah itu. Diusulkan jalan tengah: `safety_margin` ditambahkan ke perhitungan threshold, bukan estimator baru. **Poin 4** (bangun `context_limit`/`reserved_output_tokens`/`safety_margin` sekaligus) — ditolak sebagian: cukup `safety_margin` sekarang, sisanya didokumentasikan sebagai TODO eksplisit ditunda ke Sprint 8 (multi-model), karena F.R.I.D.A.Y baru punya 1 provider/model.
  3. 1 poin (poin 2, risiko degradasi repeated-summarization) disetujui substansinya tapi diusulkan solusi lebih murah: perketat `SUMMARIZATION_SYSTEM_PROMPT` (instruksi eksplisit, bukan metadata/tracking baru).
  4. Ditemukan 1 gap tambahan dari sisi saya sendiri saat membaca ulang prompt kompaksi: `SUMMARIZATION_SYSTEM_PROMPT` lama belum eksplisit melarang model menyimpulkan preferensi di luar yang dinyatakan — langsung dikaitkan ke prinsip inti user (contoh "makan nasi goreng" vs "suka nasi goreng").
  5. 1 usul kecil soal taksonomi: `current_task`/`current_objective` didudukkan sebagai bagian **working memory (M2a)**, bukan kategori ke-4 yang berdiri sendiri sejajar Working/Long-Term/Profile — disetujui user.
  6. User approve final scope: 3 perubahan kode (safety margin + wiring, prompt kompaksi diperketat, dokumentasi TODO multi-model) — dieksekusi persis sesuai scope, tidak lebih.
  7. Verifikasi: `python -m pytest backend/tests/ -v` → **47/47 lulus** (43 lama + 4 test baru untuk safety margin). Smoke test manual dengan API key asli 2x: (a) continuity 2 giliran masih normal (regresi aman), (b) tes langsung `compact()` dengan input "I ate fried rice today" → summary hasil benar tetap literal ("The user ate fried rice today"), **tidak** berubah jadi "the user likes fried rice" — bukti prompt yang diperketat bekerja nyata, bukan cuma klaim.
- **File yang diubah:**
  - `backend/agent_core/config.py` — tambah `get_memory_compaction_safety_margin_tokens()` (default 500) + `DEFAULT_MEMORY_COMPACTION_SAFETY_MARGIN_TOKENS`, tambah komentar TODO eksplisit soal `context_limit`/`reserved_output_tokens` ditunda ke Sprint 8.
  - `backend/memory/session.py` — `Session.needs_compaction()` terima parameter baru `safety_margin_tokens: int = 0` (default backward-compatible), cek jadi `last_input_tokens + safety_margin_tokens >= threshold_tokens`.
  - `backend/agent_core/loop.py` — `run_agent()` sekarang kirim `get_memory_compaction_safety_margin_tokens()` ke `needs_compaction()`.
  - `backend/memory/compaction.py` — `SUMMARIZATION_SYSTEM_PROMPT` diperketat: batas ~250 kata, larangan eksplisit menyimpulkan preferensi/fakta di luar yang dinyatakan (dengan contoh konkret nasi goreng).
  - `.env.example` — dokumentasi `MEMORY_COMPACTION_SAFETY_MARGIN_TOKENS`.
  - `backend/tests/test_memory_session.py` — 3 test baru untuk safety margin (default 0, margin bikin trigger lebih awal, margin belum cukup tetap false).
  - `backend/tests/test_agent_loop_session.py` — 1 test baru (`test_compaction_safety_margin_is_wired_through_config`) yang buktikan margin dari config beneran nyambung ke `run_agent()`, bukan cuma logic `Session` yang teruji sendirian.
  - `Memory Think/M2_memory.md` — tambah bagian "Review arsitektur (2026-08-14, sebelum commit)" merangkum hasil diskusi + alasan tiap keputusan, update daftar TODO.
  - `Memory Think/SPRINT2_LOG.md` — entry ini.
- **Alasan/keputusan:** Lihat poin 2-5 di atas — inti keputusannya adalah menjaga M2a tetap sederhana & deterministic (sesuai prinsip user), menolak menambah kompleksitas (estimator token, metadata tracking, abstraction multi-model) kalau ada solusi lebih murah yang menjawab masalah yang sama, dan menjaga batas tegas antara "context percakapan aktif" (M2a) vs "memori permanen" (M2b/M2c) supaya F.R.I.D.A.Y tidak diam-diam mulai membentuk preferensi/fakta permanen dari obrolan biasa tanpa instruksi eksplisit user.
- **Belum dikerjakan / TODO lanjutan:** Perubahan review ini **belum di-commit/push** — sesuai instruksi eksplisit user (review dulu, tunggu approval, baru commit). Semua TODO M2a lain dari entry sebelumnya masih berlaku (mid-call overflow gap, M2b/M2c belum mulai, dst.).
