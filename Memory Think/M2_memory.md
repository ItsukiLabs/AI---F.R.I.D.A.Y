# M2 — Memory System

> Status: **M2a (short-term/active-context) implementasi awal selesai (2026-08-14)** — 24 test baru lulus (43 total termasuk M0/M1). M2b (long-term/retrieval) dan M2c (profile/hierarki/forgetting) belum digarap.
> Paper rujukan: MemGPT, Generative Agents, Lost in the Middle, RAG Survey, Recursively Summarizing, dan 9 paper tambahan (forgetting/consolidation). Detail lengkap di `Memory Think/PAPER_NOTES.md` kategori #2.

---

## Kegunaan

M2 adalah **ingatan** F.R.I.D.A.Y. Tanpa M2, M1 (agent loop) mulai dari nol setiap kali dipanggil — tidak ada percakapan yang benar-benar "lanjut", apalagi diingat lintas sesi. M2 dipecah 3 sub-modul karena "mengingat" itu 3 masalah teknis berbeda:

- **M2a (digarap sekarang)** — memori jangka pendek/konteks aktif: apa yang lagi dibahas dalam satu percakapan, dan bagaimana caranya tetap rapi & tidak "meledak" kalau kepanjangan.
- **M2b (belum digarap)** — memori jangka panjang: nyari balik info relevan dari percakapan-percakapan lama lewat retrieval/embedding.
- **M2c (belum digarap)** — profile/hierarki: mengorganisir memori (bukan rata semua), dan kapan sesuatu boleh "dilupain".

## Pendekatan (M2a)

Tiga paper jadi kerangka utama:

1. **MemGPT** — analogi working context (RAM) vs archival storage (disk). M2a cuma sisi working context; hand-off ke archival adalah pekerjaan M2b nanti.
2. **Lost in the Middle** — info yang terkubur di tengah prompt panjang dipakai lebih buruk dibanding di awal/akhir. Konsekuensi desain: summary hasil kompaksi ditaruh strict di awal, turn terbaru strict di akhir — tidak pernah dibiarkan "hanyut" ke tengah.
3. **Recursively Summarizing Enables Long-Term Dialogue Memory** — kompaksi histori lama dilakukan lewat panggilan LLM yang merangkai `summary_lama + potongan_baru → summary_baru`, bukan truncation/buang begitu saja.

## Ringkasan Teknis (implementasi nyata, 2026-08-14)

Struktur file baru (`backend/memory/`, `backend/schemas/memory_contract.py`):

- `backend/schemas/memory_contract.py` — `SessionRecord`/`MessageRecord` (Pydantic), format file JSON sesi. Beda dari `ToolContract` (M0): cuma 1 field versi (`schema_version`), tidak meniru split `contract_version`/`version` karena sesi cuma punya 1 sumbu perubahan (bentuk file), bukan 2.
- `backend/memory/session.py` — `Session`: dataclass runtime yang bungkus `SessionRecord` + helper (`append_user_message`, `record_usage`, `needs_compaction`, `to_llm_messages`). `messages` (durable, dipersist apa adanya) dan `to_llm_messages()` (presentasi, dihitung ulang tiap panggilan LLM, nyisipin summary di depan + turn terbaru di belakang) sengaja dipisah — itu yang bikin urutan Lost-in-the-Middle beres tanpa bikin persistensi ribet.
- `backend/memory/compaction.py` — `compact()`: kompaksi recursive-summarization. Titik potong cuma dicari di **turn user biasa** (bukan tengah pasangan `tool_use`/`tool_result`, karena Anthropic API menolak riwayat yang motong pasangan itu) — kalau tidak ada titik potong aman, `compact()` no-op (`False`), bukan maksa motong.
- `backend/memory/store.py` — `SessionStore`: baca/tulis JSON ke `backend/memory/sessions/<session_id>.json`. Validasi `session_id` (regex filename-safe) sebelum dipakai bangun path.
- `backend/memory/runner.py` — `run_with_memory()`: wrapper tipis (load → `run_agent()` → save). **Sengaja tidak** di-re-export dari `backend/memory/__init__.py` karena dia impor `agent_core/loop.py`, sedangkan `loop.py` impor `memory/session.py` — kalau di-re-export dari `__init__.py`, jadi circular import.
- `backend/agent_core/loop.py` — `run_agent()` dapat parameter baru `session: Session | None = None`, **additive murni**: kalau `None`, perilaku identik 100% sama kayak sebelum M2a (semua test `test_agent_loop.py` lama tidak diubah sama sekali, jadi regression guard). Kalau session diisi: cek kompaksi di awal panggilan (bukan di tengah loop — lihat alasan di atas), tambah user turn ke `session.messages`, kirim `session.to_llm_messages()` ke LLM, rekam token usage asli dari respons.
- `backend/agent_core/llm_client.py` — `LLMResponse` dapat 2 field baru (`input_tokens`, `output_tokens`), diisi dari `response.usage` SDK Anthropic yang sebelumnya dibuang begitu saja. Ini sinyal "memory pressure" ala MemGPT — token asli dari API, bukan estimasi karakter.
- `backend/agent_core/config.py` — `get_memory_compaction_threshold_tokens()` (default 6000), `get_memory_compaction_safety_margin_tokens()` (default 500), `get_memory_keep_recent_messages()` (default 6), semua override-able lewat `.env`.

