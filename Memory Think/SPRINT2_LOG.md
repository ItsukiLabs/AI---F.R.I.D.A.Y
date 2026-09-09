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

## [2026-08-14] Robustness pass final — persistence integrity, schema evolution, error behavior, security boundary

- **Apa yang dikerjakan:** Setelah review arsitektur di-approve & di-push (commit `a1f5f0d`), user minta **satu robustness pass terakhir** sebelum M2a benar-benar dianggap selesai, dengan alasan: begitu data hidup di disk, M2a bukan lagi sekadar "fitur percakapan" tapi sudah jadi **persistent state layer** F.R.I.D.A.Y — masalah kayak corrupt file, schema evolution, partial write, error recovery jadi lebih penting daripada nambah fitur baru.
  1. Saya audit read-only dulu (baca ulang `store.py`, `memory_contract.py`, `runner.py` yang sudah di-push) di 5 dimensi yang diminta: persistence integrity, schema evolution, error behavior, security boundary, test boundary. Ditemukan 3 gap nyata (bukan cuma kurang test): (a) `save()` nulis langsung ke file final, non-atomic — proses mati di tengah nulis = sesi permanen korup; (b) `schema_version` cuma field dekoratif, nggak pernah dicek pas `load()` — versi lama/rusak bisa "berhasil" dimuat dengan data salah tanpa peringatan; (c) nggak ada exception handling sama sekali — file korup/gagal save = raw Python traceback sampai ke user.
  2. Untuk poin error behavior, saya kasih 2 opsi ke user: (A) fail loud — lempar error jelas, jangan diam-diam mulai sesi baru; (B) fail soft — auto-mulai sesi baru + log warning. Saya rekomendasikan (A) dengan alasan: untuk personal AI yang nyimpen fakta pribadi, kehilangan riwayat secara diam-diam lebih berbahaya daripada crash dengan pesan jelas.
  3. User setuju full sama hasil audit + pilih opsi (A), plus kasih keputusan final untuk 8 poin: atomic write (DO NOW), schema version validation (DO NOW, tanpa migration framework), error behavior fail-loudly pakai domain-specific exceptions (DO NOW), file permission cross-platform best-effort (DO NOW, bukan ACL besar), test boundary lengkap (DO NOW, termasuk angka boundary safety-margin persis: threshold 6000/margin 500 → 5499 tidak trigger, 5500 & 6000 trigger), error-path persistence (AUDIT saja, jangan auto-refactor jadi finally-save karena bisa ubah semantik), logging/privacy (AUDIT), concurrent access (NON-GOAL, didokumentasikan saja). Scope guard eksplisit: jangan nambah vector-db/embedding/retrieval/profile-inference/forgetting/ranking/multi-model-abstraction/tokenizer/distributed-locking/migration-framework.
  4. Eksekusi sesuai scope — lihat daftar file di bawah.
  5. `python -m pytest backend/tests/ -v` → **58 passed, 1 skipped** (skip: test permission POSIX di-skip otomatis di Windows, by design — `pytest.mark.skipif(sys.platform == "win32")`).
  6. Smoke test manual dengan API key asli: (a) continuity 2 giliran masih normal lewat code path baru (regresi aman), (b) tidak ada temp file tersisa setelah save asli, (c) file JSON sengaja dikorupkan → `SessionLoadError` (bukan silent None/crash mentah), (d) file dengan `schema_version` lama → `UnsupportedSessionSchemaError` — ketiganya diverifikasi nyata, bukan cuma lulus test dengan mock.
- **File yang dibuat/diubah:**
  - `backend/memory/errors.py` — baru: `SessionError` (base), `SessionLoadError`, `SessionSaveError`, `UnsupportedSessionSchemaError` (subclass `SessionLoadError`).
  - `backend/memory/store.py` — `save()` ditulis ulang jadi atomic (`tempfile.mkstemp` + `os.replace`), tambah `_restrict_permissions()` (chmod 0600 best-effort, cross-platform), `load()` sekarang cek `schema_version` eksplisit dan bungkus semua kegagalan jadi exception domain-spesifik (bukan biarin `JSONDecodeError`/`OSError`/`ValidationError` mentah bocor).
  - `backend/memory/__init__.py` — re-export 4 exception baru.
  - `backend/tests/test_memory_store.py` — 6 test baru: corrupt JSON, schema unsupported, field wajib hilang, temp file nggak pernah ke-load sebagai sesi, round-trip Unicode/emoji, permission POSIX (skip di Windows).
  - `backend/tests/test_memory_session.py` — 3 test baru: boundary safety-margin persis (5499/5500/6000), 2 test baru untuk `to_llm_messages()` dengan `messages` kosong.
  - `backend/tests/test_memory_compaction.py` — 1 test baru: `compact()` dengan `messages` kosong, no-op aman.
  - `Memory Think/M2_memory.md` — tambah bagian "Robustness pass" merangkum semua temuan & perbaikan, termasuk 3 hasil audit (error-path persistence, logging/privacy, concurrent access) yang **sengaja tidak diperbaiki**, cuma didokumentasikan sesuai instruksi user.
  - `Memory Think/SPRINT2_LOG.md` — entry ini.
