# F.R.I.D.A.Y — Dokumen Tinjauan Proyek (untuk Feedback Eksternal)

> **Untuk model AI / reviewer yang membaca dokumen ini.** Dokumen ini adalah paket lengkap untuk meminta *feedback*: tujuan proyek, roadmap 12 sprint, apa yang sudah dikerjakan di tiap sprint, kekurangan yang kami sadari, potongan kode yang kami minta ditinjau, dan daftar pertanyaan spesifik. Log pengerjaan lengkap (apa adanya, tidak disunting) ada di **Lampiran A–C** di akhir dokumen.
>
> Bahasa dokumen: Indonesia, istilah teknis dibiarkan dalam bahasa Inggris. Mohon jawab dengan kritik yang konkret (sebut file/fungsi, skenario gagal, dan alternatif), bukan pujian umum. Silakan membantah keputusan yang sudah diambil kalau ada alasan kuat.
>
> Disusun: 2026-10-25. Posisi kode: commit `94c24b2` (branch `master`), working tree bersih. Test: **280 passed, 3 skipped** (dijalankan ulang saat dokumen ini disusun).

---

## Daftar Isi

1. [Ringkasan proyek](#1-ringkasan-proyek)
2. [Prinsip desain yang dipegang](#2-prinsip-desain-yang-dipegang)
3. [Arsitektur saat ini](#3-arsitektur-saat-ini)
4. [Roadmap 12 sprint dan statusnya](#4-roadmap-12-sprint-dan-statusnya)
5. [Sprint 1 — M0 Contract + M1 Agent Core (DONE)](#5-sprint-1--m0-contract--m1-agent-core-done)
6. [Sprint 2 — M2 Memory System (DONE)](#6-sprint-2--m2-memory-system-done)
7. [Sprint 3 — M4 Tool Registry + M5 Device Layer (ON PROGRESS)](#7-sprint-3--m4-tool-registry--m5-device-layer-on-progress)
8. [Kekurangan lintas sprint (proses dan arsitektur)](#8-kekurangan-lintas-sprint-proses-dan-arsitektur)
9. [Kode yang perlu disesuaikan dan dimintai feedback](#9-kode-yang-perlu-disesuaikan-dan-dimintai-feedback)
10. [Pertanyaan untuk reviewer](#10-pertanyaan-untuk-reviewer)
11. [Lampiran A — Log Sprint 1 (lengkap)](#lampiran-a--log-sprint-1-lengkap)
12. [Lampiran B — Log Sprint 2 (lengkap)](#lampiran-b--log-sprint-2-lengkap)
13. [Lampiran C — Log Sprint 3 (lengkap, on progress)](#lampiran-c--log-sprint-3-lengkap-on-progress)

---

## 1. Ringkasan proyek

**F.R.I.D.A.Y** adalah asisten AI personal (proyek pribadi, satu developer) yang terinspirasi dari F.R.I.D.A.Y di fiksi: agent yang bisa memakai tool, mengontrol perangkat IoT/OS, punya memori jangka panjang, dan nanti bisa diajak bicara dengan suara.

- **Target realistis:** ~80–85% dari fungsionalitas yang *terlihat* (tool-use, kontrol perangkat, memori, percakapan suara), **bukan** reasoning superhuman.
- **Pemakai:** satu orang (pemilik) plus orang yang ia setujui. Bahasa sehari-hari pemakai: Indonesia.
- **Biaya dan kontrol:** pemilik ingin akhirnya bebas biaya per-token dan bebas kontrol korporat → rencananya pindah ke model open-weight lokal di Sprint 8. Sampai saat itu memakai **Anthropic Claude API** (`claude-haiku-4-5` untuk development, karena murah).
- **Metode kerja:** setiap modul diawali riset paper (±130 paper sudah dibaca dan diringkas di `Memory Think/PAPER_NOTES.md`, dipetakan ke sprint di `sprint-paper-mapping.md`), lalu desain di plan mode, implementasi, test, smoke test dengan API asli, dan pencatatan di log sprint (append-only).
- **Stack:** Python 3.13, Pydantic v2, `jsonschema`, SDK `anthropic`, `python-dotenv`, SQLite FTS5 (bawaan Python), pytest. Tanpa vector DB, tanpa GPU, tanpa layanan eksternal selain API LLM.
- **Ukuran:** ±3.900 baris Python non-test di `backend/`, 25 file test, 23 commit.
- **Antarmuka saat ini:** hanya CLI terminal (`python -m backend.cli`) dengan rumah simulasi. Belum ada perangkat nyata, belum ada suara, belum ada UI.

## 2. Prinsip desain yang dipegang

Prinsip ini muncul dari diskusi dan dipakai sebagai patokan di setiap keputusan. Reviewer dipersilakan menilai apakah prinsip ini masuk akal **dan** apakah kode benar-benar mengikutinya.

1. **Context ≠ memory.** Percakapan aktif (M2a) tidak boleh diam-diam berubah jadi "fakta tentang user". Fakta permanen hanya masuk lewat tool eksplisit (`remember_user_fact`).
2. **Ringkasan tidak boleh mengarang.** Kompaksi hanya memadatkan; "aku makan nasi goreng hari ini" tidak boleh jadi "user suka nasi goreng".
3. **Fail loud, jangan diam-diam mengganti memori rusak dengan memori kosong.** File sesi korup, versi skema salah, atau gagal simpan memunculkan exception bertipe jelas. (Pengecualian yang diputuskan: kegagalan arsip M2b hanya jadi peringatan, karena arsip bisa memperbaiki dirinya sendiri.)
4. **Dunia fisik tidak bisa di-rollback.** Kalau turn gagal setelah perangkat bergerak, yang dilakukan adalah *mencatat yang sudah terjadi* dan *membaca ulang state perangkat*, bukan membatalkan.
5. **Jujur saat tidak bisa.** Tidak ada tool yang cocok → bilang tidak bisa, jangan pakai tool lain sebagai pengganti, jangan mengaku sudah melakukan sesuatu.
6. **Mock sebelum hardware**, dan **jangan memutuskan threshold tanpa data pemakaian nyata** (decay, ranking, ambang kompaksi ditunda).
7. **Scope ketat.** Fitur yang belum ada kebutuhannya tidak dibangun (abstraksi multi-model, migrasi skema, vector store, dsb.).
8. **Riwayat append-only.** Log sprint tidak diedit; koreksi ditulis sebagai entry baru.

## 3. Arsitektur saat ini

### 3.1 Peta folder `backend/`

| Folder | Modul | Isi | Status |
|---|---|---|---|
| `schemas/` | M0 | `ToolContract` 1.1.0 (MCP-style + versi ala Agent-OS + `domain`, `examples`, `content_hash`), kontrak sesi/profil/arsip | ada |
| `agent_core/` | M1 | `loop.py` (ReAct native tool-calling), `llm_client.py` (Protocol + Anthropic), `tool_registry.py` (registry per turn), `config.py`, `tools/` (time, profile, recall) | ada |
| `memory/` | M2 | M2a `session.py` + `compaction.py` + `store.py` (JSON per sesi, atomic write); M2c `profile.py` + `profile_store.py`; M2b `archive_store.py` (SQLite FTS5) | ada |
| `orchestrator/` | M2 v2 A1/A2 | `Orchestrator.run_turn()` — satu pintu per turn, urutan tulis profil → sesi → arsip | ada |
| `registry/` | M4 | `ToolCatalog` (FTS5 in-memory, `sync` via hash), `find_tools` (meta-tool ala MCP-Zero), `AutoLoadPolicy`, retensi tool lintas turn | ada |
| `dal/` | — | helper FTS5 bersama (`fts.py`) | ada |
| `devices/` | M5 | `MockHome` + `MockHomeAdapter` (1 lampu + 1 AC, injeksi kegagalan `OFFLINE`/`LOST_ACK`) | mock saja |
| `cli.py` | — | CLI terminal: LLM asli + rumah simulasi, `/state /fail /trace /new` | ada |
| `security/` | M11 | — | **kosong** |
| `persona/` | M15 | — | **kosong** |

### 3.2 Alur satu turn

```
user ketik di CLI
  └─ Orchestrator.run_turn(input, session_id)
       ├─ load Session (JSON) + Profile (JSON)
       ├─ susun registry per turn = tool pinned + tool memori + find_tools
       │     + tool yang berhasil dipakai ≤3 turn terakhir (retensi)
       ├─ run_agent(...)                      ← agent_core/loop.py
       │    ├─ kompaksi kalau token terakhir + margin ≥ ambang (cek di awal saja)
       │    ├─ loop ≤ 6 iterasi:
       │    │    system = prompt default + blok fakta profil
       │    │    LLM → teks (Thought) + tool_use (Action)
       │    │    tiap tool_use: resolve (auto-load read-only dari katalog)
       │    │       → validasi jsonschema → jalankan → tool_result (Observation)
       │    │       error apa pun → tool_result is_error (bukan crash)
       │    └─ iterasi habis → teks "couldn't finish" disimpan
       ├─ gagal di tengah → penanda "[Turn interrupted ...]", simpan, raise ulang
       └─ _persist: profil (kalau berubah) → sesi → arsip (gagal = warning)
```

### 3.3 Tiga lapis memori

| Lapis | Analogi | Penyimpanan | Cara masuk | Cara dipakai |
|---|---|---|---|---|
| M2a sesi | papan tulis | JSON per `session_id` | otomatis tiap turn; lama → diringkas | dikirim ke LLM (ringkasan di depan, turn terbaru di belakang) |
| M2c profil | kartu identitas | satu `profile.json` | hanya tool `remember_user_fact` / `forget_user_fact` | ditempel ke system prompt tiap panggilan |
| M2b arsip | lemari arsip | SQLite FTS5, semua turn semua sesi, verbatim | otomatis (ingest setelah sesi tersimpan) | hanya lewat tool `recall_memory`, hasil = kutipan, bukan fakta |

## 4. Roadmap 12 sprint dan statusnya

| Sprint | Modul | Topik riset | Status |
|---|---|---|---|
| **1** | M0 Contract + M1 Agent Core | #1 Agentic AI / Tool Use | ✅ **DONE** (2026-08-06 → 08-13) |
| **2** | M2 Memory (M2a/M2b/M2c + v2 A1) | #2 Memory Architecture | ✅ **DONE** v1 (2026-08-13 → 09-09); sisa v2 B/C/D terbuka |
| **3** | M4 Tool Registry + M5 Device Layer | #4 Device Orchestration + #5 IoT | 🟡 **ON PROGRESS** (mulai 2026-09-10) |
| 4 | M11 Security Gate | #6 Security & Permission | ⬜ belum mulai |
| 5 | M7 Wake word, M8 STT, M9 Speaker auth, M10 TTS | #7–#10 Voice | ⬜ |
| 6 | M3 Task Planner | #3 Planning | ⬜ |
| 7 | M6 Computer/OS Control | #4 lanjutan | ⬜ |
| 8 | M12 Local Inference + M13 Cloud–Edge Routing | #11, #12 | ⬜ |
| 9 | M14 Multi-Agent | #13 | ⬜ |
| 10 | M15 Persona | #15 | ⬜ |
| 11 | M17 Proactive & Context-Aware | #14 | ⬜ |
| 12 | M16 Evaluation & Benchmarking | #16 | ⬜ |

Catatan: riset paper untuk **semua** 16 kategori sudah dikerjakan di awal (Sprint 1), jadi tiap sprint mendatang sudah punya bahan bacaan.

---

## 5. Sprint 1 — M0 Contract + M1 Agent Core (DONE)

### 5.1 Tujuan
Fondasi: bentuk baku deskripsi tool (M0) dan loop agent yang bisa memanggil tool (M1). Paper: ReAct, Toolformer, MCP, LLM Agent Survey, Agent-OS, Reflexion.

### 5.2 Yang dikerjakan (ringkas, detail di Lampiran A)
- **2026-08-06** — setup repo, venv Python 3.13, struktur folder lengkap untuk semua modul. Riset ±96 paper lintas 12 sprint → `PAPER_NOTES.md`.
- **2026-08-07** — `ToolContract` (Pydantic v2): `name` snake_case, `version` + `contract_version` semver terpisah, `description` wajib, `input_schema`/`output_schema`, `ToolAnnotations` (4 hint MCP), `PermissionTier` (`read_only`/`standard`/`critical`, label saja). 11 test. Keputusan: **cloud API dulu, lokal di Sprint 8**; M1 didesain provider-agnostic.
- **2026-08-12 → 08-13** — perapian koleksi paper: folder per modul M0–M17, verifikasi isi tiap PDF dengan `pdftotext` + md5 (ditemukan beberapa file salah isi/duplikat dan diganti).
- **2026-08-13** — M1: `run_agent()` ReAct dengan **native tool-calling Claude** (teks = Thought, `tool_use` = Action, `tool_result` = Observation), validasi argumen `jsonschema`, error tool → observasi `is_error` ("Reflexion minimal"), batas `max_iterations`. Satu tool contoh `get_current_time`. 19 test. Smoke test API asli berhasil.

### 5.3 Keputusan penting
- Native tool-calling, bukan parsing teks ala paper ReAct 2022.
- Scope M0 hanya Tool Contract; kontrak Task/Event/Memory/Device ditunda ke modul masing-masing.
- `permission_tier` sudah ada di kontrak sejak awal, penegakan di M11.
- Model development `claude-haiku-4-5` (anggaran awal $5).

### 5.4 Kekurangan Sprint 1 (masih berlaku)
1. **"Provider-agnostic" belum terbukti.** `LLMClient` adalah Protocol, tapi format `messages` yang dipakai loop, sesi, dan kompaksi adalah bentuk content-block Anthropic (`tool_use`/`tool_result`). Provider `openai` masih `NotImplementedError`. Kemungkinan besar perpindahan ke model lokal (Sprint 8) akan menyentuh loop, sesi, kompaksi, dan retensi, bukan hanya `llm_client.py`.
2. **Reflexion hanya nama.** Yang ada sekarang: pesan error dikembalikan sebagai observasi. Tidak ada langkah refleksi verbal, dan tidak persisten lintas sesi (TODO "C" sejak M1, belum dikerjakan).
3. **`permission_tier` belum ditegakkan**, padahal sekarang sudah ada tool yang mengubah dunia (lampu, AC). Semua aktuator ditandai `STANDARD` dan dijalankan tanpa konfirmasi.
4. **`max_iterations = 6` tetap.** `find_tools` memakan satu iterasi; tugas device multi-langkah bisa mentok.
5. **`get_current_time` mengembalikan UTC**, bukan zona waktu user (terbukti di smoke test).
6. **Test semua memakai LLM palsu.** Perilaku model asli hanya diverifikasi lewat smoke test manual sekali-sekali; tidak ada regresi otomatis untuk perilaku LLM.
7. **Kontrak M0 belum lengkap.** Device sudah ada (mock) tapi belum ada kontrak Device; tool device didefinisikan ad hoc di adapter.
8. **Catatan modul basi.** `M0_contract_layer.md` masih berstatus "Sedang digarap", `M1_agent_core.md` masih menyebut 19 test dan belum mencerminkan perubahan M4/A2. Sudah tercatat sebagai TODO penutup Sprint 3.
9. **README basi**: masih menyebut kontrak task/event/memory/device di `schemas/` dan tidak menyebut `devices/`, `cli.py`.
10. Porsi waktu Sprint 1 banyak habis untuk manajemen paper (96 PDF, rename, verifikasi). Bermanfaat untuk riset, tapi menunda kode.

---

## 6. Sprint 2 — M2 Memory System (DONE)

### 6.1 Tujuan
F.R.I.D.A.Y bisa melanjutkan percakapan, mengingat fakta tentang user lintas sesi, dan mencari ulang obrolan lama. Paper: MemGPT, Lost in the Middle, Recursively Summarizing, Generative Agents, RAG survey, MemoryBank, FSFM, Mem0, Zep, Storage Is Not Memory, HippoRAG, Memory OS, dll. (20 paper).

### 6.2 Yang dikerjakan (ringkas, detail di Lampiran B)
- **2026-08-14 — M2a (konteks aktif).** Sesi JSON per `session_id`; kompaksi *recursive summarization* saat `usage.input_tokens` + margin ≥ ambang (6000/500); titik potong hanya di turn user teks (tidak memotong pasangan `tool_use`/`tool_result`); ringkasan di depan, turn terbaru di belakang (Lost in the Middle). Review "context ≠ memory" → prompt kompaksi diperketat. **Robustness pass:** atomic write (`mkstemp` + `os.replace`), cek `schema_version`, exception domain (`SessionLoadError`, dst.), chmod 0600 best-effort. 58 test.
- **2026-08-18 — M2c (profil).** Fakta masuk hanya lewat tool `remember_user_fact` (keputusan user: tidak ada ekstraksi otomatis); konflik = fakta terbaru menang + jejak `superseded`; lupa = manual `forget_user_fact` (`STANDARD`). Profil disuntik ke **system prompt**, bukan ke `messages`, supaya tidak pernah lewat jalur ringkasan. 97 test. Smoke test 4 skenario berhasil.
- **2026-09-09 — M2b (arsip).** Pendekatan *retrieval-centered verbatim* (bukan ekstraksi ala Mem0/Zep): semua turn semua sesi di SQLite FTS5 (`unicode61 remove_diacritics 2`), bm25, AND lalu fallback OR, kunci idempotensi `(session_id, session_created_at)`, tool eksplisit `recall_memory` yang hasilnya dideskripsikan sebagai **kutipan**, bukan fakta. 135 test. Smoke test: model memanggil `recall_memory` sendiri dan mengutip dengan benar.
- **2026-09-09 — M2 v2 A1.** Tiga runner yang 80% identik diganti satu `Orchestrator.run_turn()`. 136 test.
- **Diskusi M2 v2:** A1 (satu pintu) ✅; A2 (error-path persistence) dipindah ke Sprint 3 dan sudah ✅; B (ranking/tokenizer/`read_conversation_around`), C (Reflexion persisten), D (decay/forgetting, encoding gate, validitas waktu fakta) **masih terbuka**, menunggu data pemakaian nyata.

### 6.3 Keputusan penting
- JSON per sesi untuk M2a, SQLite hanya untuk arsip.
- Token asli dari API, bukan estimasi karakter.
- Fakta profil hanya lewat tool eksplisit; arsip verbatim, bukan ekstraksi.
- Fail loud untuk load/save sesi dan profil.
- Decay/forgetting otomatis ditunda sampai ada data.

### 6.4 Kekurangan Sprint 2 (masih berlaku)
1. **Ambang kompaksi masih tebakan** (6000 token / margin 500 / simpan 6 pesan terakhir), belum divalidasi dengan pemakaian nyata.
2. **Overflow di tengah turn tidak dijaga.** Kompaksi hanya dicek di awal `run_agent()`. Turn dengan banyak tool call dan hasil tool besar bisa melewati batas konteks; satu-satunya pengaman adalah `max_iterations`.
3. **Kompaksi bisa kehilangan isi diam-diam** — lihat §9.3: kalau LLM mengembalikan teks kosong, ringkasan lama dipertahankan tetapi pesan lama tetap dipindah keluar dari konteks.
4. **Ringkasan tidak diverifikasi.** Larangan mengarang hanya ada di prompt; diuji dengan satu contoh (nasi goreng). Tidak ada pemeriksaan otomatis.
5. **Blok profil tidak dibatasi.** Semua fakta aktif ditempel ke system prompt di setiap panggilan LLM; biaya dan risiko "lost in the middle" naik seiring jumlah fakta. Tidak ada kategori baku, tidak ada decay.
6. **Model bingung profil vs arsip.** Di smoke test Sprint 3 model memanggil `recall_memory` padahal faktanya sudah ada di blok profil.
7. **Pencarian FTS5 tanpa stemming — buruk untuk bahasa Indonesia.** `kucing` ≠ `kucingnya`, `nyalakan` ≠ `menyalakan`, `lampu` ≠ `lampunya`. Ranking bm25 polos; turn yang isinya cuma blok tool mendapat skor tinggi karena pendek.
8. **Keamanan data pribadi minim.** Sesi dan profil disimpan sebagai JSON teks polos, arsip SQLite tanpa enkripsi. Di Windows, "restrict permission" hanya toggle read-only. Seluruh isi percakapan dikirim ke API cloud.
9. **Arsip verbatim = jalur prompt injection tersimpan.** Teks lama (termasuk hasil tool dari sumber luar nantinya) bisa masuk lagi ke konteks lewat `recall_memory` tanpa penanda kepercayaan. Belum dipikirkan (wilayah M11).
10. **Akses bersamaan** (dua proses menulis sesi yang sama) adalah non-goal yang didokumentasikan; akan relevan saat ada suara + CLI + proaktif berjalan bersamaan.
11. **Tidak ada evaluasi memori** (mis. LongMemEval/DMR); kualitas hanya diverifikasi lewat smoke test.
12. Churn desain: tiga runner dibuat lalu dihapus di A1, dan keputusan error-path persistence ditunda tiga kali (M2a, M2c, M2b) sebelum diputuskan di Sprint 3.

---

## 7. Sprint 3 — M4 Tool Registry + M5 Device Layer (ON PROGRESS)

### 7.1 Tujuan
Agent bisa menemukan tool yang dibutuhkan dari katalog yang bisa tumbuh (puluhan sampai ratusan tool per device) tanpa menyuntik semuanya ke prompt, dan bisa mengontrol perangkat lewat adapter. Paper: MCP-Zero, ScaleMCP, Tool-to-Agent Retrieval, EasyTool, ToolLLM, Enhancing IoT with LLM, HearthNet, Agentic IoT Survey, SAGE, Sasha.

### 7.2 Yang sudah dikerjakan (ringkas, detail di Lampiran C)
- **2026-09-10 → 09-11 — paper.** 7 PDF baru diverifikasi dan dibaca penuh; 2 paper salah folder dipindah.
- **2026-09-11 — M4 v1.** Kontrak 1.1.0 (`domain`, `examples` yang divalidasi ke `input_schema` dan ditampilkan ke LLM, `content_hash`). `ToolCatalog` (FTS5 in-memory; hit pada domain → semua tool domain itu; `sync(provider, tools)` berbasis hash ala ScaleMCP, validasi dulu baru mutasi). Meta-tool `find_tools` ala MCP-Zero; registry per turn dibaca ulang tiap iterasi. Hasil kosong → suruh jujur. 210 test.
- **2026-09-17 — M5 mock.** `MockHome` (lampu + AC, `diff()` ala benchmark SAGE, `fail_next` OFFLINE/LOST_ACK), `MockHomeAdapter.sync_into(catalog)` dengan 5 tool domain `home`. **Trace A2** 9 skenario ditulis sebagai *characterization test* (`test_a2_trace.py`). 238 test.
- **2026-10-23 — keputusan dan implementasi A2** (error-path persistence):
  1. Turn terputus setelah aksi disimpan dengan penanda `[Turn interrupted ...]`; teks "couldn't finish" saat iterasi habis disimpan.
  2. Adapter membaca ulang state setelah `DeviceError` (LOST_ACK terdeteksi sebagai sukses + `note`).
  3. Log aksi durable ditunda ke M11 → **celah S5 diketahui** (sesi gagal disimpan setelah lampu menyala = jejak hilang).
  4. Arsip gagal → `AgentResult.warnings`, tidak di-raise.
  5. Urutan tulis diubah jadi profil → sesi → arsip; profil gagal → sesi tetap disimpan dengan catatan koreksi.
  247 test.
- **2026-10-23 — TODO M4:** `AutoLoadPolicy` (`read_only` default / `all` / `never`) untuk tool katalog yang dipanggil tanpa dimuat; `tool_retention_turns` (default 3, hanya panggilan sukses) dihitung dari riwayat sesi tanpa state baru. 266 test.
- **2026-10-23 — CLI** `python -m backend.cli` + **smoke test API asli** 8/8 skenario sesuai desain (alur `find_tools` → aksi, retensi, auto-load read-only, LOST_ACK read-back, offline jujur, profil lintas sesi, "buatkan kopi" → jujur tidak bisa). Biaya: 18 panggilan, ±60,8 rb token input (±3,4 rb per panggilan). 280 test.
- **Keputusan user:** adapter device nyata dan pilihan gateway (Home Assistant / hibrida / buatan sendiri) **ditunda** ke versi berikutnya karena perangkat belum ada.

### 7.3 Sisa pekerjaan Sprint 3 (usulan, belum dikonfirmasi user)
1. Perbaikan kecil hasil smoke test: zona waktu lokal di `get_current_time`; instruksi blok profil (fakta profil = sumber utama, `recall_memory` untuk percakapan lama).
2. Antarmuka device generik (`list_devices` / `read_state` / `apply`) + kontrak Device di M0 + nama key state yang jelas (`target_temperature`).
3. State "pending" di mock (perangkat lambat seperti LoRa) → disambiguasi / bertanya balik (gerbang *Clarifying* ala Sasha) → koreksi catatan M0/M1/M2 (penutup sprint).

### 7.4 Kekurangan Sprint 3 (sampai saat ini)
1. **Belum ada perangkat nyata maupun antarmuka device generik.** Tool rumah ditulis khusus di `MockHomeAdapter`; adapter nyata nanti harus menulis ulang pola yang sama. Mock hanya 2 perangkat, sehingga disambiguasi ("lampu yang mana?") belum pernah teruji.
2. **Aksi fisik tanpa gerbang keamanan.** Aktuator `STANDARD`, langsung dijalankan. M11 baru di Sprint 4, padahal device control sudah ada di Sprint 3. Untuk lampu/AC risikonya kecil; untuk kunci pintu/kompor tidak.
3. **`AutoLoadPolicy` mempercayai `read_only_hint` yang dideklarasikan adapter sendiri.** Adapter yang salah/berbahaya bisa menandai aktuator sebagai read-only sehingga dimuat otomatis tanpa `find_tools`.
4. **Celah S5 (A2):** kalau penyimpanan sesi gagal setelah perangkat bergerak, tidak ada jejak aksi sama sekali sampai ada log aksi M11.
5. **Pencarian katalog bergantung kata kunci.** Smoke test berhasil karena model menulis query bahasa Inggris (`"turn on light"`); query bahasa Indonesia berimbuhan bisa meleset (lihat §6.4 no. 7). Skala katalog yang diuji hanya ±10 tool — klaim "siap ratusan tool" belum diuji.
6. **Nama key state ambigu** (`temperature` = suhu target, model menyebutnya "suhu terukur").
7. **Hasil tool tidak dikompresi** sebelum masuk konteks (ToolLLM) — akan jadi masalah dengan state perangkat nyata yang besar.
8. **Rumah simulasi reset tiap CLI dijalankan** sementara riwayat percakapan tersimpan. Disengaja sebagai uji "jangan percaya riwayat", tapi membingungkan saat dicoba manual.
9. **Smoke test hanya sekali, satu model (Haiku), 8 skenario.** Tidak ada pengulangan untuk melihat variasi perilaku, tidak ada metrik *tool correctness* terpisah dari *task completion* (ScaleMCP), belum dinilai dengan 7 mode kegagalan Sasha.
10. **Biaya per panggilan ±3,4 rb token input** dan tidak memakai prompt caching (lihat §9.8).
11. **Gaya bahasa model tidak konsisten** (campur "Anda"/"kamu", emoji) dan model menjanjikan perilaku proaktif yang belum ada ("nanti saya sesuaikan") — rumahnya M15/M17, tapi sampai saat itu ini klaim berlebihan.
12. **Masalah proses di Sprint 3:** ada jeda ±5 minggu (17 Sep → 23 Okt); hasil satu sesi (2026-09-11 lanjutan: koreksi catatan, smoke test, tabel trace A2) **hilang karena tidak sempat ditulis ke file** dan harus disusun ulang. Sprint juga menampung pekerjaan Sprint 2 (A2) sehingga batas sprint kabur.

---

## 8. Kekurangan lintas sprint (proses dan arsitektur)

1. **Urutan roadmap.** Keamanan (Sprint 4) datang *setelah* kontrol perangkat (Sprint 3); planner (M3, Sprint 6) datang setelah tugas multi-langkah sudah muncul; **evaluasi (M16) baru di Sprint 12**, padahal tanpa evaluasi sejak awal setiap keputusan "sudah cukup baik" tidak terukur.
2. **Ketergantungan cloud vs tujuan privasi.** Semua percakapan, profil, dan arsip dikirim ke API Anthropic sampai Sprint 8. Belum ada keputusan data apa yang boleh keluar mesin.
3. **Satu proses, satu pengguna, sinkron.** Tidak ada server/daemon, tidak ada antrean; suara (Sprint 5) dan perilaku proaktif (Sprint 11) akan butuh proses yang selalu jalan dan akses bersamaan ke store.
4. **Tidak ada observability.** Tidak ada log terstruktur, tidak ada pencatatan biaya/latensi per turn (biaya smoke test dihitung manual), tidak ada CI.
5. **System prompt berbahasa Inggris, pemakai berbahasa Indonesia;** persona (M15) folder kosong.
6. **Overhead dokumentasi tinggi.** Log tiga sprint ±145 KB, `PAPER_NOTES.md` ±190 KB. Membantu kesinambungan antar sesi, tapi catatan modul tetap sempat basi dan satu sesi kerja sempat hilang — artinya proses dokumentasi belum menjamin konsistensi.
7. **Hampir semua kode ditulis oleh asisten AI** dengan review pemilik; risiko desain yang "terlihat rapi" tapi belum teruji di dunia nyata cukup besar. Reviewer diminta skeptis.

---

## 9. Kode yang perlu disesuaikan dan dimintai feedback

Potongan di bawah disalin dari kode di commit `94c24b2`. Setiap bagian berisi **masalah/keraguan** dan **pertanyaan** spesifik.

### 9.1 Loop agent dan eksekusi tool — `backend/agent_core/loop.py:69` dan `:94`

```python
def _execute_tool_call(call: ToolCallRequest, registry: ToolRegistry) -> tuple[str, bool]:
    """Run one tool call. Returns (tool_result_content, is_error) — never raises."""
    try:
        registered = registry.resolve(call.name)
    except ToolNotLoadedError as exc:
        return str(exc), True
    except KeyError as exc:
        return f"Tool '{call.name}' is not registered: {exc}", True

    try:
        jsonschema.validate(call.arguments, registered.contract.input_schema)
    except jsonschema.ValidationError as exc:
        return (
            f"Invalid arguments for tool '{call.name}': {exc.message}. "
            "Fix the arguments and try again."
        ), True

    try:
        result = registered.fn(**call.arguments)
    except Exception as exc:  # tool failures become reflections, not crashes
        return f"Tool '{call.name}' failed: {exc}", True

    return (result if isinstance(result, str) else json.dumps(result)), False
```

```python
    for iteration in range(1, max_iterations + 1):
        tools = registry.to_llm_tools()
        llm_input = session.to_llm_messages() if session is not None else messages
        effective_system = system
        if profile is not None:
            block = profile.to_context_block()
            if block:
                effective_system = f"{system}\n\n{block}"
        response = llm.send(messages=llm_input, tools=tools, system=effective_system)
        if session is not None:
            session.record_usage(response)

        messages.append(_assistant_message(response))

        if not response.tool_calls:
            return AgentResult(text=response.text or "", iterations=iteration)

        tool_results = []
        for call in response.tool_calls:
            content, is_error = _execute_tool_call(call, registry)
            tool_results.append({... "content": content, "is_error": is_error})
        messages.append({"role": "user", "content": tool_results})
```

**Masalah / keraguan:**
- Tidak ada titik untuk izin (M11) di antara validasi dan eksekusi; semua tool dijalankan langsung.
- Hasil tool di-`json.dumps` utuh tanpa batas ukuran (risiko konteks meledak; kompaksi hanya di awal turn).
- Pesan exception tool dikirim verbatim ke LLM (bisa membocorkan detail internal/kredensial dari adapter nyata nanti).
- Beberapa tool_use dalam satu respons dijalankan berurutan tanpa memperhatikan ketergantungan atau aksi yang saling bertentangan.
- `max_iterations=6` tetap dan `find_tools` memakan satu iterasi.

**Pertanyaan:** Di mana sebaiknya gerbang izin M11 dipasang (di `_execute_tool_call`, di `ToolRegistry.resolve`, atau pembungkus `fn` per tool)? Bagaimana batas ukuran hasil tool yang masuk akal? Apakah `max_iterations` sebaiknya berbasis anggaran token/biaya, bukan jumlah langkah?

### 9.2 Orchestrator dan urutan tulis (A2) — `backend/orchestrator/orchestrator.py:162` dan `:220`

```python
        try:
            result = run_agent(user_input, self._turn_registry(profile, session), self.llm,
                               max_iterations=self.max_iterations, system=self.system,
                               session=session, profile=profile)
        except Exception as exc:
            if session.messages:
                if session.messages[-1]["role"] == "user":
                    _append_assistant_note(session, _interrupted_note(exc))
                try:
                    self._persist(session, profile)
                except Exception as save_exc:
                    exc.add_note(f"Saving the interrupted turn also failed: {save_exc!r}")
            raise

        result.warnings.extend(self._persist(session, profile))
        return result

    def _persist(self, session: Session, profile: Profile) -> list[str]:
        if profile.dirty:
            try:
                self.profile_store.save(profile)
            except Exception as exc:
                _append_assistant_note(session, _profile_not_saved_note(exc))
                try:
                    self.session_store.save(session)
                except Exception as save_exc:
                    exc.add_note(f"Saving the session afterwards also failed: {save_exc!r}")
                raise
        self.session_store.save(session)
        try:
            self.archive_store.ingest(session)
        except Exception as exc:
            logger.warning("archive ingest failed for session %s: %r", session.session_id, exc)
            return [f"archive not updated: {exc!r} (will retry on the next turn)"]
        return []
```

**Masalah / keraguan:**
- Tiga store terpisah (2 file JSON + 1 SQLite) tanpa transaksi bersama; konsistensi dijaga dengan urutan tulis dan catatan koreksi. Celah S5 (sesi gagal disimpan setelah aksi fisik) masih terbuka.
- Deteksi "turn terputus" bergantung pada invarian "turn yang tersimpan selalu diakhiri pesan assistant".
- Penanda/koreksi ditempel sebagai teks ke pesan assistant terakhir — model membacanya sebagai ucapannya sendiri.
- `except Exception` lebar; `KeyboardInterrupt` (Ctrl+C di tengah aksi) tidak menyimpan turn parsial.

**Pertanyaan:** Apakah lebih baik semua store dipindah ke satu SQLite dengan satu transaksi per turn (sesi + profil + arsip + log aksi)? Apakah pendekatan "catatan koreksi dalam teks" wajar, atau sebaiknya pakai struktur/flag di skema sesi?

### 9.3 Kompaksi — `backend/memory/compaction.py:78`

```python
def compact(session: Session, llm: LLMClient, keep_recent_messages: int = 6) -> bool:
    cut = _find_safe_cut_index(session.messages, keep_recent_messages)
    if cut is None:
        return False

    to_summarize = session.messages[:cut]
    remaining = session.messages[cut:]

    response = llm.send(
        messages=_build_summarization_messages(session.summary, to_summarize),
        tools=[],
        system=SUMMARIZATION_SYSTEM_PROMPT,
    )

    session.summary = response.text or session.summary
    session.archived_turns.extend(to_summarize)  # M2b hook — not read/pruned by M2a
    session.messages = remaining
    session.compaction_count += 1
    return True
```

**Masalah yang kami temukan saat menyusun dokumen ini:** kalau `response.text` kosong, ringkasan lama dipertahankan **tetapi** `to_summarize` tetap dipindahkan keluar dari `messages`. Isi percakapan itu hilang dari konteks aktif tanpa peringatan (masih ada di arsip, tapi hanya terjangkau lewat `recall_memory`). Ini bertentangan dengan prinsip "fail loud". Kandidat perbaikan: anggap respons kosong sebagai kegagalan (`return False` atau raise).

**Keraguan lain:** ringkasan dibuat oleh model yang sama (Haiku) tanpa verifikasi; `_find_safe_cut_index` hanya memotong di pesan user berupa teks, sehingga satu rantai tool yang panjang tidak pernah bisa dikompaksi; ambang 6000/500/6 tebakan.

**Pertanyaan:** Bagaimana cara murah memverifikasi bahwa ringkasan tidak menambah fakta baru? Apakah strategi "kompaksi hanya di awal turn" bisa dipertahankan, atau perlu pemangkasan hasil tool lama di tengah turn?

### 9.4 Blok profil di system prompt — `backend/memory/profile.py:123`

```python
    def to_context_block(self) -> str:
        active = self.active_facts()
        if not active:
            return ""
        lines = [f"- [{f.id}] ({f.category}) {f.text}" for f in active]
        return (
            "Known facts about the user (from earlier conversations — cite "
            "the id in brackets if you need to supersede or forget one):\n"
            + "\n".join(lines)
        )
```

**Masalah / keraguan:** tidak ada batas jumlah fakta; tidak ada urutan prioritas; instruksi tidak menjelaskan bahwa profil adalah sumber utama sehingga model malah memanggil `recall_memory` (temuan smoke test); system prompt berubah setiap kali fakta berubah (mengganggu prompt caching).

**Pertanyaan:** Bagaimana bentuk instruksi yang baik untuk membedakan "fakta profil" vs "kutipan arsip"? Kapan profil harus dibatasi/diseleksi (retrieval atas profil) alih-alih ditempel semua?

### 9.5 Tokenizer pencarian (arsip M2b dan katalog M4) — `backend/dal/fts.py:16`

```python
TOKENIZER = "unicode61 remove_diacritics 2"
TOKEN_PATTERN = re.compile(r"[^\W_]+")

def fts_query(query_tokens: list[str], operator: str) -> str:
    quoted = ['"' + token.replace('"', '""') + '"' for token in query_tokens]
    return operator.join(quoted)
```

Dipakai di `ToolCatalog.search` (`backend/registry/catalog.py:246`): coba semua kata (AND), kalau kosong coba OR.

**Masalah / keraguan:** tidak ada stemming atau pencocokan awalan, jadi imbuhan bahasa Indonesia (me-/-kan/-nya/di-) membuat pencarian meleset. Opsi yang dipertimbangkan: prefix `*`, tokenizer `trigram` (tersedia di SQLite venv), stemmer Indonesia sederhana sebelum indexing, atau embedding lokal kecil.

**Pertanyaan:** Untuk korpus kecil (puluhan tool, ribuan turn) berbahasa campur Indonesia–Inggris, mana pilihan dengan rasio manfaat/kompleksitas terbaik?

### 9.6 Auto-load tool katalog — `backend/registry/discovery_tool.py:219`

```python
    def resolve(name: str) -> RegisteredTool | None:
        if not catalog.has(name):
            return None
        contract = catalog.get(name).contract
        read_only = contract.annotations.read_only_hint
        if policy is AutoLoadPolicy.ALL or (policy is AutoLoadPolicy.READ_ONLY and read_only):
            entry = catalog.get(name)
            turn_registry.bind(entry.contract, entry.fn)
            return turn_registry.get(name)
        reason = "" if read_only else " It is not read-only, so it is never loaded automatically."
        raise ToolNotLoadedError(
            f"Tool '{name}' exists in the catalog but is not loaded in this turn.{reason} "
            f"Load it first with {FIND_TOOLS_NAME} (e.g. query: '{name.replace('_', ' ')}'), "
            "read its description, then call it."
        )
```

**Masalah / keraguan:** keputusan keamanan bergantung pada `read_only_hint` yang dideklarasikan penyedia tool sendiri (MCP sendiri menyebut annotation sebagai *hint*, bukan jaminan). "Model harus lewat `find_tools` dulu" adalah gerbang yang lemah, karena model bisa memanggil `find_tools` lalu langsung aksi tanpa user tahu.

**Pertanyaan:** Apakah pembedaan read-only vs aktuator sebaiknya ditentukan oleh pihak yang dipercaya (allowlist per provider / M11), bukan oleh kontrak? Apakah gerbang `find_tools` ini memberi nilai nyata atau hanya menambah langkah?

### 9.7 Retensi tool lintas turn — `backend/registry/retention.py:24`

```python
def recently_used_tool_names(messages: list[dict[str, Any]], turns: int | None) -> list[str]:
    if turns is not None and turns <= 0:
        return []
    succeeded = {
        block["tool_use_id"]
        for m in messages
        if m["role"] == "user" and isinstance(m["content"], list)
        for block in m["content"]
        if block.get("type") == "tool_result" and not block.get("is_error")
    }
    names: list[str] = []
    seen_turns = 0
    for message in reversed(messages):
        if message["role"] == "user" and isinstance(message["content"], str):
            seen_turns += 1
            if turns is not None and seen_turns >= turns:
                break
            continue
        if message["role"] != "assistant" or not isinstance(message["content"], list):
            continue
        for block in message["content"]:
            if (block.get("type") == "tool_use" and block.get("id") in succeeded
                    and block["name"] not in names):
                names.append(block["name"])
    return names
```

**Masalah / keraguan:** logika bergantung pada bentuk pesan Anthropic (konsisten dengan §5.4 no. 1); hanya membaca `session.messages`, jadi turn yang sudah dikompaksi tidak dihitung; tool yang gagal karena perangkat offline tidak dipertahankan (sengaja), sehingga model harus mencari ulang tepat saat sedang ada masalah.

**Pertanyaan:** Apakah retensi berbasis riwayat ini lebih baik daripada state eksplisit (daftar tool aktif yang disimpan di sesi)?

### 9.8 Pemanggilan LLM tanpa prompt caching — `backend/agent_core/llm_client.py`

Tidak ada `cache_control` di seluruh `backend/`. Setiap iterasi mengirim ulang system prompt + blok profil + definisi tool + riwayat. Smoke test: ±3,4 rb token input per panggilan, 18 panggilan untuk 12 baris input. Daftar tool juga berubah di tengah turn (setelah `find_tools`), yang memecah prefix cache.

**Pertanyaan:** Bagaimana menyusun urutan (tool stabil → system → profil → riwayat) supaya cache efektif walau tool dimuat dinamis? Apakah `find_tools` dinamis justru lebih mahal daripada memasang semua tool sekaligus ketika katalog masih kecil?

### 9.9 Adapter device dan read-back — `backend/devices/mock_home.py:199`

```python
    def _command(self, device_id: str, **changes: Any) -> dict[str, Any]:
        try:
            return {"device_id": device_id, "state": self.home.apply(device_id, **changes)}
        except DeviceError as exc:
            try:
                actual = self.home.read_state(device_id)
            except DeviceError:
                raise DeviceError(f"{exc}. Read-back failed too; actual state unknown.") from exc
            if all(actual.get(k) == v for k, v in changes.items()):
                return {"device_id": device_id, "state": actual,
                        "note": f"{exc}, but reading the state back shows the change took effect."}
            raise DeviceError(f"{exc}. Actual state read back: {actual}") from exc
```

Tool AC: `ac_set_temperature(device_id, temperature)` memanggil `self._command(device_id, on=True, temperature=temperature)`; state AC disimpan sebagai `{"on": ..., "temperature": 24}`.

**Masalah / keraguan:** read-back langsung setelah error tidak cocok untuk perangkat lambat (LoRa kelas A, Zigbee yang lambat melapor) → perlu state "pending"; perbandingan `==` tidak cocok untuk nilai analog (brightness/suhu yang dibulatkan perangkat); key `temperature` ambigu (target vs terukur); pola ini ada di adapter mock, belum di antarmuka generik yang wajib diikuti adapter nyata.

**Pertanyaan:** Bagaimana bentuk antarmuka device generik dan kontrak Device yang baik (`read_state`/`apply`/`pending`, `desired` vs `reported` seperti device shadow)? Apakah tool per jenis aksi (`home_set_power`, `lamp_set_brightness`, …) lebih baik daripada satu tool generik `device_apply(device_id, changes)`?

### 9.10 Waktu — `backend/agent_core/tools/time_tool.py:21` dan `:42`

```python
    description="Get the current date and time in UTC, ISO 8601 format.",
...
def get_current_time() -> dict[str, Any]:
    return {"iso_datetime": datetime.now(timezone.utc).isoformat()}
```

**Masalah:** model menjawab dalam UTC. Rencana: zona waktu dari config (`.env`, mis. `Asia/Jakarta`) atau dari OS, kembalikan waktu lokal + offset + nama zona.

**Pertanyaan:** Zona waktu lebih tepat disimpan di config atau sebagai fakta profil (berubah saat user bepergian)?

---

## 10. Pertanyaan untuk reviewer

Mohon jawab sebanyak yang relevan; prioritas tertinggi di atas.

1. **Urutan roadmap:** apakah M11 (keamanan) dan M16 (evaluasi) seharusnya dimajukan? Kalau ya, versi minimal apa yang perlu dibuat sekarang?
2. **Arsitektur penyimpanan:** tiga store terpisah (JSON sesi, JSON profil, SQLite arsip) + urutan tulis + catatan koreksi, atau satu SQLite dengan transaksi per turn?
3. **Portabilitas ke model lokal (Sprint 8):** apa yang harus diubah sekarang supaya format pesan tidak terikat Anthropic? Seberapa realistis model open-weight lokal menjalankan alur `find_tools` + tool calling ini?
4. **Retrieval berbahasa Indonesia:** FTS5 + stemming/trigram, atau embedding lokal kecil? (katalog tool dan arsip percakapan)
5. **Memori:** apakah pemisahan sesi / profil / arsip sudah tepat? Apa yang kurang dibanding Mem0/Zep/MemGPT untuk asisten personal satu pengguna?
6. **Keamanan aksi fisik:** desain izin seperti apa untuk agent rumah (konfirmasi, lease ala HearthNet, allowlist, batas waktu)? Bagaimana menangani prompt injection lewat arsip dan hasil tool?
7. **Antarmuka device generik:** bentuk kontrak Device dan tool yang direkomendasikan (lihat §9.9).
8. **Evaluasi:** benchmark kecil apa yang bisa dibuat sekarang tanpa hardware (mis. skenario ala SAGE + 7 mode kegagalan Sasha), dan metrik apa yang wajib dicatat?
9. **Biaya:** strategi prompt caching / pemilihan model / ukuran konteks yang sesuai untuk pola tool dinamis ini.
10. **Proses:** apakah cara kerja (riset paper dulu, plan mode, log append-only, test dengan LLM palsu + smoke test manual) efisien untuk proyek satu orang? Apa yang sebaiknya dipangkas atau ditambah?
11. **Bug atau celah** yang Anda lihat di kode §9 atau di log lampiran yang belum kami sebut.

---

> **Catatan lampiran.** Lampiran A–C adalah salinan apa adanya dari `Memory Think/SPRINT1_LOG.md`, `SPRINT2_LOG.md`, dan `SPRINT3_LOG.md` per commit `94c24b2`. Satu-satunya perubahan: level heading diturunkan dua tingkat supaya struktur dokumen ini tetap rapi. Isi tidak disunting, jadi beberapa TODO di dalamnya sudah basi; entry yang lebih baru di log yang sama mengoreksinya (konvensi append-only).


---

## Lampiran A — Log Sprint 1 (lengkap)

> Sumber: `Memory Think/SPRINT1_LOG.md`

### Sprint 1 — Log Pengerjaan (M0 Contract Layer + M1 Agent Core)

> Datasheet pengerjaan Sprint 1. Setiap kali ada update fitur/logika (kode, schema, struktur), tambahkan entry baru di bawah — jangan edit entry lama, supaya riwayat tetap utuh dan tidak ambigu soal apa yang sudah dikerjakan.
>
> Selain kode, **diskusi/pembahasan penting** (pertanyaan konsep, keputusan arsitektur yang muncul dari obrolan, penjelasan yang mengubah pemahaman) juga dicatat di sini sebagai entry tersendiri — supaya ada jejak "kenapa" di balik keputusan, bukan cuma "apa" yang berubah di kode.

#### Format Entry

```
## [YYYY-MM-DD] Judul singkat

- **Apa yang dikerjakan:** ...
- **File yang dibuat/diubah:** ...
- **Alasan/keputusan:** ... (kalau ada keputusan desain yang perlu diingat)
- **Belum dikerjakan / TODO lanjutan:** ...
```

---

#### [2026-08-06] Setup environment awal

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

#### [2026-08-06] Riset paper Sprint 1 & seluruh roadmap

- **Apa yang dikerjakan:** Membaca dan meringkas ~96 paper/jurnal di `Paper & Journal/F.R.I.D.A.Y/` (bukan cuma yang wajib untuk Sprint 1, tapi seluruh koleksi lintas 12 sprint atas permintaan user), disusun jadi satu file referensi.
- **File yang dibuat/diubah:**
  - `Memory Think/PAPER_NOTES.md` — catatan per paper (kategori, sprint terkait, ide inti, relevansi ke F.R.I.D.A.Y, sumber informasi), plus tabel "File Bermasalah" untuk file yang isinya tidak cocok dengan nama filenya.
- **Alasan/keputusan:** File catatan paper ditaruh di `Memory Think/`, bukan di dalam `Paper & Journal/`, supaya folder paper tetap murni data (PDF) dan tidak tercampur catatan olahan — sama alasannya kenapa log ini juga dipindah ke sini.
- **Belum dikerjakan / TODO lanjutan:**
  - 5 file paper perlu dicari ulang (isinya salah/tertukar), terutama untuk kategori Proactive (#14) dan Persona (#15) yang jadi belum lengkap
  - 4 paper soal jailbreak/sandbox-escape belum dibaca (memicu safety filter otomatis berulang) — perlu ditinjau manual oleh user
  - Detail lengkap ada di `Memory Think/PAPER_NOTES.md`

#### [2026-08-07] M0 Contract Layer — Tool Contract schema

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

#### [2026-08-07] Diskusi: verifikasi test M0 + konsep "tool vs pengetahuan umum" + catatan per-modul

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

#### [2026-08-07] Penegasan aturan: log setiap instruksi, bukan cuma kode

- **Apa yang dikerjakan:** User menegaskan aturan standing untuk proyek ini: **setiap kali user menyuruh sesuatu**, entry baru harus ditambahkan ke `SPRINT1_LOG.md` — bukan cuma saat kode berubah, tapi juga diskusi/pertanyaan/keputusan. Ini penguatan dari entry sebelumnya ("Diskusi: verifikasi test M0..."), sekarang eksplisit dijadikan default tanpa perlu diminta ulang tiap kali.
- **File yang dibuat/diubah:**
  - `SPRINT1_LOG.md` — entry ini.
  - Memory eksternal (`friday_progress_tracking.md` di sistem memori Claude, bukan bagian dari repo ini) — diupdate supaya aturan ini terbawa otomatis ke sesi-sesi berikutnya, tidak perlu user ulang instruksi ini lagi.
- **Alasan/keputusan:** Tujuannya dua arah — (1) jadi data rujukan/"training" buat asisten supaya nggak salah asumsi soal apa yang sudah dibahas, (2) jadi pengingat buat user sendiri biar nggak lupa progres/keputusan yang sudah diambil.
- **Belum dikerjakan / TODO lanjutan:** Tidak ada perubahan teknis — murni penegasan konvensi kerja. TODO teknis sebelumnya (`.env`, commit git M0, mulai coding M1) masih berlaku.

#### [2026-08-07] Commit pertama M0 Contract Layer

- **Apa yang dikerjakan:** Semua hasil kerja M0 (schema, test, catatan modul, update log) di-stage dan di-commit ke git lokal dengan pesan `feat(m0): add ToolContract schema for tool manifest`.
- **File yang dibuat/diubah:** 10 file masuk commit `46c7be7` — `backend/__init__.py`, `backend/schemas/__init__.py`, `backend/schemas/tool_contract.py`, `backend/schemas/versioning.py`, `backend/tests/__init__.py`, `backend/tests/test_tool_contract.py`, `Memory Think/M0_contract_layer.md`, `Memory Think/M1_agent_core.md`, `Memory Think/SPRINT1_LOG.md`, `requirements.txt`. File `backend/schemas/.gitkeep` terhapus (tergantikan isi asli).
- **Alasan/keputusan:** Commit dipisah per unit kerja logis (M0 selesai = satu commit), bukan digabung sekaligus sama commit besar berikutnya — supaya riwayat git gampang ditelusuri per modul.
- **Belum dikerjakan / TODO lanjutan:**
  - Commit ini **belum di-push** ke `origin/master` — masih 1 commit ahead secara lokal, menunggu instruksi push.
  - `.env`/`.env.example` untuk API key LLM masih belum ada.
  - M1 (agent loop ReAct) belum mulai coding.

#### [2026-08-07] Push commit M0 + diskusi biaya LLM & keputusan cloud-dulu-lokal-nanti

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

#### [2026-08-12] Rombak struktur folder paper jadi per-modul (M0–M17)

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

#### [2026-08-12] Audit & update PAPER_NOTES.md — 9 paper baru M11/M17 dibaca, ketemu `pdftotext` tersedia

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

#### [2026-08-12] Eksekusi 2 rekomendasi: upgrade 12 entry "Pengetahuan umum" + baca 4 paper DILEWATI

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

#### [2026-08-13] Verifikasi & perbaikan file paper pengganti (M7/M14/M15/M17) — 3 berhasil, 1 ternyata duplikat bukan paper baru

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

#### [2026-08-13] M1 Agent Core — implementasi awal loop ReAct

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

#### [2026-08-13] Verifikasi smoke test manual M1 dengan API key asli

- **Apa yang dikerjakan:** User mengisi `ANTHROPIC_API_KEY` asli di `.env` (dibuat dari Anthropic Console, key baru). Dijelaskan alur pengambilan key (console.anthropic.com → Settings → API Keys → Create Key) dan bagaimana key itu mengalir ke kode (`.env` → `config.py` baca via `load_dotenv()` → `AnthropicLLMClient` pakai buat inisialisasi SDK `anthropic`). Setelah key terisi, dijalankan smoke test manual: `run_agent("jam berapa sekarang?", registry, get_llm_client("anthropic"))` dengan tool `get_current_time` terdaftar.
- **Hasil:** **Berhasil** — API call asli ke `claude-haiku-4-5` sukses, model manggil tool `get_current_time` di iterasi 1, jawab final pakai hasilnya di iterasi 2 ("Waktu sekarang adalah 08:42:06 UTC, Kamis 13 Agustus 2026"). `exceeded_max_iterations=False`. Ini pertama kalinya loop M1 diverifikasi jalan end-to-end lewat API asli, bukan cuma lulus test dengan `FakeLLMClient`.
- **File yang dibuat/diubah:**
  - `.env` — `ANTHROPIC_API_KEY` diisi user (tidak masuk git, sudah di-`.gitignore`).
  - `Memory Think/M1_agent_core.md` — tambah catatan "Verifikasi nyata", hapus item TODO smoke test (sudah selesai).
  - `Memory Think/SPRINT1_LOG.md` — entry ini.
- **Alasan/keputusan:** Tidak menampilkan isi API key asli di percakapan/log manapun — cukup konfirmasi baris `ANTHROPIC_API_KEY=` terisi via `grep -c`, bukan `cat` isi filenya, supaya key tidak pernah muncul di transcript.
- **Belum dikerjakan / TODO lanjutan:** Sama seperti entry sebelumnya (provider OpenAI, tool IoT/OS nyata, Reflexion persisten M2) — commit/push sesi ini masih menunggu instruksi user.

#### [2026-08-13] Commit & push paper fixes M7/M14/M15/M17; cari & verifikasi 3 paper pengganti terakhir

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

#### [2026-08-13] Penutup hari: rekap status commit/push + koreksi 2 TODO basi

- **Apa yang dikerjakan:** User tanya apakah seluruh hasil kerja hari ini sudah tercatat. Dicek ulang urutan kronologis vs urutan entry di file ini (`grep` commit hash) — ketemu **2 baris TODO yang sudah basi**: entry "M1 Agent Core" (di atas, TODO poin terakhir) dan entry "Commit & push paper fixes..." (TODO di atasnya) sama-sama bilang "belum di-commit/push", padahal keduanya **sudah** di-push di turn-turn setelahnya. Entry lama sengaja tidak diedit langsung (konvensi append-only project ini — riwayat harus tetap utuh), jadi dikoreksi lewat entry penutup ini.
- **Rekap status commit/push hari ini (2026-08-13), urut kronologis nyata:**
  1. `0c05301` — fix M7/M14/M15/M17 mismatch pertama (dicatat entry "Verifikasi & perbaikan file paper pengganti..." di atas)
  2. `552496e` — fix 3 mismatch terakhir + migrasi folder 100% (dicatat entry "Commit & push paper fixes..." di atas — TODO "belum di-commit"-nya sudah tidak berlaku, sudah di-push sebagai commit ini)
  3. `f12d10a` — implementasi M1 Agent Core lengkap (dicatat entry "M1 Agent Core — implementasi awal loop ReAct" di atas — TODO "belum di-commit/push"-nya juga sudah tidak berlaku, sudah di-push sebagai commit ini)
- **File yang dibuat/diubah:** `Memory Think/SPRINT1_LOG.md` — entry ini saja (tidak ada perubahan kode/paper baru).
- **Alasan/keputusan:** Catatan chronological order di file ini sempat tidak pas dengan urutan waktu tulis sebenarnya (entry "Commit & push paper fixes..." ditulis sebelum entry M1, tapi posisinya di file muncul setelah) — bukan salah data, cuma urutan append yang meleset satu langkah. Diputuskan tidak reorder entry lama (berisiko dianggap mengubah riwayat), cukup diberi rekap eksplisit di sini supaya pembaca berikutnya tidak salah asumsi urutan kejadian.
- **Belum dikerjakan / TODO lanjutan:** Tidak ada tambahan baru — semua pekerjaan hari ini (paper fixes 2x commit + M1 implementation) sudah ter-push ke `origin/master`. Next step: mulai Sprint 2 (M2 Memory) atau perkuat M1 (tool IoT/OS nyata nunggu M4/M5, Reflexion persisten nunggu M2) — keputusan di tangan user.

---

## Lampiran B — Log Sprint 2 (lengkap)

> Sumber: `Memory Think/SPRINT2_LOG.md`

### Sprint 2 — Log Pengerjaan (M2 Memory System)

> Datasheet pengerjaan Sprint 2. Setiap kali ada update fitur/logika (kode, schema, struktur), tambahkan entry baru di bawah — jangan edit entry lama, supaya riwayat tetap utuh dan tidak ambigu soal apa yang sudah dikerjakan.
>
> Selain kode, **diskusi/pembahasan penting** (pertanyaan konsep, keputusan arsitektur yang muncul dari obrolan, penjelasan yang mengubah pemahaman) juga dicatat di sini sebagai entry tersendiri — supaya ada jejak "kenapa" di balik keputusan, bukan cuma "apa" yang berubah di kode.

#### Format Entry

```
## [YYYY-MM-DD] Judul singkat

- **Apa yang dikerjakan:** ...
- **File yang dibuat/diubah:** ...
- **Alasan/keputusan:** ... (kalau ada keputusan desain yang perlu diingat)
- **Belum dikerjakan / TODO lanjutan:** ...
```

---

#### [2026-08-13] Setup log Sprint 2

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

#### [2026-08-13] Penegasan aturan: log setiap instruksi, bukan cuma kode

- **Apa yang dikerjakan:** User minta aturan standing yang sama seperti di Sprint 1 (lihat `SPRINT1_LOG.md`, entry "[2026-08-07] Penegasan aturan...") ditulis eksplisit juga di file log Sprint 2 ini — **setiap kali user menyuruh sesuatu**, entry baru ditambahkan ke `SPRINT2_LOG.md`, bukan cuma saat kode berubah, tapi juga diskusi/pertanyaan/keputusan konsep. Ini bukan aturan baru, cuma ditegaskan ulang supaya berlaku jelas per-file, tidak diasumsikan otomatis "nempel" dari Sprint 1.
- **File yang dibuat/diubah:**
  - `Memory Think/SPRINT2_LOG.md` — entry ini.
- **Alasan/keputusan:** Sama seperti alasan aslinya di Sprint 1 — jadi rujukan/"training" biar asisten nggak salah asumsi soal apa yang sudah dibahas, dan pengingat buat user sendiri biar nggak lupa progres/keputusan yang sudah diambil. Konvensi ini sudah tercatat juga di memori eksternal (`friday_progress_tracking.md`), tapi user tetap minta ditulis eksplisit di file log tiap sprint supaya jelas dari sisi dokumen proyek sendiri, tidak bergantung ke memori asisten di luar repo.
- **Belum dikerjakan / TODO lanjutan:** Tidak ada perubahan teknis — murni penegasan konvensi kerja, sama seperti TODO entry sebelumnya (desain/implementasi M2 belum mulai).

#### [2026-08-14] Audit kecukupan paper M2 + verifikasi & perbaikan 10 file baru

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

#### [2026-08-14] M2a — desain arsitektur + implementasi lengkap short-term/active-context memory

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

#### [2026-08-14] Review arsitektur M2a sebelum commit — validasi terhadap prinsip "context ≠ memory"

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

#### [2026-08-14] Robustness pass final — persistence integrity, schema evolution, error behavior, security boundary

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

#### [2026-08-18] M2c — desain arsitektur + implementasi lengkap profile memory

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

#### [2026-09-04] Commit + push M2c

- **Apa yang dikerjakan:** User minta commit & push hasil implementasi M2c. Test suite dijalankan ulang sebelum commit (`python -m pytest backend/tests/ -q` → 97 passed, 2 skipped). Semua 21 file M2c (5 modul baru + 6 file test baru + `profile/.gitkeep` + perubahan additive di `loop.py`/`runner.py`/`tool_registry.py`/`__init__.py` + `.gitignore` + `M2_memory.md` + `SPRINT2_LOG.md`) di-stage dan di-commit sebagai `643fd2d` (`feat(m2c): implement profile memory (long-term user facts)`), lalu di-push ke `origin/master` (`d6611c6..643fd2d`).
- **File yang dibuat/diubah:** `Memory Think/SPRINT2_LOG.md` — entry ini. (Sisanya = isi commit `643fd2d`, sudah didetailkan di entry `[2026-08-18]`.)
- **Alasan/keputusan:** TODO "belum di-commit/push" dari entry `[2026-08-18]` sekarang **selesai** — M2c sudah ada di remote.
- **Belum dikerjakan / TODO lanjutan:** Sama seperti entry `[2026-08-18]` minus item commit/push: decay otomatis (v2), M2b belum mulai, error-path persistence lintas store, revisit `permission_tier` di M11.

#### [2026-09-09] Rekap posisi + verifikasi 6 paper baru M2b

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

#### [2026-09-09] M2b — desain arsitektur + implementasi lengkap long-term cross-session recall

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

#### [2026-09-09] Commit + push M2b (2 commit) + diskusi arah M2 v2

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

#### [2026-09-09] Sesi ditutup — user pulang kerja, lanjut nanti dari diskusi M2 v2

- **Apa yang dikerjakan:** User minta dicatat bahwa sesi berhenti di sini (pulang dari tempat kerja). Instruksi eksplisit: saat dia tanya lagi soal M2 v2, asisten balas dengan jawaban prioritas A/B/C/D dari entry sebelumnya, lalu **tanyakan mau mulai dari mana** — user menyebut "A1, A2 dan A3"; opsi yang ditawarkan asisten adalah A1 (satu entry point), A2 (keputusan error-path persistence), atau langsung Sprint 3 — perlu dikonfirmasi apakah "A3" = Sprint 3. Dicatat juga di memori persisten asisten (`friday_m2_v2_next_step.md`) supaya tidak bergantung pada file ini saja.
- **File yang dibuat/diubah:** `Memory Think/SPRINT2_LOG.md` — entry ini.
- **Alasan/keputusan:** Tidak ada keputusan teknis — murni checkpoint supaya sesi berikutnya lanjut persis dari titik ini tanpa mengulang diskusi.
- **Belum dikerjakan / TODO lanjutan:** Entry ini **belum di-commit** (menunggu instruksi user, sesuai aturan standing). Sesi berikutnya: rekap + pilih A1 / A2 / Sprint 3.

#### [2026-09-09] M2 v2 A1 — satu entry point (`backend/orchestrator/`)

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

#### [2026-09-09] Commit + push A1 + rekomendasi langkah berikutnya

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

---

## Lampiran C — Log Sprint 3 (lengkap, on progress)

> Sumber: `Memory Think/SPRINT3_LOG.md`

### Sprint 3 — Log Pengerjaan (M4 Tool Registry + M5 Device Abstraction Layer)

> Datasheet pengerjaan Sprint 3. Setiap kali ada update fitur/logika (kode, schema, struktur), tambahkan entry baru di bawah — jangan edit entry lama, supaya riwayat tetap utuh dan tidak ambigu soal apa yang sudah dikerjakan.
>
> Selain kode, **diskusi/pembahasan penting** (pertanyaan konsep, keputusan arsitektur yang muncul dari obrolan, penjelasan yang mengubah pemahaman) juga dicatat di sini sebagai entry tersendiri — supaya ada jejak "kenapa" di balik keputusan, bukan cuma "apa" yang berubah di kode. Aturan standing dari Sprint 1/2 berlaku: **setiap instruksi user dicatat**, bukan cuma perubahan kode.

#### Format Entry

```
## [YYYY-MM-DD] Judul singkat

- **Apa yang dikerjakan:** ...
- **File yang dibuat/diubah:** ...
- **Alasan/keputusan:** ... (kalau ada keputusan desain yang perlu diingat)
- **Belum dikerjakan / TODO lanjutan:** ...
```

---

#### [2026-09-10] Setup log Sprint 3 — keputusan lompat dari M2 v2 ke Sprint 3

- **Apa yang dikerjakan:** Sprint 2 (M2a/M2b/M2c v1 + M2 v2 A1 entry point tunggal) selesai dan sudah di-push (commit terakhir `7dcecf6` kode + `e850b65` docs — detail di `SPRINT2_LOG.md`). User minta penjelasan awam untuk 4 opsi lanjutan (A2 error-path persistence / B polish M2b / C Reflexion persistence / Sprint 3) beserta risiko masing-masing kalau dikerjakan sekarang vs ditunda, lalu **memilih Sprint 3** (opsi yang direkomendasikan asisten). File log ini dibuat mengikuti format `SPRINT2_LOG.md`, konvensi standing satu file log per sprint.
- **File yang dibuat/diubah:**
  - `Memory Think/SPRINT3_LOG.md` — baru (file ini).
- **Alasan/keputusan:**
  - Inti argumen (versi lengkap di `SPRINT2_LOG.md` entry `[2026-09-09] Commit + push A1 + rekomendasi langkah berikutnya`): A2, B, C, D semuanya butuh *bahan dari pemakaian nyata* — tool ber-efek-samping (A2), data pemakaian pencarian (B), kegagalan tool yang berulang (C) — yang baru ada setelah ada device. Sprint 3 sendiri tidak butuh apa pun lagi dari v2 karena satu-satunya blocker struktural (entry point tunggal) sudah selesai di A1: `Orchestrator(llm, registry, ...)` menerima registry milik caller, tool device tinggal didaftarkan di situ.
  - **A2 dijadikan checkpoint wajib di dalam Sprint 3** — diputuskan saat tool device pertama didesain, dengan kasus konkret ("lampu nyala tapi turn tidak tersimpan"), bukan secara abstrak. C menyusul begitu ada kegagalan device yang berulang. B/D setelah beberapa minggu pemakaian.
  - Risiko Sprint 3 yang disebut ke user dan harus dijaga: (1) A2 terlewat kalau tidak dijadikan langkah eksplisit; (2) terlalu cepat ke hardware — mulai dengan device tiruan/simulator; (3) efek samping nyata berarti M11 (Security) harus mulai dipikirkan lebih awal, minimal konfirmasi untuk aksi `permission_tier=CRITICAL` (label ini sudah ada di `ToolContract` sejak M0).
  - Urutan kerja yang disepakati: verifikasi paper #4/#5 → desain M4 dulu (M5 bergantung padanya) → tool device pertama (mock) → keputusan A2 → M5 adapter nyata.
- **Belum dikerjakan / TODO lanjutan:**
  - `Memory Think/M4_tool_registry.md` / `M5_device_abstraction.md` (catatan per-modul, konvensi `M2_memory.md`) belum dibuat — dibuat saat diskusi/implementasi modul mulai.
  - Verifikasi paper — lihat entry berikutnya.

#### [2026-09-10] Verifikasi paper Sprint 3 (kategori #4/#5) — 6/6 cocok, 3 paper M4 belum ada file-nya

- **Apa yang dikerjakan:**
  1. Peta `sprint-paper-mapping.md` bagian Sprint 3 dibaca: 5 paper wajib + 1 opsional — M4: **MCP-Zero** ⭐, **ScaleMCP**, *Tool-to-Agent Retrieval* (opsional); M5: **Enhancing IoT with LLM** ⭐, **HearthNet** ⭐, **Agentic IoT Survey**.
  2. Isi folder `Paper & Journal/F.R.I.D.A.Y/M4/` dan `M5/` diverifikasi dengan standar lama (`pdftotext` halaman pertama + md5, jangan percaya nama file): **6/6 cocok isi vs judul, 0 duplikat** (md5 unik). Rincian:
     - `M5/Agentic IoT ... (2026).pdf` — arXiv 2607.04219v1, Jul 2026. Cocok. Sudah ada entry di `PAPER_NOTES.md` #5.
     - `M5/AI on Edge IoT ... (2025).pdf` — cocok. Sudah ada entry #5 (relevansi utamanya #11/#12, bukan Sprint 3).
     - `M5/Enhancing IoT Interactions ... (2025).pdf` — cocok. **Klaim peta "blueprint Home Assistant + MQTT" dikonfirmasi dari teks penuh**: Home Assistant API (18 sebutan) + Eclipse Mosquitto MQTT (7) + Prometheus via MQTT2Prometheus (15); toolset dibungkus `BaseTool` LangChain dengan resolusi nama entitas (`_get_entity_name`: nama ramah user → entity ID Home Assistant). Catatan kritis: prototipe kecil, evaluasi terbatas pada pembacaan telemetri; aktuasi masih "future work" di paper ini.
     - `M5/HearthNet ... (2026).pdf` — arXiv 2604.09618v2, CAIS '26, 5 halaman. Cocok. Klaim "adapter tipis, edge orchestration" dikonfirmasi: MQTT (13), *thin adapters* (6), *root-issued actuation leases* (24) — lease model ini yang jadi rujukan wajib M11. Entry-nya ada di `PAPER_NOTES.md` **kategori #13** (satu salinan fisik, relevansi lintas modul dicatat di teks) — tidak perlu entry duplikat di #5.
     - `M4/An Abstraction Layer Exploiting Voice Assistant Technologies for Effective Human–Robot Interaction.pdf` — Appl. Sci. 2021 (tahun tidak ada di nama file). Cocok. **Tapi ini bukan paper M4 (Tool Registry)** — isinya middleware yang memisahkan platform voice assistant (Alexa/Google) dari kontrol robot; relevansinya ke **M5** (abstraction layer device), bukan M4. Entry `PAPER_NOTES.md`-nya menyebut "Sprint 4-5 (M4-M6)" — **penomoran sprint basi** (peta sekarang: Sprint 3 = M4+M5, Sprint 4 = M11).
     - `M4/Voxia; A Virtual Voice Assistant.pdf` — cocok. Paper implementasi voice assistant end-to-end (Whisper + BERT intent + gTTS), relevansi ke pipeline voice (Sprint 5), bukan tool registry. Entry-nya juga punya penomoran sprint basi yang sama.
  3. **Gap:** 3 paper M4 yang dipetakan (MCP-Zero, ScaleMCP, Tool-to-Agent Retrieval) **tidak ada PDF-nya di repo** — peta cuma menyimpan link arXiv (2506.01056, 2505.06416, 2511.01854). Folder `M4/` saat ini berisi 2 paper voice assistant yang salah kamar. Artinya untuk desain M4, satu-satunya rujukan tool-discovery yang ada di repo adalah paper MCP (`M0/`) + Agent-OS (`M0/`).
  4. `PAPER_NOTES.md`: 2 entry M4 (Voxia, Abstraction Layer) dan entry Enhancing IoT diberi anotasi tanggal (bukan ditulis ulang) — koreksi penomoran sprint + hasil konfirmasi klaim. Tidak ada entry baru (tidak ada file baru).
- **File yang dibuat/diubah:**
  - `Memory Think/PAPER_NOTES.md` — 3 anotasi `[2026-09-10]`.
  - `Memory Think/SPRINT3_LOG.md` — entry ini.
- **Alasan/keputusan:**
  - Standar "cek isi PDF, jangan percaya nama file" dipertahankan; kali ini bersih. Nama file tanpa tahun (2 paper M4) **tidak di-rename** — precedent sebelumnya cuma memperbaiki tahun yang salah, bukan menambah yang tidak ada; tahun dicatat di anotasi saja.
  - 2 paper voice assistant **tidak dipindah** dari `M4/` dulu — menunggu keputusan user soal 3 paper M4 yang hilang, supaya folder `M4/` dirapikan sekali saja.
- **Belum dikerjakan / TODO lanjutan:**
  - **Keputusan user:** 3 PDF M4 diunduh (oleh asisten atau user) ke `M4/` lalu diverifikasi + ditulis entry-nya, atau desain M4 jalan dengan rujukan MCP + Agent-OS saja. Kalau diunduh: 2 paper voice assistant di `M4/` sebaiknya dipindah (Abstraction Layer → `M5/`, Voxia → folder voice) dan path di `PAPER_NOTES.md` diupdate.
  - Setelah paper beres: diskusi arah M4 (apa yang sudah ada: `ToolRegistry` in-memory + `ToolContract` ber-versi + `PermissionTier`; apa yang kurang: discovery/lazy-load ala MCP-Zero, sync tanpa restart ala ScaleMCP, isi folder `backend/registry/` yang kosong sejak Sprint 1) → plan mode.

#### [2026-09-10] Keputusan user: 3 PDF M4 diunduh manual, 2 paper salah kamar dipindah

- **Apa yang dikerjakan:**
  1. Ketiga link arXiv di peta dicek via web sebelum ditawarkan ke user — semuanya menunjuk judul yang benar: **MCP-Zero: Active Tool Discovery for Autonomous LLM Agents** (2506.01056, Jun 2025), **ScaleMCP: Dynamic and Auto-Synchronizing Model Context Protocol Tools for LLM Agents** (2505.06416, Mei 2025), **Tool-to-Agent Retrieval: Bridging Tools and Agents for Scalable LLM Multi-Agent Systems** (2511.01854, Nov 2025).
  2. User memilih lewat `AskUserQuestion`: (a) 3 PDF M4 **diunduh manual oleh user** ke `M4/` (bukan oleh asisten); (b) 2 paper salah kamar **dipindah sekarang**.
  3. `git mv`: `M4/An Abstraction Layer ... Human–Robot Interaction.pdf` → `M5/` (relevansi: abstraction layer device); `M4/Voxia; A Virtual Voice Assistant.pdf` → `M8/` (pipeline speech end-to-end; `M8/` sudah berisi paper ASR streaming + 1 studi usability asisten suara). Folder `M4/` sekarang **kosong** — menunggu 3 PDF dari user.
  4. `PAPER_NOTES.md`: kedua entry **dipindah blok utuh** ke kategori yang benar (Abstraction Layer → akhir #5, Voxia → akhir #8), path `Lokasi file` diupdate, anotasi `[2026-09-10]` dari entry sebelumnya diperbarui jadi "dipindah". Kategori #4 sekarang cuma berisi Agent-OS (file fisik di `M0/`). Sanity check otomatis: tidak ada path `M4/` tersisa di kategori #4.
- **File yang dibuat/diubah:**
  - `Paper & Journal/F.R.I.D.A.Y/M5/An Abstraction Layer ... .pdf`, `M8/Voxia; A Virtual Voice Assistant.pdf` — dipindah dari `M4/` (git rename, ter-stage).
  - `Memory Think/PAPER_NOTES.md` — 2 entry dipindah kategori + path.
  - `Memory Think/SPRINT3_LOG.md` — entry ini.
- **Alasan/keputusan:** Voxia ke `M8/` (bukan M7/M9/M10) karena isinya pipeline utuh STT→intent→TTS, paling dekat dengan kategori #8 Real-Time Speech Pipeline; bukan blueprint utama, cuma baseline pembanding (sesuai catatan lama). Link arXiv dicek dulu supaya user tidak mengunduh paper yang salah.
- **Belum dikerjakan / TODO lanjutan:**
  - **Menunggu user:** 3 PDF ke `M4/`. Setelah masuk → verifikasi (`pdftotext` + md5) → 3 entry baru `PAPER_NOTES.md` kategori #4 → update total & tabel di `sprint-paper-mapping.md`.
  - Perubahan sesi ini (SPRINT3_LOG.md baru, PAPER_NOTES.md, 2 rename) **belum di-commit** — menunggu instruksi user.
  - Sambil menunggu PDF, diskusi arah M4 bisa dimulai dengan rujukan MCP + Agent-OS (`M0/`) — atau ditunda sampai 3 paper masuk, terserah user.

#### [2026-09-10] Sesi ditutup — daftar unduhan M4 disimpan sebagai backup

- **Apa yang dikerjakan:** User minta daftar PDF yang harus diunduh **disimpan** supaya ada backup; dia akan mengunduh saat bertanya lagi di sesi berikutnya. Daftar (link sudah diverifikasi benar 2026-09-10), semua ke `Paper & Journal/F.R.I.D.A.Y/M4/`:
  1. **MCP-Zero: Active Tool Discovery for Autonomous LLM Agents** — `https://arxiv.org/pdf/2506.01056` ⭐ wajib
  2. **ScaleMCP: Dynamic and Auto-Synchronizing Model Context Protocol Tools for LLM Agents** — `https://arxiv.org/pdf/2505.06416` wajib
  3. **Tool-to-Agent Retrieval: Bridging Tools and Agents for Scalable LLM Multi-Agent Systems** — `https://arxiv.org/pdf/2511.01854` opsional
  Saran nama file (ikut konvensi folder lain, tahun di akhir): `MCP-Zero Active Tool Discovery for Autonomous LLM Agents (2025).pdf`, `ScaleMCP Dynamic and Auto-Synchronizing Model Context Protocol Tools for LLM Agents (2025).pdf`, `Tool-to-Agent Retrieval Bridging Tools and Agents for Scalable LLM Multi-Agent Systems (2025).pdf`.
- **File yang dibuat/diubah:** `Memory Think/SPRINT3_LOG.md` — entry ini.
- **Alasan/keputusan:** Tidak ada keputusan teknis — checkpoint supaya sesi berikutnya lanjut dari sini.
- **Belum dikerjakan / TODO lanjutan:** Semua perubahan Sprint 3 sesi ini (`SPRINT3_LOG.md` baru, `PAPER_NOTES.md`, 2 rename PDF) **belum di-commit** — menunggu instruksi user. Sesi berikutnya: user unduh 3 PDF → verifikasi → 3 entry `PAPER_NOTES.md` → update peta → diskusi arah M4.

#### [2026-09-11] Diskusi: jadwal sisa M2 v2 (A2/B/C/D) + kebutuhan paper tambahan Sprint 3

- **Apa yang dikerjakan:** Sesi dibuka dengan rekap posisi (folder `M4/` masih kosong, perubahan 2026-09-10 belum di-commit). User bertanya dua hal: (1) A2/B/C M2 v2 dikerjakan setelah sprint/modul berapa; (2) apakah asisten butuh paper tambahan untuk Sprint 3 (M4+M5), dan tema apa yang harus dicari.
- **Jawaban asisten (diskusi, bukan keputusan baru):**
  1. Sisa v2 **tidak diikat ke nomor sprint**, tapi ke *pemicu kejadian*: **A2** = di dalam Sprint 3, tepat saat tool device pertama (mock) didesain, sebelum M5 adapter nyata. **C** (Reflexion persistence) = begitu ada kegagalan device berulang — realistisnya akhir Sprint 3 / selama pemakaian di Sprint 4; secara paper C juga bersinggungan dengan Sprint 6 (M3, paper Reflexion). **B** (polish M2b) dan **D** = setelah beberapa minggu pemakaian nyata, jadi paling cepat setelah Sprint 3 ditutup, berjalan paralel dengan Sprint 4/5.
  2. Konfirmasi: Sprint 3 = M4 + M5 (benar). Paper M5 sudah cukup (3 dipetakan + 2 tambahan, semua terverifikasi). Paper M4 = **0 PDF**, 3 yang dipetakan wajib diunduh dulu (MCP-Zero, ScaleMCP, Tool-to-Agent). Di luar itu asisten menyebut 2 gap tematik yang belum tercakup: (a) M5 **aktuasi** — Enhancing IoT baru evaluasi pembacaan telemetri, aktuasi masih future work; kandidat: SAGE (2311.00772), Sasha (2305.09802); (b) M4 **kualitas deskripsi tool & seleksi tool skala besar** — kandidat: EasyTool, ToolLLM/ToolBench. Prioritas: 3 paper M4 dulu, sisanya opsional.
- **File yang dibuat/diubah:** `Memory Think/SPRINT3_LOG.md` — entry ini.
- **Belum dikerjakan / TODO lanjutan:** Sama seperti entry sebelumnya: menunggu 3 PDF M4 (+ opsional 2-4 paper tambahan di atas) → verifikasi → entry `PAPER_NOTES.md` → update peta. Commit perubahan 2026-09-10 masih menunggu instruksi user.

#### [2026-09-11] Daftar unduhan lengkap Sprint 3 dikirim ke user (7 link, semua diverifikasi via arXiv abs page)

- **Apa yang dikerjakan:** User minta link untuk diunduh sendiri. 4 link paper opsional dicek judulnya via web sebelum dikirim (standar "cek link dulu"): SAGE (2311.00772, Rivkin et al. 2023), Sasha (2305.09802, King et al. 2023), EasyTool (2401.06201, Yuan et al. 2024), ToolLLM (2307.16789, Qin et al. 2023) — 4/4 cocok. Tujuan folder: 3 paper M4 + EasyTool + ToolLLM → `M4/`; SAGE + Sasha → `M5/`.
- **File yang dibuat/diubah:** `Memory Think/SPRINT3_LOG.md` — entry ini.
- **Belum dikerjakan / TODO lanjutan:** Menunggu user unduh (3 wajib + 4 opsional). Setelah masuk: verifikasi `pdftotext` + md5 → entry `PAPER_NOTES.md` (#4 dan #5) → update tabel Sprint 3 di `sprint-paper-mapping.md` (jumlah paper 5 → maks 10). Commit perubahan 2026-09-10 masih menunggu instruksi.

#### [2026-09-11] 7 PDF Sprint 3 masuk — diverifikasi, dibaca penuh, 7 entry PAPER_NOTES.md, peta diupdate

- **Apa yang dikerjakan:**
  1. User mengunduh manual 7 PDF sesuai daftar (3 wajib M4 + 4 opsional), nama file sudah sesuai saran (tahun di akhir). Diverifikasi dengan standar lama (`pdftotext` halaman pertama + md5 seluruh file): **7/7 cocok isi vs judul, 0 duplikat** (md5 unik). Rincian: `M4/` MCP-Zero (2506.01056v4, md5 `2cdb1bad4dac`), ScaleMCP (2505.06416v1, `f23c2f047115`), Tool-to-Agent Retrieval (2511.01854v2, `b8eb632d2994`), EasyTool (2401.06201v3, `7f12f2c82544`), ToolLLM (2307.16789v2, `67cb0b425e28`); `M5/` SAGE (2311.00772v2, `b9caf0c7a7bb`), Sasha (2305.09802v3, IMWUT 2024, `ee3b019b642d`).
  2. Ketujuh paper **dibaca teks penuh** (bukan abstract saja) dan ditulis sebagai 7 entry baru di `PAPER_NOTES.md` — 5 di kategori #4 (setelah Agent-OS), 2 di kategori #5 (setelah Abstraction Layer). Tiap entry: ide inti dengan angka dari tabel paper, relevansi konkret ke modul F.R.I.D.A.Y, sumber = Teks penuh + md5, catatan kritis (bias dataset, usia paper, apa yang *tidak* dicakup).
  3. `PAPER_NOTES.md`: total diupdate ~123 → ~130 file; ditambah blok "Update tambahan #6" di bagian ringkasan.
  4. `sprint-paper-mapping.md`: tabel induk Sprint 3 jumlah paper 5 → 10; tabel Sprint 3 ditulis ulang dengan kolom Status (semua ✅ Punya) + 4 baris baru; blok link download diperluas jadi 7 dan ditandai sudah diunduh.
  5. User juga menawarkan mencarikan paper lagi kalau dibutuhkan — dijawab di bawah (Belum dikerjakan).
- **File yang dibuat/diubah:**
  - `Paper & Journal/F.R.I.D.A.Y/M4/` — 5 PDF baru (dari user, untracked).
  - `Paper & Journal/F.R.I.D.A.Y/M5/` — 2 PDF baru (dari user, untracked).
  - `Memory Think/PAPER_NOTES.md` — 7 entry baru, total, update #6.
  - `Memory Think/sprint-paper-mapping.md` — tabel Sprint 3 + tabel induk.
  - `Memory Think/SPRINT3_LOG.md` — entry ini.
- **Alasan/keputusan (temuan yang mengarahkan desain M4/M5, dicatat supaya diskusi arah M4 berikutnya tidak mulai dari nol):**
  - **M4 = tiga lapis dari tiga paper:** (1) MCP-Zero — agent *meminta* tool lewat blok terstruktur `server/tool`, registry mengembalikan top-k, iterasi kalau salah; jangan suntik semua `ToolContract` ke prompt. (2) ScaleMCP — registry sync otomatis via `SHA-256(name+description+args)` tiap kontrak; adapter M5 daftar ulang → registry ikut tanpa restart. (3) Tool-to-Agent — indeks device/adapter dan tool di *satu* indeks, bukan dua tingkat kaku.
  - **Standar deskripsi tool (M0/M4):** EasyTool + ScaleMCP sama-sama menemukan *contoh kalimat pemicu ber-parameter* di dokumen tool adalah perbaikan paling murah dan paling besar dampaknya (model 7B dari 0% jadi 37-47%). Ini kandidat perubahan kecil di `ToolContract` (field contoh skenario) — belum diputuskan, dibawa ke diskusi arah M4.
  - **M5 = SAGE sebagai cetak biru:** adapter membaca dokumentasi device secara lazy; exception device dikembalikan ke agent sebagai observasi (jawaban parsial A2); disambiguation deskripsi → device ID; benchmark **tanpa hardware** (state awal + perintah + cek state akhir) = bentuk konkret "device mock" yang sudah disepakati.
  - **Evaluasi:** Sasha memberi 7 mode kegagalan + metrik FP/FN/relevansi, dan gerbang *Clarifying* ("ada device relevan?") sebelum memilih tool; ToolLLM memberi aksi eksplisit `Finish by Giving Up` yang dinilai benar. Keduanya jadi pertahanan pertama terhadap aksi fisik salah sasaran — irisan dengan M11.
  - **Peringatan lintas paper:** tidak satu pun dari 7 paper punya lapisan konfirmasi/keamanan aksi; ScaleMCP menunjukkan *task completion* tinggi bisa menutupi *tool correctness* rendah — metrik harus dipisah saat evaluasi M4.
  - Konvensi: nama file SAGE memakai "Smart home" (h kecil) sesuai judul arXiv — tidak di-rename.
- **Belum dikerjakan / TODO lanjutan:**
  - **Paper tambahan: tidak ada yang wajib lagi untuk Sprint 3.** Kandidat opsional kalau nanti terasa kurang (tidak perlu dicari sekarang): MemTool (arXiv 2507.21428, manajemen tool yang sudah di-bind lintas turn, penulis ScaleMCP) — relevan kalau pengelolaan konteks tool jadi masalah; LiveMCPBench (2508.01780) — kalau mau benchmark retrieval sendiri.
  - **Commit:** semua perubahan Sprint 3 (sejak 2026-09-10: `SPRINT3_LOG.md` baru, `PAPER_NOTES.md`, `sprint-paper-mapping.md`, 2 rename PDF, 7 PDF baru) **belum di-commit** — menunggu instruksi user. Saran pesan: `docs(sprint3): add 7 M4/M5 papers, notes, mapping; move 2 misfiled PDFs`.
  - **Langkah berikutnya sesuai urutan yang disepakati:** diskusi arah M4 → plan mode. Bahan sudah lengkap: apa yang ada (`ToolRegistry` in-memory, `ToolContract` ber-versi, `PermissionTier`, `backend/registry/` kosong), apa yang kurang (request-tool ala MCP-Zero, hash-sync ala ScaleMCP, indeks gabungan, field contoh skenario), lalu tool device pertama pakai mock ala benchmark SAGE → keputusan A2 → M5 adapter nyata.

#### [2026-09-11] Commit + push fase paper Sprint 3; pertanyaan user: M4 dulu atau M5 dulu?

- **Apa yang dikerjakan:** Atas instruksi user, semua perubahan Sprint 3 sejak 2026-09-10 di-commit sebagai `047c4fa` (`docs(sprint3): add 7 M4/M5 papers + notes, open Sprint 3 log, move 2 misfiled PDFs` — 12 file: 7 PDF baru, 2 rename, 3 dokumen Memory Think) dan di-push ke `origin/master` mengikuti konvensi commit+push sprint sebelumnya. Working tree bersih.
- **File yang dibuat/diubah:** `Memory Think/SPRINT3_LOG.md` — entry ini (akan masuk commit berikutnya).
- **Alasan/keputusan:** Jawaban asisten untuk "M4 dulu atau M5 dulu": **M4 dulu**, sesuai urutan yang sudah disepakati 2026-09-10 dan diperkuat bacaan paper: (1) M5 bergantung pada M4 — adapter device harus *mendaftar* ke registry (hash-sync ScaleMCP, indeks gabungan Tool-to-Agent), jadi bentuk registry harus ada sebelum adapter pertama ditulis; (2) `backend/registry/` kosong sejak Sprint 1 sementara `ToolContract` + `PermissionTier` + `ToolRegistry` in-memory (`backend/agent_core/tool_registry.py`) sudah ada — M4 adalah pekerjaan *menyusun ulang* yang sudah ada, risiko rendah, cocok untuk pembukaan sprint; (3) tool device pertama (mock ala benchmark SAGE) adalah jembatan M4→M5 dan tempat keputusan A2 — kalau M5 duluan, A2 terlewat. Urutan tetap: desain M4 → implementasi M4 (request-tool ala MCP-Zero, hash-sync, contoh skenario di kontrak) → tool device mock → A2 → M5 adapter nyata.
- **Belum dikerjakan / TODO lanjutan:** Menunggu konfirmasi user untuk mulai M4. Langkah pertama M4: baca `tool_contract.py`, `tool_registry.py`, `orchestrator.py` → tulis `Memory Think/M4_tool_registry.md` (catatan per-modul, konvensi `M2_memory.md`) → plan mode.

#### [2026-09-11] Implementasi M4 Tool Registry v1 — katalog, find_tools, sync via hash, kontrak 1.1.0

- **Apa yang dikerjakan:**
  1. User: "gas M4". Kode yang ada dibaca dulu (`tool_contract.py`, `tool_registry.py`, `loop.py`, `orchestrator.py`, `llm_client.py`, 3 file tool, `archive_store.py`, test registry/orchestrator). Masuk plan mode, rencana ditulis dan **disetujui user** (file rencana: `~/.claude/plans/fuzzy-tickling-clover.md`).
  2. Diimplementasi sesuai rencana, 7 langkah: helper FTS5 bersama → kontrak 1.1.0 → `ToolRegistry.bind/has` + loop baca ulang tool tiap iterasi → `ToolCatalog` → `find_tools` → wiring `Orchestrator` + domain/contoh untuk 4 tool lama → dokumentasi.
  3. Test: `.venv/Scripts/python.exe -m pytest backend/tests -q` → **210 passed, 3 skipped** (sebelumnya 136 passed). 74 test baru di 5 file baru; file test lama tidak diubah sebaris pun.
  4. Catatan modul baru `Memory Think/M4_tool_registry.md` (Kegunaan / Pendekatan / Ringkasan Teknis / Alur / Bahasa Awam / Keputusan desain / TODO). `M0_contract_layer.md` diberi anotasi bertanggal soal kontrak 1.1.0.
- **File yang dibuat/diubah:**
  - Baru: `backend/registry/{__init__,catalog,discovery_tool}.py`, `backend/dal/{__init__,fts}.py`, 5 file test (`test_tool_contract_examples.py`, `test_tool_catalog.py`, `test_discovery_tool.py`, `test_agent_loop_discovery.py`, `test_orchestrator_catalog.py`), `Memory Think/M4_tool_registry.md`.
  - Diubah: `backend/schemas/{tool_contract,versioning,__init__}.py`, `backend/agent_core/{tool_registry,loop,llm_client}.py`, `backend/agent_core/tools/{time_tool,profile_tools,recall_tools}.py`, `backend/orchestrator/{orchestrator,__init__}.py`, `backend/memory/archive_store.py` (hanya impor helper FTS5), `Memory Think/M0_contract_layer.md`.
  - Dihapus: `backend/registry/.gitkeep`, `backend/dal/.gitkeep` (folder sekarang berisi kode).
- **Alasan/keputusan:**
  - Inti desain dari paper (detail di `M4_tool_registry.md`): katalog vs registry per turn (MCP-Zero), `sync` berbasis `content_hash` (ScaleMCP), indeks gabungan tool+domain (Tool-to-Agent), `examples` di kontrak yang ditampilkan ke LLM dan diindeks (EasyTool/ScaleMCP), hasil kosong = suruh jujur (ToolLLM/Sasha).
  - **Deviasi dari rencana yang disetujui (dicatat supaya tidak ambigu):** (a) `content_hash` mencakup semua field kecuali `version`/`contract_version`, bukan subset field yang disebut di rencana — aturan lebih sederhana, tidak bisa kelewatan field baru; (b) `register()` dibuat terpisah dan aditif, bukan "`sync` untuk satu tool" — karena `sync` menghapus tool penyedia yang tidak ditawarkan, rencana awal akan menghapus tool yang didaftar sebelumnya; (c) `examples` ditambahkan ke deskripsi tool di `llm_client.py` — tidak tertulis di rencana, tapi tanpa ini LLM tidak pernah melihat contohnya; (d) parameter `registry` di `Orchestrator` jadi opsional; (e) test tambahan ditaruh di file baru, bukan menambah file test lama.
  - Satu kesalahan saat implementasi, sudah diperbaiki sebelum test dijalankan: penggantian impor di `archive_store.py` sempat menaruh teks literal `" + TOKENIZER + "` di dalam string DDL; diperbaiki jadi f-string `{TOKENIZER}` (DDL diverifikasi tidak mengandung kurung kurawal lain). Test arsip lulus.
  - Tidak ada perubahan urutan tulis orchestrator dan semantik exception: **A2 tetap belum diputuskan**, sesuai kesepakatan (diputuskan saat tool device mock pertama).
- **Belum dikerjakan / TODO lanjutan:**
  - **Commit** perubahan M4 — menunggu instruksi user (aturan standing).
  - Smoke test dengan API key asli belum dijalankan (opsional di rencana; memakai kredit API user).
  - Langkah berikutnya Sprint 3: tool device **mock** pertama (pola benchmark SAGE, adapter `sync` ke katalog) → **keputusan A2** → M5 adapter nyata. TODO lain (M11 gate `CRITICAL`, `find_tools` memakan satu iterasi, tool tidak bertahan lintas turn, embedding kalau ratusan tool, belum ada entry point produksi) tercatat di `M4_tool_registry.md`.

#### [2026-09-17] Commit M4, tool device mock pertama (M5), trace A2 disusun ulang sebagai test

- **Apa yang dikerjakan:**
  1. Sesi dibuka dengan rekap. Ditemukan ketidakcocokan: memori asisten mencatat sesi 2026-09-11 lanjutan (tracing ulang semua modul, koreksi catatan M0/M1/M2, smoke test API asli, tabel trace A2 9 skenario), tapi **hasilnya tidak ada di file**: `M2_memory.md` terakhir diubah 9 Sep tanpa tabel A2, `M1_agent_core.md` masih versi 13 Agu, log ini tidak punya entry-nya. Kemungkinan sesi itu tidak sempat menulis ke disk. Diberitahukan ke user.
  2. User: "lanjutkan langkah berikutnya". Test dijalankan (210 passed, 3 skipped), lalu perubahan M4 di-commit sebagai `d54481b` (`feat(registry): M4 Tool Registry v1 — catalog, find_tools, hash sync, contract 1.1.0`, 27 file) dan di-push ke `origin/master`.
  3. **Tool device mock pertama** (`backend/devices/`, paket baru untuk M5): `MockHome` (state lampu + AC di memori, `diff()` ala benchmark SAGE, injeksi kegagalan `OFFLINE` dan `LOST_ACK`), `MockHomeAdapter.sync_into(catalog)` dengan 5 tool di domain `home`. Detail di `M5_device_layer.md`.
  4. **Trace A2 disusun ulang dari nol sebagai characterization test** (`backend/tests/test_a2_trace.py`, 9 skenario), tabel + pola + opsi (a)/(b)/(c) + rekomendasi + 5 pertanyaan di `M2_memory.md` bagian "M2 v2 — A2: trace konkret". Nomor skenario tidak sama dengan versi 2026-09-11 yang hilang.
  5. Test: **238 passed, 3 skipped** (sebelumnya 210). 28 kasus baru di 2 file baru; file test lama tidak diubah.
- **File yang dibuat/diubah:**
  - Baru: `backend/devices/{__init__,mock_home}.py`, `backend/tests/{test_mock_home,test_a2_trace}.py`, `Memory Think/M5_device_layer.md`.
  - Diubah: `Memory Think/M2_memory.md` (bagian A2 baru), `Memory Think/M4_tool_registry.md` (anotasi 2 TODO), `Memory Think/SPRINT3_LOG.md` (entry ini).
- **Alasan/keputusan:**
  - Trace dibuat sebagai test, bukan tabel saja, supaya tidak bisa hilang atau basi lagi: kalau perilaku berubah, test gagal.
  - Temuan utama trace: lima skenario tidak konsisten (S3 lost ack, S4 LLM gagal setelah aksi, S5 simpan sesi gagal, S6 simpan profil gagal, S8 iterasi habis), satu konsisten tapi caller menerima exception (S7 arsip gagal). Dunia fisik tidak bisa di-rollback, jadi A2 harus berbentuk "catat yang sudah terjadi" + "cek dunia saat ragu".
  - Kekurangan yang tidak ditutup mock: S8 menghasilkan dua pesan `user` berturut-turut ke API; menurut dokumentasi Messages API keduanya digabung, **belum diverifikasi dengan API asli**.
  - Tidak ada perubahan pada orchestrator, loop, atau urutan tulis: **A2 belum diputuskan**.
- **Belum dikerjakan / TODO lanjutan:**
  - **Keputusan A2 oleh user** (5 pertanyaan di `M2_memory.md`). Rekomendasi asisten: (a) simpan turn terputus + teks fallback iterasi habis, (c) adapter membaca ulang state setelah perintah tidak terkonfirmasi, (b) log aksi durable ditunda ke M11.
  - Dua TODO M4 yang juga menunggu keputusan: pesan saat model memanggil tool yang ada di katalog tapi belum dimuat (temuan smoke 2026-09-11, hanya ada di memori asisten), dan apakah tool yang dimuat bertahan lintas turn.
  - Pekerjaan sesi 2026-09-11 yang hilang (koreksi catatan M0/M1/M2, smoke test API asli) belum diulang.
  - Commit perubahan sesi ini: menunggu instruksi user.

#### [2026-10-23] Jawaban A2 dari user: Q1 + Q2 diputuskan, Q3-Q5 minta penjelasan

- **Apa yang dikerjakan:** Sesi dibuka setelah jeda ~5 minggu dengan rekap posisi. User menjawab: **Q1 = ya** (turn terputus setelah aksi disimpan sebagian dengan penanda; teks fallback iterasi habis ikut disimpan), **Q2 = ya** (adapter membaca ulang state device setelah perintah tidak terkonfirmasi). Q3 (log aksi durable vs M11), Q4 (arsip gagal: raise atau dicatat), Q5 (profil sebelum sesi) — user minta penjelasan dulu.
- **Koreksi tabel trace:** di S5 (dan S6) caller **tidak** menerima jawaban model; `run_turn` melempar exception dari `save`, jadi teks "Lampu sudah nyala." hanya dibuat model, tidak sampai ke user lewat API saat ini. Klaim "user sudah diberi tahu berhasil" di tabel `M2_memory.md` hanya benar kalau nanti ada UI streaming.
- **Penjelasan yang diberikan (ringkas):** Q3 — log aksi = file terpisah yang ditulis saat aksi, jadi tetap ada walau simpan sesi gagal; tumpang tindih dengan audit log M11. Q4 — masalahnya bukan "mencatat" tapi "melempar": raise membuang jawaban untuk turn yang sudah sukses dan mendorong user mengulang perintah (aksi device bisa jalan dua kali); usulan: kembalikan jawaban + catat + tanda peringatan. Q5 — urutan sesi→profil dipertahankan saat refactor supaya perilaku tidak berubah, keputusannya memang ditunda ke A2.
- **File yang dibuat/diubah:** `Memory Think/SPRINT3_LOG.md` — entry ini.
- **Belum dikerjakan / TODO lanjutan:** jawaban user untuk Q3-Q5 → implementasi A2 → update test trace → commit (menunggu instruksi).

#### [2026-10-23] Keputusan A2 final + implementasi

- **Apa yang dikerjakan:** User menjawab Q3 = tunda ke M11, Q4 = setuju (dicatat + kembalikan jawaban + tanda peringatan), Q5 = ubah urutan. Bersama Q1/Q2 (ya, ya), A2 diimplementasi:
  1. `backend/agent_core/loop.py`: `AgentResult.warnings`; teks fallback iterasi habis disimpan sebagai pesan assistant (S8); satu kalimat di `DEFAULT_SYSTEM_PROMPT` agar status device dibaca dengan tool, bukan dari riwayat (S3).
  2. `backend/orchestrator/orchestrator.py`: urutan tulis profil → sesi → arsip (S6); arsip gagal → `logging.warning` + `AgentResult.warnings`, tidak di-raise (S7); `run_agent` raise setelah turn dimulai → penanda `[Turn interrupted ...]`, simpan semua, raise ulang exception asli (S4). Deteksi "turn sudah dimulai" memakai identitas objek pesan terakhir (kompaksi tidak memutasi sebelum panggilan LLM-nya sukses dan mempertahankan objek pesan yang tersisa).
  3. `backend/devices/mock_home.py`: `MockHomeAdapter._command` membaca ulang state setelah `DeviceError` (S3).
  4. Test: `test_a2_trace.py` ditulis ulang untuk skenario yang berubah + 5 kasus baru; `test_orchestrator.py::test_ingest_failure_raises_*` diubah jadi `..._is_a_warning_...` (perilaku lama yang memang sengaja diubah oleh keputusan 4). **243 passed, 3 skipped.**
- **File yang dibuat/diubah:** `backend/agent_core/loop.py`, `backend/orchestrator/orchestrator.py`, `backend/devices/mock_home.py`, `backend/tests/test_a2_trace.py`, `backend/tests/test_orchestrator.py`, `Memory Think/M2_memory.md` (tabel keputusan A2), `Memory Think/M5_device_layer.md`, entry ini.
- **Alasan/keputusan:** lihat tabel "Keputusan A2" di `M2_memory.md`. Satu-satunya test lama yang diubah adalah yang merekam "arsip gagal = raise", karena keputusan 4 sengaja membalik perilaku itu.
- **Belum dikerjakan / TODO lanjutan:**
  - Commit (menunggu instruksi user): perubahan 2026-09-17 (mock M5, trace A2) + implementasi A2 ini.
  - S5 tetap celah yang diketahui sampai audit log M11.
  - 2 TODO M4 (tool katalog yang belum dimuat, tool bertahan lintas turn), koreksi catatan M0/M1/M2 dan smoke test API asli yang hilang dari sesi 2026-09-11.
  - Langkah berikutnya: M5 adapter nyata.

#### [2026-10-23] Perbaikan 2 celah kecil A2 (poin 9 rekap kekurangan)

- **Apa yang dikerjakan:** User minta poin 9 dari rekap kekurangan diperbaiki dan dites.
  1. **Profil gagal tidak lagi menghilangkan turn.** `Orchestrator._persist`: kalau `ProfileStore.save` gagal, catatan koreksi (`[Saving the user profile failed ...: facts ... were NOT saved ...]`) ditempel ke pesan assistant terakhir, sesi tetap disimpan, exception di-raise (kegagalan simpan sesi saat itu ditempel sebagai note). Helper baru `_append_assistant_note` dipakai juga untuk penanda "turn interrupted".
  2. **Deteksi "turn sudah dimulai" (identitas objek pesan) dihapus.** Mutation test: mengganti pengecekan itu dengan `True` tidak menggagalkan test apa pun, karena setelah A2 setiap turn tersimpan berakhir dengan assistant; cukup cek role pesan terakhir. Kode jadi lebih sederhana dan tidak bergantung pada detail implementasi kompaksi.
  3. Test baru di `test_a2_trace.py`: S6 ditulis ulang (sesi tersimpan + koreksi), S6 aksi device + profil gagal (lampu tetap tercatat), S6 turn terputus + profil gagal (dua catatan, note di exception), kompaksi gagal (tanpa penanda, sesi tidak berubah), kompaksi sukses lalu LLM gagal (penanda ada, ringkasan tersimpan). Mutation check kedua: menghapus pengecekan role → test kompaksi gagal, sesuai harapan.
  4. **247 passed, 3 skipped** (sebelumnya 243).
- **File yang dibuat/diubah:** `backend/orchestrator/orchestrator.py`, `backend/tests/test_a2_trace.py`, `Memory Think/M2_memory.md`, entry ini.
- **Alasan/keputusan:** Koreksi di sesi tetap memenuhi tujuan keputusan 5 (tidak ada klaim palsu yang bertahan) sambil tidak membuang catatan aksi fisik. Urutan profil → sesi → arsip tidak berubah.
- **Belum dikerjakan / TODO lanjutan:** commit (menunggu instruksi user); sisa kekurangan non-modul dari rekap (entry point CLI/server, smoke test API asli, 2 TODO M4, catatan M0/M1/M2 basi, M2 v2 B/D); M5 adapter nyata.

#### [2026-10-23] Diskusi: apa yang didaftarkan ke registry saat memakai MQTT / device pihak ketiga

- **Apa yang dikerjakan:** User bertanya apakah F.R.I.D.A.Y nanti akan meminta IP publisher + alamat queue MQTT saat pendaftaran, dan bagaimana kalau memakai beberapa device pihak ketiga. Diskusi saja, tidak ada perubahan kode.
- **Jawaban asisten (belum keputusan):**
  - Registry M4 mendaftarkan **kemampuan** (tool + kontrak), bukan detail koneksi. Tiga lapis: (1) konfigurasi koneksi adapter (host/port broker, kredensial, TLS) ditulis user sekali di config/.env, tidak ditanyakan lewat obrolan dan tidak pernah masuk konteks LLM; (2) daftar device (id, nama, ruangan, jenis, topic) didapat adapter lewat discovery (mis. topic `homeassistant/.../config`, Zigbee2MQTT) atau file daftar; (3) tool per jenis aksi dengan `device_id` enum (pola `MockHomeAdapter`) yang di-`sync` ke katalog.
  - Alasan tidak lewat obrolan: M2 menyimpan percakapan verbatim (sesi + arsip FTS) dan mengirimnya ke API LLM, jadi kredensial akan tersebar; menambah device lewat obrolan bisa jadi fitur nanti di bawah izin M11.
  - Koreksi istilah: MQTT punya **broker** dan **topic**, bukan IP publisher / queue address.
  - Device pihak ketiga: satu adapter = satu `provider` di katalog (sudah didukung `catalog.sync(provider, tools)`). Rekomendasi: Home Assistant sebagai hub (satu adapter untuk banyak merek, ada mode demo tanpa hardware), MQTT langsung kalau device DIY.
- **File yang dibuat/diubah:** `Memory Think/SPRINT3_LOG.md` — entry ini.
- **Belum dikerjakan / TODO lanjutan:** menunggu user memilih jalur device (HA / MQTT langsung / per-vendor) dan menyebut device yang dimiliki → desain adapter M5 nyata.

#### [2026-10-23] Diskusi lanjutan: gateway/hub sendiri untuk semua provider (MQTT, LoRa, vendor)

- **Apa yang dikerjakan:** User mengusulkan membuat service/proyek terpisah yang memegang semua koneksi provider (home service, MQTT, LoRa) dan mengekspos satu API; F.R.I.D.A.Y cukup menyimpan akses ke API itu, supaya F.R.I.D.A.Y lebih ringan. Diskusi saja.
- **Jawaban asisten (belum keputusan):**
  - Pola benar: hub/gateway terpisah, F.R.I.D.A.Y hanya punya satu adapter + satu token (di config/.env, bukan lewat obrolan). Home Assistant sudah merupakan gateway seperti itu; membangun sendiri hanya layak untuk bagian yang tidak tertangani HA (mis. protokol LoRa custom), bisa sebagai bridge kecil ke MQTT → HA.
  - Klaim "lebih ringan" dikoreksi: beban utama F.R.I.D.A.Y adalah panggilan LLM, bukan I/O device. Keuntungan nyata gateway: koneksi 24/7 + cache state + retry di luar proses F.R.I.D.A.Y, kredensial provider tidak di F.R.I.D.A.Y, kode F.R.I.D.A.Y tetap satu adapter, F.R.I.D.A.Y bisa restart tanpa memutus device.
  - Opsi bentuk API gateway: REST/WebSocket, atau **MCP server** (cocok dengan desain M4; HA punya integrasi MCP Server — perlu dicek versinya saat desain).
  - LoRa: latensi tinggi dan downlink kelas A hanya setelah uplink, jadi gateway harus melaporkan state "pending" — terkait keputusan A2 no. 2 (baca ulang state).
- **File yang dibuat/diubah:** `Memory Think/SPRINT3_LOG.md` — entry ini.
- **Belum dikerjakan / TODO lanjutan:** user memilih: HA sebagai gateway / gateway sendiri / hibrida; daftar device yang dimiliki (termasuk apakah LoRa sudah ada).

#### [2026-10-23] Keputusan user: adapter device nyata DITUNDA — jadi PR untuk versi F.R.I.D.A.Y berikutnya

- **Apa yang dikerjakan:** User menyatakan banyak device belum tersedia dan proyek ini masih tahap percobaan, jadi model koneksi ke perangkat IoT belum bisa dipastikan. Semua pengujian device di Sprint 3 tetap memakai simulasi (mock). Bagian yang butuh perangkat nyata dicatat sebagai **PR user** untuk versi F.R.I.D.A.Y yang lebih matang.
- **PR (pekerjaan rumah) untuk versi berikutnya — butuh perangkat nyata:**
  1. Pilih jalur gateway: Home Assistant sebagai hub (rekomendasi asisten) / hibrida HA + bridge sendiri (mis. LoRa custom) / gateway buatan sendiri. Lihat 2 entry diskusi sebelumnya hari ini.
  2. Inventaris device yang dimiliki (merek, protokol: Wi-Fi/Zigbee/MQTT/LoRa, cloud atau lokal).
  3. Adapter M5 nyata ke gateway terpilih: satu `provider` di katalog, kredensial di config/.env (tidak lewat obrolan), discovery device otomatis, operasi baca state per device (syarat keputusan A2 no. 2).
  4. State "pending" untuk device lambat (LoRa kelas A) — perintah tertunda bukan gagal.
  5. Kompresi respons state device nyata sebelum masuk konteks LLM (ToolLLM).
  6. Benchmark tugas ala SAGE dengan device nyata / demo HA, dinilai 7 mode kegagalan Sasha (irisan M16).
- **Alasan/keputusan:** Tanpa perangkat dan pilihan gateway, adapter nyata hanya tebakan. Sprint 3 ditutup dengan yang bisa dikerjakan tanpa hardware (daftar dibahas di chat 2026-10-23).
- **File yang dibuat/diubah:** `Memory Think/SPRINT3_LOG.md` — entry ini.

#### [2026-10-23] Commit + push mock M5 dan A2

- **Apa yang dikerjakan:** Atas persetujuan user, semua perubahan sejak 2026-09-17 (mock M5, trace A2, implementasi A2 + perbaikan celah kecil, catatan modul, entry log) di-commit sebagai `603471e` (`feat(devices,memory): M5 mock home + M2 v2 A2 error-path persistence`, 11 file) dan di-push ke `origin/master`. Test sebelum commit: 247 passed, 3 skipped.
- **File yang dibuat/diubah:** `Memory Think/SPRINT3_LOG.md` — entry ini (masuk commit berikutnya).
- **Belum dikerjakan / TODO lanjutan:** urutan yang disepakati: (1) pesan untuk tool katalog yang belum dimuat → (2) tool bertahan lintas turn → (3) antarmuka device generik + kontrak Device → (4) state pending di mock → (5) disambiguasi/bertanya balik → (6) CLI → (7) smoke test API asli → (8) koreksi catatan M0/M1/M2.

#### [2026-10-23] M4 TODO #1: memanggil tool katalog yang belum dimuat — `AutoLoadPolicy`

- **Apa yang dikerjakan:** Asisten menawarkan (a) pesan yang mengarahkan ke `find_tools` atau (b) dimuat otomatis, dengan saran: (b) untuk read-only, (a) untuk yang mengubah sesuatu. User: jadikan kondisi, semua opsi tetap bisa dipakai. Implementasi `AutoLoadPolicy` (`read_only` default / `all` / `never`) lewat parameter `Orchestrator(catalog_auto_load=...)`; detail di `M4_tool_registry.md`.
- **File yang dibuat/diubah:** `backend/agent_core/{tool_registry,loop}.py`, `backend/registry/{discovery_tool,__init__}.py`, `backend/orchestrator/orchestrator.py`, `backend/tests/test_catalog_auto_load.py` (baru, 11 test), `backend/tests/test_orchestrator_catalog.py` (1 assertion), `Memory Think/M4_tool_registry.md`, entry ini.
- **Hasil:** **258 passed, 3 skipped** (sebelumnya 247). Mutation check: default `all` → 2 test gagal, sesuai harapan.
- **Alasan/keputusan:** aksi yang mengubah dunia tetap lewat jalur yang dipilih sengaja (deskripsi + tier terlihat, bekal M11); pembacaan tidak membuang langkah. Arah dependensi tetap `registry` → `agent_core`.
- **Belum dikerjakan / TODO lanjutan:** belum di-commit. Berikutnya: TODO M4 #2 (tool bertahan lintas turn) → antarmuka device generik → pending di mock → disambiguasi → CLI → smoke test → catatan M0/M1/M2.

#### [2026-10-23] M4 TODO #2: tool bertahan lintas turn — `tool_retention_turns`

- **Apa yang dikerjakan:** Asisten menawarkan (a) selama sesi, (b) beberapa turn (MemTool), (c) tetap seperti sekarang; saran (b) dijadikan pengaturan. User setuju. Implementasi `Orchestrator(tool_retention_turns=3 | None | 0)` dengan helper `recently_used_tool_names` yang membaca riwayat sesi (tanpa state baru); hanya panggilan berhasil yang dihitung. Detail di `M4_tool_registry.md`.
- **File yang dibuat/diubah:** `backend/registry/retention.py` (baru), `backend/registry/__init__.py`, `backend/orchestrator/orchestrator.py` (wiring + docstring kelas), `backend/tests/test_tool_retention.py` (baru, 8 test), `Memory Think/M4_tool_registry.md`, entry ini.
- **Hasil:** **266 passed, 3 skipped** (sebelumnya 258). Dua mutation check tertangkap test. Test lama `test_tools_loaded_in_one_turn_are_gone_at_the_start_of_the_next` tetap lulus tanpa diubah (tool di sana hanya dimuat, tidak dipakai).
- **Belum dikerjakan / TODO lanjutan:** belum di-commit (bersama `AutoLoadPolicy`). Berikutnya: antarmuka device generik + kontrak Device → pending di mock → disambiguasi → CLI → smoke test → catatan M0/M1/M2.

#### [2026-10-23] Commit TODO M4 + CLI pertama (`python -m backend.cli`)

- **Apa yang dikerjakan:**
  1. Perbaikan 2 TODO M4 (`AutoLoadPolicy`, `tool_retention_turns`) di-commit `d327685` dan di-push.
  2. User bertanya apakah "antarmuka device" berarti UI; dijelaskan bahwa itu interface kode, bukan tampilan. README dan peta sprint **belum punya modul UI** (web/dashboard); interaksi yang direncanakan: CLI (Sprint 3) dan suara (Sprint 5, M7-M10). User memilih CLI dulu baru antarmuka device; asisten setuju (bisa langsung dicoba, jadi smoke test API asli, mulai mengumpulkan data pemakaian untuk M2 v2 B/D, CLI hanya memanggil `MockHomeAdapter(...).sync_into(...)` sehingga tidak terdampak refactor antarmuka device).
  3. **CLI baru `backend/cli.py`**: `Orchestrator` asli + LLM asli (`get_llm_client()`, memakai kredit API) + rumah simulasi. `get_current_time` selalu terpasang; tool rumah **discoverable** (bukan pinned) supaya `find_tools`, auto-load, dan retensi teruji (`--pin-home` untuk memasang semuanya). Perintah: `/state`, `/fail <device_id> offline|lost_ack`, `/trace on|off` (default on: tiap tool call + hasilnya dicetak, dibaca dari sesi tersimpan), `/new`, `/session`, `/help`, `/quit`. Error per turn ditampilkan (termasuk `__notes__`) tanpa menghentikan CLI; `AgentResult.warnings` dan batas langkah ditampilkan. Opsi: `--session`, `--pin-home`, `--debug`.
  4. Test `backend/tests/test_cli.py` (14 kasus, LLM palsu, store di `tmp_path`). Dicek: test tidak membuat file di folder memori asli. Dicek manual: `--help` dan startup + `/state` + `/help` + `/quit` lewat pipe (tanpa panggilan API).
  5. **280 passed, 3 skipped** (sebelumnya 266).
- **Cara pakai:** `.venv/Scripts/python.exe -m backend.cli` (butuh `ANTHROPIC_API_KEY` di `.env`; model default `ANTHROPIC_MODEL`, sekarang `claude-haiku-4-5`). Sesi default `cli`, tersimpan di `backend/memory/sessions/` (gitignored).
- **Catatan desain:** rumah simulasi hidup di memori dan mulai dari "semua mati" setiap run, sedangkan riwayat obrolan tersimpan; setelah restart riwayat bisa bilang "lampu nyala" padahal mati. Ini sengaja dibiarkan sebagai uji aturan A2 (cek state, jangan percaya riwayat).
- **File yang dibuat/diubah:** `backend/cli.py` (baru), `backend/tests/test_cli.py` (baru), entry ini.
- **Belum dikerjakan / TODO lanjutan:** user mencoba CLI = smoke test API asli (poin 6/7 daftar Sprint 3) → antarmuka device generik → pending di mock → disambiguasi → catatan M0/M1/M2. CLI belum di-commit.

#### [2026-10-23] Smoke test API asli lewat CLI (model `claude-haiku-4-5`)

- **Apa yang dikerjakan:** User mencoba CLI sendiri (hasilnya belum ditempel ke chat), lalu minta asisten menjalankan skenario otomatis. Dijalankan dengan kelas `Cli` + `build_orchestrator` + LLM asli, tetapi store diarahkan ke folder scratchpad supaya profil global user tidak terisi data test (skrip di scratchpad sesi, bukan di repo). 12 baris input, 8 skenario.
- **Hasil per skenario:**
  1. Jam → `get_current_time` ✅. Temuan: jawaban dalam **UTC**, bukan waktu lokal user.
  2. "nyalakan lampu ruang tamu" → `find_tools(query="turn on light", domain="home")` → `home_set_power` ✅ (alur MCP-Zero terbukti dengan model asli).
  3. "matikan lagi" → langsung `home_set_power`, **tanpa** `find_tools` ✅ (retensi tool).
  4. "lampunya nyala nggak?" → `home_get_state` ✅. `home_get_state` tidak dipakai sebelumnya, jadi dimuat lewat `AutoLoadPolicy.read_only` (kedua mekanisme terbukti).
  5. `lost_ack` → tool_result sukses + `note` read-back, jawaban "sudah dinyalakan" sesuai kondisi nyata ✅ (A2 keputusan 2).
  6. AC offline → error dengan state aktual, jawaban jujur ✅. Temuan: model menyebut "suhu **terukur** 24°C", padahal itu suhu target — nama key `temperature` ambigu.
  7. "inget ya..." → `remember_user_fact` ✅; sesi baru → jawaban benar ✅, tetapi model memanggil `recall_memory` (arsip) padahal fakta sudah ada di blok profil system prompt, dan menjawab dengan mengutip ucapan lama. Temuan lain: model menjanjikan "nanti saya sesuaikan brightness-nya" — perilaku proaktif yang belum ada.
  8. "buatkan aku kopi" → tidak memakai tool apa pun, jujur tidak bisa ✅.
- **Biaya:** 18 panggilan LLM, 60.771 token input, 1.189 token output (~3,4 rb token input per panggilan; definisi tool + system prompt + riwayat mendominasi).
- **Temuan dan rumahnya:**
  - Gaya: campur "Anda"/"kamu", emoji, jawaban kopi bertele-tele → **M15** (persona).
  - Janji proaktif ("nanti saya sesuaikan") → **M17** (proaktif); sampai saat itu termasuk klaim berlebihan.
  - Waktu UTC, bukan zona waktu user → kecil, tanpa modul lain: zona waktu lokal di `get_current_time` / config.
  - `temperature` ambigu → dikerjakan bersama antarmuka device generik (nama key state yang jelas, mis. `target_temperature`).
  - Profil di prompt tapi model tetap `recall_memory` → kecil, tanpa modul lain: perjelas instruksi blok profil (fakta profil = sumber utama; recall untuk percakapan lama). Pantau dulu di pemakaian nyata.
- **File yang dibuat/diubah:** `Memory Think/SPRINT3_LOG.md` — entry ini.
- **Belum dikerjakan / TODO lanjutan:** commit CLI; 2 perbaikan kecil (zona waktu, instruksi profil) kalau user setuju; antarmuka device generik (+ nama key state); minta user menempel hasil percobaannya sendiri untuk dibandingkan.

#### [2026-10-23] Sesi ditutup — checkpoint untuk besok

- **Apa yang dikerjakan:** User pulang; minta pembahasan terakhir dicatat lalu di-push. Perubahan yang belum di-commit (CLI `backend/cli.py` + `test_cli.py` + entry log sejak `d327685`) di-commit dan di-push bersama entry ini.
- **Posisi saat ditutup:** Sprint 3. Selesai hari ini: keputusan + implementasi A2 (`603471e`), 2 TODO M4 (`d327685`), CLI, smoke test API asli 8/8. Test: 280 passed, 3 skipped.
- **Menunggu dari user:** hasil terminal percobaan CLI-nya sendiri (Cara 1) untuk dibandingkan dengan smoke test asisten.
- **Langkah berikutnya (urutan yang diusulkan asisten, belum dikonfirmasi user):**
  1. Perbaikan kecil dari smoke test: zona waktu lokal untuk `get_current_time`; instruksi blok profil (fakta profil = sumber utama, `recall_memory` untuk percakapan lama).
  2. Antarmuka device generik (`list_devices` / `read_state` / `apply`) + kontrak Device M0 + nama key state yang jelas (`target_temperature`).
  3. State "pending" di mock → disambiguasi / bertanya balik → koreksi catatan M0/M1/M2 (penutup Sprint 3).
- **PR user (versi berikutnya, butuh perangkat nyata):** lihat entry "adapter device nyata DITUNDA" hari ini.
