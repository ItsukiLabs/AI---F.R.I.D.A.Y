# Sprint 3 — Log Pengerjaan (M4 Tool Registry + M5 Device Abstraction Layer)

> Datasheet pengerjaan Sprint 3. Setiap kali ada update fitur/logika (kode, schema, struktur), tambahkan entry baru di bawah — jangan edit entry lama, supaya riwayat tetap utuh dan tidak ambigu soal apa yang sudah dikerjakan.
>
> Selain kode, **diskusi/pembahasan penting** (pertanyaan konsep, keputusan arsitektur yang muncul dari obrolan, penjelasan yang mengubah pemahaman) juga dicatat di sini sebagai entry tersendiri — supaya ada jejak "kenapa" di balik keputusan, bukan cuma "apa" yang berubah di kode. Aturan standing dari Sprint 1/2 berlaku: **setiap instruksi user dicatat**, bukan cuma perubahan kode.

## Format Entry

```
## [YYYY-MM-DD] Judul singkat

- **Apa yang dikerjakan:** ...
- **File yang dibuat/diubah:** ...
- **Alasan/keputusan:** ... (kalau ada keputusan desain yang perlu diingat)
- **Belum dikerjakan / TODO lanjutan:** ...
```

---

## [2026-09-10] Setup log Sprint 3 — keputusan lompat dari M2 v2 ke Sprint 3

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

## [2026-09-10] Verifikasi paper Sprint 3 (kategori #4/#5) — 6/6 cocok, 3 paper M4 belum ada file-nya

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

## [2026-09-10] Keputusan user: 3 PDF M4 diunduh manual, 2 paper salah kamar dipindah

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

## [2026-09-10] Sesi ditutup — daftar unduhan M4 disimpan sebagai backup

- **Apa yang dikerjakan:** User minta daftar PDF yang harus diunduh **disimpan** supaya ada backup; dia akan mengunduh saat bertanya lagi di sesi berikutnya. Daftar (link sudah diverifikasi benar 2026-09-10), semua ke `Paper & Journal/F.R.I.D.A.Y/M4/`:
  1. **MCP-Zero: Active Tool Discovery for Autonomous LLM Agents** — `https://arxiv.org/pdf/2506.01056` ⭐ wajib
  2. **ScaleMCP: Dynamic and Auto-Synchronizing Model Context Protocol Tools for LLM Agents** — `https://arxiv.org/pdf/2505.06416` wajib
  3. **Tool-to-Agent Retrieval: Bridging Tools and Agents for Scalable LLM Multi-Agent Systems** — `https://arxiv.org/pdf/2511.01854` opsional
  Saran nama file (ikut konvensi folder lain, tahun di akhir): `MCP-Zero Active Tool Discovery for Autonomous LLM Agents (2025).pdf`, `ScaleMCP Dynamic and Auto-Synchronizing Model Context Protocol Tools for LLM Agents (2025).pdf`, `Tool-to-Agent Retrieval Bridging Tools and Agents for Scalable LLM Multi-Agent Systems (2025).pdf`.
- **File yang dibuat/diubah:** `Memory Think/SPRINT3_LOG.md` — entry ini.
- **Alasan/keputusan:** Tidak ada keputusan teknis — checkpoint supaya sesi berikutnya lanjut dari sini.
- **Belum dikerjakan / TODO lanjutan:** Semua perubahan Sprint 3 sesi ini (`SPRINT3_LOG.md` baru, `PAPER_NOTES.md`, 2 rename PDF) **belum di-commit** — menunggu instruksi user. Sesi berikutnya: user unduh 3 PDF → verifikasi → 3 entry `PAPER_NOTES.md` → update peta → diskusi arah M4.

## [2026-09-11] Diskusi: jadwal sisa M2 v2 (A2/B/C/D) + kebutuhan paper tambahan Sprint 3

- **Apa yang dikerjakan:** Sesi dibuka dengan rekap posisi (folder `M4/` masih kosong, perubahan 2026-09-10 belum di-commit). User bertanya dua hal: (1) A2/B/C M2 v2 dikerjakan setelah sprint/modul berapa; (2) apakah asisten butuh paper tambahan untuk Sprint 3 (M4+M5), dan tema apa yang harus dicari.
- **Jawaban asisten (diskusi, bukan keputusan baru):**
  1. Sisa v2 **tidak diikat ke nomor sprint**, tapi ke *pemicu kejadian*: **A2** = di dalam Sprint 3, tepat saat tool device pertama (mock) didesain, sebelum M5 adapter nyata. **C** (Reflexion persistence) = begitu ada kegagalan device berulang — realistisnya akhir Sprint 3 / selama pemakaian di Sprint 4; secara paper C juga bersinggungan dengan Sprint 6 (M3, paper Reflexion). **B** (polish M2b) dan **D** = setelah beberapa minggu pemakaian nyata, jadi paling cepat setelah Sprint 3 ditutup, berjalan paralel dengan Sprint 4/5.
  2. Konfirmasi: Sprint 3 = M4 + M5 (benar). Paper M5 sudah cukup (3 dipetakan + 2 tambahan, semua terverifikasi). Paper M4 = **0 PDF**, 3 yang dipetakan wajib diunduh dulu (MCP-Zero, ScaleMCP, Tool-to-Agent). Di luar itu asisten menyebut 2 gap tematik yang belum tercakup: (a) M5 **aktuasi** — Enhancing IoT baru evaluasi pembacaan telemetri, aktuasi masih future work; kandidat: SAGE (2311.00772), Sasha (2305.09802); (b) M4 **kualitas deskripsi tool & seleksi tool skala besar** — kandidat: EasyTool, ToolLLM/ToolBench. Prioritas: 3 paper M4 dulu, sisanya opsional.
- **File yang dibuat/diubah:** `Memory Think/SPRINT3_LOG.md` — entry ini.
- **Belum dikerjakan / TODO lanjutan:** Sama seperti entry sebelumnya: menunggu 3 PDF M4 (+ opsional 2-4 paper tambahan di atas) → verifikasi → entry `PAPER_NOTES.md` → update peta. Commit perubahan 2026-09-10 masih menunggu instruksi user.