- **Alasan/keputusan:** Lihat poin 1-3 di atas. Inti prinsip yang dijaga: **"F.R.I.D.A.Y must never silently replace broken memory with an empty memory"** — semua kegagalan persistence sekarang eksplisit (exception bertipe jelas), bukan diam-diam ke-recover jadi state kosong. Perbaikan yang dilakukan semuanya murah & langsung jawab skenario kegagalan konkret (bukan defensive programming spekulatif) — atomic write & schema check khususnya karena risikonya nyata (sesi ke-brick permanen / data salah senyap), bukan cuma teoretis.
- **Belum dikerjakan / TODO lanjutan:** Perubahan sesi ini **belum di-commit/push** — menunggu instruksi user. 3 gap yang diaudit tapi sengaja tidak diperbaiki (error-path persistence, permission Windows, concurrent access) didokumentasikan lengkap di `M2_memory.md`. M2a sekarang dianggap selesai secara robust menurut kriteria user — next step: M2b (long-term/retrieval) atau M2c (profile/forgetting), keputusan di tangan user.

## [2026-08-18] M2c — desain arsitektur + implementasi lengkap profile memory

- **Apa yang dikerjakan:**
  1. Sesi dibuka dengan user minta rekap progres proyek dari `Memory Think/` — dijawab ringkas (M0/M1 selesai, M2a selesai termasuk robustness pass, M2b/M2c belum mulai).
  2. User minta "reka ulang" list M2a + cocokkan sama alurnya + jalankan test — dilakukan audit non-destruktif (baca ulang semua file M2a), disusun daftar 8 komponen file + alur eksekusi `run_with_memory()` → `run_agent()` → kompaksi → save, dikonfirmasi konsisten dengan `M2_memory.md`. Test suite dijalankan: 58 passed, 1 skipped. Smoke test manual API asli 2 giliran (continuity) juga dijalankan ulang untuk verifikasi — berhasil, file smoke test dihapus setelahnya.
  3. User bingung milih M2b vs M2c duluan (dapat saran campur dari luar) — diberi rekomendasi M2c duluan dengan 2 alasan: (a) nilai lebih langsung kerasa (gap "F.R.I.D.A.Y amnesia lintas session_id" langsung ditutup tanpa infra baru), (b) M2b (retrieval) lebih berguna kalau sudah ada banyak data buat dicari, sementara `archived_turns` M2a sekarang masih kosong nyaris tidak terpakai.
  4. User tanya apa perlu cari paper tambahan buat M2c — dicek `sprint-paper-mapping.md` kategori #2, ditemukan cakupan sudah kuat (MemGPT untuk hirarki, FSFM+MemoryBank untuk forgetting, Generative Agents untuk reflection, plus 1 paper di M17 — "Enabling Personalized Long-term Interactions..." — yang eksplisit dicatat relevan juga ke M2). Kesimpulan: tidak perlu paper baru, langsung plan mode.
  5. Diselingi 1 diskusi konseptual (bukan kode): user tanya soal bagaimana AI umumnya "training" dengan data yang salah/miss-com dibanding cara F.R.I.D.A.Y "memory" menangani hal serupa — dijelaskan beda fundamental training (statistik, sulit "dihapus" 1 fakta) vs memory (baca-ulang konteks, tidak ada pengenceran statistik, tapi gampang diedit) — dan dikaitkan langsung ke kebutuhan desain M2c (provenance fakta, correction/override).
  6. Masuk plan mode. 3 keputusan arsitektur dikonfirmasi user lewat `AskUserQuestion`: (a) cara fakta masuk = **tool eksplisit** `remember_user_fact` (bukan ekstraksi otomatis/piggyback kompaksi), (b) konflik fakta = **newest wins + superseded trail**, (c) forgetting v1 = **manual delete saja** (decay Ebbinghaus/FSFM ditunda v2).
  7. Desain detail file-level didelegasikan ke 1 Plan agent (full context M0/M1/M2a + 3 keputusan di atas) — hasil: skema `ProfileFact`/`ProfileRecord` (id sequential, category freeform), `ProfileStore` (singleton `profile.json`, robustness properties diduplikasi dari `SessionStore` bukan diekstrak), tool binding via factory `make_profile_tools(profile)` terikat ke objek `Profile` runtime (bukan `ProfileStore`, supaya tidak ada 2 salinan yang divergen dalam 1 turn), wiring lewat `system` prompt (bukan `messages`, supaya profile fact tidak pernah lewat jalur summarization), `run_with_profile_memory()` baru terpisah dari `run_with_memory()` (tidak disentuh sama sekali).
  8. 1 keputusan produk tersisa (permission_tier `forget_user_fact`) dikonfirmasi user lewat `AskUserQuestion`: **STANDARD** (bukan `CRITICAL`) — karena tool ini by-design cuma jalan atas permintaan eksplisit user, risiko model salah panggil sendiri rendah.
  9. Plan final ditulis, di-approve user, dieksekusi penuh sesuai urutan 10 langkah di plan — lihat daftar file di bawah.
  10. `python -m pytest backend/tests/ -v` → **97 passed, 2 skipped** (58 lama + 39 baru M2c), regresi nol — `test_agent_loop.py`/`test_agent_loop_session.py`/`test_memory_runner.py` lama tidak diubah sebaris pun.
  11. Smoke test manual dengan `ANTHROPIC_API_KEY` asli, 4 giliran mencakup seluruh fitur: remember (session A) → recall lintas session_id beda (session B) → supersede otomatis lewat model manggil tool sendiri saat dikasih info kontradiktif → forget eksplisit. Semua 4 skenario jalan tanpa intervensi manual, file `profile.json`/session smoke test dihapus setelah verifikasi.
