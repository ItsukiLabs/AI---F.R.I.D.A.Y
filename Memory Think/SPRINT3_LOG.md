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