## [2026-09-11] Daftar unduhan lengkap Sprint 3 dikirim ke user (7 link, semua diverifikasi via arXiv abs page)

- **Apa yang dikerjakan:** User minta link untuk diunduh sendiri. 4 link paper opsional dicek judulnya via web sebelum dikirim (standar "cek link dulu"): SAGE (2311.00772, Rivkin et al. 2023), Sasha (2305.09802, King et al. 2023), EasyTool (2401.06201, Yuan et al. 2024), ToolLLM (2307.16789, Qin et al. 2023) — 4/4 cocok. Tujuan folder: 3 paper M4 + EasyTool + ToolLLM → `M4/`; SAGE + Sasha → `M5/`.
- **File yang dibuat/diubah:** `Memory Think/SPRINT3_LOG.md` — entry ini.
- **Belum dikerjakan / TODO lanjutan:** Menunggu user unduh (3 wajib + 4 opsional). Setelah masuk: verifikasi `pdftotext` + md5 → entry `PAPER_NOTES.md` (#4 dan #5) → update tabel Sprint 3 di `sprint-paper-mapping.md` (jumlah paper 5 → maks 10). Commit perubahan 2026-09-10 masih menunggu instruksi.

## [2026-09-11] 7 PDF Sprint 3 masuk — diverifikasi, dibaca penuh, 7 entry PAPER_NOTES.md, peta diupdate

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

## [2026-09-11] Commit + push fase paper Sprint 3; pertanyaan user: M4 dulu atau M5 dulu?

- **Apa yang dikerjakan:** Atas instruksi user, semua perubahan Sprint 3 sejak 2026-09-10 di-commit sebagai `047c4fa` (`docs(sprint3): add 7 M4/M5 papers + notes, open Sprint 3 log, move 2 misfiled PDFs` — 12 file: 7 PDF baru, 2 rename, 3 dokumen Memory Think) dan di-push ke `origin/master` mengikuti konvensi commit+push sprint sebelumnya. Working tree bersih.
- **File yang dibuat/diubah:** `Memory Think/SPRINT3_LOG.md` — entry ini (akan masuk commit berikutnya).
- **Alasan/keputusan:** Jawaban asisten untuk "M4 dulu atau M5 dulu": **M4 dulu**, sesuai urutan yang sudah disepakati 2026-09-10 dan diperkuat bacaan paper: (1) M5 bergantung pada M4 — adapter device harus *mendaftar* ke registry (hash-sync ScaleMCP, indeks gabungan Tool-to-Agent), jadi bentuk registry harus ada sebelum adapter pertama ditulis; (2) `backend/registry/` kosong sejak Sprint 1 sementara `ToolContract` + `PermissionTier` + `ToolRegistry` in-memory (`backend/agent_core/tool_registry.py`) sudah ada — M4 adalah pekerjaan *menyusun ulang* yang sudah ada, risiko rendah, cocok untuk pembukaan sprint; (3) tool device pertama (mock ala benchmark SAGE) adalah jembatan M4→M5 dan tempat keputusan A2 — kalau M5 duluan, A2 terlewat. Urutan tetap: desain M4 → implementasi M4 (request-tool ala MCP-Zero, hash-sync, contoh skenario di kontrak) → tool device mock → A2 → M5 adapter nyata.
- **Belum dikerjakan / TODO lanjutan:** Menunggu konfirmasi user untuk mulai M4. Langkah pertama M4: baca `tool_contract.py`, `tool_registry.py`, `orchestrator.py` → tulis `Memory Think/M4_tool_registry.md` (catatan per-modul, konvensi `M2_memory.md`) → plan mode.

## [2026-09-11] Implementasi M4 Tool Registry v1 — katalog, find_tools, sync via hash, kontrak 1.1.0

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

## [2026-09-17] Commit M4, tool device mock pertama (M5), trace A2 disusun ulang sebagai test

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

## [2026-10-23] Jawaban A2 dari user: Q1 + Q2 diputuskan, Q3-Q5 minta penjelasan

- **Apa yang dikerjakan:** Sesi dibuka setelah jeda ~5 minggu dengan rekap posisi. User menjawab: **Q1 = ya** (turn terputus setelah aksi disimpan sebagian dengan penanda; teks fallback iterasi habis ikut disimpan), **Q2 = ya** (adapter membaca ulang state device setelah perintah tidak terkonfirmasi). Q3 (log aksi durable vs M11), Q4 (arsip gagal: raise atau dicatat), Q5 (profil sebelum sesi) — user minta penjelasan dulu.
- **Koreksi tabel trace:** di S5 (dan S6) caller **tidak** menerima jawaban model; `run_turn` melempar exception dari `save`, jadi teks "Lampu sudah nyala." hanya dibuat model, tidak sampai ke user lewat API saat ini. Klaim "user sudah diberi tahu berhasil" di tabel `M2_memory.md` hanya benar kalau nanti ada UI streaming.
- **Penjelasan yang diberikan (ringkas):** Q3 — log aksi = file terpisah yang ditulis saat aksi, jadi tetap ada walau simpan sesi gagal; tumpang tindih dengan audit log M11. Q4 — masalahnya bukan "mencatat" tapi "melempar": raise membuang jawaban untuk turn yang sudah sukses dan mendorong user mengulang perintah (aksi device bisa jalan dua kali); usulan: kembalikan jawaban + catat + tanda peringatan. Q5 — urutan sesi→profil dipertahankan saat refactor supaya perilaku tidak berubah, keputusannya memang ditunda ke A2.
- **File yang dibuat/diubah:** `Memory Think/SPRINT3_LOG.md` — entry ini.
- **Belum dikerjakan / TODO lanjutan:** jawaban user untuk Q3-Q5 → implementasi A2 → update test trace → commit (menunggu instruksi).

## [2026-10-23] Keputusan A2 final + implementasi

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

## [2026-10-23] Perbaikan 2 celah kecil A2 (poin 9 rekap kekurangan)

- **Apa yang dikerjakan:** User minta poin 9 dari rekap kekurangan diperbaiki dan dites.
  1. **Profil gagal tidak lagi menghilangkan turn.** `Orchestrator._persist`: kalau `ProfileStore.save` gagal, catatan koreksi (`[Saving the user profile failed ...: facts ... were NOT saved ...]`) ditempel ke pesan assistant terakhir, sesi tetap disimpan, exception di-raise (kegagalan simpan sesi saat itu ditempel sebagai note). Helper baru `_append_assistant_note` dipakai juga untuk penanda "turn interrupted".
  2. **Deteksi "turn sudah dimulai" (identitas objek pesan) dihapus.** Mutation test: mengganti pengecekan itu dengan `True` tidak menggagalkan test apa pun, karena setelah A2 setiap turn tersimpan berakhir dengan assistant; cukup cek role pesan terakhir. Kode jadi lebih sederhana dan tidak bergantung pada detail implementasi kompaksi.
  3. Test baru di `test_a2_trace.py`: S6 ditulis ulang (sesi tersimpan + koreksi), S6 aksi device + profil gagal (lampu tetap tercatat), S6 turn terputus + profil gagal (dua catatan, note di exception), kompaksi gagal (tanpa penanda, sesi tidak berubah), kompaksi sukses lalu LLM gagal (penanda ada, ringkasan tersimpan). Mutation check kedua: menghapus pengecekan role → test kompaksi gagal, sesuai harapan.
  4. **247 passed, 3 skipped** (sebelumnya 243).
- **File yang dibuat/diubah:** `backend/orchestrator/orchestrator.py`, `backend/tests/test_a2_trace.py`, `Memory Think/M2_memory.md`, entry ini.
- **Alasan/keputusan:** Koreksi di sesi tetap memenuhi tujuan keputusan 5 (tidak ada klaim palsu yang bertahan) sambil tidak membuang catatan aksi fisik. Urutan profil → sesi → arsip tidak berubah.
- **Belum dikerjakan / TODO lanjutan:** commit (menunggu instruksi user); sisa kekurangan non-modul dari rekap (entry point CLI/server, smoke test API asli, 2 TODO M4, catatan M0/M1/M2 basi, M2 v2 B/D); M5 adapter nyata.

## [2026-10-23] Diskusi: apa yang didaftarkan ke registry saat memakai MQTT / device pihak ketiga

- **Apa yang dikerjakan:** User bertanya apakah F.R.I.D.A.Y nanti akan meminta IP publisher + alamat queue MQTT saat pendaftaran, dan bagaimana kalau memakai beberapa device pihak ketiga. Diskusi saja, tidak ada perubahan kode.
- **Jawaban asisten (belum keputusan):**
  - Registry M4 mendaftarkan **kemampuan** (tool + kontrak), bukan detail koneksi. Tiga lapis: (1) konfigurasi koneksi adapter (host/port broker, kredensial, TLS) ditulis user sekali di config/.env, tidak ditanyakan lewat obrolan dan tidak pernah masuk konteks LLM; (2) daftar device (id, nama, ruangan, jenis, topic) didapat adapter lewat discovery (mis. topic `homeassistant/.../config`, Zigbee2MQTT) atau file daftar; (3) tool per jenis aksi dengan `device_id` enum (pola `MockHomeAdapter`) yang di-`sync` ke katalog.
  - Alasan tidak lewat obrolan: M2 menyimpan percakapan verbatim (sesi + arsip FTS) dan mengirimnya ke API LLM, jadi kredensial akan tersebar; menambah device lewat obrolan bisa jadi fitur nanti di bawah izin M11.
  - Koreksi istilah: MQTT punya **broker** dan **topic**, bukan IP publisher / queue address.
  - Device pihak ketiga: satu adapter = satu `provider` di katalog (sudah didukung `catalog.sync(provider, tools)`). Rekomendasi: Home Assistant sebagai hub (satu adapter untuk banyak merek, ada mode demo tanpa hardware), MQTT langsung kalau device DIY.
- **File yang dibuat/diubah:** `Memory Think/SPRINT3_LOG.md` — entry ini.
- **Belum dikerjakan / TODO lanjutan:** menunggu user memilih jalur device (HA / MQTT langsung / per-vendor) dan menyebut device yang dimiliki → desain adapter M5 nyata.

## [2026-10-23] Diskusi lanjutan: gateway/hub sendiri untuk semua provider (MQTT, LoRa, vendor)

- **Apa yang dikerjakan:** User mengusulkan membuat service/proyek terpisah yang memegang semua koneksi provider (home service, MQTT, LoRa) dan mengekspos satu API; F.R.I.D.A.Y cukup menyimpan akses ke API itu, supaya F.R.I.D.A.Y lebih ringan. Diskusi saja.
- **Jawaban asisten (belum keputusan):**
  - Pola benar: hub/gateway terpisah, F.R.I.D.A.Y hanya punya satu adapter + satu token (di config/.env, bukan lewat obrolan). Home Assistant sudah merupakan gateway seperti itu; membangun sendiri hanya layak untuk bagian yang tidak tertangani HA (mis. protokol LoRa custom), bisa sebagai bridge kecil ke MQTT → HA.
  - Klaim "lebih ringan" dikoreksi: beban utama F.R.I.D.A.Y adalah panggilan LLM, bukan I/O device. Keuntungan nyata gateway: koneksi 24/7 + cache state + retry di luar proses F.R.I.D.A.Y, kredensial provider tidak di F.R.I.D.A.Y, kode F.R.I.D.A.Y tetap satu adapter, F.R.I.D.A.Y bisa restart tanpa memutus device.
  - Opsi bentuk API gateway: REST/WebSocket, atau **MCP server** (cocok dengan desain M4; HA punya integrasi MCP Server — perlu dicek versinya saat desain).
  - LoRa: latensi tinggi dan downlink kelas A hanya setelah uplink, jadi gateway harus melaporkan state "pending" — terkait keputusan A2 no. 2 (baca ulang state).
- **File yang dibuat/diubah:** `Memory Think/SPRINT3_LOG.md` — entry ini.
- **Belum dikerjakan / TODO lanjutan:** user memilih: HA sebagai gateway / gateway sendiri / hibrida; daftar device yang dimiliki (termasuk apakah LoRa sudah ada).

## [2026-10-23] Keputusan user: adapter device nyata DITUNDA — jadi PR untuk versi F.R.I.D.A.Y berikutnya

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

## [2026-10-23] Commit + push mock M5 dan A2

- **Apa yang dikerjakan:** Atas persetujuan user, semua perubahan sejak 2026-09-17 (mock M5, trace A2, implementasi A2 + perbaikan celah kecil, catatan modul, entry log) di-commit sebagai `603471e` (`feat(devices,memory): M5 mock home + M2 v2 A2 error-path persistence`, 11 file) dan di-push ke `origin/master`. Test sebelum commit: 247 passed, 3 skipped.
- **File yang dibuat/diubah:** `Memory Think/SPRINT3_LOG.md` — entry ini (masuk commit berikutnya).
- **Belum dikerjakan / TODO lanjutan:** urutan yang disepakati: (1) pesan untuk tool katalog yang belum dimuat → (2) tool bertahan lintas turn → (3) antarmuka device generik + kontrak Device → (4) state pending di mock → (5) disambiguasi/bertanya balik → (6) CLI → (7) smoke test API asli → (8) koreksi catatan M0/M1/M2.

## [2026-10-23] M4 TODO #1: memanggil tool katalog yang belum dimuat — `AutoLoadPolicy`

- **Apa yang dikerjakan:** Asisten menawarkan (a) pesan yang mengarahkan ke `find_tools` atau (b) dimuat otomatis, dengan saran: (b) untuk read-only, (a) untuk yang mengubah sesuatu. User: jadikan kondisi, semua opsi tetap bisa dipakai. Implementasi `AutoLoadPolicy` (`read_only` default / `all` / `never`) lewat parameter `Orchestrator(catalog_auto_load=...)`; detail di `M4_tool_registry.md`.
- **File yang dibuat/diubah:** `backend/agent_core/{tool_registry,loop}.py`, `backend/registry/{discovery_tool,__init__}.py`, `backend/orchestrator/orchestrator.py`, `backend/tests/test_catalog_auto_load.py` (baru, 11 test), `backend/tests/test_orchestrator_catalog.py` (1 assertion), `Memory Think/M4_tool_registry.md`, entry ini.
- **Hasil:** **258 passed, 3 skipped** (sebelumnya 247). Mutation check: default `all` → 2 test gagal, sesuai harapan.
- **Alasan/keputusan:** aksi yang mengubah dunia tetap lewat jalur yang dipilih sengaja (deskripsi + tier terlihat, bekal M11); pembacaan tidak membuang langkah. Arah dependensi tetap `registry` → `agent_core`.
- **Belum dikerjakan / TODO lanjutan:** belum di-commit. Berikutnya: TODO M4 #2 (tool bertahan lintas turn) → antarmuka device generik → pending di mock → disambiguasi → CLI → smoke test → catatan M0/M1/M2.

## [2026-10-23] M4 TODO #2: tool bertahan lintas turn — `tool_retention_turns`

- **Apa yang dikerjakan:** Asisten menawarkan (a) selama sesi, (b) beberapa turn (MemTool), (c) tetap seperti sekarang; saran (b) dijadikan pengaturan. User setuju. Implementasi `Orchestrator(tool_retention_turns=3 | None | 0)` dengan helper `recently_used_tool_names` yang membaca riwayat sesi (tanpa state baru); hanya panggilan berhasil yang dihitung. Detail di `M4_tool_registry.md`.
- **File yang dibuat/diubah:** `backend/registry/retention.py` (baru), `backend/registry/__init__.py`, `backend/orchestrator/orchestrator.py` (wiring + docstring kelas), `backend/tests/test_tool_retention.py` (baru, 8 test), `Memory Think/M4_tool_registry.md`, entry ini.
- **Hasil:** **266 passed, 3 skipped** (sebelumnya 258). Dua mutation check tertangkap test. Test lama `test_tools_loaded_in_one_turn_are_gone_at_the_start_of_the_next` tetap lulus tanpa diubah (tool di sana hanya dimuat, tidak dipakai).
- **Belum dikerjakan / TODO lanjutan:** belum di-commit (bersama `AutoLoadPolicy`). Berikutnya: antarmuka device generik + kontrak Device → pending di mock → disambiguasi → CLI → smoke test → catatan M0/M1/M2.

## [2026-10-23] Commit TODO M4 + CLI pertama (`python -m backend.cli`)

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

## [2026-10-23] Smoke test API asli lewat CLI (model `claude-haiku-4-5`)

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

## [2026-10-23] Sesi ditutup — checkpoint untuk besok

- **Apa yang dikerjakan:** User pulang; minta pembahasan terakhir dicatat lalu di-push. Perubahan yang belum di-commit (CLI `backend/cli.py` + `test_cli.py` + entry log sejak `d327685`) di-commit dan di-push bersama entry ini.
- **Posisi saat ditutup:** Sprint 3. Selesai hari ini: keputusan + implementasi A2 (`603471e`), 2 TODO M4 (`d327685`), CLI, smoke test API asli 8/8. Test: 280 passed, 3 skipped.
- **Menunggu dari user:** hasil terminal percobaan CLI-nya sendiri (Cara 1) untuk dibandingkan dengan smoke test asisten.
- **Langkah berikutnya (urutan yang diusulkan asisten, belum dikonfirmasi user):**
  1. Perbaikan kecil dari smoke test: zona waktu lokal untuk `get_current_time`; instruksi blok profil (fakta profil = sumber utama, `recall_memory` untuk percakapan lama).
  2. Antarmuka device generik (`list_devices` / `read_state` / `apply`) + kontrak Device M0 + nama key state yang jelas (`target_temperature`).
  3. State "pending" di mock → disambiguasi / bertanya balik → koreksi catatan M0/M1/M2 (penutup Sprint 3).
- **PR user (versi berikutnya, butuh perangkat nyata):** lihat entry "adapter device nyata DITUNDA" hari ini.

## [2026-10-25] Dokumen tinjauan proyek untuk feedback model AI lain (`FRIDAY_PROJECT_REVIEW.md`)

- **Apa yang dikerjakan:** Sesi dibuka dengan rekap posisi. User minta satu file `.md` di root repo yang menjelaskan proyek dan seluruh roadmap sprint, menyertakan semua log sprint (done dan on progress), kekurangan tiap sprint, dan (permintaan susulan) potongan kode/logika yang perlu disesuaikan dan dimintai feedback. Tujuannya: dibagikan ke beberapa model AI untuk minta feedback.
  1. Isi: ringkasan proyek, prinsip desain, arsitektur saat ini, roadmap 12 sprint + status, per sprint (yang dikerjakan, keputusan, kekurangan), kekurangan lintas sprint, §9 sepuluh potongan kode dengan masalah dan pertanyaan, §10 pertanyaan untuk reviewer, Lampiran A–C = tiga log sprint apa adanya (heading diturunkan dua tingkat).
  2. Angka diverifikasi ulang: test **280 passed, 3 skipped**; ±3.900 baris Python non-test; 25 file test; 23 commit.
  3. **Temuan baru saat menyusun (belum diperbaiki):** `compact()` (`backend/memory/compaction.py`) — kalau LLM mengembalikan teks kosong, ringkasan lama dipertahankan tetapi pesan lama tetap dipindah keluar dari konteks aktif, sehingga isinya hilang dari konteks tanpa peringatan (masih ada di arsip). Bertentangan dengan prinsip fail loud. Temuan lain yang dicatat sebagai bahan feedback: tidak ada prompt caching (`cache_control`) sama sekali; `AutoLoadPolicy` mempercayai `read_only_hint` dari penyedia tool; hasil tool tanpa batas ukuran; blok profil tanpa batas.
- **File yang dibuat/diubah:** `FRIDAY_PROJECT_REVIEW.md` (baru, root repo), `Memory Think/SPRINT3_LOG.md` (entry ini).
- **Belum dikerjakan / TODO lanjutan:** belum di-commit (menunggu instruksi user). Perbaikan `compact()` untuk respons kosong menunggu persetujuan user. Langkah Sprint 3 berikutnya tidak berubah (zona waktu + instruksi profil → antarmuka device generik → pending/disambiguasi → koreksi catatan M0/M1/M2). Masukan dari model AI lain akan dicatat sebagai entry baru setelah user menempelkannya.

## [2026-10-25] Feedback 4 model AI masuk — dibaca dan diringkas per model

- **Apa yang dikerjakan:** User menaruh 4 file feedback atas `FRIDAY_PROJECT_REVIEW.md` di `Memory Think/feedback_another_ai/`: ChatGPT (`FRIDAY_FEEDBACK_REVIEW-chatgpt.md`, paling rinci), DeepSeek (`deepseek_markdown_20261025_38c8c2.md`), Gemini (`f_r_i_d_a_y_tinjauan_dan_feedback_proyek-gemini.md`), Copilot (`FRIDAY_AI_Feedback-copilot.md`). User minta: jelaskan pendapat masing-masing satu per satu dengan bahasa awam dulu; usulan apa yang akan dijalankan harus diberitahukan dulu sebelum dikerjakan, dan disesuaikan dengan alur yang sudah disepakati.
- **Kesepakatan keempatnya:** perbaiki bug kompaksi respons kosong; majukan versi mini M11 (izin) dan M16 (evaluasi); `read_only_hint` tidak boleh jadi sumber izin; format pesan masih terikat Anthropic; batasi ukuran hasil tool dan blok profil; device shadow (desired/reported) + `target_temperature`; ukur `find_tools` vs semua tool sebelum memilih.
- **Perbedaan pendapat utama:** satu SQLite bertransaksi (DeepSeek, Gemini: sekarang; Copilot: nanti; ChatGPT: jangan dulu, transaksi DB tidak bisa me-rollback lampu, buat action journal dulu); konfirmasi untuk STANDARD (Gemini: ya; Copilot/DeepSeek: hanya CRITICAL); zona waktu (Gemini: profil; ChatGPT/DeepSeek: config; Copilot: config + override); retensi tool (DeepSeek/Gemini: state eksplisit; Copilot: pertahankan riwayat; ChatGPT: tergantung definisi); pencarian (Gemini: embedding `sqlite-vec`; lainnya: FTS5 dulu, ukur).
- **Diverifikasi di kode:** temuan ChatGPT benar — `json.dumps(result)` di `_execute_tool_call` (`backend/agent_core/loop.py`) berada di luar `try`, jadi hasil tool yang tidak bisa diserialisasi akan crash meski docstring bilang "never raises". `output_schema` tidak divalidasi saat runtime (hanya di 2 test `find_tools`). Klaim DeepSeek "deteksi turn terputus fragile, dibuktikan mutation test" keliru baca: mutation test justru menunjukkan pengecekan role dijaga test.
- **File yang dibuat/diubah:** `Memory Think/SPRINT3_LOG.md` — entry ini.
- **Belum dikerjakan / TODO lanjutan:** ringkasan per model sudah disampaikan ke user. Berikutnya: usulan rencana adopsi (apa diambil, apa ditolak, alasan, urutan) disampaikan ke user untuk disetujui sebelum ada perubahan kode. Belum ada commit.

## [2026-10-25] Usulan rencana asisten setelah feedback 4 model AI (belum disetujui)

- **Apa yang dikerjakan:** User minta usulan rencana dari asisten. Disusun 5 tahap, mempertahankan alur Sprint 3 yang sudah disepakati (perbaikan kecil → antarmuka device → pending/disambiguasi → catatan) dan menyisipkan masukan yang disetujui:
  - **Tahap 1 — perbaikan bug kecil (Sprint 3):** kompaksi respons kosong tidak mengubah sesi; `json.dumps` hasil tool masuk pengaman error; batas ukuran hasil tool (JSON tetap valid, penanda `truncated`); pesan error ke model dipendekkan; Ctrl+C menyimpan turn parsial; `max_iterations` 6 → 10; zona waktu dari config; instruksi blok profil.
  - **Tahap 2 — kontrak Device (Sprint 3):** pola device shadow (`desired`/`reported`/koneksi/`pending`/`operation_id`), `target_temperature` vs `current_temperature`, tool spesifik untuk model + `apply` generik di dalam adapter, toleransi nilai analog.
  - **Tahap 3 — penutup Sprint 3:** pending di mock + disambiguasi (2 lampu satu ruangan) + koreksi catatan M0/M1/M2 + README + `STATUS.md` satu halaman.
  - **Tahap 4 — Sprint 4 = mini-M11 + buku catatan aksi:** gerbang izin di titik eksekusi (cari → cek argumen → cek izin → jalankan → catat); klasifikasi alat dari config pemilik, bukan `read_only_hint`; READ_ONLY & STANDARD otomatis (STANDARD bisa diatur minta konfirmasi), CRITICAL konfirmasi y/n terikat aksi + kedaluwarsa, alat mengubah dunia yang belum terklasifikasi ditolak; action journal SQLite PREPARED→SUCCEEDED/FAILED/UNKNOWN (menutup S5), saat start dilaporkan, tidak diulang otomatis; label "data, bukan perintah" untuk hasil `recall_memory`/tool; tolak dua aksi ke device yang sama dalam satu respons.
  - **Tahap 5 — Sprint 4 paralel = mini-M16 + observability:** ±15–20 skenario uji (FakeLLM di pytest + runner LLM asli manual), metrik (tugas selesai, alat benar, klaim sukses palsu, aksi tanpa izin, token, latensi, biaya), trace per turn JSONL; eksperimen berbasis data: `find_tools` vs semua alat, prompt caching, baseline pencarian bahasa Indonesia.
  - **Ditunda / ditolak (dengan alasan):** satu SQLite sekarang (ditunda sampai ada akses bersamaan; journal dulu); embedding (tunggu data baseline); konfirmasi semua STANDARD sebagai default (ditolak, jadi opsi); zona waktu hanya di profil (ditolak, config dulu); format pesan internal + status turn terstruktur (digabung jadi satu perubahan skema sebelum Sprint 8); retensi tetap dari riwayat; juri LLM untuk ringkasan (setelah ada harness); pindah ke GitHub Issues (cukup `STATUS.md`).
- **File yang dibuat/diubah:** `Memory Think/SPRINT3_LOG.md` — entry ini.
- **Belum dikerjakan / TODO lanjutan:** menunggu persetujuan user dan 3 keputusan (konfirmasi STANDARD, CI GitHub Actions, posisi mini-M11/M16 di Sprint 4). Belum ada perubahan kode.

## [2026-10-25] Rencana disetujui; Tahap 1 (perbaikan bug dan hal kecil) selesai

- **Apa yang dikerjakan:** User menyetujui rencana 5 tahap. Tiga keputusan memakai usulan asisten: STANDARD (lampu/AC) tetap otomatis, bisa diatur minta konfirmasi (dikerjakan di Tahap 4); CI GitHub Actions dengan LLM palsu saja; mini-M11 + mini-M16 di awal Sprint 4. Tahap 1 dikerjakan:
  1. **Kompaksi** (`backend/memory/compaction.py`): ringkasan kosong/spasi saja → `CompactionError` baru (`backend/memory/errors.py`, subclass `SessionError`) sebelum sesi diubah. `run_agent` menangkapnya, turn jalan terus dengan konteks utuh, `AgentResult.warnings` berisi "compaction skipped" (tampil di CLI). Exception API saat kompaksi tetap dilempar seperti sebelumnya. Ringkasan disimpan setelah di-`strip()`.
  2. **Serialisasi** (`backend/agent_core/loop.py`): `json.dumps` hasil tool masuk pengaman; gagal → tool_result error ("bug in the tool, not in your call"). `ensure_ascii=False` supaya teks Indonesia terbaca apa adanya (dan lebih hemat token).
  3. **Batas ukuran hasil tool:** `TOOL_RESULT_MAX_CHARS` (default 8000 karakter, batas pengaman bukan hasil tuning). Lebih panjang → `{"truncated": true, "original_chars", "preview", "note"}`, JSON tetap valid.
  4. **Pesan error tool:** menyebut tipe exception, teks dipotong di 500 karakter (`TOOL_ERROR_MAX_CHARS`), traceback lengkap ke log lokal (`logging`). Catatan jujur: ini bukan sanitasi penuh; pemisahan "error untuk model" vs "detail internal" yang sebenarnya menunggu adapter nyata/M11.
  5. **Ctrl+C:** `Orchestrator.run_turn` menangani `KeyboardInterrupt` seperti kegagalan lain (penanda turn terputus, simpan, raise ulang); CLI menampilkan `[interrupted]` dan tetap hidup.
  6. **Batas langkah** 6 → 10 (`DEFAULT_MAX_ITERATIONS`, dipakai `run_agent` dan `Orchestrator`).
  7. **Zona waktu:** `get_current_time` 1.1.0 mengembalikan waktu lokal + `timezone` + `utc_offset`; zona dari `FRIDAY_TIMEZONE` (IANA), kosong = zona OS; nama zona salah = error (fail loud). Dependensi baru `tzdata` (Windows tidak punya basis data zona waktu). `.env` milik user tidak diubah (tanpa `FRIDAY_TIMEZONE` dipakai zona OS); `.env.example` diberi contoh `Asia/Jakarta`.
  8. **Instruksi blok profil** (`Profile.to_context_block`): fakta profil = sumber utama, jawab langsung; `recall_memory` hanya untuk hal di percakapan lama yang tidak ada di profil.
  9. **CI:** `.github/workflows/tests.yml` (pytest di ubuntu + windows, Python 3.13, tanpa API key). Belum pernah jalan — baru aktif setelah di-push.
- **Test:** file baru `backend/tests/test_hardening_stage1.py` (23 kasus). **303 passed, 3 skipped** (sebelumnya 280); test lama tidak diubah. Mutation check: kompaksi lama → 5 gagal; pengaman serialisasi dicopot → 1 gagal; batas ukuran dicopot → 2 gagal; Ctrl+C tidak ditangani → 1 gagal; instruksi profil diubah → 1 gagal.
- **Catatan teknis:** beberapa file sempat tersimpan dengan akhir baris CRLF oleh skrip edit; dinormalkan kembali ke LF (repo memakai `core.autocrlf=input`).
- **File yang dibuat/diubah:** `backend/agent_core/{config,loop}.py`, `backend/agent_core/tools/time_tool.py`, `backend/memory/{compaction,errors,profile,__init__}.py`, `backend/orchestrator/orchestrator.py`, `backend/cli.py`, `backend/tests/test_hardening_stage1.py` (baru), `.github/workflows/tests.yml` (baru), `requirements.txt`, `.env.example`, entry ini.
- **Belum dikerjakan / TODO lanjutan:** belum di-commit (menunggu instruksi user). Berikutnya Tahap 2: kontrak Device (desired/reported/koneksi/pending/operation_id, `target_temperature`, tool spesifik + `apply` generik, toleransi nilai analog).

## [2026-10-25] Commit + push dokumen tinjauan, feedback 4 AI, dan Tahap 1

- **Apa yang dikerjakan:** Atas instruksi user ("commit dan push, sertakan semua pembahasan di log"), test dijalankan ulang (**303 passed, 3 skipped**), lalu dibuat 3 commit dan di-push ke `origin/master`:
  1. `211304a` — `docs: project review for external feedback + feedback from 4 AI models` (`FRIDAY_PROJECT_REVIEW.md` + 4 file di `Memory Think/feedback_another_ai/`, disimpan apa adanya).
  2. `4526593` — `fix(core): stage 1 hardening after external review` (kode Tahap 1, test baru, CI `.github/workflows/tests.yml`, `requirements.txt` + `tzdata`, `.env.example`, dan entry log hari ini: dokumen tinjauan, ringkasan feedback, usulan rencana, Tahap 1).
  3. Commit docs berisi entry ini (precedent `2586d33`, `bb4bb59`, `e850b65`).
- **Pembahasan hari ini yang tercatat di log (urut):** rekap posisi → pembuatan `FRIDAY_PROJECT_REVIEW.md` (+ permintaan susulan menyertakan potongan kode) → 4 feedback dibaca dan diringkas per model → usulan rencana 5 tahap + yang ditunda/ditolak → user setuju (3 keputusan memakai usulan asisten) → Tahap 1 selesai → commit + push (entry ini).
- **Catatan:** CI baru akan berjalan pertama kali karena push ini; hasilnya dicek di tab Actions GitHub. `.env` tidak ikut commit (gitignored).
- **File yang dibuat/diubah:** `Memory Think/SPRINT3_LOG.md` — entry ini.
- **Belum dikerjakan / TODO lanjutan:** Tahap 2 (kontrak Device: desired/reported/koneksi, status perintah + `operation_id`, `target_temperature`/`current_temperature`, tool spesifik + `apply` generik, toleransi nilai analog) — menunggu aba-aba user.

## [2026-10-25] `gh` terpasang + CI pertama hijau; Tahap 2 (kontrak Device) selesai

- **`gh` (GitHub CLI):** user bertanya apa itu `gh`, lokasi pemasangan `winget` (selalu `C:\Program Files\GitHub CLI\`, bukan folder aktif), dan HTTPS vs SSH (disarankan HTTPS: remote repo sudah HTTPS, `gh` mengatur kredensial git, port 443 jarang diblokir). User memasang dan login (akun `Lux7San`, HTTPS, scope `repo`/`workflow`/`gist`/`read:org`). Sesi ini memanggil `gh` lewat path lengkap karena PATH belum ter-refresh.
- **CI pertama (`c69fe6a`): hijau** — ubuntu 306 passed (3 test izin file POSIX ikut jalan dan lulus untuk pertama kali), windows 303 passed + 3 skipped. Peringatan: `actions/checkout@v4` dan `actions/setup-python@v5` memakai Node.js 20 yang usang → dinaikkan ke `@v7` (keduanya `node24`, rilis v7.0.0 Jun/Jul 2026, input `python-version`/`cache` dicek masih ada).
- **User: "lanjut ke tahap 2, masih Sprint 3?"** → ya; Tahap 1–3 = sisa Sprint 3, Tahap 4–5 = awal Sprint 4.
- **Tahap 2 dikerjakan** (detail di `M5_device_layer.md` bagian 2026-10-25, ringkasan kontrak di `M0_contract_layer.md`):
  1. Kontrak Device M0 `backend/schemas/device_contract.py` (1.0.0).
  2. `DeviceService` (`backend/devices/service.py`): validasi sebelum driver disentuh, `operation_id`, `CommandStatus`, shadow desired/reported, baca ulang dengan toleransi. `DeviceError` pindah ke sini (tetap diekspor dari `backend.devices`).
  3. `build_device_tools` (`backend/devices/tools.py`): tool dibuat dari kemampuan; status bukan `succeeded` → tool error berisi status + `operation_id`.
  4. `MockHome` jadi driver tipis + `descriptors()`; AC: `target_temperature` + `current_temperature` (29,0). `MockHomeAdapter` tetap ada (CLI/test tidak perlu berubah cara pakainya).
- **Test lama yang diubah (semua karena perubahan nama/key yang disengaja):** `test_mock_home.py` (nama tool `home_set_brightness`/`home_set_target_temperature`, key `target_temperature`, `home_get_state` → `["reported"]`), `test_a2_trace.py` S9 (snapshot AC dengan key baru), `test_cli.py` (baca perangkat offline sekarang snapshot `connection: offline`, bukan `[error]`).
- **Temuan saat menulis test:** `True == 1` di Python membuat laporan `1` dianggap "nyala" → perbandingan boolean dibuat ketat (driver wajib menormalkan).
- **Test:** file baru `backend/tests/test_device_layer.py` (29 kasus). **332 passed, 3 skipped** (sebelumnya 303). Mutation check: toleransi dicopot → 2 gagal; validasi dicopot → 3; baca ulang dicopot → 2; `stale` dicopot → 1; status non-sukses tidak jadi error → 4.
- **File yang dibuat/diubah:** baru `backend/schemas/device_contract.py`, `backend/devices/{service,tools}.py`, `backend/tests/test_device_layer.py`; diubah `backend/devices/{__init__,mock_home}.py`, 3 file test di atas, `.github/workflows/tests.yml`, `Memory Think/{M5_device_layer,M0_contract_layer}.md`, entry ini.
- **Belum dikerjakan / TODO lanjutan:** belum di-commit (menunggu instruksi user). Berikutnya Tahap 3 (penutup Sprint 3): state `pending` di mock (perangkat lambat), disambiguasi ("lampu yang mana?"), koreksi catatan M0/M1/M2 + README, `STATUS.md`.

## [2026-10-25] Diskusi Node.js di CI + CI dikunci ke SHA commit

- **Pertanyaan user:** kenapa Node.js 20, bukannya 22/24, karena ada isu keamanan. **Jawaban:** F.R.I.D.A.Y tidak memakai Node.js sama sekali (Python murni); Node hanya runtime di dalam dua komponen CI GitHub (`actions/checkout`, `actions/setup-python`). Versi `@v4`/`@v5` di file CI pertama (kesalahan asisten memakai versi lama) membawa Node 20, yang sudah EOL (April 2026, tanpa patch keamanan). Sudah dinaikkan ke v7 (Node 24) di Tahap 2. Isu spesifik "2–4 file" yang disebut user tidak diketahui asisten — diminta link/nama kasusnya kalau ada, tidak ditebak. Risiko bagi proyek kecil: runner GitHub sementara, tanpa secret, test pakai LLM palsu.
- **Disetujui user, dikerjakan:** komponen CI dikunci ke **SHA commit penuh** (tag seperti `@v7` bisa dipindah pemiliknya atau peretas — pola serangan rantai pasok GitHub Actions): `actions/checkout@3d3c42e…` (v7.0.1, rilis 2026-07-20) dan `actions/setup-python@5fda3b9…` (**v7.0.0**, rilis 2026-07-20; v7.1.0 dilewati karena baru dirilis 2026-10-22, terlalu baru). SHA diambil dari ref tag di repo resmi lewat `gh api` dan dicek ada di repo itu; `node24` dan input `python-version`/`cache` dicek. Ditambah `permissions: contents: read` (CI hanya membaca repo).
- **File yang dibuat/diubah:** `.github/workflows/tests.yml`, entry ini.
- **Belum dikerjakan / TODO lanjutan:** CI dengan SHA baru terverifikasi setelah push. Saat memperbarui komponen CI, SHA dan komentar versi diganti bersamaan. Commit Tahap 2 menunggu instruksi user.

## [2026-10-25] `setup-python` → v7.1.0 + cek Node.js/PHP di komputer user

- **User bertanya kenapa tidak v7.1.0.** Dicek lewat `gh` (release notes + compare v7.0.0...v7.1.0, 16 commit): v7.1.0 berisi 2 PR perbaikan keamanan "npm audit high severity" (#1347, #1350: `undici` 3 advisory, `brace-expansion` 2, `js-yaml`, `fast-xml-parser`) yang mengubah `dist/setup/index.js` = kode yang benar-benar jalan di CI; sisanya fitur `mirror`, pesan error, cache 6.3.0, bump Dependabot. Tidak ada issue baru sejak rilis 2026-10-22; tag resmi `v7` sudah menunjuk v7.1.0. **Alasan asisten memilih v7.0.0 ("terlalu baru") keliru** — versi itu membawa celah yang sudah diketahui. User setuju → dikunci ke `actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0  # v7.1.0`.
- **Alasan user minta versi terbaru:** berita celah keamanan baru di PHP dan Node.js. Dicek di komputer user (bukan bagian F.R.I.D.A.Y):
  - **Node.js v24.20.0** (`C:\Program Files\nodejs`, juga menjalankan Claude Code). Terbaru di jalur 24 LTS: **v24.22.1 (2026-10-20), rilis keamanan** — CVE-2026-105481/105482/105483/106069/106073/106074/111497 (http, dns, tls, permission model, crypto, brotli) + OpenSSL 3.5.9, undici 7.30.1, sertifikat root NSS 3.131.1. User tertinggal 3 rilis.
  - **PHP 8.4.4** (XAMPP Lite, `C:\xampp_lite8\apps\php`, build Feb 2025). Terbaru: **PHP 8.4.27 (21–22 Okt 2026), rilis keamanan** (GHSA-w8hw-w9fx-j79w, GHSA-6wmf-4rv5-p3rp, banyak perbaikan use-after-free). User tertinggal 23 rilis patch.
  - Keduanya disarankan diperbarui oleh user sendiri (instalasi sistem, di luar repo); asisten tidak menjalankan upgrade.
- **File yang dibuat/diubah:** `.github/workflows/tests.yml`, entry ini.
- **Belum dikerjakan / TODO lanjutan:** commit Tahap 2 + perubahan CI (menunggu instruksi user); update Node.js/PHP oleh user.

## [2026-10-25] Commit + push Tahap 2 dan CI

- **Apa yang dikerjakan:** Atas instruksi user, test dijalankan ulang (**332 passed, 3 skipped**), lalu di-push ke `origin/master`:
  1. `24125dc` — `ci: pin actions to commit SHAs (Node 24), read-only permissions` (`actions/checkout` v7.0.1, `actions/setup-python` v7.1.0, `permissions: contents: read`).
  2. `fadca24` — `feat(devices): device contract + generic device layer (stage 2)` (kontrak Device, `DeviceService`, `build_device_tools`, mock sebagai driver, test baru + 3 test lama yang disesuaikan, catatan M0/M5, entry log hari ini).
  3. Commit docs berisi entry ini.
- **Belum dikerjakan / TODO lanjutan:** cek hasil CI dengan SHA baru (lewat `gh run list`). Berikutnya Tahap 3: `pending` di mock, disambiguasi, koreksi catatan M0/M1/M2 + README, `STATUS.md`.