- **File yang dibuat/diubah:**
  - `backend/schemas/profile_contract.py`, `backend/memory/profile_errors.py`, `backend/memory/profile.py`, `backend/memory/profile_store.py`, `backend/agent_core/tools/profile_tools.py` — baru.
  - `backend/schemas/__init__.py`, `backend/memory/__init__.py`, `backend/agent_core/tool_registry.py` (tambah `registered_tools()`), `backend/agent_core/loop.py` (tambah param `profile`), `backend/memory/runner.py` (tambah `run_with_profile_memory()`), `.gitignore` — diubah, semuanya additive.
  - `backend/memory/profile/.gitkeep` — baru (folder data, isi `*.json` di-gitignore, mirror `sessions/`).
  - `backend/tests/test_profile_contract.py`, `test_profile.py`, `test_profile_store.py`, `test_agent_loop_profile.py`, `test_profile_tools.py`, `test_memory_runner_profile.py` — baru (39 test total termasuk 1 tambahan di `test_tool_registry.py`).
  - `Memory Think/M2_memory.md` — status diupdate, bagian "Pendekatan (M2c)" + "Ringkasan Teknis" M2c ditulis lengkap, "Bahasa Awam" diperluas dengan analogi "kartu identitas".
  - `Memory Think/SPRINT2_LOG.md` — entry ini.
- **Alasan/keputusan:** Lihat poin 6-8 di atas untuk 4 keputusan arsitektur utama + alasannya masing-masing. Prinsip inti yang dijaga sama seperti M2a: **"F.R.I.D.A.Y must never confuse conversation context with memory"** — sekarang diperluas jadi 2 lapis eksplisit (context=M2a summary, memory=M2c profile), keduanya sengaja dijaga tidak saling bocor (profile tidak lewat `messages`/compaction, session tidak punya akses tulis ke profile kecuali lewat tool eksplisit).
- **Belum dikerjakan / TODO lanjutan:**
  - Perubahan sesi ini **belum di-commit/push** — menunggu instruksi user.
  - Decay otomatis (MemoryBank/FSFM) — TODO v2, didokumentasikan di `M2_memory.md`, tidak diimplementasikan.
  - M2b (retrieval/embedding) — belum mulai, `archived_turns` masih hook kosong.
  - Error-path persistence (kalau `session_store.save()` sukses tapi `profile_store.save()` gagal) — mewarisi gap yang sama dengan M2a, didokumentasikan tidak diperbaiki sepihak.
  - `permission_tier` `forget_user_fact` = `STANDARD` bisa direvisit pas M11 (Security) kalau ternyata butuh konfirmasi tambahan.

## [2026-09-04] Commit + push M2c

- **Apa yang dikerjakan:** User minta commit & push hasil implementasi M2c. Test suite dijalankan ulang sebelum commit (`python -m pytest backend/tests/ -q` → 97 passed, 2 skipped). Semua 21 file M2c (5 modul baru + 6 file test baru + `profile/.gitkeep` + perubahan additive di `loop.py`/`runner.py`/`tool_registry.py`/`__init__.py` + `.gitignore` + `M2_memory.md` + `SPRINT2_LOG.md`) di-stage dan di-commit sebagai `643fd2d` (`feat(m2c): implement profile memory (long-term user facts)`), lalu di-push ke `origin/master` (`d6611c6..643fd2d`).
- **File yang dibuat/diubah:** `Memory Think/SPRINT2_LOG.md` — entry ini. (Sisanya = isi commit `643fd2d`, sudah didetailkan di entry `[2026-08-18]`.)
- **Alasan/keputusan:** TODO "belum di-commit/push" dari entry `[2026-08-18]` sekarang **selesai** — M2c sudah ada di remote.
- **Belum dikerjakan / TODO lanjutan:** Sama seperti entry `[2026-08-18]` minus item commit/push: decay otomatis (v2), M2b belum mulai, error-path persistence lintas store, revisit `permission_tier` di M11.