**Kenapa ada `run_with_memory()` terpisah dari `run_agent()`:** `backend/orchestrator/` (folder yang secara "alami" akan jadi tempat wiring load/save sesi) masih kosong sejak Sprint 1 tanpa jadwal sprint pasti — bukan M14 (Multi-Agent Orchestration, Sprint 9) yang scope-nya beda (koordinasi banyak *agent*, bukan lem generik agent+memory+device). Kalau nunggu folder itu, fitur "F.R.I.D.A.Y inget percakapan lintas restart" nggak bakal aktif untuk waktu yang tidak pasti. Solusinya: `run_agent()` tetap bersih tanpa efek samping I/O (gampang di-test), tapi `run_with_memory()` jadi entry point yang beneran bisa dipakai sekarang — auto-save tiap giliran, tanpa nunggu modul lain.

**Verifikasi nyata (2026-08-14):** smoke test manual dengan `ANTHROPIC_API_KEY` asli — 2 panggilan `run_with_memory()` terpisah dengan `session_id` sama ("My name is Ernold and I like cats." lalu "What is my name, and what do I like?"). Giliran kedua berhasil jawab "Your name is Ernold, and you like cats!" — dibaca ulang dari file JSON di disk antar panggilan, bukan dari state proses. File sesi dicek manual, skema sesuai desain, human-readable.

**Test** (`backend/tests/test_memory_*.py`, `test_agent_loop_session.py`) — 24 test baru, semua pakai `FakeLLMClient` (test double, pola sama seperti `test_agent_loop.py`), tidak ada yang memanggil API asli. Cover: round-trip persistensi, boundary `needs_compaction`, urutan `to_llm_messages` (assert eksplisit posisi summary/ack/verbatim), kompaksi dasar + recursive-summary threading + never-split-tool-pair, integrasi `run_agent()` dengan session (termasuk urutan kompaksi-sebelum-giliran-utama), `run_with_memory()` end-to-end.

**Review arsitektur (2026-08-14, sebelum commit):** user me-review desain M2a terhadap prinsip "F.R.I.D.A.Y must never confuse conversation context with memory" — hasil diskusi lengkap ada di `SPRINT2_LOG.md`. Poin-poin yang sudah benar dikonfirmasi tanpa perubahan (Session bukan Memory, atomic tool-call safety, persistence boundary di `run_with_memory()`, archived_turns tetap raw, tidak ada M2b/M2c menyelinap masuk). 3 perbaikan kecil disepakati dan diimplementasikan:
- `Session.needs_compaction()` sekarang terima `safety_margin_tokens` opsional — cek jadi `last_input_tokens + safety_margin >= threshold`, bukan `last_input_tokens >= threshold` polos. Mengompensasi "staleness satu giliran" dari `last_input_tokens` (angka eksak dari panggilan API sebelumnya, bukan estimasi giliran sekarang) **tanpa** bikin estimator token/karakter baru — sengaja dihindari karena akan menurunkan akurasi, bukan menaikkan (angka eksak yang telat 1 giliran masih lebih dipercaya daripada tebakan real-time tanpa tokenizer asli). `MEMORY_COMPACTION_SAFETY_MARGIN_TOKENS` (default 500) ditambah ke config.
- `SUMMARIZATION_SYSTEM_PROMPT` diperketat: batas panjang (~250 kata), dan **larangan eksplisit** menyimpulkan preferensi/fakta yang tidak dinyatakan langsung user (contoh konkret dipakai: "makan nasi goreng hari ini" harus tetap kejadian sesaat di summary, bukan berubah jadi "user suka nasi goreng"). ini bentuk konkret dari prinsip "summarization compresses context; it must not invent or promote unspoken assumptions into user facts or preferences" — supaya M2a tidak diam-diam jadi jalur pembentukan preferensi permanen padahal itu ranah M2c nanti (dan idealnya baru terjadi lewat instruksi eksplisit user, bukan inferensi otomatis dari obrolan biasa).
- Konfigurasi `context_limit`/`reserved_output_tokens`/model-specific budget **sengaja tidak** dibangun sekarang (didokumentasikan sebagai TODO eksplisit di `config.py`) — abstraction multi-model itu prematur selama F.R.I.D.A.Y baru punya 1 provider/model (`claude-haiku-4-5`, Anthropic). Baru relevan pas Sprint 8 (M12/M13, local inference/model routing).

