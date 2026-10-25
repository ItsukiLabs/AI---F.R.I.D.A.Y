# M2 — Memory System

> Status: **M2a (short-term/active-context) selesai termasuk robustness pass (2026-08-14).** **M2c (profile memory) v1 selesai (2026-08-18).** **M2b (long-term recall) v1 selesai (2026-09-09)**. **M2 v2 A1 (entry point tunggal `backend/orchestrator/`) selesai (2026-09-09)** — 136 test lulus (3 skip platform-specific di Windows). Ketiga lapis M2 sekarang ada dan dipakai lewat satu pintu: `Orchestrator.run_turn()`. **[Per 2026-10-25]** M2 v2 **A2 (error-path persistence) selesai** 2026-10-23 (bagian "Keputusan A2" di bawah); kompaksi dengan ringkasan kosong kini tidak mengubah sesi (`CompactionError`, turn jalan terus dengan peringatan); blok profil menyatakan dirinya sumber utama (smoke test 2026-10-25: model menjawab dari profil tanpa `recall_memory`). Sisa v2: B (polish M2b), C (Reflexion persisten), D (decay/forgetting) — menunggu data pemakaian. Seluruh proyek: 351 test lulus.
> Paper rujukan: MemGPT, Generative Agents, Lost in the Middle, RAG Survey, Recursively Summarizing, 9 paper forgetting/consolidation (MemoryBank & FSFM jadi rujukan v2 M2c), dan 6 paper retrieval/long-term memory untuk M2b (Storage Is Not Memory, Mem0, Zep, HippoRAG, Memory OS, Graph-based Agent Memory survey). Detail lengkap di `Memory Think/PAPER_NOTES.md` kategori #2.

---

## Kegunaan

M2 adalah **ingatan** F.R.I.D.A.Y. Tanpa M2, M1 (agent loop) mulai dari nol setiap kali dipanggil — tidak ada percakapan yang benar-benar "lanjut", apalagi diingat lintas sesi. M2 dipecah 3 sub-modul karena "mengingat" itu 3 masalah teknis berbeda:

- **M2a (selesai)** — memori jangka pendek/konteks aktif: apa yang lagi dibahas dalam satu percakapan, dan bagaimana caranya tetap rapi & tidak "meledak" kalau kepanjangan.
- **M2b (selesai)** — memori jangka panjang: nyari balik kutipan relevan dari percakapan-percakapan lama lewat keyword search atas arsip verbatim (bukan embedding — lihat "Pendekatan (M2b)").
- **M2c (selesai)** — profile/hierarki: mengorganisir memori (bukan rata semua), dan kapan sesuatu boleh "dilupain".

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

**Robustness pass (2026-08-14, sebelum M2a dianggap benar-benar selesai):** begitu M2a jadi persistent state layer (bukan sekadar fitur percakapan), user minta audit 5 dimensi — persistence integrity, schema evolution, error behavior, security boundary, test boundary — plus 3 audit tambahan (error-path persistence, logging/privacy, concurrent access). Hasil & perbaikan:
- **Atomic write** — `SessionStore.save()` sebelumnya nulis langsung ke file final (`path.write_text()`), rawan file setengah-jadi kalau proses mati di tengah nulis (file sesi jadi permanen nggak bisa dimuat). Diperbaiki: tulis ke temp file di folder yang sama dulu (`tempfile.mkstemp`), baru `os.replace()` ke path final (atomic di POSIX & Windows). Nama temp file (`.{session_id}.tmp-XXXXXX`) sengaja nggak pernah cocok pola `{session_id}.json` yang dicari `load()`, jadi nggak mungkin ke-load sebagai sesi.
- **Schema version enforcement** — `schema_version` sebelumnya cuma field dekoratif, nggak pernah dicek. Sekarang `load()` bandingkan `schema_version` file vs `MEMORY_SCHEMA_VERSION` aktif; kalau beda, lempar `UnsupportedSessionSchemaError` eksplisit (bukan migrasi otomatis, bukan silent-load dengan default salah). File yang bermasalah **tidak** dihapus/diubah otomatis.
- **Fail loud, bukan silent fallback** — `backend/memory/errors.py` (baru): `SessionError` (base), `SessionLoadError`, `SessionSaveError`, `UnsupportedSessionSchemaError` (subclass `SessionLoadError`). `SessionStore.load()`/`save()` sekarang bungkus `json.JSONDecodeError`/`OSError`/`pydantic.ValidationError` jadi exception domain-spesifik ini — **tidak pernah** diam-diam balik ke `Session.new()` kalau file sebenarnya ada tapi korup/unsupported. Prinsip yang dijaga: F.R.I.D.A.Y nggak boleh pura-pura lupa.
- **File permission (cross-platform, best-effort)** — `_restrict_permissions()` di `store.py` panggil `os.chmod(path, 0o600)` sebelum `os.replace()`. Di POSIX ini restriksi akses beneran (cuma owner yang bisa baca/tulis). Di Windows, `os.chmod` cuma toggle atribut read-only, **tidak** membatasi user lain baca file — didokumentasikan eksplisit sebagai limitasi platform (bukan bug), bukan dibangun ACL/pywin32 abstraction. Kegagalan chmod nggak pernah menggagalkan save (best-effort, dibungkus try/except sendiri).
- **Error-path persistence — diaudit, TIDAK direfactor (sesuai instruksi user):** gap nyata ditemukan — lihat sub-bagian "Semantik Error-Path Persistence" di bawah untuk detail lengkap per skenario.
- **Logging/privacy — diaudit, sudah aman:** dicek `backend/` — nggak ada `import logging`/`print()` sama sekali di seluruh package `memory/` dan `agent_core/`. Nggak ada isi percakapan yang bisa "bocor" ke log karena memang belum ada logging apapun. Sisi lain dari temuan ini: observability juga nol — kalau ada masalah senyap, satu-satunya sinyal sekarang adalah exception (poin di atas), bukan log. Cukup untuk sekarang, tidak perlu perubahan.
- **Concurrent access — non-goal, didokumentasikan:** M2a v1 mengasumsikan satu writer per `session_id` dalam satu waktu. Nggak ada locking/coordination. Ini jadi masalah nyata baru kalau F.R.I.D.A.Y berkembang jadi arsitektur multi-process/multi-interface/background-agent — di luar scope M2a.
- **Safety margin exact boundary** — diverifikasi eksplisit lewat test: `threshold=6000, margin=500` → `last_input=5499` tidak memicu kompaksi, `5500` dan `6000` memicu (persis sesuai spesifikasi user).

