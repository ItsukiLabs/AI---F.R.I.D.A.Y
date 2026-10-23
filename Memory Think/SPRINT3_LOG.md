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