**Belum digarap / TODO lanjutan:**
- Mid-call token overflow belum ada pengaman darurat — kompaksi cuma dicek di awal `run_agent()` (batas aman, lihat alasan di atas), jadi satu panggilan dengan banyak iterasi tool secara teori bisa lewat budget sebelum sempat dicek lagi. Diterima sebagai gap v1 (disepakati dengan user) — dan dikonfirmasi ulang saat review: ini gap struktural (soal *di mana* boleh potong, bukan soal akurasi pengukuran token), jadi estimator token yang lebih baik pun tidak akan menutup celah ini. `max_iterations` sudah membatasi risikonya.
- Belum ada cross-session recall (M2b) — `session.archived_turns` sudah jadi seam/hook (turn yang di-drop saat kompaksi disimpan di situ, tidak dibaca/dipangkas M2a), tapi belum ada yang meng-index/embed-nya.
- Belum ada kebijakan forgetting/eviction jangka panjang (M2c) — 9 paper untuk ini sudah diriset (lihat `PAPER_NOTES.md`), belum diimplementasi.
- `context_limit`/`reserved_output_tokens`/tokenizer-model-specific budget — ditunda ke Sprint 8 (lihat catatan review di atas).
- Default `MEMORY_COMPACTION_THRESHOLD_TOKENS`/`MEMORY_COMPACTION_SAFETY_MARGIN_TOKENS`/`MEMORY_KEEP_RECENT_MESSAGES` masih tebakan awal (6000 / 500 / 6) — belum divalidasi terhadap pemakaian nyata jangka panjang.
- `current_task`/`current_objective` (konsep "lagi ngerjain apa sekarang") dikonfirmasi user sebagai bagian **working memory (M2a)**, bukan kategori memori terpisah — desain `Session` sekarang tidak menghalangi penambahan field ini nanti (perubahan aditif), tapi belum diimplementasikan sekarang.

## Bahasa Awam

Kalau M1 itu "orangnya yang mikir dan pakai alat", M2a itu **buku catatan kecil** yang dia pegang selama ngobrol sama kamu.

Sebelum M2a: F.R.I.D.A.Y kayak orang amnesia — tiap kali kamu ngomong lagi, dia lupa semua yang barusan dibahas, bahkan dalam obrolan yang sama. Sekarang, dengan M2a:

1. **Dia nyatet tiap kalimat kalian berdua** ke buku catatan (file JSON) — bukan cuma diinget di kepala doang yang hilang kalau dia "pingsan" (proses restart).
2. **Kalau buku catatannya mulai kepenuhan** (obrolan udah panjang banget), dia nggak asal sobek halaman lama — dia rangkum dulu isinya jadi beberapa baris inti, baru halaman lamanya "diarsipin" (bukan dibuang, cuma dipadatkan).
3. **Pas mau jawab**, dia taruh rangkuman itu di halaman paling depan buku catatannya (bukan diselipin di tengah-tengah) — soalnya kalau diselipin di tengah, dia gampang "kelewat baca" bagian itu. Halaman-halaman terbaru tetap ditulis lengkap apa adanya di belakang.

Ini masih "buku catatan satu obrolan" doang — F.R.I.D.A.Y belum bisa "nginget balik" hal dari obrolan yang beda sama sekali tanpa diingatkan (itu tugas M2b nanti, kayak dia buka-buka arsip buku catatan lamanya). Tapi sekarang, minimal, obrolan yang sama nggak lagi "reset" tiap kali kamu nutup dan buka lagi F.R.I.D.A.Y.