### Semantik Error-Path Persistence (didokumentasikan, sengaja belum diperbaiki)

Alur normal: `run_with_memory()` → `store.load()` → mutasi objek `session` di memory (di dalam `run_agent()`) → `store.save(session)`. **`save()` cuma dipanggil sekali, paling akhir**, setelah `run_agent()` selesai dan `return`. Kalau `run_agent()` melempar exception di titik manapun sebelum sempat `return`, eksekusi `run_with_memory()` berhenti di situ juga — baris `store.save(session)` **tidak pernah tereksekusi sama sekali**. Tidak ada `try`/`finally` di sekitar itu (sengaja, lihat alasan di bawah).

Konsekuensinya beda-beda tergantung di titik mana error terjadi:

1. **Error sebelum tool call apapun** (misal `llm.send()` gagal di panggilan pertama — network/API error) — user turn yang sudah sempat ditambahkan ke `session.messages` (`append_user_message()` jalan duluan di awal `run_agent()`) ikut hilang dari disk. Efeknya: giliran berikutnya, seolah-olah user nggak pernah nanya apa-apa saat itu.
2. **Error di tengah rantai tool call** (misal iterasi ke-2 loop ReAct gagal, padahal iterasi ke-1 sudah sukses mengeksekusi tool nyata) — ini skenario paling berisiko. Kalau tool di iterasi 1 itu **benar-benar mengubah dunia nyata** (contoh: `nyalain_lampu`), aksinya sudah benar-benar kejadian — tapi jejak bahwa itu diminta dan dilakukan **hilang total** dari memory begitu error di iterasi berikutnya bikin seluruh giliran gagal disimpan. Lampu nyala di realita, tapi `session.messages` di disk tidak pernah mencatatnya — F.R.I.D.A.Y "lupa" dia baru saja melakukan sesuatu yang efeknya masih ada.
3. **Error setelah semua tool call sukses tapi sebelum jawaban akhir terbentuk** — mirip poin 2: seluruh histori tool call yang sudah lengkap tetap hilang semua dari disk, bukan cuma bagian yang gagal.

**Yang PASTI berlaku di semua skenario di atas:** `run_with_memory()` tetap **melempar exception ke atas**, tidak pernah silent — caller/user tahu ada yang gagal di giliran itu. Yang **belum didefinisikan** adalah apa yang tersisa di disk setelahnya (jawabannya sekarang: tidak ada yang berubah dari state sebelum giliran itu mulai, sesuai poin 1-3).

**Kenapa ini sengaja tidak langsung "diperbaiki" pakai `try/finally: store.save(session)`:** itu bukan perbaikan teknis netral — itu keputusan semantik. Kalau session langsung disimpan apa adanya di titik gagal, sesi akan **mengklaim** semua yang sempat termutasi di memory (termasuk user turn yang belum pernah benar-benar dijawab lengkap oleh asisten, atau tool call yang baru separuh jalan) sebagai bagian resmi riwayat. Pertanyaannya: apakah itu semantik yang benar? Atau harusnya cuma giliran yang **benar-benar tuntas** (sampai `AgentResult` berhasil di-`return`) yang boleh dianggap "resmi" masuk riwayat sesi, dan giliran yang gagal di tengah jalan seharusnya punya perlakuan sendiri (misal: disimpan tapi ditandai `incomplete`, bukan cuma di-diamkan)? Ini keputusan tentang **apa yang dianggap "benar-benar terjadi" secara resmi di ingatan F.R.I.D.A.Y**, bukan sekadar soal robustness teknis — karena itu ditunda sampai didiskusikan eksplisit dengan user, bukan diputuskan sepihak lewat refactor.

**Belum digarap / TODO lanjutan:**
- Mid-call token overflow belum ada pengaman darurat — kompaksi cuma dicek di awal `run_agent()` (batas aman, lihat alasan di atas), jadi satu panggilan dengan banyak iterasi tool secara teori bisa lewat budget sebelum sempat dicek lagi. Diterima sebagai gap v1 (disepakati dengan user) — dan dikonfirmasi ulang saat review: ini gap struktural (soal *di mana* boleh potong, bukan soal akurasi pengukuran token), jadi estimator token yang lebih baik pun tidak akan menutup celah ini. `max_iterations` sudah membatasi risikonya.
- ~~Belum ada cross-session recall (M2b)~~ — **selesai 2026-09-09**, lihat bagian "Pendekatan (M2b)". `session.archived_turns` sekarang dibaca `ArchiveStore.ingest()` (bersama `messages`) — M2a sendiri tetap tidak menyentuhnya.
- Belum ada kebijakan forgetting/eviction jangka panjang (M2c) — 9 paper untuk ini sudah diriset (lihat `PAPER_NOTES.md`), belum diimplementasi.
- `context_limit`/`reserved_output_tokens`/tokenizer-model-specific budget — ditunda ke Sprint 8 (lihat catatan review di atas).
- Default `MEMORY_COMPACTION_THRESHOLD_TOKENS`/`MEMORY_COMPACTION_SAFETY_MARGIN_TOKENS`/`MEMORY_KEEP_RECENT_MESSAGES` masih tebakan awal (6000 / 500 / 6) — belum divalidasi terhadap pemakaian nyata jangka panjang.
- `current_task`/`current_objective` (konsep "lagi ngerjain apa sekarang") dikonfirmasi user sebagai bagian **working memory (M2a)**, bukan kategori memori terpisah — desain `Session` sekarang tidak menghalangi penambahan field ini nanti (perubahan aditif), tapi belum diimplementasikan sekarang.
- Error-path persistence (giliran hilang total/parsial kalau `run_agent()` exception di tengah jalan) — didokumentasikan lengkap di sub-bagian "Semantik Error-Path Persistence" di atas, belum diperbaiki, butuh keputusan produk dulu (apa yang dianggap "resmi" masuk riwayat sesi) sebelum dikode.
- File permission di Windows cuma toggle read-only, bukan restriksi akses user lain yang sesungguhnya (butuh pywin32/ACL manipulation untuk itu) — didokumentasikan sebagai limitasi platform.
- Concurrent access (multi-writer ke `session_id` yang sama) — non-goal eksplisit untuk M2a v1, relevan lagi kalau arsitektur berubah jadi multi-process/background-agent.

## Pendekatan (M2c)

Tiga keputusan arsitektur disepakati lewat diskusi + pertanyaan pilihan ganda sebelum coding:

1. **Cara fakta masuk: tool eksplisit** (`remember_user_fact`), bukan ekstraksi otomatis/background. Model manggil sendiri di tengah ReAct loop cuma saat user jelas-jelas minta diingat — traceable, satu tool call = satu jejak sebab-akibat, tidak nambah panggilan LLM tersembunyi.
2. **Konflik fakta: newest wins + superseded trail.** Fakta baru (`remember_user_fact` dengan `supersedes=<id lama>`) langsung aktif, fakta lama ditandai `superseded` (bukan dihapus — tetap ada jejak audit).
3. **Forgetting v1: manual delete saja** (`forget_user_fact`, hanya atas permintaan eksplisit user). Decay otomatis ala MemoryBank (kurva Ebbinghaus) atau eviction berbasis kapasitas ala FSFM **ditunda ke v2** — didokumentasikan sebagai TODO, bukan dibangun sekarang, karena threshold decay masih tebakan buta tanpa data pemakaian nyata (alasan yang sama kenapa threshold kompaksi M2a juga masih "tebakan awal").

## Ringkasan Teknis (implementasi nyata, 2026-08-18)

Struktur file baru:

- `backend/schemas/profile_contract.py` — `ProfileFact`/`ProfileRecord` (Pydantic), `PROFILE_SCHEMA_VERSION` independen dari `MEMORY_SCHEMA_VERSION` (sumbu perubahan beda, sama alasan kenapa M2a juga tidak reuse versi M0). `ProfileFact.id` sequential (`fact_0001`, dst, bukan UUID) supaya model bisa cite balik id-nya dengan hemat token. `category` freeform string (bukan enum) — taksonomi fakta personal belum diketahui tanpa data pemakaian nyata; guardrail-nya cuma `maxLength` + instruksi tool description supaya model reuse kategori yang sudah ada.
- `backend/memory/profile.py` — `Profile` (dataclass runtime, wraps `ProfileRecord` + flag `dirty` runtime-only). `remember_fact()`: assign id baru, kalau `supersedes` diisi validasi target masih `active` (raise `ProfileFactNotFoundError` kalau tidak), flip status lama jadi `superseded` + link `superseded_by`. `forget_fact()`: idempotent (forget fakta yang sudah `deleted` = no-op sukses, bukan error — supaya "lupain X" yang diulang tidak nge-error), raise kalau id genuinely tidak ada. `to_context_block()`: render fakta aktif jadi teks buat system prompt, `""` kalau kosong (supaya profile kosong tidak nambah section aneh ke prompt).
- `backend/memory/profile_store.py` — `ProfileStore`: singleton file `profile.json` (beda dari `SessionStore` yang per-`session_id`). Robustness properties ditiru **persis** dari `SessionStore` M2a (atomic write, fail-loud exceptions, schema_version check, `_restrict_permissions` best-effort chmod) — **diduplikasi**, bukan diekstrak ke util bersama, supaya tidak menyentuh file M2a yang sudah di-review & di-push untuk manfaat kosmetik semata.
- `backend/memory/profile_errors.py` — `ProfileError` (base) → `ProfileLoadError`, `ProfileSaveError`, `UnsupportedProfileSchemaError`, `ProfileFactNotFoundError`. Mirror `backend/memory/errors.py`.
- `backend/agent_core/tools/profile_tools.py` — `make_profile_tools(profile)`: factory yang bind closure `remember_user_fact`/`forget_user_fact` ke objek `Profile` **runtime** (bukan `ProfileStore`) — kalau tool dibind ke store dan tiap panggilan `load()`/`save()` sendiri, akan ada 2 salinan `Profile` independen dalam 1 turn yang bisa divergen (iterasi ReAct ke-2 tidak lihat fakta yang baru ditulis tool di iterasi ke-1). Karena butuh state per-turn, tool ini **tidak** masuk `ALL_TOOLS` statis. Kedua tool `permission_tier=STANDARD` (bukan `CRITICAL`) — menulis/hapus fakta personal bukan `READ_ONLY`, tapi juga bukan aksi ireversibel ke dunia luar; `forget_user_fact` khususnya cuma jalan atas permintaan eksplisit user by design.
- `backend/agent_core/loop.py` — `run_agent()` dapat param baru `profile: Profile | None = None`, **additive murni** (`profile=None` → behavior identik 100%). Blok `to_context_block()` di-append ke `system` prompt (bukan ke `messages`) — profile facts sengaja dijaga di luar jalur `messages` supaya tidak pernah lewat compaction/summarization yang bisa menyimpulkan hal yang tidak dinyatakan. Dihitung ulang tiap iterasi loop (mirror pola `session.to_llm_messages()`) supaya mutasi tool di iterasi 1 langsung kelihatan di iterasi 2 dalam turn yang sama.
- `backend/memory/runner.py` — `run_with_profile_memory()` baru, **`run_with_memory()` tidak disentuh sebaris pun**. Registry dikompos ulang tiap panggilan (tool caller stateless + 2 tool profile fresh-bound) karena `ToolRegistry.register()` raise error kalau nama sudah terdaftar — kalau register langsung ke `registry` yang caller kasih dan dipanggil berulang (loop chat nyata), panggilan kedua akan meledak. Butuh 1 method baru additive di `ToolRegistry`: `registered_tools()`. Profile cuma di-save kalau `profile.dirty` — hemat I/O untuk turn yang tidak menyentuh fakta apa pun.

**Verifikasi nyata (2026-08-18):** smoke test manual dengan `ANTHROPIC_API_KEY` asli, 4 giliran: (a) session A minta diingat alergi kacang → tersimpan `fact_0001`; (b) session **B** (session_id beda sama sekali) tanya "aku alergi apa?" → jawab benar merujuk `fact_0001` (bukti recall lintas sesi, bukan cuma lintas restart proses seperti M2a); (c) session B kasih info kontradiktif (alergi shellfish, bukan kacang) → model panggil `remember_user_fact(supersedes=fact_0001)` sendiri, `fact_0001` jadi `superseded`, `fact_0002` aktif; (d) minta lupain info alergi → `forget_user_fact` dipanggil, `fact_0002` jadi `deleted`, `to_context_block()` balik kosong. Semua 4 skenario jalan tanpa intervensi manual.

**Test** (`test_profile*.py`, `test_agent_loop_profile.py`, `test_memory_runner_profile.py`, +1 di `test_tool_registry.py`) — 39 test baru, semua pakai `FakeLLMClient`/`tmp_path`, tidak ada yang hit API/disk asli. **97 passed, 2 skipped** total (58 lama M0/M1/M2a + 39 baru M2c), regresi nol — `test_agent_loop.py`, `test_agent_loop_session.py`, `test_memory_runner.py` lama tidak diubah sebaris pun.