## [2026-09-09] Rekap posisi + verifikasi 6 paper baru M2b

- **Apa yang dikerjakan:**
  1. Sesi dibuka dengan user tanya "pembahasan kemarin sampai mana" — dijawab dari `SPRINT2_LOG.md` + `git log`: terakhir tercatat 2026-09-04 (commit+push M2c), M2b belum mulai, dan ditemukan 6 PDF baru untracked di `M2/` (semua ditambahkan user 2026-09-09 sore, belum diverifikasi/dicatat).
  2. User minta lanjut M2b dengan referensi tambahan dari jurnal yang baru ditambahkan (user menyebut "2 jurnal", tapi di folder ada **6** file baru — semuanya diperiksa, tidak ada yang diasumsikan). Verifikasi via `pdftotext` halaman pertama + md5 untuk 6 file: **6/6 cocok isi vs judul, 0 duplikat** (md5 unik, beda dari 14 file lama). 1 koreksi kecil: survei "Graph-based Agent Memory" dinamai "(2025)" padahal arXiv 2602.05665 = Feb 2026 → di-rename "(2026)". Catatan: HippoRAG "(2025)" = tahun arXiv v3, publikasi resmi NeurIPS 2024 — bukan mismatch, cuma dicatat.
  3. Tulis 6 entry baru di `PAPER_NOTES.md` kategori #2 (ringkasan dari abstract+intro, relevansi ke M2b, catatan kritis untuk paper vendor: Zep & Mem0 & Storage Is Not Memory semuanya technical report perusahaan dengan angka benchmark yang tidak bisa dibandingkan lintas paper mentah-mentah). Update total (117→123) + update log #5. `sprint-paper-mapping.md`: tabel kategori #2 14→20 baris, tabel induk diupdate.
- **File yang dibuat/diubah:**
  - `Paper & Journal/F.R.I.D.A.Y/M2/Graph-based Agent Memory ... (2025).pdf` → di-rename `(2026)`.
  - `Memory Think/PAPER_NOTES.md` — 6 entry baru kategori #2, total & update log.
  - `Memory Think/sprint-paper-mapping.md` — tabel kategori #2 + tabel induk.
  - `Memory Think/SPRINT2_LOG.md` — entry ini.
- **Alasan/keputusan:**
  - Standar "cek isi PDF, jangan percaya nama file" dipertahankan — kali ini semua bersih kecuali 1 salah tahun.
  - Pembacaan awal untuk arah M2b (belum diputuskan, baru bahan diskusi): 6 paper ini terbelah jadi 2 kubu — **extraction-centered** (Mem0, Zep: parse percakapan jadi fakta/graph saat ingest) vs **retrieval-centered** (Storage Is Not Memory: simpan event verbatim, pintar di sisi retrieval). Kubu kedua paling selaras dengan prinsip proyek yang sudah dipegang sejak M2a ("summarization must not invent facts", `archived_turns` disimpan mentah) dan konstrain lokal satu-mesin (SQLite, tanpa vector DB/GPU). Memory OS memvalidasi pemecahan 3-lapis short/mid/long yang sudah kita punya, dengan **mid-term = celah yang akan diisi M2b**.
- **Belum dikerjakan / TODO lanjutan:**
  - 6 PDF + 3 markdown **belum di-commit** — menunggu instruksi user.
  - Desain arsitektur M2b belum mulai — next step: diskusi arah (extraction vs retrieval-centered, SQLite vs vector store, apa yang di-index: `archived_turns` saja atau seluruh sesi) lalu plan mode.

## [2026-09-09] M2b — desain arsitektur + implementasi lengkap long-term cross-session recall

- **Apa yang dikerjakan:**
  1. Setelah verifikasi 6 paper (entry sebelumnya), user minta lanjut M2b. Dijelaskan dulu (diskusi, bukan kode) bahwa 6 paper terbelah 2 kubu — extraction-centered (Mem0, Zep) vs retrieval-centered (Storage Is Not Memory) — dan kubu kedua paling selaras dengan prinsip proyek ("context ≠ memory", `archived_turns` disimpan mentah, fakta cuma lewat tool eksplisit) + konstrain lokal satu-mesin (SQLite, tanpa vector DB/GPU). Memory OS memvalidasi struktur 3-lapis: mid-term = celah M2b.
  2. 3 keputusan arsitektur dikonfirmasi user lewat `AskUserQuestion`: (a) **retrieval-centered verbatim + SQLite FTS5** (bukan hybrid embedding, bukan extraction ala Mem0), (b) **index semua turn semua sesi** (bukan cuma `archived_turns`), (c) **tool eksplisit `recall_memory`** (bukan auto-inject tiap turn).
  3. Masuk plan mode. Eksplorasi kode M2a/M2c dilakukan langsung (codebase kecil), lalu desain file-level didelegasikan ke 1 Plan agent dengan full context + draft desain + 5 pertanyaan teknis. Agent memverifikasi semua perilaku FTS5 yang diandalkan secara empiris di SQLite venv (external-content FTS5 + `bm25()`, fold diakritik, sanitasi sintaks, `UNIQUE` di tabel dasar) dan menemukan **2 lubang di draft awal**: (i) kunci idempotensi `session_id` saja salah — file sesi rutin dihapus & dibuat ulang dengan id sama saat smoke test, turn baru akan dinomori seolah lanjutan yang lama → kunci jadi `(session_id, session_created_at)`; (ii) tabel FTS5 tunggal tidak bisa punya `UNIQUE` → tabel dasar `turns` + external-content `turns_fts`. Plus: AND→OR fallback (model sering nulis query longgar), live window sesi sendiri dikecualikan tapi `archived_turns` ikut (cutoff dibaca lazy karena kompaksi jalan setelah registry disusun), `loop.py` dikonfirmasi tidak perlu berubah.
  4. Plan final ditulis, di-approve user, dieksekusi penuh — lihat daftar file di bawah.
  5. `.venv/Scripts/python.exe -m pytest backend/tests/ -q` → **135 passed, 3 skipped** (99 kasus lama + 39 baru; 1 skip baru = permission POSIX di Windows), hijau di run pertama, regresi nol — `git diff --stat backend/tests/` kosong (cuma file baru).
  6. Smoke test manual `ANTHROPIC_API_KEY` asli, folder data terisolasi di scratchpad: sesi A cerita sambil lalu soal "Pak Budi bilang printer lantai 3 rusak lagi" (tanpa minta diingat) → model tidak memanggil `remember_user_fact` (benar). Sesi B (session_id beda): "Kemarin aku pernah cerita soal printer nggak ya?" → model memanggil `recall_memory(query="printer")` **sendiri**, menjawab "Dalam obrolan sebelumnya, kamu menceritakan bahwa… printer lantai 3 rusak lagi" — kutipan, bukan fakta. `profile.json` tidak dibuat, 6 turn di `memory.db`. Data smoke dihapus.
- **File yang dibuat/diubah:**
  - `backend/schemas/archive_contract.py`, `backend/memory/archive_errors.py`, `backend/memory/archive_store.py`, `backend/agent_core/tools/recall_tools.py`, `backend/memory/archive/.gitkeep` — baru.
  - `backend/schemas/__init__.py`, `backend/memory/__init__.py` (re-export + docstring diperluas jadi 3 lapis), `backend/memory/runner.py` (tambah `run_with_long_term_memory()`, 2 fungsi lama utuh), `backend/agent_core/config.py` (`get_memory_recall_default_limit()`), `.env.example`, `.gitignore` (`archive/*.db` + journal/wal/shm) — diubah, semuanya additive.
  - `backend/tests/test_archive_store.py` (22 fungsi, 1 di-parametrize 4 kasus), `test_recall_tools.py` (8), `test_memory_runner_long_term.py` (6) — baru, 39 kasus total. Test lama tidak diubah sebaris pun.
  - `Memory Think/M2_memory.md` — status, bullet M2b, 2 TODO lama dicoret, bagian "Pendekatan (M2b)" + "Ringkasan Teknis (M2b)" + "Bahasa Awam" (analogi **lemari arsip**) + TODO v2 M2b.
  - `Memory Think/SPRINT2_LOG.md` — entry ini.
- **Alasan/keputusan:** Lihat poin 1-3 di atas. Inti: memilih kubu retrieval-centered bukan karena skor benchmark, tapi karena extractor fakta ala Mem0 akan jadi jalur belakang yang mengubah obrolan biasa jadi "fakta" tanpa instruksi user — persis yang dilarang sejak review M2a. Deskripsi tool `recall_memory` sengaja dibuat *load-bearing* (VERBATIM QUOTES, bukan fakta, kutip sebagai "in an earlier conversation you said…") — dan smoke test membuktikan model mengikutinya. Urutan tulis di runner: sesi → profil → **arsip terakhir**, karena arsip data turunan & self-healing (idempoten by count) — `ArchiveSaveError` tetap propagate (fail loud), turn berikutnya catch-up.
- **Belum dikerjakan / TODO lanjutan:**
  - Perubahan sesi ini (kode M2b + docs + 6 PDF + rename 1 PDF) **belum di-commit/push** — menunggu instruksi user.
  - TODO v2 M2b didokumentasikan di `M2_memory.md`: ranking (observasi smoke: turn `[tool_use …]` pendek dapat bm25 tinggi — kandidat down-weight; recency/importance ala Generative Agents), tokenizer tanpa stemming (`kucing` ≠ `kucingnya`; opsi prefix `*`/trigram), tool `read_conversation_around`, forgetting/encoding gate, Reflexion persistence (arsip ini kandidat tempatnya), trigger delete di `turns_fts` kalau nanti ada hapus.
  - Ketiga lapis M2 sekarang ada — Sprint 2 secara fungsional selesai v1. Next: keputusan user (robustness pass M2b seperti M2a? lanjut Sprint 3? atau rapikan 3 runner jadi 1 entry point?).