**Belum digarap / TODO v2:**
- Decay otomatis (MemoryBank, kurva Ebbinghaus) atau eviction berbasis kapasitas (FSFM) — sengaja ditunda, 9 paper forgetting/consolidation sudah diriset (`PAPER_NOTES.md` kategori #2) tapi threshold-nya butuh data pemakaian nyata dulu.
- Ekstraksi fakta otomatis/background (piggyback compaction) — sudah diputuskan tidak dipakai untuk v1, tool-eksplisit-only.
- ~~M2b (retrieval/embedding/vector store)~~ — **selesai 2026-09-09** tanpa embedding/vector store, lihat bagian "Pendekatan (M2b)".
- Error-path persistence: kalau `session_store.save()` sukses tapi `profile_store.save()` gagal setelahnya (network hiccup, disk penuh, dst di antara 2 write terpisah), turn tercatat di sesi tapi fakta baru bisa hilang — mewarisi kelas masalah yang sama dengan gap "Semantik Error-Path Persistence" M2a (lihat sub-bagian di atas), sengaja tidak diperbaiki sepihak, butuh keputusan produk terpisah.
- `permission_tier` `forget_user_fact` dipilih `STANDARD` (bukan `CRITICAL`) — keputusan produk, bisa direvisit pas M11 (Security) kalau ternyata butuh konfirmasi tambahan sebelum eksekusi hapus data personal.

## Pendekatan (M2b)

6 paper baru (2026-09-09) terbelah 2 kubu, dan pilihan kubunya adalah keputusan arsitektur paling penting M2b:

- **Extraction-centered** (Mem0, Zep/Graphiti): saat ingest, LLM mem-parse percakapan jadi fakta atomik / node knowledge-graph, itu yang disimpan & dicari by similarity.
- **Retrieval-centered** (*Storage Is Not Memory*): simpan event **verbatim**, jangan interpretasi di depan — "apa yang dibuang sebelum query diketahui tidak bisa dipulihkan saat retrieval." Pintarnya di sisi retrieval. Seluruh sistem satu file SQLite tanpa vector DB/GPU, dan di LoCoMo justru ranking-nya paling tinggi.

Tiga keputusan user (via pertanyaan pilihan ganda sebelum coding):

1. **Retrieval-centered, verbatim, SQLite FTS5.** Ini bukan cuma soal skor benchmark — kubu ini persis selaras dengan prinsip yang sudah dipegang sejak M2a ("summarization must not invent facts", `archived_turns` sengaja disimpan mentah) dan M2c (fakta cuma lewat tool eksplisit). Extractor fakta ala Mem0 akan jadi jalur belakang yang mengubah obrolan biasa jadi "fakta" tanpa instruksi user — persis yang dilarang. Tanpa embedding/vector DB/LLM saat ingest; `sqlite3` stdlib, nol dependency baru.
2. **Index semua turn semua sesi**, bukan cuma `archived_turns` — kalau cuma hasil kompaksi, sesi pendek yang tidak pernah dikompaksi tidak akan pernah bisa di-recall.
3. **Tool eksplisit `recall_memory`** yang model panggil sendiri (pola MemGPT archival-search, konsisten dengan `remember_user_fact` M2c) — bukan auto-inject tiap turn yang nambah latensi+token setiap giliran dan berisiko mengotori konteks dengan hasil tidak relevan.

*Memory OS of AI Agent* memvalidasi struktur 3-lapis yang sekarang lengkap: short-term (M2a) / **mid-term = M2b** (arsip percakapan yang sudah keluar dari konteks aktif tapi bukan fakta profil) / long-term personal (M2c). Bedanya dengan Memory OS: kita **tidak** punya promosi otomatis mid→long — itu tetap cuma lewat `remember_user_fact`.

## Ringkasan Teknis (implementasi nyata, 2026-09-09)

Struktur file baru:

- `backend/schemas/archive_contract.py` — `ARCHIVE_SCHEMA_VERSION` (independen dari versi sesi/profil, alasan sama seperti M2c) + `RecallHit` (pydantic): `session_id, ordinal, role, text, session_started_at, indexed_at`. Tidak ada pydantic *record* on-disk — bentuk durable-nya adalah DDL SQLite.
- `backend/memory/archive_store.py` — `ArchiveStore`: satu file `backend/memory/archive/memory.db` (di-gitignore). Tabel `meta` (schema_version), `sessions_ingest`, `turns` (tabel dasar, `UNIQUE(session_id, session_created_at, ordinal)`, kolom `text` untuk search + `content_json` verbatim), dan `turns_fts` (external-content FTS5, tokenizer `unicode61 remove_diacritics 2`). Bukan tabel FTS5 tunggal karena virtual table tidak bisa punya `UNIQUE`.
- `backend/memory/archive_errors.py` — `ArchiveError` → `ArchiveLoadError`, `ArchiveSaveError`, `UnsupportedArchiveSchemaError`. Mirror M2a/M2c.
- `backend/agent_core/tools/recall_tools.py` — `RECALL_MEMORY_CONTRACT` (`permission_tier=READ_ONLY`, `read_only_hint=True`) + `make_recall_tools(archive, current_session)`. Deskripsi tool-nya *load-bearing*: hasil = **VERBATIM QUOTES** bertanggal, bukan fakta terverifikasi, kutip sebagai "in an earlier conversation you said…", jangan nyatakan sebagai kebenaran saat ini, kalau mau diingat durable pakai `remember_user_fact`. Output tiap hit dipotong 600 char + flag `truncated`; `limit` default dari config (5), hard cap 20.
- `backend/memory/runner.py` — `run_with_long_term_memory()` baru, 2 runner lama **tidak disentuh**. Registry per-turn = tool caller + 2 tool profil + `recall_memory`. Urutan tulis: sesi → profil (kalau dirty) → **arsip terakhir**.
- `backend/agent_core/config.py` — `get_memory_recall_default_limit()` (default 5), `.env.example` diupdate.
- **`loop.py` tidak berubah sama sekali** — `recall_memory` cuma tool registry biasa; `_execute_tool_call` sudah validasi `input_schema` & ubah exception (termasuk `ArchiveLoadError`) jadi observasi verbal. Bonus: `tool_result` mendarat di *ekor* message list = posisi paling optimal menurut Lost in the Middle, tanpa usaha ekstra.

Lima keputusan desain teknis (semua diverifikasi empiris di SQLite venv sebelum ditulis):

- **Kunci idempotensi ingest = `(session_id, session_created_at)`**, disimpan di DB arsip (bukan di file sesi — `SessionRecord` schema TIDAK diubah, karena `SessionStore.load()` cek versi strict tanpa migrasi, bump = semua sesi lama tidak bisa dimuat). History penuh sebuah sesi selalu `archived_turns + messages` (kompaksi cuma memindah, totalnya cuma naik), arsip menyimpan `ingested_count` per generasi. `created_at` yang membedakan dua percakapan berbeda yang kebetulan pakai `session_id` sama (file sesi dihapus & dibuat ulang — kejadian rutin di smoke test) — tanpa itu, turn percakapan baru akan dinomori seolah lanjutan yang lama. History lebih pendek dari count (cuma mungkin via edit manual) → `ArchiveSaveError`, bukan renumber diam-diam.
- **Sesi sendiri: turn yang sudah di-`archived_turns` IKUT bisa di-recall, live window (`ordinal >= len(archived_turns)`) DIKECUALIKAN** — live window sudah ada di prompt, mengembalikannya = persis "confusing context with memory". Cutoff dibaca *lazy* di dalam closure saat tool dipanggil, karena kompaksi jalan di awal `run_agent()` *setelah* registry disusun.
- **Query: tokenisasi `[^\W_]+` lalu tiap token dibungkus `"…"`** — sama dengan token yang unicode61 hasilkan, jadi sintaks FTS5 (`"`, `*`, `(`, `-`, `AND`/`OR`/`NOT`) tidak mungkin lolos sebagai operator. **AND dulu, fallback OR kalau AND kosong** (precision-first; model sering nulis query longgar). Tanpa token → `[]` tanpa buka DB.
- **Render `text` untuk index**: string apa adanya; blok list → text digabung, `[tool_use <name>] <input>`, `[tool_result] <content>` — supaya aktivitas tool lama bisa dicari by nama tool atau isi hasilnya. `content_json` tetap verbatim.
- **Fail loud, 3 arah**: file bukan SQLite → `ArchiveLoadError`; SQLite tapi tanpa tabel `meta` (DB asing) → `ArchiveLoadError`, tidak disentuh; `schema_version` beda → `UnsupportedArchiveSchemaError`. DB belum ada → dibuat saat pertama dipakai.

**Verifikasi nyata (2026-09-09):** smoke test manual dengan `ANTHROPIC_API_KEY` asli (`claude-haiku-4-5`), folder data terisolasi: sesi A cerita sambil lalu ("makan di warung… ketemu Pak Budi yang bilang printer lantai 3 rusak lagi") tanpa minta diingat → model **tidak** memanggil `remember_user_fact` (benar — bukan fakta durable). Sesi B (session_id beda sama sekali): "Kemarin aku pernah cerita soal printer nggak ya?" → model memanggil `recall_memory(query="printer")` **sendiri** (2 iterasi), menjawab dengan framing "Dalam obrolan sebelumnya, kamu menceritakan bahwa… printer lantai 3 rusak lagi" — kutipan, bukan pernyataan fakta. `profile.json` tidak pernah dibuat, 6 turn ter-arsip di `memory.db`. Data smoke dihapus setelahnya.

**Test** (`test_archive_store.py`, `test_recall_tools.py`, `test_memory_runner_long_term.py`) — 39 kasus test baru (36 fungsi, 1 di-parametrize 4 kasus; 1 skip = permission POSIX di Windows), semua `FakeLLMClient`/`tmp_path`. **135 passed, 3 skipped** total (99 kasus lama + 39 baru), regresi nol — tidak ada file test lama yang berubah. Cover termasuk: ingest setelah kompaksi tidak duplikat & ordinal kontinu; sesi dibuat ulang id sama → generasi sendiri tanpa `IntegrityError`; AND→OR fallback; sanitasi sintaks FTS5; fold diakritik; exclude live window; cutoff lazy; ingest gagal → exception propagate tapi sesi sudah durable & turn berikutnya catch-up; 2 runner lama tidak mengirim `recall_memory`.

**Belum digarap / TODO v2 (M2b):**
- **Ranking**: v1 murni bm25 + tie-break id terbaru. Observasi smoke test: turn pendek seperti `[tool_use recall_memory] {"query": "printer"}` dapat skor bm25 tinggi karena dokumennya pendek — tidak salah, tapi kandidat down-weight/exclude turn yang isinya cuma blok tool. Lebih jauh: skor gabungan relevance + recency + importance ala Generative Agents, atau fakta ber-validitas-waktu ala Zep.
- **Tokenizer**: `unicode61` tanpa stemming — `kucing` tidak match `kucingnya`. Opsi: prefix `*` di token, atau tokenizer `trigram` (sudah diverifikasi tersedia). Ditunda karena nambah noise; butuh data pemakaian nyata.
- Tool `read_conversation_around(session_id, ordinal)` — seam-nya sudah ada (`session_id`+`ordinal` di tiap hit), belum dibangun.
- Forgetting/eviction untuk arsip (FSFM, MemoryBank) & *encoding gate* ala Storage Is Not Memory — sama seperti M2c, ditunda sampai ada data pemakaian nyata. Kalau nanti ada delete, `turns_fts` butuh trigger/`'delete'` command (v1 cuma INSERT).
- Reflexion persistence lintas sesi (TODO sejak M1) — arsip ini sekarang bisa jadi tempatnya (taksonomi *experience memory* di survei Graph-based Agent Memory), belum dikerjakan.
- Error-path persistence lintas store — arsip ditulis terakhir dan self-healing (idempoten by count), tapi tetap kelas gap yang sama dengan M2a/M2c; belum ada keputusan produk untuk giliran yang gagal di tengah.
- Concurrent writers — non-goal, sama seperti M2a/M2c; SQLite locking bikin aman, bukan cepat.

## M2 v2 — A1: Entry point tunggal (implementasi nyata, 2026-09-09)

**Masalah yang diselesaikan:** tiap sub-milestone M2 datang dengan runner-nya sendiri di `backend/memory/runner.py` — `run_with_memory()` (M2a), `run_with_profile_memory()` (M2c), `run_with_long_term_memory()` (M2b). Ketiganya 80% kode yang sama (load sesi → susun registry per-turn → `run_agent()` → save), bedanya cuma lapisan mana yang aktif. Dua yang lama bertahan bukan karena dibutuhkan produk (F.R.I.D.A.Y selalu jalan dengan 3 lapis), tapi karena aturan "runner lama tidak disentuh" tiap sub-milestone. Begitu Sprint 3 (M4/M5 device) mulai wiring, harus jelas **satu** fungsi turn yang dipakai — dan `backend/orchestrator/` (kosong sejak Sprint 1, README: "koordinasi antar komponen: agent, tool, memory, device") memang tempatnya. Catatan di bagian M2a di atas ("kenapa `run_with_memory()` terpisah dari `run_agent()`… `backend/orchestrator/` masih kosong") sekarang **tidak berlaku lagi** — dibiarkan sebagai sejarah.

**Yang dibangun:**
- `backend/orchestrator/orchestrator.py` — class `Orchestrator(llm, registry, session_store=None, profile_store=None, archive_store=None, max_iterations=6, system=DEFAULT_SYSTEM_PROMPT)` dibangun **sekali**, lalu `run_turn(user_input, session_id) -> AgentResult` dipanggil tiap giliran. Isinya persis badan `run_with_long_term_memory()` yang dipindah: load sesi + profil (keduanya **dibaca ulang dari store tiap turn** — store = sumber kebenaran, tidak ada cache di objek), registry per-turn = salinan registry caller + 2 tool profil + `recall_memory` (registry caller tidak pernah dimutasi), `run_agent()`, lalu tulis: sesi → profil (kalau dirty) → arsip terakhir.
- `backend/orchestrator/__init__.py` — re-export `Orchestrator`. Arah impor satu arah (`orchestrator` → `agent_core` + `memory`; tidak ada yang impor balik), jadi circular import yang dulu memaksa runner keluar dari `backend/memory/__init__.py` tidak mungkin terjadi di sini.
- **Dihapus:** `backend/memory/runner.py` + 3 file test-nya (`test_memory_runner.py`, `test_memory_runner_profile.py`, `test_memory_runner_long_term.py`). Tidak ada caller di luar test, jadi tidak ada yang pecah.
- `backend/memory/__init__.py` — docstring diganti: package ini cuma model + store, entry point ada di `backend.orchestrator`.

**Yang sengaja TIDAK berubah:**
- Urutan tulis dan perilaku exception (fail loud, arsip self-healing) — identik dengan M2b. Keputusan produk error-path persistence lintas store tetap terbuka → **M2 v2 A2**, bukan A1.
- `run_agent()` tetap bebas efek samping I/O; `loop.py` tidak disentuh.
- Tidak ada factory `Orchestrator.from_env()` yang memanggil `get_llm_client()` — belum ada caller nyata; ditambah saat wiring Sprint 3 kalau memang perlu.
- `.gitkeep` di `backend/orchestrator/` dibiarkan (precedent: `backend/memory/.gitkeep` masih ada).

**Test** (`backend/tests/test_orchestrator.py`) — 13 kasus test: 11 porting 1:1 dari 3 file runner (subjek diganti `Orchestrator`, perilaku & assertion sama), 1 gugur (`test_existing_runners_do_not_offer_recall_memory` — subjeknya tidak ada lagi), 2 baru untuk kontrak class (registry caller tidak dimutasi setelah 2 turn; store yang di-inject dipakai apa adanya lintas turn). Porting "lanjut sesi yang ada" sengaja memakai **satu objek** `Orchestrator` untuk 2 turn — sekaligus membuktikan registry per-turn dibangun ulang (register tool memori dua kali ke registry yang sama akan raise). **136 passed, 3 skipped** (135 − 13 + 14), hijau di run pertama; tidak ada file test lain yang berubah.

**Belum digarap / TODO v2 (sisa setelah A1):** A2 (error-path persistence, butuh keputusan produk + kemungkinan bump `SessionRecord` 1.0.0→1.1.0 + migrasi minimal), B (polish ranking/tokenizer M2b, tool `read_conversation_around`), C (Reflexion persistence), D (decay/forgetting, encoding gate — tunggu data pemakaian nyata).

## M2 v2 — A2: trace konkret (disusun ulang 2026-09-17)

**Kenapa disusun ulang:** memori asisten mencatat tabel trace A2 dibuat 2026-09-11, tapi isinya tidak pernah tersimpan ke file ini. Versi ini dibangun ulang dari nol, dan kali ini **setiap baris adalah test yang bisa dijalankan**: `backend/tests/test_a2_trace.py` (characterization test, merekam perilaku *saat ini*, termasuk yang salah). Rumah yang dipakai: mock M5 `backend/devices/mock_home.py` (satu lampu + satu AC, semua mati), store asli di `tmp_path`, LLM palsu yang diskrip. Nomor skenario di bawah **tidak sama** dengan S1-S9 versi 2026-09-11 yang hilang.

**Pertanyaan A2:** kalau satu turn gagal di tengah, apa yang dianggap "resmi terjadi", dan store mana yang harus tahu?

| # | Kejadian | Dunia (lampu) | Sesi di disk | Profil | Arsip | Konsisten? |
|---|---|---|---|---|---|---|
| S1 | Normal: nyalakan lampu, jawab | nyala | lengkap + jawaban | – | tersimpan | ✅ |
| S2 | Device offline, error jadi observasi, model bilang gagal | mati | tool_result error | – | tersimpan | ✅ |
| S3 | Device **menerapkan** perintah tapi konfirmasi timeout (`LOST_ACK`) | **nyala** | tool_result "did not confirm", model bilang gagal | – | tersimpan | ❌ percakapan bilang gagal, lampu nyala; turn berikutnya model menjawab dari riwayat tanpa `home_get_state` |
| S4 | Lampu nyala, lalu panggilan LLM berikutnya gagal (API 503) | **nyala** | **tidak ada** | – | tidak ada | ❌ turn hilang total; turn berikutnya model hanya melihat "halo" |
| S5 | Lampu nyala, model sudah bilang "sudah nyala", `SessionStore.save` gagal | **nyala** | **tidak ada** | – | tidak ada | ❌ seperti S4, tapi user sudah diberi tahu berhasil |
| S6 | `remember_user_fact` jalan, model bilang "saya ingat", `ProfileStore.save` gagal | – | ada, berisi "Siap, saya ingat." | **kosong** | tidak ada | ❌ sesi mengklaim diingat, profil tidak |
| S7 | Turn sukses, `ArchiveStore.ingest` gagal | nyala | lengkap | – | belum | ⚠️ durable konsisten (arsip self-healing di turn berikutnya), tapi caller menerima exception untuk turn yang berhasil |
| S8 | Lampu nyala, iterasi habis (`max_iterations`) | **nyala** | aksi tersimpan, **jawaban "couldn't finish" tidak** | – | tersimpan | ❌ sesi berakhir di tool_result; turn berikutnya model menerima dua pesan `user` berturut-turut dan tidak pernah melihat jawaban yang dilihat user |
| S9 | Dua aksi dalam satu langkah: lampu sukses, AC offline | lampu nyala, AC mati | dua tool_result: sukses + error | – | tersimpan | ✅ |

Catatan S8: dokumentasi Messages API menyebut pesan ber-role sama yang berturut-turut digabung jadi satu turn, jadi kemungkinan besar tidak error. **Belum diverifikasi dengan panggilan API asli.**

**Pola yang terlihat:**
- **Dunia fisik tidak bisa di-rollback.** Semua ❌ kecuali S6 punya bentuk sama: efek samping sudah terjadi, catatan tidak ikut. Maka jawaban A2 tidak bisa "batalkan turn"; yang bisa hanya "catat apa yang sudah terjadi" dan "cek dunia saat ragu".
- **Kegagalan ada di tiga tempat berbeda:** di dalam loop setelah aksi (S4, S8), saat menulis store (S5, S6, S7), dan di device sendiri (S3). Satu mekanisme tidak menutup ketiganya.
- `session.messages` sudah dimutasi di tempat oleh `run_agent()`, jadi di S4 orchestrator **sebenarnya memegang** turn parsial di memori; ia hanya tidak menyimpannya karena exception melompati `save`.

**Opsi (dari trace 2026-09-11, dipetakan ke skenario):**

| Opsi | Isi | Menutup | Tidak menutup | Biaya |
|---|---|---|---|---|
| (a) try/except di `Orchestrator.run_turn` + penanda turn terputus | saat `run_agent` raise, tambahkan pesan assistant penanda ("[turn terputus: …]"), simpan sesi/profil/arsip, lalu raise ulang; saat iterasi habis, simpan teks fallback ke sesi | S4, S8 | S3, S5, S6 | kecil, tanpa bump `SessionRecord` kalau penanda berupa pesan teks biasa |
| (b) log aksi durable untuk tool non-read-only | append-only (mis. JSONL) ditulis oleh eksekutor tool sebelum/sesudah aksi, terpisah dari sesi | S5 (dan jejak audit semua kasus) | S3 (log hanya tahu "tidak terkonfirmasi") | sedang; tumpang tindih dengan audit log M11 |
| (c) device state sebagai sumber kebenaran | adapter membaca ulang state setelah perintah gagal/timeout dan mengembalikan state aktual di observasi; prompt: cek state sebelum menjawab pertanyaan status | S3 | S4, S5, S8 | kecil di adapter mock; di adapter nyata butuh `get_state` per device |

**Rekomendasi asisten (belum diputuskan user):** (a) + (c) sekarang, (b) ditunda ke M11 sebagai audit log. S6 dan S7 butuh keputusan terpisah: urutan tulis profil vs sesi, dan apakah kegagalan arsip tetap di-raise.

**Pertanyaan yang harus dijawab user:**
1. Turn yang gagal di tengah setelah aksi (S4, S8): disimpan sebagian dengan penanda terputus? Rekomendasi: ya.
2. Perintah device yang tidak terkonfirmasi (S3): adapter otomatis membaca ulang state? Rekomendasi: ya.
3. Log aksi durable (b): sekarang, atau bersama audit log M11? Rekomendasi: M11. Konsekuensinya S5 tetap celah yang diketahui.
4. Kegagalan arsip (S7): tetap raise ke caller (keputusan M2b "fail loud"), atau cukup dicatat karena arsip self-healing? Rekomendasi: cukup dicatat.
5. Profil gagal disimpan (S6): tulis profil **sebelum** sesi, supaya kegagalan profil tidak meninggalkan klaim palsu di sesi? Rekomendasi: ya, tapi ini mengubah urutan tulis yang sengaja dipertahankan sejak M2b.

### Keputusan A2 (user, 2026-10-23) dan implementasinya

| # | Pertanyaan | Keputusan | Implementasi |
|---|---|---|---|
| 1 | Turn gagal setelah aksi (S4, S8) | **Ya**, simpan sebagian | `Orchestrator.run_turn`: kalau `run_agent` raise setelah pesan user ditambahkan, pesan assistant penanda `[Turn interrupted ...]` ditambahkan, semua store ditulis, exception asli di-raise ulang (kegagalan simpan saat itu ditempel sebagai `add_note`, tidak menimpa penyebab). `run_agent`: teks "couldn't finish" saat iterasi habis disimpan sebagai pesan assistant. |
| 2 | Perintah tidak terkonfirmasi (S3) | **Ya**, baca ulang state | `MockHomeAdapter._command`: setelah `DeviceError`, state dibaca ulang; kalau perubahan yang diminta sudah terjadi → sukses + `note`; kalau tidak → error berisi state aktual; kalau baca ulang gagal → "actual state unknown". `DEFAULT_SYSTEM_PROMPT` ditambah: status device dibaca dengan tool, bukan dari riwayat. |
| 3 | Log aksi durable (b) | **Ditunda ke M11** (audit log) | Tidak ada. S5 jadi celah yang diketahui; test S5 tetap merekam perilaku lama dan diberi label KNOWN GAP. |
| 4 | Arsip gagal (S7) | **Dicatat, tidak di-raise**, plus tanda peringatan | `AgentResult.warnings` (field baru, default kosong) + `logging.warning`. Arsip tetap self-healing di turn berikutnya. Mengubah keputusan "fail loud" M2b khusus untuk arsip; load/save sesi dan profil tetap fail loud. |
| 5 | Urutan tulis (S6) | **Diubah**: profil → sesi → arsip | `Orchestrator._persist`. Profil gagal → sesi **tetap** ditulis, dengan catatan koreksi `[Saving the user profile failed ... NOT saved ...]` ditempel ke jawaban assistant terakhir, lalu exception di-raise (perbaikan 2026-10-23, lihat di bawah). Sesi gagal setelah profil tersimpan → profil berisi fakta yang memang diucapkan user (aman). |

Test: `test_a2_trace.py` ditulis ulang untuk S3, S4, S6, S7, S8 (+ kasus tambahan: offline membawa state aktual, gagal di panggilan LLM pertama, kegagalan simpan tidak menutupi penyebab, profil tersimpan saat sesi gagal); `test_orchestrator.py::test_ingest_failure_*` diubah ke perilaku peringatan. Total 243 passed, 3 skipped.

Celah yang tersisa: S5 (sampai M11); S8 dengan API asli belum diverifikasi, tapi kini tidak relevan karena peran pesan selalu bergantian.


**Perbaikan celah kecil (2026-10-23, sesi yang sama):**
- *Profil gagal menghilangkan aksi device di turn yang sama* → ditutup. Versi pertama tidak menulis sesi sama sekali saat profil gagal; sekarang sesi ditulis dengan catatan koreksi, jadi tool_result aksi device tetap tercatat dan klaim "saya ingat" langsung dikoreksi di turn yang sama (peran pesan tetap bergantian karena catatan ditempel ke pesan assistant terakhir, bukan pesan baru). Arsip dilewati, menyusul di turn berikutnya.
- *Deteksi "turn sudah dimulai" bergantung pada asumsi kompaksi* → dihapus. Mutation test menunjukkan pengecekan identitas objek tidak mengubah hasil apa pun: setiap turn tersimpan selalu berakhir dengan pesan assistant, jadi penanda "terputus" cukup ditambahkan bila pesan terakhir ber-role `user`. Kalau kompaksi gagal sebelum input user ditambahkan, sesi tidak berubah dan hanya ditulis ulang apa adanya. Dua test kompaksi baru (gagal → tanpa penanda; sukses lalu LLM gagal → ada penanda) dan mutation check memastikan pengecekan role memang dijaga test.

## Bahasa Awam

Kalau M1 itu "orangnya yang mikir dan pakai alat", M2a itu **buku catatan kecil** yang dia pegang selama ngobrol sama kamu.

Sebelum M2a: F.R.I.D.A.Y kayak orang amnesia — tiap kali kamu ngomong lagi, dia lupa semua yang barusan dibahas, bahkan dalam obrolan yang sama. Sekarang, dengan M2a:

1. **Dia nyatet tiap kalimat kalian berdua** ke buku catatan (file JSON) — bukan cuma diinget di kepala doang yang hilang kalau dia "pingsan" (proses restart).
2. **Kalau buku catatannya mulai kepenuhan** (obrolan udah panjang banget), dia nggak asal sobek halaman lama — dia rangkum dulu isinya jadi beberapa baris inti, baru halaman lamanya "diarsipin" (bukan dibuang, cuma dipadatkan).
3. **Pas mau jawab**, dia taruh rangkuman itu di halaman paling depan buku catatannya (bukan diselipin di tengah-tengah) — soalnya kalau diselipin di tengah, dia gampang "kelewat baca" bagian itu. Halaman-halaman terbaru tetap ditulis lengkap apa adanya di belakang.

Ini masih "buku catatan satu obrolan" doang — F.R.I.D.A.Y belum bisa "nginget balik" hal dari obrolan yang beda sama sekali tanpa diingatkan (itu tugas M2b nanti, kayak dia buka-buka arsip buku catatan lamanya). Tapi sekarang, minimal, obrolan yang sama nggak lagi "reset" tiap kali kamu nutup dan buka lagi F.R.I.D.A.Y.

Kalau M2a itu buku catatan satu obrolan, **M2c itu kartu identitas** yang dia bawa ke SETIAP obrolan, obrolan baru sekalipun. Bedanya penting: buku catatan M2a ditutup begitu obrolan itu selesai (obrolan lain nggak bisa buka buku itu), tapi kartu identitas M2c selalu ikut, obrolan mana pun yang kamu mulai.

1. **Dia cuma nulis di kartu itu kalau kamu bilang eksplisit** ("inget ya, aku alergi kacang") — dia nggak diam-diam nyimpulin dari obrolan biasa terus dianggap fakta permanen. Ini beda banget sama M2a yang cuma "mringkas" apa yang dibahas — M2c "mencatat" fakta tentang kamu.
2. **Kalau ada info baru yang beda dari catatan lama** (misal pindah alamat), dia nggak nimpa diam-diam — catatan lama ditandai "sudah nggak berlaku" (bukan dihapus, biar ada jejak kalau mau ditelusuri), catatan baru yang jadi aktif.
3. **Kalau kamu bilang "lupain soal itu"**, dia coret dari kartu identitasnya — tapi HARUS kamu yang minta, dia nggak akan hapus sendiri.

Sekarang kalau kamu mulai obrolan baru sama sekali, F.R.I.D.A.Y tetap "kenal" kamu — bukan cuma inget percakapan yang sama, tapi inget KAMU.

Kalau M2a itu buku catatan satu obrolan dan M2c itu kartu identitas, **M2b itu lemari arsip** tempat SEMUA buku catatan lama disimpan — dan dia bisa buka-buka lemari itu pakai kata kunci.

1. **Tiap obrolan selesai, buku catatannya masuk lemari apa adanya** — nggak dirangkum, nggak "ditafsirkan" dulu. Persis kata-katanya. Soalnya kalau dirangkum duluan, detail yang nanti ternyata penting bisa keburu hilang sebelum ada yang nanya.
2. **Dia baru buka lemari kalau merasa perlu** ("kemarin aku pernah cerita soal printer nggak?") — dia cari pakai kata kunci, dapat beberapa kutipan lengkap dengan "dari obrolan mana" dan "kapan". Nggak tiap ngobrol dia bongkar lemari.
3. **Yang dia dapat itu kutipan, bukan kesimpulan.** Dia bakal bilang "di obrolan sebelumnya kamu pernah bilang…", bukan "kamu itu orangnya begini". Kalau kamu mau sesuatu beneran dicatat sebagai fakta tentang kamu, itu tetap harus lewat kartu identitas (M2c) — lemari arsip nggak pernah nulis ke kartu itu sendiri.

Jadi sekarang lengkap: dia inget obrolan yang lagi jalan (M2a), inget siapa kamu (M2c), dan bisa buka arsip obrolan-obrolan lama kalau kamu tanya (M2b).

Dulu, buat pakai tiga-tiganya, ada tiga "pintu masuk" berbeda tergantung fitur mana yang mau diaktifkan — sisa dari cara membangunnya bertahap. Sekarang cuma ada **satu resepsionis** (`Orchestrator`): kamu ngomong ke dia, dia yang buka buku catatan, bawa kartu identitas, dan siapin kunci lemari arsip — tiap giliran, tanpa kamu perlu tahu ada tiga hal di belakangnya. Ini penting buat langkah berikutnya (Sprint 3, kontrol perangkat): apa pun yang nanti mau "ngobrol" sama F.R.I.D.A.Y cukup tahu satu pintu itu.