## [2026-09-09] Commit + push M2b (2 commit) + diskusi arah M2 v2

- **Apa yang dikerjakan:**
  1. User setuju skema 2 commit. Di-push ke `origin/master`: `939eadc` (`docs(papers): add 6 M2b memory papers, fix 1 filename year` — 6 PDF + rename + `PAPER_NOTES.md` + `sprint-paper-mapping.md`) dan `9e48016` (`feat(m2b): implement long-term cross-session recall (SQLite FTS5)` — semua kode/test/docs M2b termasuk `M2_memory.md` & `SPRINT2_LOG.md`). Entry ini di-commit terpisah setelahnya (precedent `2586d33`).
  2. User tanya: kalau lanjut ke **M2 v2**, apa yang akan dikembangkan? Dijawab sebagai diskusi (bukan plan), diprioritaskan berdasarkan gap nyata yang ketemu selama Sprint 2, bukan daftar fitur dari paper:
     - **(A) Struktural, sebaiknya SEBELUM Sprint 3** — (A1) **satu entry point**: sekarang ada 3 runner (`run_with_memory` / `run_with_profile_memory` / `run_with_long_term_memory`) yang saling duplikasi; begitu Sprint 3 (M4/M5 device) mulai wiring, harus jelas satu fungsi turn yang dipakai — kandidat isi pertama `backend/orchestrator/` yang kosong sejak Sprint 1. (A2) **keputusan error-path persistence** yang sudah ditunda 3x (M2a, M2c, M2b): apa yang dianggap "resmi terjadi" kalau giliran gagal di tengah (tool sudah nyalain lampu tapi turn tidak tersimpan). Butuh keputusan produk + kemungkinan `schema_version` bump `SessionRecord` → berarti harus bangun migrasi minimal (1.0.0→1.1.0), yang selama ini dihindari.
     - **(B) Polish murah M2b** — ranking: down-weight/exclude turn yang isinya cuma blok tool (observasi smoke test), recency tie-break ala Generative Agents; prefix `*` di token supaya `kucing` match `kucingnya`; tool `read_conversation_around(session_id, ordinal)` (seam sudah ada). Total mungkin 1 sesi kerja.
     - **(C) Reflexion persistence** — TODO terbuka sejak M1: refleksi kegagalan tool-call sekarang cuma hidup 1 run. Arsip M2b atau tabel `experiences` terpisah = tempat alaminya (taksonomi *experience memory* di survei Graph-based Agent Memory); dibaca saat tool yang sama mau dipanggil lagi. Menutup 1 TODO lintas-sprint.
     - **(D) Sengaja DITUNDA sampai ada data pemakaian nyata** — decay/forgetting (MemoryBank/FSFM) untuk profil & arsip, *encoding gate* (Storage Is Not Memory), validitas-waktu fakta profil (Zep), konsolidasi background/"tidur" (Rasch & Born) — semua butuh threshold yang tanpa data cuma tebakan buta, alasan yang sama kenapa threshold kompaksi M2a juga masih "tebakan awal".
     - **Rekomendasi:** kerjakan (A) sekarang sebagai penutup Sprint 2 (prasyarat wiring Sprint 3), (B)+(C) bisa diselipkan kapan saja, (D) baru setelah F.R.I.D.A.Y dipakai beneran beberapa minggu.
- **File yang dibuat/diubah:** `Memory Think/SPRINT2_LOG.md` — entry ini.
- **Alasan/keputusan:** Belum ada keputusan — user baru bertanya arah. Prioritas di atas adalah rekomendasi asisten, menunggu pilihan user.
- **Belum dikerjakan / TODO lanjutan:** Keputusan user soal (A)/(B)/(C) — atau langsung Sprint 3.

## [2026-09-09] Sesi ditutup — user pulang kerja, lanjut nanti dari diskusi M2 v2

- **Apa yang dikerjakan:** User minta dicatat bahwa sesi berhenti di sini (pulang dari tempat kerja). Instruksi eksplisit: saat dia tanya lagi soal M2 v2, asisten balas dengan jawaban prioritas A/B/C/D dari entry sebelumnya, lalu **tanyakan mau mulai dari mana** — user menyebut "A1, A2 dan A3"; opsi yang ditawarkan asisten adalah A1 (satu entry point), A2 (keputusan error-path persistence), atau langsung Sprint 3 — perlu dikonfirmasi apakah "A3" = Sprint 3. Dicatat juga di memori persisten asisten (`friday_m2_v2_next_step.md`) supaya tidak bergantung pada file ini saja.
- **File yang dibuat/diubah:** `Memory Think/SPRINT2_LOG.md` — entry ini.
- **Alasan/keputusan:** Tidak ada keputusan teknis — murni checkpoint supaya sesi berikutnya lanjut persis dari titik ini tanpa mengulang diskusi.
- **Belum dikerjakan / TODO lanjutan:** Entry ini **belum di-commit** (menunggu instruksi user, sesuai aturan standing). Sesi berikutnya: rekap + pilih A1 / A2 / Sprint 3.

## [2026-09-09] M2 v2 A1 — satu entry point (`backend/orchestrator/`)

- **Apa yang dikerjakan:**
  1. Sesi dibuka dengan rekap posisi dari `SPRINT2_LOG.md` + memori asisten (sesuai checkpoint entry sebelumnya), lalu user memilih lewat `AskUserQuestion`: mulai dari **A1** (bukan A2 / Sprint 3 / B-C).
  2. Eksplorasi kode (`runner.py`, `loop.py`, `tool_registry.py`, 3 file test runner, `M2_memory.md`, README) dilakukan langsung — codebase kecil, tidak perlu agent. Temuan: 3 runner 80% identik; `backend/orchestrator/` masih `.gitkeep`; tidak ada caller eksternal selain test; arah impor `orchestrator` → `agent_core`/`memory` satu arah, aman dari circular import.
  3. 2 keputusan desain dikonfirmasi user: (a) bentuk **class `Orchestrator` + `run_turn()`** (dibangun sekali, dipanggil per turn — cocok loop chat nyata & wiring device), bukan fungsi tunggal; (b) runner lama **dihapus** dan test-nya diporting, bukan dijadikan wrapper deprecated. (Jawaban (a) tidak masuk lewat UI, dipakai opsi yang direkomendasikan dan disebut eksplisit ke user.)
  4. Plan mode: plan ditulis & di-approve user, lalu dieksekusi penuh — lihat daftar file di bawah.
  5. `.venv/Scripts/python.exe -m pytest backend/tests/ -q` → **136 passed, 3 skipped** (135 − 13 test runner lama + 14 test orchestrator), hijau di run pertama, regresi nol. Import sanity `from backend.orchestrator import Orchestrator; import backend.memory` bersih. `grep run_with_|memory.runner backend/` → sisa hanya di docstring historis (`orchestrator.py`, `test_orchestrator.py` menyebut asal-usulnya).
  6. Smoke test manual dengan API key asli **tidak dijalankan** di sesi ini — logika `run_turn()` adalah pemindahan 1:1 dari `run_with_long_term_memory()` yang sudah di-smoke-test pada entry M2b; porting test menutup perilaku yang sama. Bisa dijalankan kapan saja kalau user mau.
- **File yang dibuat/diubah:**
  - `backend/orchestrator/orchestrator.py`, `backend/orchestrator/__init__.py`, `backend/tests/test_orchestrator.py` — baru.
  - `backend/memory/runner.py`, `backend/tests/test_memory_runner.py`, `backend/tests/test_memory_runner_profile.py`, `backend/tests/test_memory_runner_long_term.py` — **dihapus** (`git rm`, sudah ter-stage; belum di-commit).
  - `backend/memory/__init__.py` — docstring: entry point pindah ke `backend.orchestrator`.
  - `Memory Think/M2_memory.md` — status, bagian baru "M2 v2 — A1", 1 paragraf tambahan "Bahasa Awam" (analogi resepsionis satu pintu). Bagian M2a/M2c/M2b **tidak ditulis ulang** — catatan lama soal runner dibiarkan sebagai sejarah, ditandai "tidak berlaku lagi" di bagian baru.
  - `Memory Think/SPRINT2_LOG.md` — entry ini.
- **Alasan/keputusan:** Produk selalu jalan dengan 3 lapis memori, jadi 2 runner lama tidak punya alasan produk untuk hidup — cuma sisa cara membangun bertahap. Class dipilih supaya store dibangun sekali (bukan per panggilan) dan supaya Sprint 3 punya satu objek untuk di-wiring. Hapus (bukan wrapper) dipilih karena wrapper yang setia ke perilaku lama akan memaksa `Orchestrator` punya saklar per-lapisan yang tidak dibutuhkan siapa pun. **Batas A1 dijaga ketat:** urutan tulis & semantik exception tidak diubah sama sekali (itu A2), `loop.py` tidak disentuh, tidak ada factory `from_env()` (belum ada caller).
- **Belum dikerjakan / TODO lanjutan:**
  - Perubahan sesi ini **belum di-commit/push** — menunggu instruksi user. Entry checkpoint sebelumnya (`Sesi ditutup`) juga masih belum di-commit; keduanya bisa masuk satu commit `refactor(orchestrator): single per-turn entry point, drop memory runners` (+ commit docs terpisah untuk entry log, mengikuti precedent).
  - Sisa M2 v2: **A2** (error-path persistence), **B** (polish M2b), **C** (Reflexion persistence), **D** (ditunda sampai ada data pemakaian). Atau langsung Sprint 3 — sekarang sudah ada satu pintu untuk di-wiring.

## [2026-09-09] Commit + push A1 + rekomendasi langkah berikutnya

- **Apa yang dikerjakan:**
  1. User minta commit & push. Test suite dijalankan ulang (136 passed, 3 skipped). Semua perubahan A1 (2 file orchestrator baru + `test_orchestrator.py` + 4 file dihapus + `backend/memory/__init__.py` + `M2_memory.md` + `SPRINT2_LOG.md` termasuk entry checkpoint "Sesi ditutup" yang tertunda) di-commit sebagai `7dcecf6` (`refactor(orchestrator): single per-turn entry point, drop memory runners`), di-push ke `origin/master`. Entry ini di-commit terpisah setelahnya (precedent `2586d33`, `bb4bb59`).
  2. User tanya: setelah perubahan Sprint 2 ini, lebih baik A2 / B / C atau lompat ke Sprint 3? Jawaban asisten (diskusi, bukan keputusan):
     - **Rekomendasi: lompat ke Sprint 3 (M4 Tool Registry + M5 Device Abstraction), dengan A2 dilebur sebagai sub-langkah eksplisit saat mendesain tool device pertama.** Ini **merevisi** rekomendasi entry `Commit + push M2b` yang bilang "A (A1+A2) sebelum Sprint 3" — A1 memang prasyarat struktural dan sekarang selesai, tapi A2 ternyata tidak bisa diputuskan dengan baik *sebelum* ada tool ber-efek-samping nyata.
     - **Kenapa A2 tidak sekarang:** pertanyaan A2 adalah "apa yang dianggap resmi terjadi kalau giliran gagal di tengah" — dan jawabannya bergantung pada sifat tool: tool yang ada sekarang (`get_current_time`, 2 tool profil, `recall_memory`) semuanya read-only atau menyimpan dirinya sendiri, jadi A2 hari ini cuma abstraksi tanpa kasus konkret. Tool device (lampu nyala, tapi turn tidak tersimpan) adalah kasus pertama yang membuatnya nyata, dan jawabannya beda kalau device bisa di-query state-nya (idempoten/observable) vs tidak. Memutuskan sekarang = menebak; memutuskan saat tool device pertama ada = keputusan berdasar.
     - **Kenapa B tidak sekarang:** semua item B (down-weight turn tool-only, recency, prefix `*`) adalah tuning ranking — persis kelas keputusan yang di M2a/M2c/M2b konsisten ditunda "sampai ada data pemakaian nyata". Satu observasi dari smoke test bukan data. Sprint 3 justru yang akan menghasilkan data itu.
     - **Kenapa C tidak sekarang:** Reflexion persistence bernilai saat tool gagal dengan cara yang *berulang dan bisa dipelajari* (device offline, argumen salah untuk perangkat tertentu). Tool sekarang hampir tidak pernah gagal. Tempatnya (arsip M2b / tabel `experiences`) sudah siap — bangun begitu ada kegagalan nyata untuk direfleksikan, kemungkinan di tengah/akhir Sprint 3.
     - **Kenapa Sprint 3 sekarang bisa:** satu-satunya blocker struktural (tidak ada entry point tunggal untuk di-wiring) sudah hilang di A1. `Orchestrator` menerima `registry` milik caller — tool device tinggal didaftarkan di situ. M4 (MCP-Zero/ScaleMCP: agent minta tool saat butuh, auto-sync) dan M5 (HearthNet/Enhancing IoT: adapter tipis, Home Assistant + MQTT) sama-sama masuk lewat `registry` itu tanpa menyentuh loop maupun memori.
     - **Urutan yang disarankan di Sprint 3:** verifikasi paper kategori #4/#5 (standar "cek isi PDF") → desain M4 dulu (registry/discovery, karena M5 bergantung padanya) → tool device pertama (mock/simulator sebelum hardware) → **di titik itu putuskan A2** dengan kasus konkret → C menyusul kalau kegagalan device mulai berulang → B/D setelah beberapa minggu pemakaian.
- **File yang dibuat/diubah:** `Memory Think/SPRINT2_LOG.md` — entry ini.
- **Alasan/keputusan:** Belum ada keputusan — rekomendasi asisten, menunggu pilihan user. Poin utamanya: sisa v2 (A2/B/C/D) semuanya butuh *input dari pemakaian nyata* yang baru akan ada setelah Sprint 3, sedangkan Sprint 3 tidak butuh apa pun lagi dari v2.
- **Belum dikerjakan / TODO lanjutan:** Pilihan user: Sprint 3 (rekomendasi) atau A2 / B / C dulu. Kalau Sprint 3: entry pertama masuk `SPRINT3_LOG.md` (file baru), mulai dari verifikasi paper #4/#5.
