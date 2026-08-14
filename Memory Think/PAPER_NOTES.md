# F.R.I.D.A.Y — Memori Pembelajaran Paper & Jurnal

> Catatan pembelajaran dari paper/jurnal di `Paper & Journal/F.R.I.D.A.Y/`. Disusun berdasarkan 16 kategori riset dari `Memory Think/sprint-paper-mapping.md`. Tujuannya: jadi rujukan cepat "paper ini bilang apa, dan relevan ke bagian F.R.I.D.A.Y yang mana" — supaya keputusan desain di kode tidak ambigu dan bisa dilacak balik ke sumbernya.
>
> File ini sengaja ditaruh di `Memory Think/` (bukan di dalam `Paper & Journal/`) supaya folder paper tetap murni berisi data (PDF), tidak tercampur dengan catatan olahan.
>
> **Setiap entry punya field "Sumber informasi"** yang menjelaskan dari mana isi catatan ini benar-benar diambil — supaya jelas mana yang bisa dipercaya langsung dan mana yang perlu dibaca ulang manual sebelum dijadikan dasar keputusan kode. Legend:
> - `Teks penuh` — dibaca langsung dari isi file PDF secara utuh/mendalam
> - `Ekstraksi parsial` — hanya sebagian file yang terbaca (biasanya abstract + intro + kesimpulan via ekstraksi teks/pdftotext, karena PDF terlalu panjang atau tool render halaman tidak tersedia di environment ini), bagian tengah diasumsikan konsisten
> - `Pengetahuan umum` — file gagal diekstrak berulang kali; isi catatan berasal dari pengetahuan model tentang paper ini, **belum terverifikasi dari file lokal**
> - `MISMATCH` — isi file PDF di folder ini **tidak cocok** dengan judul nama filenya; catatan (kalau ada) ditulis dari pengetahuan umum tentang paper yang seharusnya, file lokal perlu diganti
> - `DILEWATI` — file tidak dibuka sama sekali (memicu error teknis/safety filter berulang saat proses otomatis), perlu ditinjau manual oleh user
> - `Gagal dibaca` — file di luar kapasitas tool baca (ukuran/halaman) dan tidak ada fallback yang berhasil

> **[2026-08-12] Skema folder dirombak jadi per-modul.** Folder fisik di `Paper & Journal/F.R.I.D.A.Y/` sekarang `M0/` s.d. `M17/` (bukan lagi folder angka `1-5` atau folder tematik lama), supaya struktur folder langsung mencerminkan modul roadmap. Tiap paper ditaruh di **satu folder modul utama** (yang paling wajib/kritis menurut `sprint-paper-mapping.md`); paper yang relevan lintas modul (MCP, Agent-OS, HearthNet, OSWorld 2.0, dll.) tetap cuma satu salinan fisik — relevansi ke modul lain tetap dicatat di teks entry masing-masing, bukan digandakan filenya. Semua path `Lokasi file` di bawah sudah diupdate mengikuti skema baru. Tiga file mismatch tanpa kategori jelas (belum ketahuan modulnya) sengaja belum dipindah — lihat bagian **File Bermasalah**.

---

## Kategori #1 — Agentic AI / Tool Use & Function Calling

### A Survey on Large Language Model based Autonomous Agents (2023)
- **Lokasi file:** `M1/A Survey on Large Language Model based Autonomous Agents (2023).pdf`
- **Sprint/Modul terkait:** Sprint 1 (M0+M1) — juga rujukan lintas Sprint 2, 6, dan Multi-Agent Orchestration
- **Ide inti:** Survey ini mengusulkan unified framework agen LLM dengan modul Profiling, Memory, Planning, dan Action, lalu meninjau strategi konstruksi agen, area aplikasi, dan strategi evaluasi.
- **Relevansi ke F.R.I.D.A.Y:** Blueprint arsitektur modular untuk agent core — pemisahan Profiling (persona), Memory, Planning, Action bisa langsung dipetakan ke modul M0-M3 sebagai kerangka desain awal.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan via pdftotext (paper survey panjang, bagian tengah di-skim)
- **Catatan tambahan:** Sifatnya generik/survey, tidak ada resep implementasi konkret — cocok sebagai peta konsep awal, bukan panduan teknis detail.

### Agentic Artificial Intelligence (AI): Architectures, Taxonomies, and Evaluation of Large Language Model Agents (2026)
- **Lokasi file:** `M1/Agentic Artificial Intelligence (AI) Architectures, Taxonomies, and Evaluation of Large Language Model Agents (2026).pdf`
- **Sprint/Modul terkait:** Sprint 1 (M0+M1) — juga menyentuh Sprint 6, Multi-Agent, Security, dan Evaluation lewat metrik CLASSic
- **Ide inti:** Taksonomi terbaru yang membedah agen LLM ke 6 dimensi (Core Components, Cognitive Architecture, Learning, Multi-Agent Systems, Environments, Evaluation), menekankan inference-time reasoning, MCP, native computer-use, controllable orchestration, dan evaluasi via CLASSic (cost, latency, accuracy, security, stability).
- **Relevansi ke F.R.I.D.A.Y:** Paling dekat dengan kebutuhan nyata proyek — MCP untuk tool-calling (M1), computer-use untuk device/OS control (M4), controllable orchestration untuk multi-agent, CLASSic sebagai kerangka evaluasi holistik (kategori 16).
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan via pdftotext
- **Catatan tambahan:** Paper sangat baru dan luas, banyak referensi ke rilis 2025 yang klaimnya belum tervalidasi ketat — perlakukan sebagai peta arah, bukan kebenaran final.

### Gorilla: Large Language Model Connected with Massive APIs (2023)
- **Lokasi file:** `M1/Gorilla Large Language Model Connected with Massive APIs (2023).pdf`
- **Sprint/Modul terkait:** Sprint 1 (M0+M1)
- **Ide inti:** LLaMA-7B yang di-finetune untuk menghasilkan API call akurat dari >1600 API ML, dikombinasikan retriever dokumentasi API saat inference — mengungguli GPT-4 dalam akurasi call dan mengurangi halusinasi API.
- **Relevansi ke F.R.I.D.A.Y:** Pendekatan retrieval-aware fine-tuning untuk tool-calling akurat — relevan kalau F.R.I.D.A.Y punya banyak skill custom IoT/OS dan butuh akurasi tool-call tinggi tanpa selalu bergantung model besar generik.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan via pdftotext
- **Catatan tambahan:** Butuh fine-tuning plus dataset API besar (mahal) — versi awal F.R.I.D.A.Y cukup pakai function-calling native LLM komersial; pendekatan Gorilla lebih cocok jadi optimisasi lanjutan di M11.

### ReAct: Synergizing Reasoning and Acting in Language Models (2022)
- **Lokasi file:** `M1/ReAct Synergizing Reasoning and Acting in Language Models (2022).pdf`
- **Sprint/Modul terkait:** Sprint 1 (M0+M1) — ⭐ Wajib
- **Ide inti:** Menggabungkan reasoning verbal (thought) dan aksi (tool call) secara interleaved dalam satu trajectory — thought membantu tracking/adjust plan, aksi mengambil info eksternal sehingga mengurangi halusinasi dibanding CoT murni.
- **Relevansi ke F.R.I.D.A.Y:** Pola dasar loop agent (Thought → Action → Observation → Thought...) — langsung dipakai sebagai kerangka loop utama agent core (M1).
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan via pdftotext (paper 63 halaman)
- **Catatan tambahan:** Rawan terjebak loop berulang tanpa progres — perlu guard/heuristic timeout; ini justru motivasi langsung munculnya Reflexion sebagai mekanisme recovery.

### Reflexion: Language Agents with Verbal Reinforcement Learning (2023)
- **Lokasi file:** `M1/Reflexion Language Agents with Verbal Reinforcement Learning (2023).pdf`
- **Sprint/Modul terkait:** Sprint 1 (M0+M1) — juga relevan Sprint 2 (Memory episodik) dan Sprint 6 (self-correction)
- **Ide inti:** Agen menghasilkan refleksi verbal (bukan update bobot) dari feedback biner/skalar, menyimpannya di memori episodik, dan memakainya sebagai konteks tambahan di trial berikutnya — naik signifikan di ALFWorld/HotPotQA/HumanEval tanpa fine-tuning.
- **Relevansi ke F.R.I.D.A.Y:** Mekanisme "belajar dari kesalahan" tanpa training ulang, pas untuk asisten lintas-sesi — simpan refleksi kegagalan tool-call/plan sebagai bagian memory (M2).
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan via pdftotext
- **Catatan tambahan:** Butuh sinyal evaluasi jelas (binary success/fail) — perlu dirancang "evaluator" per jenis tugas agar refleksi punya sinyal yang bisa dipercaya.

### Toolformer: Language Models Can Teach Themselves to Use Tools (2023)
- **Lokasi file:** `M1/Toolformer Language Models Can Teach Themselves to Use Tools (2023).pdf`
- **Sprint/Modul terkait:** Sprint 1 (M0+M1) — ⭐ Wajib
- **Ide inti:** LLM mengajari dirinya sendiri kapan memanggil tool secara self-supervised — men-sample kandidat API call, memfilter yang benar-benar menurunkan loss prediksi token, lalu finetune pada data yang sudah diberi anotasi.
- **Relevansi ke F.R.I.D.A.Y:** Prinsip filtering "tool call yang benar-benar membantu" berguna sebagai kriteria tool-selection — tool dipanggil hanya kalau mengurangi ketidakpastian, penting untuk efisiensi biaya/latensi saat F.R.I.D.A.Y punya banyak tool IoT/OS.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan via pdftotext
- **Catatan tambahan:** Tidak mendukung chaining tool (output A → input B) karena disample independen dan sensitif wording — kalau butuh multi-hop tool use, ReAct/Decomposed Prompting lebih cocok.

### The Model Context Protocol (MCP): Standardizing Agentic Interoperability (2026)
- **Lokasi file:** `M0/The Model Context Protocol (MCP) Standardizing Agentic Interoperability (2026).pdf`
- **Sprint/Modul terkait:** Sprint 1 (M0+M1) — **KRITIS**, juga Sprint 3 (M4/M5), Sprint 4 (M11), Sprint 9 (M14). ⭐ Wajib. **Jangan dihapus dari Project Knowledge.**
- **Ide inti:** Protokol terbuka (client-host-server, JSON-RPC 2.0) yang menstandardisasi cara LLM agent men-discover dan memanggil tool/resource eksternal. Server mengekspos tiga primitif: **Tools** (fungsi callable dengan JSON Schema input/output), **Resources** (data read-only yang bisa disubscribe), dan **Prompts** (template interaksi). Client melakukan handshake `initialize` untuk negosiasi capability.
- **Relevansi ke F.R.I.D.A.Y:** Fondasi format **tool manifest/schema** untuk M0 — setiap tool/skill F.R.I.D.A.Y sebaiknya dideskripsikan sebagai MCP Tool dengan `inputSchema`/`outputSchema` jelas dan annotation (`readOnlyHint`, `destructiveHint`) yang bisa dipetakan ke permission model M11. Arsitektur client-host-server cocok untuk M4/M5: tiap smart-home/IoT gateway sebagai MCP server terpisah. Primitif Resources bisa dipakai untuk state/log yang disubscribe agent tanpa polling (M14).
- **Sumber informasi:** Ekstraksi parsial (mendalam pada bagian tool manifest/schema, sesuai instruksi kritikal untuk M0)
- **Catatan tambahan:** Perhatikan transport (stdio lokal vs HTTP+SSE remote) sesuai konteks lokal/cloud F.R.I.D.A.Y. Versioning protokol (`protocolVersion`) penting diwaspadai — sejalan dengan konsep versioned contract di Agent-OS.

### A Survey of Large Language Models (2023) — ✅ pengganti file mismatch, terverifikasi 2026-08-13
- **Lokasi file:** `M1/A Survey of Large Language Models (2023).pdf` — file baru, menggantikan file lama `Recent Advances in Conversational AI; A Review of Large Language Models.pdf` (folder tematik lama, dihapus) yang isinya ternyata mismatch total (paper matematika Willmore energy). Judul aslinya tidak ditemukan; paper ini dipilih sebagai pengganti tematik terdekat setelah pencarian web tidak menemukan paper dengan judul persis file lama.
- **Sprint/Modul terkait:** Sprint 1 (M0+M1) — rujukan fondasi LLM
- **Ide inti:** Zhao, Zhou, Li, et al. (Renmin University of China, arXiv:2303.18223 — salah satu survei LLM paling dikutip). Menelusuri evolusi language modeling dari statistical language model → neural language model → pre-trained language model (PLM) → large language model (LLM), menjelaskan bagaimana scaling model PLM (jumlah parameter + data) memunculkan kapabilitas baru ("emergent abilities") yang tidak ada di model lebih kecil. Membahas empat aspek utama LLM: pre-training, adaptation tuning, utilization (prompting), dan evaluasi kapabilitas.
- **Relevansi ke F.R.I.D.A.Y:** Rujukan fondasi untuk memahami *kenapa* LLM modern (yang jadi otak M1) berperilaku seperti sekarang — konsep emergent abilities relevan untuk ekspektasi realistis kapabilitas model yang dipilih (cloud vs lokal M12/M13), dan bagian prompting/utilization langsung relevan ke desain prompt agent loop M1.
- **Sumber informasi:** Ekstraksi mendalam — abstract & intro dibaca via `pdftotext`, dikonfirmasi cocok 100% dengan judul, penulis, dan arXiv ID
- **Catatan tambahan:** Survei sangat luas (banyak revisi, versi terbaru v19 per Maret 2026) — dipakai sebagai peta konsep/rujukan silang, bukan dibaca linear sekali duduk.

### A Comprehensive Survey of Agents for Computer Use: Foundations, Challenges, and Future Directions (2025)
- **Lokasi file:** `M6/A Comprehensive Survey of Agents for Computer Use Foundations, Challenges, and Future Directions (2025).pdf`
- **Sprint/Modul terkait:** Sprint 1 (M0+M1), Sprint 3 (M4/M5)
- **Ide inti:** Survei "computer-use agent" yang beroperasi di GUI/OS nyata via vision-language model — taksonomi arsitektur (perception, planning, grounding, memory, action), dataset/benchmark, tantangan (long-horizon planning, grounding visual, keamanan aksi destruktif).
- **Relevansi ke F.R.I.D.A.Y:** Peta pola desain untuk M4/M5 — terutama "grounding" (memetakan instruksi ke elemen UI/API) dan pemisahan planner vs executor. Tantangan keamanan aksi destruktif relevan untuk M11.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan
- **Catatan tambahan:** Survei sangat luas — fokus hanya pada arsitektur generik dan taksonomi risiko.

### Large Language Model-Brained GUI Agents: A Survey (2024)
- **Lokasi file:** `M6/Large Language Model-Brained GUI Agents A Survey (2024).pdf`
- **Sprint/Modul terkait:** Sprint 3 (M4/M5)
- **Ide inti:** Survei GUI agent "berotak" LLM — taksonomi dari perception (screenshot/accessibility-tree), reasoning/planning, grounding aksi, evaluasi, serta perbandingan pendekatan vision murni vs struktur DOM/accessibility API.
- **Relevansi ke F.R.I.D.A.Y:** Trade-off vision-based (general, rawan salah grounding) vs accessibility-API-based (akurat, terbatas app) jadi keputusan desain penting untuk kontrol OS F.R.I.D.A.Y.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan (file besar ~14MB)
- **Catatan tambahan:** Cukup ambil kerangka taksonomi arsitektur generiknya saja.

---

## Kategori #2 — Memory Architecture & Long-Term Context

### A Survey on Retrieval-Augmented Text Generation: Discovering, Visualizing, and Structuring Knowledge (2022)
- **Lokasi file:** `M2/A Survey on Retrieval-Augmented Text Generation Discovering, Visualizing, and Structuring Knowledge (2022).pdf`
- **Sprint/Modul terkait:** Sprint 2 (M2)
- **Ide inti:** Review paradigma retrieval-augmented generation era pra-LLM-besar dengan taksonomi retrieval source, retrieval metric, dan metode integrasi.
- **Relevansi ke F.R.I.D.A.Y:** Dasar konseptual strategi retrieval untuk memory F.R.I.D.A.Y sebelum menyentuh RAG versi LLM modern.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan via pdftotext
- **Catatan tambahan:** Cukup lawas — pasangkan dengan "RAG for LLMs: A Survey (2023)" di bawah untuk konteks modern.

### Generative Agents: Interactive Simulacra of Human Behavior (2023)
- **Lokasi file:** `M2/Generative Agents Interactive Simulacra of Human Behavior (2023).pdf`
- **Sprint/Modul terkait:** Sprint 2 (M2) — juga relevan Persona Design dan Proactive Behavior
- **Ide inti:** Arsitektur agen dengan memory stream (retrieval relevance+recency+importance), reflection berkala yang mensintesis memori jadi insight, dan planning rekursif — perilaku sosial believable pada 25 agen di sandbox "Smallville".
- **Relevansi ke F.R.I.D.A.Y:** Cetak biru langsung untuk M2 — skema scoring retrieval gabungan, mekanisme reflection periodik, re-planning saat konteks berubah.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan via pdftotext
- **Catatan tambahan:** Agen rentan halusinasi memori dan gaya bicara terlalu formal; bagian etika (risiko parasocial, disclosure sebagai AI) penting untuk desain persona yang aman.

### Lost in the Middle: How Language Models Use Long Contexts (2023)
- **Lokasi file:** `M2/Lost in the Middle How Language Models Use Long Contexts (2023).pdf`
- **Sprint/Modul terkait:** Sprint 2 (M2)
- **Ide inti:** Performa LLM membentuk kurva-U — paling baik memakai info di awal/akhir context, menurun signifikan bila info relevan ada di tengah; menambah jumlah dokumen retrieval tidak selalu meningkatkan performa.
- **Relevansi ke F.R.I.D.A.Y:** Peringatan desain memory-injection: urutan penempatan hasil retrieval dalam prompt harus disengaja, jangan andalkan context window besar untuk "menjejalkan semua".
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan via pdftotext
- **Catatan tambahan:** Hasil spesifik ke model 2023 (mungkin sudah diperbaiki di model terbaru) — tapi prinsipnya tetap relevan sebagai heuristik default.

### MemGPT: Towards LLMs as Operating Systems (2023)
- **Lokasi file:** `M2/MemGPT Towards LLMs as Operating Systems (2023).pdf`
- **Sprint/Modul terkait:** Sprint 2 (M2) — ⭐ Wajib
- **Ide inti:** Mengelola context window seperti virtual memory OS — main context analog RAM, archival/recall storage analog disk; LLM memanggil function untuk "page" data masuk/keluar context.
- **Relevansi ke F.R.I.D.A.Y:** Cetak biru paling langsung untuk M2 — hierarki memory (working context, FIFO queue, archival storage, recall storage) bisa diadopsi hampir 1:1, termasuk "memory pressure warning".
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan via pdftotext
- **Catatan tambahan:** Proyek ini berkembang jadi "Letta" — worth cek implementasi open-source terbaru mereka. Performa sangat bergantung kemampuan function-calling model dasar.

### Retrieval-Augmented Generation for Large Language Models: A Survey (2023)
- **Lokasi file:** `M2/Retrieval-Augmented Generation for Large Language Models A Survey (2023).pdf`
- **Sprint/Modul terkait:** Sprint 2 (M2)
- **Ide inti:** Mengorganisir evolusi RAG (Naive → Advanced → Modular), membahas komponen retrieval/generation/augmentation, membandingkan RAG vs fine-tuning.
- **Relevansi ke F.R.I.D.A.Y:** Peta paling lengkap untuk merancang "recall pengetahuan eksternal" — pola Modular RAG (routing, hybrid retrieval, iterative/adaptive retrieval) relevan begitu retrieval sederhana tidak lagi cukup.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan via pdftotext
- **Catatan tambahan:** Tabel metode sangat padat (>100 metode) — cukup dipakai sebagai indeks untuk deep-dive nanti.

### A Survey on the Memory Mechanism of Large Language Model based Agents (2024)
- **Lokasi file:** `M2/A Survey on the Memory Mechanism of Large Language Model based Agents — Zhang et al. (2024).pdf`
- **Sprint/Modul terkait:** Sprint 2 (M2) — peta rujukan silang untuk M2a/M2b/M2c
- **Ide inti:** Survei sistematis (arXiv:2404.13501, Renmin University + Huawei Noah's Ark Lab) yang menjawab "apa itu" dan "kenapa perlu" memori pada agent berbasis LLM, lalu mengorganisir desain & evaluasi modul memori dari berbagai paper yang selama ini tersebar, plus contoh aplikasi nyata.
- **Relevansi ke F.R.I.D.A.Y:** Indeks/peta tingkat tinggi untuk menyusun taksonomi M2 sendiri (apa saja jenis memori, bagaimana mengevaluasinya) sebelum menyelam ke paper teknis spesifik (MemGPT, MemoryBank, A-MEM) — dipakai sebagai kerangka pembanding, bukan blueprint implementasi langsung.
- **Sumber informasi:** Ekstraksi parsial — abstract via pdftotext
- **Catatan tambahan:** Ditambahkan user 2026-08-14 sebagai bagian riset gap forgetting/consolidation untuk M2c.

### A-Mem: Agentic Memory for LLM Agents (2025)
- **Lokasi file:** `M2/A-MEM Agentic Memory for LLM Agents — Xu et al. (2025).pdf`
- **Sprint/Modul terkait:** Sprint 2 (M2b/M2c)
- **Ide inti:** arXiv:2502.12110 (Rutgers/AIOS Foundation). Sistem memori yang mengorganisir dirinya sendiri secara dinamis ala metode Zettelkasten — tiap memori baru dicatat dengan atribut terstruktur (deskripsi kontekstual, keyword, tag), lalu sistem otomatis mencari koneksi ke memori lama dan membentuk link kalau ada kemiripan bermakna. Memori lama bisa ikut ter-update representasinya saat memori baru masuk ("memory evolution").
- **Relevansi ke F.R.I.D.A.Y:** Alternatif/pelengkap MemGPT untuk M2b — bukan cuma paging in/out, tapi jaringan memori yang saling terhubung dan berevolusi, relevan kalau F.R.I.D.A.Y perlu mengaitkan preferensi/insight user lintas topik (mis. kebiasaan IoT + gaya komunikasi user jadi satu insight gabungan).
- **Sumber informasi:** Ekstraksi parsial — abstract via pdftotext
- **Catatan tambahan:** Ditambahkan user 2026-08-14. Ketergantungan pada kualitas graph-linking otomatis — perlu dicek robustness-nya kalau volume memori besar.

### FSFM: A Biologically-Inspired Framework for Selective Forgetting of Agent Memory (2026)
- **Lokasi file:** `M2/FSFM A Biologically-Inspired Framework for Selective Forgetting of Agent Memory (2026).pdf`
- **Sprint/Modul terkait:** Sprint 2 (M2c) — ⭐ Langsung menjawab gap forgetting/consolidation
- **Ide inti:** arXiv:2604.20300 (China Mobile). Berargumen bahwa forgetting yang dirancang baik sama pentingnya dengan retensi memori untuk performa optimal, lewat 3 dimensi: efisiensi komputasi/storage (pruning cerdas), kualitas memori (update preferensi/konteks usang), dan postur keamanan. Mengambil analogi langsung dari hippocampal memory indexing/consolidation theory dan kurva lupa Ebbinghaus.
- **Relevansi ke F.R.I.D.A.Y:** Kandidat kerangka utama untuk kebijakan eviction/forgetting di M2c — melengkapi MemGPT yang fokus ke mekanisme paging tapi tidak spesifik soal kapan/bagaimana memori lama sebaiknya "dihapus/dilupakan" secara berprinsip. Poin keamanan (forgetting sebagai bagian postur security) relevan juga untuk M11.
- **Sumber informasi:** Ekstraksi parsial — abstract via pdftotext
- **Catatan tambahan:** Ditambahkan user 2026-08-14. Paper baru/niche (April 2026, belum banyak sitasi) — treat sebagai ide awal yang perlu divalidasi lebih jauh, bukan standar yang sudah mapan.

### MemoryBank: Enhancing Large Language Models with Long-Term Memory (2023 / AAAI 2024)
- **Lokasi file:** `M2/MemoryBank Enhancing Large Language Models with Long-Term Memory — Zhong et al. (2023AAAI 2024).pdf`
- **Sprint/Modul terkait:** Sprint 2 (M2c) — ⭐ Langsung menjawab gap forgetting/consolidation
- **Ide inti:** arXiv:2305.10250 (Sun Yat-Sen University dkk). Mekanisme memori yang bisa memanggil kembali memori relevan, terus berevolusi lewat update berkelanjutan, dan memahami kepribadian user seiring waktu. Kunci utamanya: mekanisme update memori terinspirasi **kurva lupa Ebbinghaus** — AI melupakan/menguatkan memori berdasarkan waktu berlalu dan relevansi, mirip perilaku manusia.
- **Relevansi ke F.R.I.D.A.Y:** Paper paling konkret untuk mengisi gap forgetting di M2c — kurva Ebbinghaus bisa langsung jadi formula scoring "kapan memori didowngrade/dihapus" yang dipasangkan dengan hierarki paging MemGPT. Use-case yang disebut (personal companion, secretarial assistance) sangat dekat dengan visi F.R.I.D.A.Y.
- **Sumber informasi:** Ekstraksi parsial — abstract via pdftotext
- **Catatan tambahan:** Ditambahkan user 2026-08-14, menjawab langsung rekomendasi yang muncul dari diskusi kecukupan paper M2. Cek juga implementasi open-source resminya kalau ada saat mulai coding M2c.

### Recursively Summarizing Enables Long-Term Dialogue Memory in Large Language Models (2023)
- **Lokasi file:** `M2/Recursively Summarizing Enables Long-Term Dialogue Memory in Large Language Models — Wang et al. (2023).pdf`
- **Sprint/Modul terkait:** Sprint 2 (M2a/M2b)
- **Ide inti:** arXiv:2308.15022 (HKUST dkk). LLM distimulasi untuk mengingat potongan dialog kecil, lalu secara rekursif menghasilkan memori/summary baru dari memori lama + konteks berikutnya, dan respons akhir dibentuk berdasarkan memori terbaru (bukan seluruh histori mentah).
- **Relevansi ke F.R.I.D.A.Y:** Teknik konkret untuk M2a — kompresi konteks percakapan panjang jadi summary bertingkat, alternatif ringan dibanding menyimpan seluruh histori mentah di working context, mengurangi risiko "Lost in the Middle" karena konteks yang dikirim ke LLM sudah dipadatkan.
- **Sumber informasi:** Ekstraksi parsial — abstract via pdftotext
- **Catatan tambahan:** Ditambahkan user 2026-08-14. **Koreksi atribusi:** nama file awal saat diunggah tertulis "Qian et al." tapi daftar penulis asli di dalam PDF adalah Wang, Fu, Cao, Wang, Tian, Ding (tidak ada nama Qian) — nama file sudah diperbaiki jadi "Wang et al." saat verifikasi 2026-08-14, judul & isi 100% cocok.

### Learning Offline: Memory Replay in Biological and Artificial Reinforcement Learning (2021)
- **Lokasi file:** `M2/Learning Offline Memory Replay in Biological and Artificial Reinforcement Learning — Roscow, Chua, Costa, Jones & Lepora (2021), Trends in Neurosciences.pdf`
- **Sprint/Modul terkait:** Sprint 2 (M2c) — analogi biologis untuk consolidation
- **Ide inti:** arXiv:2109.10034, *Trends in Neurosciences*. Membahas bagaimana replay neuronal di otak (memutar ulang pengalaman lama secara offline) penting untuk konsolidasi memori dan proses kognitif lain (planning, generalisasi), dan bagaimana prinsip ini menginspirasi experience replay pada reinforcement learning buatan.
- **Relevansi ke F.R.I.D.A.Y:** Analogi biologis untuk desain "consolidation job" M2c — proses background yang mengulang/menyaring interaksi lama secara periodik jadi insight yang lebih padat (mirip reflection di Generative Agents), bukan cuma menyimpan mentah lalu retrieval saat butuh.
- **Sumber informasi:** Ekstraksi parsial — highlights/intro via pdftotext
- **Catatan tambahan:** Ditambahkan user 2026-08-14. Paper neurosains/RL murni, bukan LLM — perlu adaptasi konsep, bukan diadopsi teknis langsung.

### Overcoming Catastrophic Forgetting in Neural Networks — EWC (2017)
- **Lokasi file:** `M2/Overcoming Catastrophic Forgetting in Neural Networks (EWC) — Kirkpatrick et al. (2017), PNAS.pdf`
- **Sprint/Modul terkait:** Sprint 2 (M2c) — analogi biologis untuk consolidation
- **Ide inti:** arXiv:1612.00796, *PNAS* (DeepMind). Elastic Weight Consolidation (EWC): mencegah neural network "lupa total" tugas lama saat belajar tugas baru dengan memperlambat perubahan bobot yang penting untuk tugas lama, terinspirasi teori system-level consolidation McClelland et al. (1995).
- **Relevansi ke F.R.I.D.A.Y:** Bukan teknik langsung dipakai (ini soal update bobot neural net, F.R.I.D.A.Y tidak fine-tuning model dasarnya), tapi prinsip "importance-weighted retention" relevan sebagai analogi: memori/preferensi user yang sering dipakai/penting sebaiknya lebih tahan terhadap forgetting dibanding yang jarang dipakai — bisa jadi salah satu faktor scoring di M2c.
- **Sumber informasi:** Ekstraksi parsial — bagian intro via pdftotext
- **Catatan tambahan:** Ditambahkan user 2026-08-14. Paper machine learning klasik (bukan LLM/agent) — konteksnya continual learning pada neural net, adaptasi ke M2 murni konseptual/analogi.

### Why There Are Complementary Learning Systems in the Hippocampus and Neocortex (1995)
- **Lokasi file:** `M2/Why There Are Complementary Learning Systems in the Hippocampus and Neocortex — McClelland, McNaughton & O'Reilly (1995), Psychological Review.pdf`
- **Sprint/Modul terkait:** Sprint 2 (M2c) — analogi biologis fondasional untuk consolidation
- **Ide inti:** *Psychological Review* 102(3). Paper klasik yang menjelaskan kenapa otak punya dua sistem belajar terpisah — hipokampus (belajar cepat, spesifik) dan neokorteks (belajar lambat, general) — dan bagaimana "consolidation" (transfer bertahap dari hipokampus ke neokorteks, bisa berbulan-tahun) adalah prinsip desain penting, bukan sekadar keterbatasan sistem saraf.
- **Relevansi ke F.R.I.D.A.Y:** Fondasi konseptual paling dasar untuk arsitektur memori dua-lapis M2 — analog ke "working/recent memory" (cepat, spesifik, seperti hipokampus) vs "consolidated long-term knowledge" (lambat terbentuk, general, seperti neokorteks). Menjustifikasi kenapa M2a (short-term) dan M2b/M2c (long-term) memang harus dirancang sebagai sistem terpisah, bukan satu penyimpanan seragam.
- **Sumber informasi:** Ekstraksi parsial — bagian tengah artikel (pembahasan consolidation) via pdftotext
- **Catatan tambahan:** Ditambahkan user 2026-08-14. Paper neurosains kognitif tahun 1995 — sangat fondasional/teoretis, dipakai sebagai justifikasi arsitektur, bukan resep implementasi.

### About Sleep's Role in Memory (2013)
- **Lokasi file:** `M2/About Sleep's Role in Memory — Rasch & Born (2013), Physiological Reviews.pdf`
- **Sprint/Modul terkait:** Sprint 2 (M2c) — analogi biologis untuk consolidation
- **Ide inti:** *Physiological Reviews* 93:681-766 (2013). Review komprehensif soal bagaimana tidur (khususnya slow-wave sleep dan REM) berperan aktif dalam konsolidasi memori, bukan cuma waktu istirahat pasif.
- **Relevansi ke F.R.I.D.A.Y:** Analogi tambahan untuk proses konsolidasi periodik/offline di M2c — mendukung ide "consolidation job" yang berjalan saat sistem idle (analog "tidur"), memproses memori mentah jadi insight lebih padat, mirip fungsi reflection di Generative Agents dan replay di paper Roscow et al.
- **Sumber informasi:** Ekstraksi parsial — bagian intro via pdftotext
- **Catatan tambahan:** ⚠️ **Mismatch ditemukan & diperbaiki 2026-08-14** — file awalnya diberi nama "The Memory Function of Sleep — Diekelmann & Born (2010), Nature Reviews Neuroscience.pdf" tapi isi aslinya adalah paper berbeda ("About Sleep's Role in Memory" oleh Rasch & Born, *Physiological Reviews* 2013 — bukan Diekelmann & Born 2010 di *Nature Reviews Neuroscience*, walau topik & salah satu penulis, Born, sama). Nama file sudah disesuaikan dengan isi asli, bukan dicari paper penggantinya, karena isinya sendiri tetap relevan dan sah untuk topik ini.

---

## Kategori #3 — Task Planning & Decomposition

### Chain-of-Thought Prompting Elicits Reasoning in Large Language Models (2022)
- **Lokasi file:** `M3/Chain-of-Thought Prompting Elicits Reasoning in Large Language Models (2022).pdf`
- **Sprint/Modul terkait:** Sprint 6 (M3) — Penting
- **Ide inti:** Contoh few-shot berisi rangkaian langkah reasoning sebelum jawaban akhir meningkatkan akurasi drastis pada tugas aritmetika/commonsense/simbolik — emergent ability yang hanya muncul pada model besar (~100B+).
- **Relevansi ke F.R.I.D.A.Y:** Teknik prompting dasar untuk reasoning/planning sebelum eksekusi tool-call; baseline pembanding untuk teknik lebih canggih (ReAct, ToT, Decomposed Prompting).
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan via pdftotext (43 halaman)
- **Catatan tambahan:** Tidak otomatis bekerja di model kecil/lokal — untuk kandidat model lokal M11, efektivitas CoT harus divalidasi ulang.

### Decomposed Prompting: A Modular Approach for Solving Complex Tasks (2023)
- **Lokasi file:** `M3/Decomposed Prompting A Modular Approach for Solving Complex Tasks (2023).pdf`
- **Sprint/Modul terkait:** Sprint 6 (M3)
- **Ide inti:** DECOMP memecah tugas kompleks jadi sub-task yang didelegasikan ke "sub-task handler" terpisah, dikendalikan decomposer prompt yang bisa memanggil dirinya sendiri secara rekursif.
- **Relevansi ke F.R.I.D.A.Y:** Pola modular cocok untuk Planning: decomposer sebagai "orchestrator" yang memanggil skill/tool spesifik (selaras dengan M1), termasuk dukungan native memecah tugas panjang secara rekursif.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan via pdftotext (70 halaman)
- **Catatan tambahan:** Setiap sub-task handler perlu didesain manual per domain — worth direvisit begitu F.R.I.D.A.Y punya banyak skill reusable.

### LLM+P: Empowering Large Language Models with Optimal Planning Proficiency (2023)
- **Lokasi file:** `M3/LLM+P Empowering Large Language Models with Optimal Planning Proficiency (2023).pdf`
- **Sprint/Modul terkait:** Sprint 6 (M3) — Opsional; juga relevan Sprint 3 (M4/M5)
- **Ide inti:** LLM hanya sebagai penerjemah bahasa natural ke PDDL, classical planner (Fast Downward) mencari solusi optimal, lalu LLM menerjemahkan balik ke bahasa natural — LLM murni sebagai planner gagal total di 7 domain robot planning, LLM+P berhasil optimal di hampir semua kasus.
- **Relevansi ke F.R.I.D.A.Y:** Hybrid symbolic+LLM sangat relevan untuk Device Orchestration (M4) yang butuh urutan aksi valid tanpa halusinasi langkah.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan via pdftotext
- **Catatan tambahan:** Perlu domain PDDL manual — cocok untuk domain device control yang terbatas/well-defined, kurang cocok untuk task open-ended.

### Tree of Thoughts: Deliberate Problem Solving with Large Language Models (2023)
- **Lokasi file:** `M3/Tree of Thoughts Deliberate Problem Solving with Large Language Models (2023).pdf`
- **Sprint/Modul terkait:** Sprint 6 (M3) — ⭐ Wajib
- **Ide inti:** Menggeneralisasi CoT jadi pencarian pohon: setiap "thought" dievaluasi sendiri oleh LLM dan dijelajahi dengan BFS/DFS termasuk backtracking — jauh mengungguli CoT pada tugas yang butuh eksplorasi (Game of 24: 74% vs 4%).
- **Relevansi ke F.R.I.D.A.Y:** Cocok untuk Planning saat tugas butuh eksplorasi banyak opsi (misal orkestrasi banyak device) — self-evaluation LM sebagai heuristic pencarian tanpa training tambahan.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan via pdftotext
- **Catatan tambahan:** Biaya token 5-100x lebih mahal dari CoT — pakai selektif hanya untuk planning kritis; input penting untuk desain Hybrid Cloud-Edge Routing (kategori 12).

### DeepSeek-Prover-V1.5: Harnessing Proof Assistant Feedback for Reinforcement Learning and Monte-Carlo Tree Search (2024)
- **Lokasi file:** (root) `M3/2408.08152v1.pdf` — nama file arxiv ID, judul diidentifikasi dari isi
- **Sprint/Modul terkait:** Referensi tidak langsung untuk Task Planning (eksplorasi bercabang dengan reward sparse)
- **Ide inti:** Model 7B pembuktian teorema formal (Lean 4) yang mengombinasikan whole-proof generation dengan "truncate-and-resume" dipandu Monte-Carlo Tree Search (RMaxTS), memakai reward intrinsik untuk eksplorasi luas saat reward asli sangat jarang, plus fine-tuning RL (GRPO) dari feedback proof-assistant.
- **Relevansi ke F.R.I.D.A.Y:** Bukan tentang asisten personal, tapi teknik eksplorasi bercabang dengan reward sparse (intrinsic reward + tree search + truncate-resume) relevan konseptual untuk Task Planning — agent yang gagal di tengah task multi-langkah bisa "truncate" dan mencoba ulang dari titik kegagalan (resume) dengan strategi berbeda.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan
- **Catatan tambahan:** Domain sangat spesifik (matematika formal) — treat sebagai referensi metode RL/search, bukan komponen langsung.

### DeepSeek-Prover-V2: Advancing Formal Mathematical Reasoning via Reinforcement Learning for Subgoal Decomposition (2025)
- **Lokasi file:** (root) `M3/2504.21801v2.pdf` — nama file arxiv ID, judul diidentifikasi dari isi
- **Sprint/Modul terkait:** Referensi konsep Task Planning & Decomposition
- **Ide inti:** Model 671B memakai model umum untuk mendekomposisi teorema kompleks menjadi subgoal (lemma antara), lalu model prover kecil menyelesaikan tiap subgoal secara rekursif; hasil gabungan dipasangkan CoT informal sebagai data cold-start RL — state-of-the-art 88.9% MiniF2F-test.
- **Relevansi ke F.R.I.D.A.Y:** Contoh paling langsung untuk Task Planning & Decomposition — pola "model besar memecah task jadi subgoal, model kecil eksekusi tiap subgoal, hasil digabung" bisa diadaptasi jadi arsitektur planner-executor: cloud melakukan decomposition, lokal mengeksekusi tiap sub-task.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan
- **Catatan tambahan:** Paper mencatat kasus reward hacking (model kecil eksploitasi bug UI untuk "menang" tanpa benar-benar membuktikan) — pengingat bahwa verifier otomatis F.R.I.D.A.Y juga harus tahan eksploitasi serupa (lih. juga VERA di kategori #6).

---

## Kategori #4 — Device Orchestration & OS-Level Control

### Agent Operating Systems (Agent-OS): A Blueprint Architecture for Real-Time, Secure, and Scalable AI Agents (2026)
- **Lokasi file:** `M0/Agent Operating Systems (Agent-OS) A Blueprint Architecture for Real-Time, Secure, and Scalable AI Agents (2026).pdf`
- **Sprint/Modul terkait:** Sprint 1 (M0+M1) — **KRITIS**, juga Sprint 3, Sprint 4 (M11), Sprint 9 (M14). **Jangan dihapus dari Project Knowledge.**
- **Ide inti:** Mengusulkan "Agent-OS" — layer abstraksi mirip OS klasik (kernel/scheduler/driver) untuk mengorkestrasi banyak AI agent secara real-time, aman, scalable. Komponen: agent scheduler/runtime, resource & tool manager, memory/context manager, security/isolation layer. Kunci: model **plugin/kontrak ber-versi** — tiap kapabilitas didaftarkan dengan versi & skema kontrak, analog driver model/syscall ABI stability.
- **Relevansi ke F.R.I.D.A.Y:** Referensi arsitektur inti M0 — F.R.I.D.A.Y butuh "kernel" agen yang menjadwalkan task secara real-time tanpa saling blocking. Model plugin/kontrak ber-versi langsung diadopsi untuk skill/tool F.R.I.D.A.Y agar upgrade skill baru tidak memutus skill lama. Layer isolasi jadi dasar M11 (least privilege per tool). Scheduler real-time memberi pola prioritas respons reaktif vs proaktif (M14).
- **Sumber informasi:** Ekstraksi parsial (mendalam pada bagian plugin/kontrak ber-versi, sesuai instruksi kritikal untuk M0)
- **Catatan tambahan:** Bersifat blueprint/proposal, belum ada implementasi produksi besar tervalidasi luas — ambil prinsip modular plugin ber-versi + sandbox saja, bukan seluruh arsitektur distribusi enterprise-nya.

### Voxia: A Virtual Voice Assistant
- **Lokasi file:** `M4/Voxia; A Virtual Voice Assistant.pdf`
- **Sprint/Modul terkait:** Sprint 4 (M4-M6); referensi arsitektur end-to-end
- **Ide inti:** Implementasi Voxia, virtual voice assistant, mencakup arsitektur komponen (STT, pemrosesan perintah, TTS) dan integrasinya jadi satu sistem fungsional.
- **Relevansi ke F.R.I.D.A.Y:** Referensi arsitektur end-to-end pembanding pipeline F.R.I.D.A.Y sendiri (wake word → ASR → NLU/agentic core → TTS).
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan, konten dikonfirmasi cocok dengan judul
- **Catatan tambahan:** Skala proyek Voxia kemungkinan lebih sederhana dari target F.R.I.D.A.Y — cocok sebagai baseline pembanding, bukan blueprint utama.

### An Abstraction Layer Exploiting Voice Assistant Technologies for Effective Human–Robot Interaction
- **Lokasi file:** `M4/An Abstraction Layer Exploiting Voice Assistant Technologies for Effective Human–Robot Interaction.pdf`
- **Sprint/Modul terkait:** Sprint 4-5 (M4-M6)
- **Ide inti:** Mengusulkan lapisan abstraksi (middleware) yang memanfaatkan platform voice assistant existing (Alexa/Google Assistant) untuk mengontrol robot, memisahkan logika kontrol dari detail implementasi speech platform tertentu.
- **Relevansi ke F.R.I.D.A.Y:** Konsep abstraction layer applicable langsung — memisahkan "pemahaman perintah suara" dari "eksekusi kontrol perangkat/IoT" lewat interface standar, memudahkan menambah device baru tanpa mengubah core NLU.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan, konten dikonfirmasi cocok dengan judul
- **Catatan tambahan:** Konteks asli human-robot interaction (robot fisik) — prinsip abstraksinya tetap portable ke use-case IoT.

---

## Kategori #5 — IoT Integration & Protocol

### Agentic IoT: Architectures, Applications, and Challenges Toward the Internet of Agents (2026)
- **Lokasi file:** `M5/Agentic IoT Architectures, Applications, and Challenges Toward the Internet of Agents (2026).pdf`
- **Sprint/Modul terkait:** Sprint 3 (M4/M5)
- **Ide inti:** Evolusi dari IoT konvensional (rule-based) menuju "Agentic IoT"/"Internet of Agents" — tiap device/gateway punya lapisan agen LLM kecil yang bernegosiasi dan berkoordinasi otonom lintas device, dengan tantangan interoperabilitas protokol, latensi real-time, keterbatasan resource edge.
- **Relevansi ke F.R.I.D.A.Y:** Kerangka arsitektur untuk M4/M5 — pola "agent per-device/gateway" berkomunikasi via protokol standar, cocok untuk pendekatan kontrol banyak perangkat smart-home lewat satu asisten pusat. Tantangan latensi/resource relevan untuk kategori 12 (routing).
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan
- **Catatan tambahan:** Konsep "Internet of Agents" masih visioner — ambil sebagai referensi arah jangka panjang, bukan implementasi Sprint 3 langsung.

### AI on Edge IoT: Trends, Technologies, and Applications (2025)
- **Lokasi file:** `M5/AI on Edge IoT Trends, Technologies, and Applications (2025).pdf`
- **Sprint/Modul terkait:** Sprint 3 (M4/M5); juga kategori #11/#12 (Local Inference, Hybrid Cloud-Edge Routing) — ✅ sudah dipakai juga di Sprint 8
- **Ide inti:** Tinjauan tren AI-on-edge untuk IoT — teknik kompresi model (quantization, distillation, pruning), arsitektur edge-cloud hybrid, studi kasus (smart home, wearable, industrial IoT).
- **Relevansi ke F.R.I.D.A.Y:** Acuan teknik kompresi model untuk M11/M12 — apa yang layak dipakai jika F.R.I.D.A.Y menjalankan wake word/intent sederhana langsung di edge daripada roundtrip ke cloud.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan
- **Catatan tambahan:** Survei tren umum (tidak spesifik LLM percakapan) — cek ulang detail teknis terhadap paper LLM-inference lebih spesifik saat implementasi.

### Enhancing IoT Interactions with Large Language Models: A Progressive Approach (2025)
- **Lokasi file:** `M5/Enhancing IoT Interactions with Large Language Models A Progressive Approach (2025).pdf`
- **Sprint/Modul terkait:** Sprint 3 (M4/M5) — ⭐ Wajib (blueprint Home Assistant + MQTT)
- **Ide inti:** Pendekatan bertahap (progressive) mengintegrasikan LLM ke sistem IoT — dari penerjemah intent ke command IoT terstruktur, hingga pengelolaan state device dan penanganan ambiguitas instruksi secara iteratif.
- **Relevansi ke F.R.I.D.A.Y:** Pola konkret untuk M4/M5 memetakan ucapan pengguna jadi command IoT terstruktur secara progressive refinement, termasuk strategi klarifikasi instruksi ambigu — relevan langsung untuk pipeline voice-to-action.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan
- **Catatan tambahan:** Skala evaluasi kemungkinan kecil (proof-of-concept) — perlu validasi ulang untuk jumlah device lebih besar.

---

## Kategori #6 — Security, Sandboxing & Permission Model

### A Survey on the Unique Security of Autonomous and Collaborative LLM Agents: Threats, Defenses, and Futures (2026)
- **Lokasi file:** `M11/A Survey on the Unique Security of Autonomous and Collaborative LLM Agents Threats, Defenses, and Futures (2026).pdf`
- **Sprint/Modul terkait:** Sprint 4 (M11), Sprint 9 (M14 jika ada sub-agent)
- **Ide inti:** Survei risiko keamanan unik pada agent otonom — prompt injection tool-mediated, eksekusi kode tak aman, eskalasi privilese lewat tool-chaining, risiko kolaborasi multi-agent, beserta taksonomi pertahanan.
- **Relevansi ke F.R.I.D.A.Y:** Checklist langsung untuk M11 — terutama tool-chaining privilege escalation yang harus diwaspadai saat F.R.I.D.A.Y mengontrol banyak skill IoT/OS sekaligus.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan
- **Catatan tambahan:** Banyak mitigasi masih level konsep (belum benchmark kuantitatif matang) — treat sebagai daftar ancaman untuk threat-modeling.

### Llama Guard: LLM-based Input-Output Safeguard for Real-World Applications (2023)
- **Lokasi file:** `M11/Llama Guard LLM-based Input-Output Safeguard for Real-World Applications (2023).pdf`
- **Sprint/Modul terkait:** Sprint 4 (M11)
- **Ide inti:** Model klasifikasi safety (fine-tuned dari Llama) yang menjadi guard input/output — mengklasifikasikan apakah prompt/respons melanggar kategori bahaya yang didefinisikan, taksonomi mudah dikustom lewat prompt.
- **Relevansi ke F.R.I.D.A.Y:** Lapisan guardrail input/output di M11 — memfilter perintah sebelum diteruskan ke agent utama dan output/aksi sebelum dieksekusi ke device nyata.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan
- **Catatan tambahan:** Dirancang untuk moderasi konten umum, bukan verifikasi keamanan tool-call/aksi agentic — paper VERA di bawah menunjukkan guard generik seperti ini recall-nya terbatas pada skenario agentic murni.

### Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications Using Indirect Prompt Injection (2023)
- **Lokasi file:** `M11/Not What You've Signed Up For Compromising Real-World LLM-Integrated Applications Using Indirect Prompt Injection (2023).pdf` (+ 2 file duplikat identik: 1 tanpa tahun di nama file, 1 lagi ditambahkan user 2026-08-12 dengan nama `Not What You've Signed Up For Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection (Greshake et al., 2023).pdf` — sama-sama arXiv:2302.12173v2, isi identik)
- **Sprint/Modul terkait:** Sprint 4 (M11) — ⭐ Wajib
- **Ide inti:** Paper seminal yang mendefinisikan **indirect prompt injection** — konten berbahaya disuntikkan lewat data eksternal (web, email, dokumen) yang dibaca LLM-integrated app, membajak perilaku agent tanpa sepengetahuan user.
- **Relevansi ke F.R.I.D.A.Y:** Sangat kritis untuk M11 — F.R.I.D.A.Y yang mengakses data eksternal (email, kalender, web, sensor IoT) berisiko instruksi tersembunyi. Perlu isolasi channel instruksi vs channel data sejak M0/M1.
- **Sumber informasi:** Ekstraksi mendalam — abstract & intro dikonfirmasi ulang langsung via pdftotext dari salinan bernama Greshake (2026-08-12), konsisten dengan salinan lama
- **Catatan tambahan:** File kedua di folder (nama sama tanpa tahun) adalah duplikat identik — cukup satu sebagai rujukan.

### Safeguarding Large Language Models: A Survey (2024)
- **Lokasi file:** `M11/Safeguarding Large Language Models A Survey (2024).pdf`
- **Sprint/Modul terkait:** Sprint 4 (M11)
- **Ide inti:** Survei teknik "safeguarding" LLM — guardrail input/output, RLHF/alignment untuk safety, red-teaming, taksonomi jenis serangan (jailbreak, prompt injection, data poisoning) dan pertahanannya.
- **Relevansi ke F.R.I.D.A.Y:** Referensi umum untuk merancang lapisan keamanan M11 secara komprehensif (defense-in-depth), penting karena asisten ini punya akses kontrol fisik (IoT/OS).
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan
- **Catatan tambahan:** Cakupan luas dan general-purpose (tidak spesifik agentic) — kombinasikan dengan survei security agentic yang lebih spesifik.

### Safety Testing LLM Agents at Scale: From Risk Discovery to Evidence-Grounded Verification — "VERA" (2026)
- **Lokasi file:** `M11/Safety Testing LLM Agents at Scale From Risk Discovery to Evidence-Grounded Verification (2026).pdf`
- **Sprint/Modul terkait:** Sprint 4 (M11); relevan juga evaluasi berkelanjutan
- **Ide inti:** Framework VERA, testing keamanan agent otomatis 3 tahap: (1) penemuan risiko dari literatur → taksonomi, (2) komposisi kombinatorial jadi "safety case" executable, (3) eksekusi adaptif di sandbox dengan verifikasi berbasis bukti (state environment & tool-call log, bukan self-report). Diuji pada 4 framework produksi (termasuk Claude Code), attack success rate rata-rata 93.9% pada multi-channel; guard model off-the-shelf kurang transfer ke skenario agentic murni tapi naik signifikan setelah fine-tune dengan data VERA.
- **Relevansi ke F.R.I.D.A.Y:** Metodologi konkret untuk M11 security testing — "safety case executable dengan verifier deterministik berbasis state environment" bisa diadopsi untuk menguji skill/tool baru F.R.I.D.A.Y sebelum deploy (simulasikan prompt injection lewat data palsu, verifikasi lewat log tool-call, bukan cuma jawaban teks).
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan
- **Catatan tambahan:** Framework berskala penelitian besar — untuk F.R.I.D.A.Y skala personal-assistant, cukup adopsi prinsip metodologinya (verifier berbasis state nyata) dalam skala kecil/manual dulu.

### Security Risk Analysis in IoT Systems through Factor Identification over IoT Devices
- **Lokasi file:** `M11/Security Risk Analysis in IoT Systems through Factor Identification over IoT Devices.pdf`
- **Sprint/Modul terkait:** Sprint 4 (M11, untuk faktor risiko IoT) — Penting; juga kategori #5
- **Ide inti:** Mengidentifikasi faktor risiko keamanan spesifik perangkat IoT (permukaan serangan, kerentanan protokol, kelemahan autentikasi) dan mengusulkan metodologi analisis risiko.
- **Relevansi ke F.R.I.D.A.Y:** Checklist ancaman untuk merancang permission model kontrol IoT — membatasi command apa saja yang boleh dikirim ke perangkat tertentu, validasi sebelum aksi fisik (misal unlock pintu).
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan, konten dikonfirmasi cocok dengan judul
- **Catatan tambahan:** Perlu dipetakan eksplisit ke tier permission (read-only sensor vs actuator kritikal) agar faktor risiko benar-benar termitigasi, bukan cuma daftar teoretis.

### A Systematic Survey of Security Threats and Defenses in LLM-Based AI Agents: A Layered Attack Surface Framework (2026)
- **Lokasi file:** `M11/A Systematic Survey of Security Threats and Defenses in LLM-Based AI Agents- A Layered Attack Surface Framework (2026).pdf`
- **Sprint/Modul terkait:** Sprint 4 (M11) — ⭐ Sangat relevan, ditambahkan user 2026-08-12 sebagai bahan tambahan/pengganti untuk memperkuat kategori #6
- **Ide inti:** Mengusulkan **LASM (Layered Attack Surface Model)** — dekomposisi 7 lapis stack agentic (Foundation, Cognitive, Memory, Tool Execution, Multi-Agent Coordination, Ecosystem, Governance) dengan bukti formal bahwa kontrol keamanan di satu lapis punya **nol daya deteksi** terhadap serangan di lapis lain (non-transferability theorem). Ditambah sumbu **temporalitas** ortogonal (T1 instan, T2 sepanjang sesi, T3 kumulatif lintas-sesi, T4 tersembunyi di bobot/tanpa event diskret). Dari 116 paper (2021-2026) yang dipetakan ke grid 7×4: zona under-studied {L5-L7}×{T3-T4} cuma 6.3% dari semua paper tapi berisi ancaman paling parah; 7 dari 28 sel grid nol cakupan defense; tidak ada benchmark yang menguji T3/T4 sama sekali.
- **Relevansi ke F.R.I.D.A.Y:** Kerangka paling tajam untuk mendesain M11 secara sistematis — bukan cuma checklist ancaman, tapi **peta di mana kontrol keamanan harus ditempatkan** per lapis arsitektur F.R.I.D.A.Y (mirip pemisahan M0-M17: kontrak/tool di L1/L4, memori M2 di L3, multi-agent M14 di L5). Poin paling penting: F.R.I.D.A.Y yang punya memori jangka panjang (M2) dan tool eksekusi nyata (M4/M5) otomatis rawan di T3/T4 (payload yang baru "meledak" berminggu-minggu kemudian) — kategori yang justru paling minim riset defense-nya. Juga menyediakan skema ABOM (semacam SBOM untuk agent) yang bisa jadi inspirasi format audit-trail M11.
- **Sumber informasi:** Ekstraksi mendalam — abstract, intro, dan metodologi survei (PRISMA-style, 116 paper primer dari 1634 kandidat) dibaca langsung via pdftotext
- **Catatan tambahan:** Survei sangat baru (2026) dan cakupannya luas/padat (paper eksplisit bilang "tidak perlu dibaca linear", ada 4 jalur baca per audiens) — paling relevan buat F.R.I.D.A.Y adalah jalur "Agent-system designer" (fokus ke bagian LASM, layer L4 tool-execution, dan taksonomi defense).

### AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents (2024)
- **Lokasi file:** `M11/AgentDojo- A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents (2024).pdf`
- **Sprint/Modul terkait:** Sprint 4 (M11) — ⭐ Sangat relevan, ditambahkan user 2026-08-12
- **Ide inti:** Framework evaluasi (bukan benchmark statis) untuk agent yang mengeksekusi tool atas data tak terpercaya — 97 task realistis (kelola email, e-banking, booking travel) + 629 test case keamanan. Mengukur trade-off utility vs security dengan formal utility check atas state environment, bukan LLM-judge. Temuan: LLM SOTA gagal >34% task bahkan tanpa serangan; serangan prompt injection berhasil <25% di agent terbaik; defense sederhana (secondary attack detector) menurunkan attack success rate jadi 8%.
- **Relevansi ke F.R.I.D.A.Y:** Blueprint konkret untuk **test-harness keamanan M11** — bukan cuma baca teori, tapi bisa langsung diadopsi polanya: bikin skenario task (kalender, smart-home) + "attacker goal" tersembunyi di data yang F.R.I.D.A.Y proses (misal instruksi jahat nyempil di transkrip email/notifikasi IoT), lalu ukur apakah agent tetap solve task dengan benar TANPA terjebak instruksi tersembunyi itu.
- **Sumber informasi:** Ekstraksi mendalam — abstract & intro dibaca langsung via pdftotext (NeurIPS 2024 Datasets & Benchmarks Track)
- **Catatan tambahan:** Framework-nya open-source dan extensible (bukan cuma paper) — https://github.com/ethz-spylab/agentdojo — layak dicoba langsung dijalankan lokal untuk uji coba M11, bukan cuma dibaca.

### InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated LLM Agents (2024)
- **Lokasi file:** `M11/InjecAgent- Benchmarking Indirect Prompt Injections in Tool-Integrated LLM Agents (2024).pdf`
- **Sprint/Modul terkait:** Sprint 4 (M11) — Penting, ditambahkan user 2026-08-12
- **Ide inti:** Benchmark pertama khusus indirect prompt injection (IPI) pada tool-integrated agent — 1.054 test case, 17 tool user berbeda, 62 tool attacker, dikategorikan jadi 2 intent serangan (harm langsung ke user vs eksfiltrasi data privat). ReAct-prompted GPT-4 rentan 24% dari semua kasus; dengan "hacking prompt" tambahan di instruksi jahatnya, attack success rate naik hampir 2x lipat.
- **Relevansi ke F.R.I.D.A.Y:** Pelengkap AgentDojo — dataset test case IPI siap pakai untuk menguji ketahanan agent loop M1 terhadap instruksi tersembunyi di hasil tool-call (mis. review palsu yang menyuruh booking janji tanpa izin user, analog ke skenario IoT/kalender F.R.I.D.A.Y). Kategorisasi "direct harm vs data exfiltration" bisa dipetakan langsung ke `permission_tier` M0 (aksi `critical` vs `read_only`/`standard` yang bocor data).
- **Sumber informasi:** Ekstraksi mendalam — abstract & intro dibaca langsung via pdftotext
- **Catatan tambahan:** Angka 24% attack success rate itu untuk model 2024 (GPT-4) tanpa defense apapun — perlu dites ulang terhadap model/provider yang benar-benar dipakai F.R.I.D.A.Y sebelum dipakai sebagai baseline kepercayaan diri keamanan.

### Toward Secure LLM Agents: Threat Surfaces, Attacks, Defenses, and Evaluation (2026)
- **Lokasi file:** `M11/Toward Secure LLM Agents- Threat Surfaces, Attacks, Defenses, and Evaluation (2026).pdf`
- **Sprint/Modul terkait:** Sprint 4 (M11) — Penting, ditambahkan user 2026-08-12
- **Ide inti:** Survei lain (247 paper, terpisah dari LASM di atas) dengan framework **lifecycle-based & systems-oriented**: keamanan agent dilihat dari interaksi antara information flow, delegated authority, dan persistent state di sepanjang loop agent (input→planning→decision→tool execution→output→memory→monitoring→multi-agent coordination). Temuan: prompt injection & tool-mediated control-flow hijacking masih paling dominan diriset, tapi persistent state corruption & multi-agent propagation makin jadi concern; defense yang ada "weakly compositional" (tidak nyambung rapi kalau digabung); benchmark yang ada masih underrepresent risiko long-horizon/stateful.
- **Relevansi ke F.R.I.D.A.Y:** Sudut pandang komplementer ke LASM — kalau LASM fokus "di layer arsitektur mana", paper ini fokus "di titik mana dalam loop eksekusi agent" (align langsung dengan siklus M1: input→planning→tool-call→output→memory M2). Argumen intinya (agent butuh trust boundary eksplisit, kontrol privilese berbasis prinsip, state management yang sadar provenance) jadi requirement desain langsung untuk M0 (permission_tier) dan M11.
- **Sumber informasi:** Ekstraksi mendalam — abstract & intro dibaca langsung via pdftotext
- **Catatan tambahan:** Dua survei besar (paper ini + LASM di atas) sama-sama baru terbit 2026 dan saling melengkapi tapi TIDAK saling mengutip/membandingkan secara eksplisit di bagian yang terbaca — kalau nanti butuh sumber tunggal paling otoritatif untuk desain M11, worth dibaca lebih dalam mana yang taksonominya lebih cocok diadopsi in praktik, bukan dipakai dua-duanya mentah-mentah.

### Breaking the Code: Security Assessment of AI Code Agents Through Systematic Jailbreaking Attacks (2025) — ✅ berhasil dibaca 2026-08-12
- **Lokasi file:** `M11/Breaking the Code Security Assessment of AI Code Agents Through Systematic Jailbreaking Attacks (2025).pdf`
- **Sprint/Modul terkait:** Sprint 4 (M11) — sebelumnya DILEWATI, sekarang terbaca
- **Ide inti:** Saha et al. (Univ. of Maryland + AWS AI Labs + Meta Superintelligence Labs). Benchmark **JAWS-BENCH** yang mengukur bukan cuma "apakah code agent MENOLAK/menuruti permintaan berbahaya" (seperti evaluasi lama), tapi apakah kode jahat yang dihasilkan **benar-benar bisa dikompilasi & dijalankan** (deployable harm) — 3 tingkat workspace (kosong, single-file, multi-file) mensimulasikan kemampuan attacker yang makin canggih, dinilai lewat Judge Framework berlapis (compliance → attack success → syntax benar → bisa jalan end-to-end). Temuan penting: **membungkus LLM jadi agent (dengan planning+tool use) MENAIKKAN attack success rate 1.6x** dibanding model mentah — karena proses planning/tool-use bisa "membalik" penolakan awal si model.
- **Relevansi ke F.R.I.D.A.Y:** Sangat relevan untuk M6 (OS-level control) + M11 — kalau F.R.I.D.A.Y nanti bisa menulis/menjalankan kode (skrip otomasi, dsb.), metodologi JAWS-BENCH bisa diadopsi sebagai test suite sebelum fitur itu dirilis: bukan cuma cek apakah F.R.I.D.A.Y "menolak" perintah berbahaya secara teks, tapi cek apakah hasil actionnya benar-benar bisa dieksekusi jadi kerusakan nyata. Temuan "agentic wrapping menaikkan ASR 1.6x" adalah peringatan langsung: guardrail yang cuma difilter di level prompt/output teks TIDAK CUKUP begitu F.R.I.D.A.Y jadi agent penuh dengan tool-use — perlu guardrail di titik eksekusi aksi juga (selaras dengan temuan LASM survey di atas soal L4 tool-execution layer).
- **Sumber informasi:** Ekstraksi mendalam — abstract & intro dibaca langsung via `pdftotext` (fokus ke deskripsi metodologi benchmark & temuan agregat, BUKAN contoh prompt jailbreak/payload spesifik — sesuai prinsip defensif: pelajari kerangka pertahanannya, bukan resep serangannya)
- **Catatan tambahan:** Kenapa dulu DILEWATI sekarang berhasil: kemungkinan besar masalah lama ada di tool render PDF (Read tool/`pdftoppm`), bukan konten filenya — `pdftotext` (ekstraksi teks murni) berhasil tanpa hambatan untuk keempat paper DILEWATI ini.

### Breaking the Protocol: Security Analysis of the Model Context Protocol Specification and Prompt Injection Vulnerabilities in Tool-Integrated LLM Agents (2026) — ✅ berhasil dibaca 2026-08-12, ⭐ KRITIS untuk M0/M11
- **Lokasi file:** `M11/Breaking the Protocol Security Analysis of the Model Context Protocol Specification and Prompt Injection Vulnerabilities in Tool-Integrated LLM Agents (2026).pdf`
- **Sprint/Modul terkait:** Sprint 1 (M0) DAN Sprint 4 (M11) — sebelumnya DILEWATI, prioritas tinggi karena langsung bahas MCP yang jadi fondasi M0
- **Ide inti:** Maloyan & Namiot. Analisis keamanan FORMAL pertama terhadap **spesifikasi MCP itu sendiri** (bukan implementasi tertentu) — menemukan 3 kerentanan level-protokol yang tidak bisa diperbaiki cuma dengan hardening implementasi: (1) **tidak ada capability attestation** — server bisa mengklaim permission apapun tanpa verifikasi; (2) **bidirectional sampling tanpa autentikasi origin** — memungkinkan server-side prompt injection; (3) **implicit trust propagation** di konfigurasi multi-server. Dibangun **PROTOAMP** (framework testing) dan diuji di 847 skenario serangan lintas 5 implementasi server MCP — arsitektur MCP TERBUKTI memperbesar attack success rate 23-41% dibanding integrasi non-MCP setara. Diusulkan **ATTESTMCP**, ekstensi protokol backward-compatible (attestation + autentikasi pesan) yang menurunkan attack success rate dari 52.8% → 12.4%, overhead cuma ~8.3ms/pesan.
- **Relevansi ke F.R.I.D.A.Y:** **Sangat kritis** — F.R.I.D.A.Y sudah memutuskan pakai MCP sebagai format tool manifest/contract (M0). Paper ini bilang tegas: kelemahan MCP itu **arsitektural, bukan bug implementasi** — jadi F.R.I.D.A.Y tidak bisa cuma "hati-hati implementasi", perlu mitigasi tambahan di level desain M0/M11: (a) jangan percaya penuh capability yang diklaim server MCP pihak ketiga tanpa verifikasi tambahan, (b) autentikasi origin untuk sampling/pesan dari server, (c) jangan otomatis propagate trust antar-server di setup multi-MCP-server. ATTESTMCP bisa jadi referensi konkret desain lapisan keamanan tambahan di atas MCP standar untuk M11, dengan overhead latensi yang kecil (~8ms).
- **Sumber informasi:** Ekstraksi mendalam — abstract, intro, dan background arsitektur MCP dibaca langsung via `pdftotext`
- **Catatan tambahan:** Paper masih cs.CR arXiv 2026, belum tentu peer-reviewed — tapi metodologinya (formal protocol analysis + eksperimen terkontrol 847 skenario) cukup rigorous untuk dijadikan rujukan desain. Worth ditandai sebagai bacaan wajib sebelum M0/M11 mendesain lapisan permission untuk MCP server pihak ketiga.

### Quantifying Frontier LLM Capabilities for Container Sandbox Escape (2026) — ✅ berhasil dibaca 2026-08-12
- **Lokasi file:** `M11/Quantifying Frontier LLM Capabilities for Container Sandbox Escape (2026).pdf`
- **Sprint/Modul terkait:** Sprint 4 (M11) — sebelumnya DILEWATI, ICML 2026
- **Ide inti:** Marchand et al. (Oxford + UK AI Security Institute). Benchmark **SANDBOXESCAPEBENCH** — mengukur kemampuan LLM agent KABUR dari sandbox container (Docker/OCI) tempat dia dijalankan, dibingkai sebagai CTF (Capture The Flag) bertingkat nested-sandbox (lapisan luar berisi "flag" tanpa kerentanan diketahui). Threat model: attacker (agent) SUDAH punya akses shell di dalam container (bukan soal initial access, tapi soal ESCAPE dari isolasi) — mencakup spektrum mekanisme escape: misconfiguration, kesalahan alokasi privilege, kernel flaw, kelemahan runtime/orkestrasi. Temuan: ketika kerentanan sengaja ditambahkan, LLM frontier BISA mengidentifikasi dan mengeksploitasinya — menegaskan evaluasi semacam ini perlu ada supaya sandboxing tetap efektif untuk model yang makin capable.
- **Relevansi ke F.R.I.D.A.Y:** Kalau F.R.I.D.A.Y nanti menjalankan tool/kode di sandbox (mis. untuk M6 OS-control atau eksekusi skrip otomasi), paper ini adalah pengingat langsung: **sandbox container biasa (Docker) tidak otomatis aman** dari agent yang capable — perlu evaluasi eksplisit apakah setup sandbox F.R.I.D.A.Y rentan escape, bukan asumsi "sudah di-sandbox jadi aman". Poin penting: banyak tooling agent open-source (termasuk yang mungkin dipakai F.R.I.D.A.Y) mengandalkan isolasi Docker standar, BUKAN isolasi hardware-level (microVM/Firecracker) yang dipakai provider skala besar — trade-off keamanan vs kompleksitas setup yang perlu disadari sejak M11 didesain.
- **Sumber informasi:** Ekstraksi mendalam — abstract & intro dibaca langsung via `pdftotext` (fokus ke desain benchmark/metodologi evaluasi, bukan detail teknik eksploitasi kernel/container spesifik)
- **Catatan tambahan:** Paper eksplisit menyebut kerentanan HANYA muncul ketika "sengaja ditambahkan" ke benchmark (bukan menemukan 0-day di Docker asli) — jadi ini alat EVALUASI kesiapan sandbox, bukan daftar exploit siap pakai. Cocok dipakai sebagai checklist audit sebelum F.R.I.D.A.Y diberi kemampuan eksekusi kode nyata.

### Optimizing Safety Alignment and Jailbreak Defense for Large Language Models (2025) — ✅ berhasil dibaca 2026-08-12, ⚠️ belum peer-review
- **Lokasi file:** `M11/Optimizing Safety Alignment and Jailbreak Defense for Large Language Models (2025).pdf`
- **Sprint/Modul terkait:** Sprint 4 (M11) — sebelumnya DILEWATI
- **Ide inti:** Wu & Lin (Juntendo University + Univ. of Florida) — **preprint, BELUM peer-reviewed** (dari Preprints.org, bukan venue akademik ter-review). Framework pertahanan multi-lapis: **DeepRefusal** (modul keputusan "refusal-first" — tentukan APAKAH & KENAPA menolak dulu sebelum memutuskan apa yang di-generate), guard model (Qwen3Guard-Gen-8B), kepatuhan ke kerangka governance (NIST AI RMF, EU AI Act), plus **FedMSBA** (federated learning dengan privacy-preserving telemetry untuk kurangi leakage). Diklaim: baseline model rentan 57% (adversarial suffix) dan 88% (indirect injection); dengan DeepRefusal, rata-rata attack success TURUN 95%; guard detector capai F1 83.9%, blokir 66.7% prompt jahat dalam 128 token pertama; FedMSBA kurangi risiko gradient-leakage 70%.
- **Relevansi ke F.R.I.D.A.Y:** Pola "refusal-first decision module" (putuskan apakah/kenapa menolak SEBELUM generate) relevan sebagai desain guardrail M11 — beda dari filter output pasca-generate yang lebih gampang di-bypass. Tapi karena statusnya preprint belum di-review, angka-angka klaim (95% penurunan, dst.) HARUS ditreat skeptis — jangan langsung dipakai sebagai baseline kepercayaan diri keamanan tanpa validasi independen.
- **Sumber informasi:** Ekstraksi mendalam — abstract & awal intro dibaca langsung via `pdftotext`
- **Catatan tambahan:** **Kualitas sumber lebih rendah** dari 3 paper DILEWATI lain di atas (bukan dari arXiv/venue peer-review, dari Preprints.org yang eksplisit menandai "Not peer-reviewed version") — pakai sebagai referensi ide arsitektur (refusal-first module) saja, jangan kutip angka performanya sebagai fakta tervalidasi.

**Catatan proses:** Keempat paper di atas sebelumnya ditandai DILEWATI karena berulang kali memicu error/safety-filter otomatis saat dibaca lewat Read tool/render PDF. Di sesi 2026-08-12, dicoba ulang pakai `pdftotext` (ekstraksi teks murni, bukan render visual) dan **semua berhasil terbaca tanpa hambatan** — dibaca dengan fokus ke abstrak/metodologi/temuan (kerangka pertahanan & evaluasi), bukan meng-copy detail teknik eksploitasi/payload konkret, konsisten dengan prinsip riset keamanan defensif.

---

## Kategori #7 — Wake Word Detection

### A Depthwise Separable CNN for Keyword Spotting on an Embedded System (2020)
- **Lokasi file:** `M7/A Depthwise Separable CNN for Keyword Spotting on an Embedded System (2020).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M7)
- **Ide inti:** Sørensen, Epp & May (EURASIP JASMP 2020) mengganti convolution biasa dengan depthwise-separable convolution pada DS-CNN untuk keyword spotting, memangkas parameter/MAC signifikan sambil menjaga akurasi tinggi di Google Speech Commands, dengan pengukuran deployment nyata di embedded system.
- **Relevansi ke F.R.I.D.A.Y:** Kandidat arsitektur inti untuk M7 ("Hey Friday") yang harus always-on di edge/embedded dengan power sangat terbatas.
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF
- **Catatan tambahan:** Trade-off klasik: parameter/MAC lebih rendah menekan akurasi sedikit dibanding CNN penuh, tapi power/memori jauh lebih hemat — baseline sebelum eksperimen model lain.

### Accurate Detection of Wake Word Start and End Using a CNN (2020) — ✅ terverifikasi 2026-08-12
- **Lokasi file:** `M7/Accurate Detection of Wake Word Start and End Using a CNN (2020).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M7, endpointing/boundary detection)
- **Ide inti:** Amazon Alexa Research (Jose et al., Interspeech-style paper). Untuk KWS single-stage word-level CNN (input window ~1 detik) yang secara desain TIDAK punya cara alami menentukan endpoint (beda dari AM+HMM klasik yang otomatis dapat endpoint dari Viterbi decoding), diusulkan 2 metode: (1) **start-end regression model** — model regresi kedua paralel yang memakai representasi intermediate dari CNN utama untuk memprediksi offset start/end; (2) **multi-aligned output CNN** — CNN utama ditambah output tambahan yang dilatih mendeteksi WW pada alignment berbeda (center/start/end) di dalam window input, lalu posisi puncak posterior tiap output dipakai sebagai estimasi start/end. Diuji pada wake word "Alexa": multi-aligned output CNN paling akurat (~20ms error utk start, ~40ms utk end vs gold-standard AM+HMM), setara dengan akurasi manusia (~30ms STD) untuk start point.
- **Relevansi ke F.R.I.D.A.Y:** Krusial untuk handoff M7→M8 — endpoint tidak presisi bisa memotong sebagian wake word atau menyisakan silence berlebih, menambah latensi dan menurunkan akurasi STT. Pendekatan multi-aligned output CNN paling praktis untuk F.R.I.D.A.Y karena cukup 1 model (bukan 2 model terpisah) dan generalisasinya disebut penulis applicable juga ke ASR endpointing, bukan cuma wake word.
- **Sumber informasi:** Ekstraksi mendalam — dibaca penuh via `pdftotext` (paper cuma ~4 halaman ICASSP/Interspeech-style, seluruh isi terbaca)
- **Catatan tambahan:** Semua eksperimen memakai wake word tunggal "Alexa" — generalisasi ke wake word custom F.R.I.D.A.Y ("Hey Friday") belum tentu identik akurasinya, terutama kalau custom wake word lebih panjang/berbeda struktur fonemnya.

### Deep Spoken Keyword Spotting: An Overview (2021, arXiv) / (IEEE Access, 2022)
- **Lokasi file:** `M7/Deep Spoken Keyword Spotting An Overview (2021).pdf` dan `M7/Deep Spoken Keyword Spotting An Overview (IEEE Access, 2022).pdf` — **duplikat/versi lain satu sama lain** (preprint arXiv vs jurnal terbit resmi, penulis & konten sama: López-Espejo, Tan, Hansen, Jensen)
- **Sprint/Modul terkait:** Sprint 5 (M7)
- **Ide inti:** Overview komprehensif keyword spotting berbasis deep learning — front-end feature extraction, taksonomi arsitektur (CNN/RNN/attention/hybrid), teknik small-footprint, dataset standar, tantangan terbuka (noise robustness, far-field, personalisasi, efisiensi energi).
- **Relevansi ke F.R.I.D.A.Y:** Peta literatur paling lengkap untuk M7 — dipakai sebagai "index" memilih arsitektur mana (dari paper lain di folder ini) yang paling sesuai kebutuhan power/akurasi, dan daftar open problem jadi checklist risiko.
- **Sumber informasi:** Ekstraksi mendalam 2026-08-12 — abstract & intro versi IEEE Access dibaca langsung via `pdftotext`, dikonfirmasi cocok 100% dengan judul (López-Espejo, Tan, Hansen, Jensen, IEEE Access 2022)
- **Catatan tambahan:** Kutip versi IEEE Access (2022) karena sudah peer-reviewed final; tidak perlu baca kedua file terpisah.

### DONUT: CTC-Based Query-by-Example Keyword Spotting (2018)
- **Lokasi file:** `M7/DONUT CTC-Based Query-by-Example Keyword Spotting (2018).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M7, custom wake word tanpa retraining)
- **Ide inti:** Lugosch, Myer & Tomar (Fluent.ai, NeurIPS 2018): user merekam beberapa contoh ucapan custom wake word, sistem menjalankan beam search CTC menghasilkan beberapa hipotesis fonem, skor CTC-forward digabung saat inferensi — tanpa retraining jaringan atau upload data ke cloud. EER 3.7-7.8% di dataset English-Fewshot, mengungguli DTW konvensional.
- **Relevansi ke F.R.I.D.A.Y:** Solusi konkret fitur "custom wake word" — user ucapkan nama panggilan pilihan 3x, sistem belajar on-device tanpa kirim suara ke cloud (privacy-friendly).
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF
- **Catatan tambahan:** Komputasi sangat ringan (model label ~168K parameter), layak jalan di embedded; akurasi bergantung phoneme error rate model dasar.

### Efficient On-Device Domain Learning for Keyword Spotting on Ultra-Low-Power Platforms — "ODDA" (2026)
- **Lokasi file:** `M7/Efficient On-Device Domain Learning for Keyword Spotting on Ultra-Low-Power Platforms (2026).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M7, adaptasi noise di lapangan)
- **Ide inti:** Cioflan et al. (ETH Zürich/Huawei/KU Leuven): model KWS DS-CNN offline (backbone int8 dibeku), lalu HANYA classifier/layer akhir di-fine-tune di MCU (GAP9, ~26mW) dengan noise lingkungan riil + subset kecil sampel bersih (bisa 10 sampel/kelas, 10kB memori). Akurasi naik hingga 14% (noise non-stasioner) dan 21% (koartikulasi tak terlihat), biaya 357mJ, adaptasi 13.5 detik.
- **Relevansi ke F.R.I.D.A.Y:** Konsep kunci untuk M7 produksi — wake word dipakai di lingkungan beragam (dapur, kamar, mobil, kantor); ODDA membuat model beradaptasi ke noise lokal on-device tanpa kirim data ke cloud, hanya update layer terakhir. Relevan juga untuk M14 (context-aware terhadap lingkungan).
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF
- **Catatan tambahan:** Trade-off adaptation depth vs resource; hanya menangani additive background noise, TIDAK reverberasi/karakteristik mic/aksen — perlu solusi tambahan (MCT/augmentasi) untuk itu.

### Sub-mW Keyword Spotting on an MCU: Analog Binary Feature Extraction and Binary Neural Networks (2022)
- **Lokasi file:** `M7/Sub-mW Keyword Spotting on an MCU Analog Binary Feature Extraction and Binary Neural Networks (2022).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M7, ekstrem low-power always-on)
- **Ide inti:** Cerutti et al.: pipeline KWS konsumsi <1mW, menggabungkan ekstraksi fitur biner analog (sebelum digitalisasi) dengan Binary Neural Network (bobot/aktivasi -1/+1, MAC diganti XNOR+popcount).
- **Relevansi ke F.R.I.D.A.Y:** Titik ekstrem paling agresif untuk M7 always-on 24/7 dengan baterai kecil/energy harvesting.
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF
- **Catatan tambahan:** Trade-off akurasi vs power sangat tajam — cocok untuk stage pertama "trigger kasar" pada arsitektur cascade dua-tahap (BNN sub-mW selalu jalan, model lebih besar hanya jalan saat trigger).
- **[2026-08-13] Resolusi duplikat:** file `A Depthwise Separable CNN for Keyword Spotting on an Embedded System (2022).pdf` yang sebelumnya "menyembunyikan" konten ini (nama salah, isi sama persis dengan file di atas — dikonfirmasi via `diff` full-text, kosong total) sudah **dihapus** dari `M7/`. User sempat coba cari paper DS-CNN 2022 yang genuinely berbeda dan tidak menemukan — kesimpulan bersama: tidak ada paper terpisah dengan judul itu, "2022" di nama file lama cuma kesalahan penamaan/duplikasi. Kategori #7 tetap lengkap dengan paper Sørensen (2020) sebagai referensi DS-CNN.

---

## Kategori #8 — Real-Time Speech Pipeline

### A Low-Latency Streaming On-Device Automatic Speech Recognition System Using a CNN Acoustic Model on FPGA and a Language Model on Smartphone (2022)
- **Lokasi file:** `M8/A Low-Latency Streaming On-Device Automatic Speech Recognition System Using a CNN Acoustic Model on FPGA and a Language Model on Smartphone.pdf`
- **Sprint/Modul terkait:** Sprint 5 (M8)
- **Ide inti:** Park et al. (Electronics 2022, POSTECH): acoustic model CNN TDS ramping (9.3M weight, dari 115M) di FPGA, input unit 80ms tanpa future context, dipasangkan LM 3-gram di smartphone; latency worst-case 125.5ms, RTF 0.57, WER AM 13.2%/WER+LM 9.1% (LibriSpeech test-clean).
- **Relevansi ke F.R.I.D.A.Y:** Blueprint split acoustic-model (edge) + language-model (device lebih kuat) untuk M8 hybrid edge-cloud (lihat juga kategori #12).
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF
- **Catatan tambahan:** 0ms lookahead demi latensi minimal menaikkan WER ~3% absolut; LM dictionary 1.3GB jadi bottleneck memori untuk perangkat sangat kecil.

### Building Accurate Low Latency ASR for Streaming Voice Search (2023) — ✅ terverifikasi 2026-08-12
- **Lokasi file:** `M8/Building Accurate Low Latency ASR for Streaming Voice Search (2023).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M8)
- **Ide inti:** Goyal & Garera (Flipkart, ACL 2023 Industry Track). Bukan "two-pass decoding" seperti dugaan sebelumnya — pendekatannya beda: arsitektur **hierarchical CTC (HCTC) 3-level** berbasis LSTM+attention (memprediksi karakter → subword pendek → subword panjang secara fine-to-coarse dalam satu model, terinspirasi Fernández et al. 2007), plus strategi training+inference sederhana untuk **joint ASR + end-of-speech (EOS) detection** dalam satu model CTC end-to-end (pakai token `</s>` dengan early/late penalty, threshold dinamis saat inference). Dievaluasi di voice search Hinglish (Hindi-English campur) skala produksi Flipkart (~6 juta query/hari): WER 3.69% (tanpa EOS)/4.78% (dengan EOS), latensi pencarian turun ~46.64% (1300ms) dibanding pakai VAD independen terpisah.
- **Relevansi ke F.R.I.D.A.Y:** Koreksi penting dari catatan lama — bukan two-pass rescoring, tapi joint EOS detection di dalam model CTC itu sendiri. Pola ini langsung relevan untuk M8: F.R.I.D.A.Y bisa deteksi "user selesai bicara" tanpa VAD model terpisah, mengurangi latensi respons secara signifikan (temuan Flipkart: ~1.3 detik lebih cepat). Konteks Hinglish (kode-campur bahasa) juga relevan kalau F.R.I.D.A.Y perlu dengar campuran Indonesia-Inggris.
- **Sumber informasi:** Ekstraksi mendalam — abstract, intro, related work, dan awal metodologi dibaca langsung via `pdftotext`
- **Catatan tambahan:** Arsitektur HCTC 3-level dan skema EOS token spesifik untuk basis CTC — perlu adaptasi kalau F.R.I.D.A.Y pakai basis model streaming lain (RNN-T/Transducer, lihat FastEmit di bawah).

### FastEmit: Low-Latency Streaming ASR with Sequence-Level Emission Regularization (2021)
- **Lokasi file:** `M8/FastEmit Low-latency Streaming ASR with Sequence-level Emission Regularization (2021).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M8)
- **Ide inti:** Yu et al. (Google, ICASSP 2021): regularisasi loss level-sequence pada RNN-Transducer yang mendorong model emit token lebih cepat saat streaming, tanpa constraint alignment eksplisit — mengurangi latensi emission dengan degradasi WER minimal.
- **Relevansi ke F.R.I.D.A.Y:** Teknik murah (hanya loss training) untuk M8 jika basis modelnya RNN-T — menekan persepsi latensi tanpa redesain arsitektur besar.
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF
- **Catatan tambahan:** Regularisasi terlalu agresif bisa menaikkan WER — perlu tuning bobot sesuai kebutuhan responsivitas.

### Pushing the Limits of On-Device Streaming ASR: A Compact, High-Accuracy English Model for Low-Latency Inference (2026)
- **Lokasi file:** `M8/Pushing the Limits of On-Device Streaming ASR A Compact, High-Accuracy English Model for Low-Latency Inference (2026).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M8, model produksi) — kuat kaitannya juga ke kategori #11
- **Ide inti:** Tim CoreAI Microsoft (2026), studi empiris >50 konfigurasi 6 keluarga model (Whisper, Nemotron, Parakeet TDT, Canary, Conformer Transducer, Qwen3-ASR) untuk ASR streaming CPU-only edge. Model streaming NATIVE (Nemotron Speech Streaming ~0.6B) jauh lebih unggul dari model batch besar yang dipaksa chunking. Model final: int4 k-quant custom, 2.47GB→0.67GB, WER 8.20%, RTFx >6x realtime (AMD EPYC 32-core), latensi algoritmik 0.56 detik.
- **Relevansi ke F.R.I.D.A.Y:** Sangat relevan untuk M8 produksi CPU-only: (1) pilih model streaming native, bukan model batch di-chunk paksa; (2) resep kuantisasi int4 k-quant menekan ukuran model ASR <1GB dengan WER turun <0.2% absolut; (3) metrik RTFx & effective-latency formula sebagai kriteria evaluasi M8 (relevan juga #16).
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF
- **Catatan tambahan:** Context history cukup (5.6 detik cached) krusial untuk akurasi; kuantisasi integer murni end-to-end justru MEMPERBURUK WER (akumulasi rounding error) — dequantize-ke-float tetap perlu dipertahankan. Belum mencakup diarization/code-switching/normalisasi teks terbalik.

### WhisperPipe: A Resource-Efficient Streaming Architecture for Real-Time Automatic Speech Recognition (2026)
- **Lokasi file:** `M8/WhisperPipe A Resource-Efficient Streaming Architecture for Real-Time Automatic Speech Recognition (2026).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M8)
- **Ide inti:** Mengadaptasi Whisper (aslinya batch/offline) jadi arsitektur pipeline streaming hemat resource — chunking/pipelining cerdas + manajemen cache/context antar-chunk, tanpa retrain arsitektur dari nol.
- **Relevansi ke F.R.I.D.A.Y:** Jalan praktis memanfaatkan kualitas Whisper tanpa menanggung latensi mode-batch — opsi menengah antara "Whisper apa adanya" vs "bangun model streaming native dari nol".
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF
- **Catatan tambahan:** Bandingkan head-to-head dengan model native-streaming (Nemotron, lihat entri "Pushing the Limits...") sebelum dipilih untuk produksi — riset lain menemukan Whisper yang di-chunk paksa mengalami degradasi WER besar.

### WhisperRT — Turning Whisper into a Causal Streaming Model (2026)
- **Lokasi file:** `M8/WhisperRT – Turning Whisper into a Causal Streaming Model (2026).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M8)
- **Ide inti:** Mengubah mekanisme atensi Whisper (bidirectional/non-causal) menjadi CAUSAL agar model streaming secara alami, bukan sekadar chunking eksternal — menyentuh arsitektur internal, bukan hanya wrapper inferensi.
- **Relevansi ke F.R.I.D.A.Y:** Solusi lebih fundamental dibanding chunking eksternal untuk mendapat Whisper versi streaming asli — relevan kalau F.R.I.D.A.Y ingin kualitas setara Whisper dengan latensi lebih konsisten.
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF
- **Catatan tambahan:** Butuh finetuning ulang (bukan cuma perubahan inferensi) — cost lebih tinggi dari WhisperPipe, tapi potensi kualitas streaming lebih baik.

### Interacting with Smart Virtual Assistants for Individuals with Dysarthria: A Comparative Study on Usability and User Preferences
- **Lokasi file:** `M8/Interacting with Smart Virtual Assistants for Individuals with Dysarthria A Comparative Study on Usability and User Preferences.pdf`
- **Sprint/Modul terkait:** Sprint 6-7 (M8-M9); relevan juga Sprint 12 (Evaluation)
- **Ide inti:** Studi komparatif usability & preferensi pengguna dengan dysarthria (gangguan motorik bicara) saat berinteraksi dengan smart virtual assistant komersial — mengukur seberapa baik sistem ASR menangani ucapan non-standar.
- **Relevansi ke F.R.I.D.A.Y:** Pengingat robustness ASR terhadap variasi ucapan non-standar; kalau F.R.I.D.A.Y menyasar accessibility, preferensi UX di paper ini (toleransi kesalahan, input alternatif) jadi requirement desain tambahan.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan, konten dikonfirmasi cocok dengan judul
- **Catatan tambahan:** Niche use-case — prioritas tergantung apakah F.R.I.D.A.Y menyasar pengguna speech impairment; kalau tidak, jadi referensi sekunder.

---

## Kategori #9 — Speaker Identification & Voice Authentication

### A Survey on Presentation Attack Detection for Automatic Speaker Verification Systems (2021)
- **Lokasi file:** `M9/A Survey on Presentation Attack Detection for Automatic Speaker Verification Systems (2021).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M9)
- **Ide inti:** Tan et al. mensurvei 172 artikel PAD untuk ASV (2015-2021), membangun taksonomi 7 atribut (jenis attack, fitur, classifier, fusion, metodologi, dataset, kriteria evaluasi).
- **Relevansi ke F.R.I.D.A.Y:** Peta jalan M9 — PAD efektif harus menangani MULTIPLE jenis spoof, fitur majemuk, idealnya diuji cross-dataset — checklist requirement modul verifikasi suara.
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF
- **Catatan tambahan:** GMM masih classifier paling sering dipakai meski deep learning naik; replay attack PALING mudah dilakukan penyerang non-profesional — prioritas pertahanan lapis pertama. Generalisasi cross-dataset masih lemah di seluruh literatur.

### A Survey on Speech Deepfake Detection (2025) — ✅ terverifikasi 2026-08-12
- **Lokasi file:** `M9/A Survey on Speech Deepfake Detection (2025).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M9)
- **Ide inti:** Li, Ahmadiadli, Zhang (Toronto Metropolitan University). Survei sistematis >200 paper deteksi speech deepfake (sampai Maret 2024), cakupan lebih luas dari survei sejenis: eksplisit membedakan **fully-fake vs partial-deepfake** (potongan audio yang cuma sebagian palsu — belum dibahas survei sebelumnya), plus model speaker-aware detection (integrasi speaker verification + deepfake countermeasure — nyambung langsung ke entry "Speaker-Aware Anti-Spoofing" di bawah). Fokus ke serangan TTS/Voice-Conversion (termasuk metode berbasis LLM+neural audio codec generasi terbaru), SENGAJA TIDAK mencakup replay attack (fisik, beda mekanisme) — beda scope dari ASVspoof.
- **Relevansi ke F.R.I.D.A.Y:** Karena F.R.I.D.A.Y juga akan punya modul voice cloning/TTS (M10), survei ini penting untuk risiko "deepfake" pada M9 sendiri — desain M9 harus tahan generator TTS generasi terbaru (termasuk LLM-based codec, bukan cuma vocoder lama), bukan cuma dataset lama. Konsep **partial deepfake detection** relevan kalau nanti ada skenario audio panjang yang cuma sebagian disuntik instruksi palsu (mirip indirect prompt injection versi audio — overlap dengan M11).
- **Sumber informasi:** Ekstraksi mendalam — abstract & intro dibaca langsung via `pdftotext`, dikonfirmasi cocok 100% dengan judul
- **Catatan tambahan:** Survei eksplisit TIDAK membahas replay attack (physical attack) — untuk itu tetap perlu paper ASVspoof/PAD di bawah, dua-duanya saling melengkapi bukan tumpang tindih.

### ASVspoof: The Automatic Speaker Verification Spoofing and Countermeasures Challenge (2017) — ⚠️ koreksi 2026-08-12, isi beda dari catatan lama
- **Lokasi file:** `M9/ASVspoof The Automatic Speaker Verification Spoofing and Countermeasures Challenge (2017).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M9)
- **Ide inti:** **KOREKSI:** catatan lama ("fokus replay attack, corpus RedDots, EER 30.6%/6.73%") ternyata salah paper — itu deskripsi edisi **ASVspoof 2017** (replay-focused), sedangkan file PDF ini isinya justru laporan jurnal (IEEE JSTSP 2017, Wu/Yamagishi/Kinnunen/Hanilçi/Sahidullah/Sizov/Evans/Todisco/Delgado) yang mereview **ASVspoof 2015** — dataset genuine+spoofed dari 106 pembicara, spoofing dibuat dari **10 algoritma speech-synthesis/voice-conversion berbeda** (BUKAN replay attack). Paper ini membangun protokol/dataset standar industri untuk countermeasure ASV, mereview hasil evaluasi 2015 secara detail, dan sekilas mempreview rencana edisi 2017.
- **Relevansi ke F.R.I.D.A.Y:** Tetap jadi dataset/protokol acuan standar industri untuk M9, tapi fokusnya **TTS/voice-conversion spoofing**, bukan replay attack seperti diklaim sebelumnya — kalau butuh referensi replay attack "in the wild" secara spesifik (RedDots), itu perlu dicari paper terpisah (ASVspoof 2017 edition paper, belum ada di koleksi ini).
- **Sumber informasi:** Ekstraksi mendalam — abstract, intro, dan bagian dataset (ASVspoof 2015 database, 10 algoritma spoofing, hasil EER per sistem) dibaca langsung via `pdftotext`
- **Catatan tambahan:** Karena scope-nya TTS/VC (bukan replay), paper ini lebih komplementer ke "A Survey on Speech Deepfake Detection" di atas daripada ke replay-attack testing. Kalau butuh protokol replay-specific, itu masih jadi gap koleksi paper M9.

### ECAPA-TDNN: Emphasized Channel Attention, Propagation and Aggregation in TDNN Based Speaker Verification (2020)
- **Lokasi file:** `M9/ECAPA-TDNN Emphasized Channel Attention, Propagation and Aggregation in TDNN Based Speaker Verification (2020).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M9, arsitektur inti speaker embedding)
- **Ide inti:** Desplanques, Thienpondt & Demuynck (Ghent University, Interspeech 2020): menyempurnakan x-vector/TDNN dengan SE-Res2Net 1D, multi-layer feature aggregation, attentive statistics pooling — EER 0.87% di VoxCeleb1, ~19% perbaikan relatif dari baseline.
- **Relevansi ke F.R.I.D.A.Y:** Salah satu arsitektur speaker-embedding paling kuat & populer — kandidat utama backbone speaker verification M9 (bedakan suara pemilik vs orang lain sebelum eksekusi perintah sensitif).
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF
- **Catatan tambahan:** Varian 512-channel (6.2M parameter) tetap mengungguli baseline lama dengan parameter jauh lebih hemat dari varian 1024-channel — pilihan lebih baik untuk device kecil.

### Speaker-Aware Anti-Spoofing (2023) — ✅ terverifikasi 2026-08-12
- **Lokasi file:** `M9/Speaker-Aware Anti-Spoofing (2023).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M9)
- **Ide inti:** Liu, Sahidullah, Lee, Kinnunen (University of Eastern Finland dkk). Formalisasi masalah "speaker-aware anti-spoofing" sebagai **conditional hypothesis test** (H0: sample asli DAN cocok speaker target; H1: sample palsu DAN mengklaim jadi speaker target) — beda dari definisi anti-spoofing konvensional yang tidak dikondisikan ke identitas. Diimplementasi sebagai ekstensi speaker-aware ke model SOTA **AASIST** (audio anti-spoofing pakai integrated spectro-temporal graph attention), dengan 2 strategi integrasi info speaker target (level frame vs level utterance) via speaker embedding dari model ASV terlatih (ECAPA-TDNN — sama seperti entry lain di kategori ini). Hasil di protokol custom berbasis ASVspoof 2019: **perbaikan relatif hingga 25.1% (EER)** dan 11.6% (t-DCF) dibanding baseline speaker-independent.
- **Relevansi ke F.R.I.D.A.Y:** Sangat relevan karena F.R.I.D.A.Y biasanya punya satu/segelintir pengguna terdaftar — countermeasure lebih personal & presisi terhadap profil suara pemilik (pakai sample enrollment), alih-alih model generic populasi umum. Bisa langsung dikombinasikan dengan ECAPA-TDNN yang sudah jadi kandidat backbone M9 di entry lain — pipeline-nya kompatibel (sama-sama pakai speaker embedding dari model ASV).
- **Sumber informasi:** Ekstraksi mendalam — abstract, intro, dan awal metodologi (definisi masalah, arsitektur integrasi) dibaca langsung via `pdftotext`
- **Catatan tambahan:** Perbaikan 25.1%/11.6% diukur di protokol custom (bukan benchmark standar ASVspoof resmi) — perlu dicatat kalau dipakai sebagai angka pembanding, bukan hasil head-to-head apple-to-apple dengan sistem lain.

### Voice Spoofing Countermeasures: Taxonomy, State-of-the-art, Experimental Analysis of Generalizability, Open Challenges, and the Way Forward (2022)
- **Lokasi file:** `M9/Voice Spoofing Countermeasures Taxonomy, State-of-the-art, Experimental Analysis of Generalizability, Open Challenges, and the Way Forward (2022).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M9)
- **Ide inti:** Survei besar (10.4MB) membangun taksonomi countermeasure voice spoofing, mereview SOTA, DAN melakukan analisis eksperimental generalisasi countermeasure lintas dataset/kondisi (bukan hanya tinjauan pasif).
- **Relevansi ke F.R.I.D.A.Y:** Bersama survei PAD dan ASVspoof 2017, melengkapi trio referensi utama merancang lapisan pertahanan M9 secara menyeluruh — komponen analisis generalisasi eksperimentalnya berguna untuk protokol pengujian robustness sebelum rilis.
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF
- **Catatan tambahan:** Untuk detail eksperimen spesifik, fokus baca ulang bagian "Experimental Analysis of Generalizability" — kontribusi paling unik dibanding survei PAD lain.

### Vulnerability Issues in Automatic Speaker Verification (ASV) Systems (2024)
- **Lokasi file:** `M9/Vulnerability Issues in Automatic Speaker Verification (ASV) Systems (2024).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M9); beririsan dengan kategori #6
- **Ide inti:** Meninjau berbagai isu kerentanan sistem ASV — vektor spoofing (replay, synthesis, voice conversion), kemungkinan serangan adversarial pada model deep learning ASV, implikasi keamanan sistemik saat ASV jadi satu-satunya gerbang otentikasi.
- **Relevansi ke F.R.I.D.A.Y:** Acuan checklist ancaman sebelum M9 dijadikan satu-satunya gate untuk perintah sensitif — mendukung keputusan agar F.R.I.D.A.Y tidak bergantung 100% pada voice auth saja untuk aksi berisiko tinggi (kombinasikan dengan permission model kategori #6).
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF
- **Catatan tambahan:** Rincian daftar vektor serangan spesifik sebaiknya dikonfirmasi ulang langsung dari file untuk kutipan presisi.

---

## Kategori #10 — Expressive TTS

### EmoKnob: Enhance Voice Cloning with Fine-Grained Emotion Control (2024) — ✅ terverifikasi 2026-08-12
- **Lokasi file:** `M10/EmoKnob Enhance Voice Cloning with Fine-Grained Emotion Control (2024).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M10) — EMNLP 2024, Columbia University
- **Ide inti:** Menambahkan "knob" kontrol emosi berbutir halus (bukan kategori diskrit terbatas seperti kerja sebelumnya) ke ATAS model voice cloning foundation yang sudah ada (few-shot) — mengekstrak representasi emosi dari sedikit sampel demonstratif (few-shot) di ruang embedding speaker yang ekspresif, lalu 2 metode diusulkan untuk kontrol emosi dari **teks bebas open-ended** (bukan cuma dari label emosi tetap) — cukup deskripsikan emosinya pakai kalimat biasa. Juga memperkenalkan metrik evaluasi baru khusus untuk menilai faithfulness & recognizability kontrol emosi. Diklaim mengungguli ekspresivitas TTS komersial di evaluasi objektif & subjektif.
- **Relevansi ke F.R.I.D.A.Y:** Relevan untuk M10 + M15 (Persona) — suara F.R.I.D.A.Y bisa punya "dial" intensitas emosi (ceria saat menyapa, tegas saat peringatan) di atas satu identitas suara persona konsisten. Kontrol via teks bebas ("agak khawatir tapi tenang") jauh lebih praktis diintegrasikan ke pipeline generasi respons LLM F.R.I.D.A.Y dibanding harus memetakan ke kategori emosi diskrit.
- **Sumber informasi:** Ekstraksi mendalam — abstract & intro dibaca langsung via `pdftotext`
- **Catatan tambahan:** Bergantung pada model voice cloning foundation yang sudah kuat (dibangun di atas, bukan dari nol) — kualitas hasil akan terikat kualitas base model cloning yang dipilih untuk M10.

### Emotional Prosody Control for Speech Generation (2021) — ✅ terverifikasi 2026-08-12
- **Lokasi file:** `M10/Emotional Prosody Control for Speech Generation (2021).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M10) — Sivaprasad, Kosgi, Gandhi (IIIT Hyderabad + TCS Research)
- **Ide inti:** TTS berbasis **FastSpeech2** yang diperluas jadi multi-speaker DAN dikondisikan pada ruang emosi kontinu **Arousal-Valence (AV)** — bukan kategori emosi diskrit (mis. "senang/sedih/marah") tapi 2 skalar kontinu yang bisa dipetakan ke berbagai emosi (arousal = intensitas, valence = positif/negatif). Ditambahkan blok "Prosody Control" ke arsitektur FastSpeech2 yang mengkondisikan fitur level-phoneme (pitch, energi, durasi) pada nilai AV level-kalimat. Bisa generalize ke speaker & emosi yang tidak dilihat saat training, tanpa degradasi kualitas suara yang bisa diamati.
- **Relevansi ke F.R.I.D.A.Y:** Fondasi konseptual M10 ekspresif — kontrol prosodi terpisah dari identitas suara memungkinkan F.R.I.D.A.Y menyesuaikan nada bicara sesuai konteks (urgent vs santai) sambil konsisten dengan suara dasarnya. Ruang Arousal-Valence yang kontinu (bukan diskrit) lebih fleksibel dipetakan dari hasil reasoning LLM F.R.I.D.A.Y (mis. "situasi darurat" → arousal tinggi) dibanding harus pilih dari daftar emosi tetap.
- **Sumber informasi:** Ekstraksi mendalam — abstract, intro, related work dibaca langsung via `pdftotext`
- **Catatan tambahan:** Berbasis FastSpeech2 (non-autoregressive, cepat) — cocok untuk kebutuhan latensi rendah F.R.I.D.A.Y dibanding TTS autoregresif yang lebih lambat.

### Expressive Neural Voice Cloning (2021) — ✅ terverifikasi 2026-08-12
- **Lokasi file:** `M10/Expressive Neural Voice Cloning (2021).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M10) — Neekhara, Hussain, Dubnov, Koushanfar, McAuley (UC San Diego, ACML 2021)
- **Ide inti:** Voice cloning yang bisa dikontrol secara fine-grained di berbagai aspek gaya (style) untuk speaker yang belum pernah dilihat (unseen speaker) — dicapai dengan mengkondisikan model sintesis secara eksplisit pada 3 hal terpisah: **speaker encoding**, **pitch contour**, dan **latent style tokens**. Mendukung beberapa mode cloning: transfer style dari referensi ucapan, sintesis langsung dari teks, dan kontrol style fine-grained dengan memanipulasi variabel conditioning saat inference — semua cukup pakai sedikit sampel (few-shot/zero-shot).
- **Relevansi ke F.R.I.D.A.Y:** Relevan jika F.R.I.D.A.Y ingin fitur "clone suara pengguna sebagai persona" namun bisa mengatur gaya bicara secara independen — disentanglement identity vs style penting untuk fleksibilitas ini. Pola 3-conditioning (speaker/pitch/style) bisa dijadikan kerangka desain kontrol M10: identitas suara tetap (persona konsisten), tapi pitch & style diatur dinamis sesuai konteks percakapan.
- **Sumber informasi:** Ekstraksi mendalam — abstract & awal intro dibaca langsung via `pdftotext`
- **Catatan tambahan:** Paper cenderung ringkas (fokus arsitektur+eval, bukan survei) — untuk detail arsitektur conditioning yang lebih dalam (bagaimana 3 conditioning digabung), perlu baca bagian metodologi lebih jauh saat mau diimplementasi nyata.

### Meta-Voice: Fast Few-Shot Style Transfer for Expressive Voice Cloning Using Meta Learning (2021) — ✅ terverifikasi 2026-08-12
- **Lokasi file:** `M10/Meta-Voice Fast Few-Shot Style Transfer for Expressive Voice Cloning Using Meta Learning (2021).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M10) — Liu, Su, Yu (Tencent AI Lab)
- **Ide inti:** Dugaan lama benar secara umum, sekarang detail teknisnya terverifikasi — memakai **MAML (model-agnostic meta-learning)** yang di-extend ke TTS: base model multi-speaker+multi-prosody dilatih di corpus besar, lalu **parameter dipisah jadi "shared" vs "style-specific"** — cuma parameter style-specific yang di-meta-train supaya sangat sensitif terhadap adaptasi cepat. Speaker & prosody representation di-disentangle pakai **domain adversarial training + orthogonal constraint**. Hasil: voice cloning berkualitas dari cuma **5 sampel (~12 detik audio)**, hanya **100 langkah adaptasi**.
- **Relevansi ke F.R.I.D.A.Y:** Relevan untuk fitur "voice cloning instan" dari sedikit sampel (5-10 detik) untuk personalisasi cepat tanpa fine-tuning lama — cocok untuk onboarding cepat di M10. Angka konkret (5 sampel/12 detik/100 step) berguna sebagai target benchmark realistis kalau F.R.I.D.A.Y mau fitur "user rekam suara sebentar, F.R.I.D.A.Y langsung bisa clone".
- **Sumber informasi:** Ekstraksi mendalam — abstract, intro, dan awal arsitektur model dibaca langsung via `pdftotext`
- **Catatan tambahan:** Butuh proses meta-training awal yang mahal (banyak speaker/style) — cocok dilakukan sekali di cloud/training pipeline, model hasilnya dipakai ringan di edge. Domain adversarial training menambah kompleksitas training (butuh gradient reversal layer) — bukan sekadar fine-tuning biasa.

### Prosody-TTS: Improving Prosody with Masked Autoencoder and Conditional Diffusion Model for Expressive Text-to-Speech (2023) — ✅ terverifikasi 2026-08-12
- **Lokasi file:** `M10/Prosody-TTS Improving Prosody with Masked Autoencoder and Conditional Diffusion Model for Expressive Text-to-Speech (2023).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M10) — Huang, Zhang, Ren, Zhao, Yu (Zhejiang University + Tencent AI Lab, ACL Findings 2023)
- **Ide inti:** Dugaan lama benar, sekarang terverifikasi detail: mengatasi 2 masalah TTS ekspresif sekaligus — (1) **Prosody-MAE**: masked autoencoder self-supervised yang belajar representasi prosodi HANYA dari audio (tanpa butuh teks/transkripsi), jadi generalisasinya bagus ke berbagai corpus; (2) **diffusion model** di latent space untuk sampling prosodi — mengatasi masalah regresi biasa (MSE) yang menghasilkan prediksi "blurry"/rata-rata karena prosodi sebenarnya multimodal (satu fonem bisa diucapkan banyak gaya berbeda, regresi biasa cuma prediksi rata-ratanya). SOTA di benchmark LJSpeech & LibriTTS.
- **Relevansi ke F.R.I.D.A.Y:** Diffusion-based prosody generation adalah SOTA kualitas ekspresi suara sintetis — referensi upgrade M10 dari TTS netral ke TTS natural secara prosodik sesuai konteks percakapan. Insight penting: masalah "TTS terdengar monoton/rata" itu sumbernya dari loss regresi MSE, bukan cuma kurang data — kalau M10 nanti terasa monoton, diffusion-based sampling adalah salah satu solusi arsitektural, bukan cuma soal data training.
- **Sumber informasi:** Ekstraksi mendalam — abstract, intro, related work dibaca langsung via `pdftotext`
- **Catatan tambahan:** Diffusion model lebih mahal komputasi (multiple denoising steps) — mungkin lebih cocok mode "high-quality narration" daripada respons cepat sehari-hari. Prosody-MAE-nya sendiri (bagian self-supervised) mungkin tetap berguna dipisah dari diffusion samplernya kalau butuh versi lebih ringan.

### Zero-Shot Voice Cloning Text-to-Speech for Dysphonia Disorder Speakers (2024)
- **Lokasi file:** `M10/Zero-Shot Voice Cloning Text-to-Speech for Dysphonia Disorder Speakers (2024).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M10)
- **Ide inti:** Menerapkan zero-shot voice cloning TTS khusus untuk pengguna dengan gangguan suara (dysphonia) — memungkinkan sintesis suara mendekati suara asli dari sedikit sampel referensi (zero/few-shot), tanpa data training besar per individu.
- **Relevansi ke F.R.I.D.A.Y:** Relevan untuk aksesibilitas M10 dan sebagai referensi robustness — model voice cloning modern tetap berkualitas baik meski data referensi jauh dari ideal studio, berguna untuk cloning dari sampel rekaman user yang bervariasi kualitasnya.
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF
- **Catatan tambahan:** Fokus etis/medis berbeda dari kebutuhan utama F.R.I.D.A.Y, tapi teknik intinya (zero-shot speaker adaptation dari input tidak sempurna) tetap transferable ke skenario onboarding suara realistis (mic murah, noise).

---

## Kategori #11 — Local LLM Inference & Optimization

### AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration (2026)
- **Lokasi file:** `M12/AWQ Activation-aware Weight Quantization for LLM Compression and Acceleration (2026).pdf`
- **Sprint/Modul terkait:** Sprint 8 (M12)
- **Ide inti:** Kuantisasi bobot low-bit yang hanya melindungi ~1% "salient weight channel" berdasarkan distribusi aktivasi (bukan bobot itu sendiri), tanpa backprop/reconstruction — generalisasi baik ke domain baru. Runtime TinyChat: speedup 3-4x vs FP16 di GPU mobile/edge, berhasil menjalankan Llama-2 70B di GPU mobile.
- **Relevansi ke F.R.I.D.A.Y:** Kandidat utama teknik kuantisasi untuk LLM lokal mode offline/privacy-first di perangkat resource terbatas, menjaga kualitas jawaban sambil mempercepat token generation untuk respons voice real-time.
- **Sumber informasi:** Ekstraksi parsial — judul & abstrak diverifikasi langsung dari teks PDF
- **Catatan tambahan:** Butuh kalibrasi aktivasi offline sebelum deployment — perlu pipeline kuantisasi terpisah setiap update model lokal.

### Highly Optimized Kernels and Fine-Grained Codebooks for LLM Inference on Arm CPUs (2024)
- **Lokasi file:** `M12/Highly Optimized Kernels and Fine-Grained Codebooks for LLM Inference on Arm CPUs (2024).pdf`
- **Sprint/Modul terkait:** Sprint 8 (M12)
- **Ide inti:** Kernel inferensi LLM dioptimalkan untuk CPU Arm — mengurangi overhead dequantization lewat layout data interleaved dan kuantisasi codebook non-uniform per grup: 3-3.2x lebih cepat prompt processing, 2x decoding vs baseline llama.cpp (4-bit & 2-bit).
- **Relevansi ke F.R.I.D.A.Y:** Relevan menjalankan F.R.I.D.A.Y di perangkat tanpa GPU dedicated (Raspberry Pi, smartphone Arm, mini-PC ARM) — modul kontrol IoT/wake-word/local inference on-device murni.
- **Sumber informasi:** Ekstraksi parsial — judul & abstrak diverifikasi langsung dari teks PDF
- **Catatan tambahan:** Optimasi spesifik Arm (NEON/SVE) tidak otomatis berlaku di x86 — perlu jalur optimasi kernel berbeda untuk PC desktop x86.

### Optimization of Armv9 Architecture General Large Language Model Inference Performance Based on llama.cpp (2024)
- **Lokasi file:** `M12/Optimization of Armv9 Architecture General Large Language Model Inference Performance Based on llama.cpp (2024).pdf`
- **Sprint/Modul terkait:** Sprint 8 (M12)
- **Ide inti:** Studi kasus optimasi llama.cpp untuk Qwen-1.8B di CPU server Arm (Yitian 710, Armv9): kuantisasi Int8, vektorisasi NEON/VDOT/MMLA, compiler flag optimal — prefill 1.6x lebih cepat, decoding 24x lebih cepat, memori turun 1/5, akurasi hampir tidak berubah.
- **Relevansi ke F.R.I.D.A.Y:** Panduan teknis konkret deployment model lokal berbasis llama.cpp di hardware Arm — kombinasi Int8 + compiler flag sebagai langkah optimasi low-effort/high-impact sebelum teknik lebih kompleks (AWQ/SqueezeLLM).
- **Sumber informasi:** Ekstraksi parsial — judul & abstrak diverifikasi langsung dari teks PDF
- **Catatan tambahan:** Angka speedup 24x sangat spesifik untuk kombinasi model kecil (1.8B) + chip tertentu — jangan generalisasi langsung ke model lebih besar atau chip konsumer biasa.

### Optimizing LLMs for Resource-Constrained Environments: A Survey of Model Compression Techniques (2025)
- **Lokasi file:** `M12/Optimizing LLMs for Resource-Constrained Environments A Survey of Model Compression Techniques (2025).pdf`
- **Sprint/Modul terkait:** Sprint 8 (M12)
- **Ide inti:** Survei tiga pendekatan utama kompresi LLM untuk edge/mobile: Knowledge Distillation, Model Quantization, Model Pruning (plus singkat mixture-of-experts dan early-exit).
- **Relevansi ke F.R.I.D.A.Y:** Peta/menu teknik untuk M12 sebelum memilih teknik spesifik — distilasi untuk model kecil khusus voice/wake-word, quantization untuk model penalaran umum, pruning untuk command-following sederhana.
- **Sumber informasi:** Ekstraksi parsial — judul & abstrak diverifikasi langsung dari teks PDF
- **Catatan tambahan:** Sebagai survei, luas tapi tidak sedalam paper teknik individual — cocok untuk keputusan strategis awal saja.

### PocketLLM: Enabling On-Device Fine-Tuning for Personalized LLMs (2024)
- **Lokasi file:** `M12/PocketLLM Enabling On-Device Fine-Tuning for Personalized LLMs (2024).pdf`
- **Sprint/Modul terkait:** Sprint 8 (M12); bersinggungan dengan kategori #2 untuk personalisasi jangka panjang
- **Ide inti:** Optimisasi derivative-free (tanpa gradien/optimizer state memory-intensive) agar fine-tuning LLM personal jalan langsung di smartphone — RoBERTa-large & OPT-1.3B di-fine-tune di HP dengan hanya 4-6.5GB memori, data pribadi tidak pernah keluar dari device.
- **Relevansi ke F.R.I.D.A.Y:** Relevan langsung untuk visi personalisasi jangka panjang — model lokal terus "belajar" dari kebiasaan pengguna di device tanpa kirim data ke cloud, mendukung memori privasi-aman.
- **Sumber informasi:** Ekstraksi parsial — judul & abstrak diverifikasi langsung dari teks PDF
- **Catatan tambahan:** Optimisasi derivative-free konvergen lebih lambat/kurang presisi dibanding fine-tuning gradien biasa — trade-off wajar untuk mobile, tapi butuh lebih banyak data/iterasi.

### SqueezeLLM: Dense-and-Sparse Quantization (2026)
- **Lokasi file:** `M12/SqueezeLLM Dense-and-Sparse Quantization (2026).pdf`
- **Sprint/Modul terkait:** Sprint 8 (M12)
- **Ide inti:** Framework kuantisasi post-training yang mengidentifikasi bottleneck utama inferensi LLM adalah memory bandwidth (bukan compute) — sensitivity-based non-uniform quantization plus dekomposisi dense-and-sparse (outlier disimpan sparse terpisah), kuantisasi 3-bit hampir lossless, speedup hingga 2.3x di GPU.
- **Relevansi ke F.R.I.D.A.Y:** Alternatif/pelengkap AWQ, khususnya saat memory bandwidth jadi bottleneck utama — cocok untuk perangkat dengan GPU kecil/terbatas yang butuh model besar (kualitas reasoning) tetap ringan di memori.
- **Sumber informasi:** Ekstraksi parsial — judul & abstrak diverifikasi langsung dari teks PDF
- **Catatan tambahan:** Dekomposisi dense-and-sparse menambah kompleksitas implementasi (dua jalur komputasi) — trade-off kompleksitas engineering demi kualitas lebih baik di bit rate ultra-rendah.

---

## Kategori #12 — Hybrid Cloud–Edge Routing

### BEST-Route: Adaptive LLM Routing with Test-Time Optimal Compute (2025)
- **Lokasi file:** `M13/BEST-Route Adaptive LLM Routing with Test-Time Optimal Compute (2025).pdf`
- **Sprint/Modul terkait:** Sprint 8 (M13)
- **Ide inti:** Router yang juga memutuskan berapa banyak sampel respons (best-of-n) digenerate dari model kecil berdasarkan kesulitan query dan threshold kualitas — beberapa respons model kecil kadang mengalahkan satu respons model besar dengan biaya lebih murah. Memangkas cost hingga 60% dengan penurunan performa <1%.
- **Relevansi ke F.R.I.D.A.Y:** Untuk query kompleksitas sedang, F.R.I.D.A.Y bisa multi-sampling dari model lokal kecil dulu sebelum memutuskan perlu cloud atau tidak — hemat biaya API sambil menjaga latensi rendah.
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF
- **Catatan tambahan:** Menambah beban komputasi lokal (multi-sampling) — trade-off daya/CPU device vs biaya cloud, perlu tuning threshold sesuai kapasitas hardware target.

### Collaborative Inference and Learning between Edge SLMs and Cloud LLMs: A Survey of Algorithms, Execution, and Open Challenges (2025)
- **Lokasi file:** `M13/Collaborative Inference and Learning between Edge SLMs and Cloud LLMs A Survey of Algorithms, Execution, and Open Challenges (2025).pdf`
- **Sprint/Modul terkait:** Sprint 8 (M13)
- **Ide inti:** Survei taksonomi kolaborasi edge-cloud untuk inferensi (task assignment/division, mixture-based di level task/token termasuk speculative decoding) dan training (parameter alignment, pruning, distilasi dua arah).
- **Relevansi ke F.R.I.D.A.Y:** Peta desain arsitektur hybrid — opsi selain routing biner cloud vs local, misal token-level mixture (draft token SLM lokal, verifikasi cloud lewat speculative decoding) untuk voice assistant latensi rendah + kualitas tinggi.
- **Sumber informasi:** Ekstraksi parsial — judul & abstrak diverifikasi langsung dari teks PDF
- **Catatan tambahan:** Menekankan desain sistem (bukan hanya algoritma) — jaringan, orkestrasi resource, privacy adalah tantangan besar; pertimbangkan bandwidth/latency real koneksi pengguna, bukan asumsi teoretis.

### Efficient Routing of Inference Requests across LLM Instances in Cloud-Edge Computing (2026)
- **Lokasi file:** `M13/Efficient Routing of Inference Requests across LLM Instances in Cloud-Edge Computing (2026).pdf`
- **Sprint/Modul terkait:** Sprint 8 (M13)
- **Ide inti:** Algoritma routing berbasis NSGA-II (multi-objective genetic algorithm) mendistribusikan request ke instance LLM heterogen (edge vs cloud), menyeimbangkan kualitas, response time, biaya adaptif — 95.2% kualitas vs cloud-only dengan biaya turun 34.9%.
- **Relevansi ke F.R.I.D.A.Y:** Cocok jadi algoritma inti M13 saat F.R.I.D.A.Y punya lebih dari satu instance model (HP, PC rumah, API cloud) — routing multi-objektif membantu keputusan berdasarkan panjang prompt, urgensi, kondisi jaringan, bukan aturan if-else statis.
- **Sumber informasi:** Ekstraksi parsial — judul & abstrak diverifikasi langsung dari teks PDF
- **Catatan tambahan:** NSGA-II butuh proses training/kalibrasi tersendiri dan overhead optimasi multi-objektif — lebih cocok untuk versi F.R.I.D.A.Y yang sudah punya banyak node inferensi, bukan MVP awal.

### FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance (2023)
- **Lokasi file:** `M13/FrugalGPT How to Use Large Language Models While Reducing Cost and Improving Performance (2023).pdf`
- **Sprint/Modul terkait:** Sprint 8 (M13)
- **Ide inti:** Tiga strategi hemat biaya LLM: prompt adaptation, LLM approximation, LLM cascade (coba model murah dulu, escalate ke mahal hanya jika perlu). FrugalGPT (instansiasi cascade) setara GPT-4 dengan hingga 98% pengurangan biaya.
- **Relevansi ke F.R.I.D.A.Y:** Pola cascade paling sederhana & praktis untuk M13 — coba model lokal murah dulu, escalate ke cloud hanya kalau confidence rendah/task kompleks — langsung menghemat biaya operasional jangka panjang.
- **Sumber informasi:** Ekstraksi parsial — judul & abstrak diverifikasi langsung dari teks PDF
- **Catatan tambahan:** Efektivitas cascade sangat bergantung scorer/predictor "apakah jawaban murah sudah cukup bagus" — kalau tidak akurat, malah menambah latensi tanpa penghematan.

### Hybrid LLM: Cost-Efficient and Quality-Aware Query Routing (2024)
- **Lokasi file:** `M13/Hybrid LLM Cost-Efficient and Quality-Aware Query Routing (2024).pdf`
- **Sprint/Modul terkait:** Sprint 8 (M13)
- **Ide inti:** Router memprediksi "query difficulty" untuk memutuskan model kecil (edge) atau besar (cloud), dengan quality threshold yang bisa ditune dinamis saat runtime — mengurangi hingga 40% panggilan model besar tanpa penurunan kualitas.
- **Relevansi ke F.R.I.D.A.Y:** Blueprint router M13 — bisa jadi "dial" yang diatur pengguna (mode "hemat baterai/data" vs "kualitas maksimal") yang menggeser threshold cloud vs lokal.
- **Sumber informasi:** Ekstraksi parsial — judul & abstrak diverifikasi langsung dari teks PDF
- **Catatan tambahan:** Prediktor difficulty perlu dilatih dengan data representatif distribusi perintah nyata pengguna — risiko miskalibrasi jika pola pemakaian personal sangat berbeda dari data training router.

### RouteLLM: Learning to Route LLMs with Preference Data (2025)
- **Lokasi file:** `M13/RouteLLM Learning to Route LLMs with Preference Data (2025).pdf`
- **Sprint/Modul terkait:** Sprint 8 (M13)
- **Ide inti:** Melatih router pakai data preferensi manusia untuk memilih dinamis antara model kuat vs lemah saat inferensi, generalisasi baik ke pasangan LLM belum pernah dilihat saat training. Mengurangi biaya >2x tanpa mengorbankan kualitas.
- **Relevansi ke F.R.I.D.A.Y:** Bisa melatih router M13 dari feedback pengguna nyata (jawaban lokal ditandai kurang memuaskan) sehingga router makin akurat, dan generalize walau model cloud/lokal diganti kemudian.
- **Sumber informasi:** Ekstraksi parsial — judul & abstrak diverifikasi langsung dari teks PDF
- **Catatan tambahan:** Butuh dataset preferensi berkualitas untuk training awal — mulai dengan router rule-based sederhana (FrugalGPT/Hybrid LLM) dulu sebelum data preferensi cukup terkumpul.

---

## Kategori #13 — Multi-Agent Orchestration

### AgentVerse: Facilitating Multi-Agent Collaboration and Exploring Emergent Behaviors (2023)
- **Lokasi file:** `M14/AgentVerse Facilitating Multi-Agent Collaboration and Exploring Emergent Behaviors (2023).pdf`
- **Sprint/Modul terkait:** Sprint 9 (M14) — ⭐ Wajib
- **Ide inti:** Framework multi-agent 4-tahap siklus (Expert Recruitment, Collaborative Decision-Making, Action Execution, Evaluation) yang meniru dinamika kelompok manusia, menyesuaikan komposisi agen dinamis dari feedback evaluator. Mengungguli agen tunggal (reasoning, coding, tool-use, embodied AI); mendokumentasikan perilaku emergent (volunteer, conformity, destructive behavior).
- **Relevansi ke F.R.I.D.A.Y:** Blueprint orkestrasi sub-agent (agent perencana, eksekusi IoT, memori) — mekanisme "recruiter" dinamis dan evaluator feedback loop sebelum eksekusi nyata ke perangkat.
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF
- **Catatan tambahan:** Perilaku destructive (agen "merusak" demi efisiensi) adalah peringatan penting untuk sandboxing/permission model saat multi-agent diberi akses eksekusi nyata ke OS/IoT.

### AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation (2024)
- **Lokasi file:** `M14/AutoGen Enabling Next-Gen LLM Applications via Multi-Agent Conversation (2024).pdf`
- **Sprint/Modul terkait:** Sprint 9 (M14)
- **Ide inti:** Framework open-source (Microsoft) membangun aplikasi LLM lewat agen "conversable" yang bisa dikombinasikan bebas (LLM, tools, human-in-the-loop), mendukung pola percakapan fleksibel (joint chat, hierarchical chat).
- **Relevansi ke F.R.I.D.A.Y:** Model "conversable agent" cocok jadi pondasi arsitektur internal — tiap kapabilitas (IoT, memori, OS) dibungkus sebagai agent yang "ngobrol" dengan agent lain, dengan opsi human-in-the-loop untuk konfirmasi aksi sensitif.
- **Sumber informasi:** Ekstraksi parsial — judul & abstrak diverifikasi langsung dari teks PDF
- **Catatan tambahan:** Fleksibel tapi butuh desain pola percakapan jelas — kompleksitas orkestrasi naik cepat dengan jumlah agent, perlu dibatasi topologi komunikasinya.

### CAMEL: Communicative Agents for "Mind" Exploration of Large Language Model Society (2023)
- **Lokasi file:** `M14/CAMEL Communicative Agents for 'Mind' Exploration (2023).pdf`
- **Sprint/Modul terkait:** Sprint 9 (M14)
- **Ide inti:** Framework role-playing dua-agen (AI User memberi instruksi, AI Assistant mengeksekusi) dengan "inception prompting" untuk menjaga agen konsisten dengan intent manusia tanpa campur tangan terus-menerus.
- **Relevansi ke F.R.I.D.A.Y:** Pola user-assistant role-play berguna untuk simulasi/testing internal — satu agent sebagai "pengguna virtual" menguji rangkaian tool-use agent F.R.I.D.A.Y lain tanpa manusia asli.
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF
- **Catatan tambahan:** Rawan "flattery loop" (kedua agen saling menyetujui tanpa kemajuan) — perlu mekanisme terminasi/kriteria selesai jelas untuk mencegah loop tak berujung.

### MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework (2024)
- **Lokasi file:** `M14/MetaGPT Meta Programming for Multi-Agent Collaborative Framework (2024).pdf`
- **Sprint/Modul terkait:** Sprint 9 (M14)
- **Ide inti:** Meng-encode Standardized Operating Procedures (SOP) manusia ke urutan prompt, menugaskan peran spesifik (PM, arsitek, engineer, QA) dalam paradigma "assembly line" — tiap agen verifikasi hasil antara, mengurangi cascading hallucination.
- **Relevansi ke F.R.I.D.A.Y:** Pola SOP + assembly-line cocok untuk task planning multi-langkah dengan verifikasi antara — misal task "atur rumah mode liburan" dipecah ke sub-agent dengan SOP masing-masing yang saling verifikasi sebelum eksekusi final.
- **Sumber informasi:** Ekstraksi parsial — judul & abstrak diverifikasi langsung dari teks PDF
- **Catatan tambahan:** SOP hardcoded ke prompt butuh usaha desain manual signifikan per domain — kurang fleksibel untuk task baru yang belum ada SOP-nya (kontras dengan AutoAgents).

### HearthNet: Edge Multi-Agent Orchestration for Smart Homes (2026)
- **Lokasi file:** `M5/HearthNet Edge Multi-Agent Orchestration for Smart Homes (2026).pdf`
- **Sprint/Modul terkait:** Sprint 3 (M4/M5), Sprint 4 (M11, bagian Authorization — root-issued lease model), Sprint 9 (M14). ⭐ Wajib di 3 sprint. **Jangan dihapus dari Project Knowledge.**
- **Ide inti:** Arsitektur multi-agent yang berjalan di EDGE (bukan cloud) khusus smart-home — tiap domain (keamanan, energi, kenyamanan) dikelola agent spesialis berkoordinasi lewat orchestrator pusat, menekankan latensi rendah & privasi karena semua pemrosesan tetap lokal.
- **Relevansi ke F.R.I.D.A.Y:** Model paling dekat dengan visi smart-home F.R.I.D.A.Y — pola "orchestrator pusat + agent spesialis per-domain" langsung dicontoh untuk M4/M5 dan basis kuat untuk M14 jika berkembang dari monolitik ke multi sub-agent. Bagian Authorization-nya (root-issued lease model) jadi rujukan wajib untuk M11.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan
- **Catatan tambahan:** Berjudul "2026" dan arsitektur baru — validasi/benchmark skala nyata mungkin masih terbatas, perlu dicek klaim performa untuk rumah lebih kompleks dari yang diuji.

### AutoAgents: A Framework for Automatic Agent Generation (2024) — ✅ diganti & terverifikasi 2026-08-13
- **Lokasi file:** `M14/AutoAgents A Framework for Automatic Agent Generation.pdf` — file lama yang mismatch (isi fisika kuantum) sudah dihapus, diganti user dengan file yang benar
- **Sprint/Modul terkait:** Sprint 9 (M14)
- **Ide inti:** Chen et al. (Peking University/HKUST/BAAI, arXiv:2309.17288). Framework yang secara adaptif men-generate dan mengoordinasikan multiple agen spesialis berdasarkan konten task (bukan peran statis yang sudah ditentukan sebelumnya) — dinamai "AutoAgents". Meng-couple hubungan task↔peran: agen-agen yang dibutuhkan digenerate secara dinamis berdasarkan isi task, lalu solusi direncanakan berdasarkan expert agent yang sudah digenerate itu. Ditambahkan peran **observer** yang merefleksikan rencana & respons agen lain untuk perbaikan berkelanjutan. Ada mekanisme **self-refinement** (agen menyempurnakan output sendiri lintas iterasi, membawa "completed steps" dari eksekusi sebelumnya ke prompt berikutnya) dan **collaborative refinement** (dua agen bergantian menyempurnakan hasil satu sama lain).
- **Relevansi ke F.R.I.D.A.Y:** Berguna untuk skenario task pengguna tak terduga — sistem membentuk "tim" agen ad-hoc (agent cuaca + kalender + smart-home) otomatis daripada daftar agent statis hardcoded. Mekanisme observer + self/collaborative-refinement bisa jadi pola konkret untuk M14 mengurangi cascading error tanpa harus hardcode SOP per domain (kontras dengan pendekatan MetaGPT yang SOP-nya hardcoded ke prompt).
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF yang sudah benar (arXiv:2309.17288, dikonfirmasi cocok 100% dengan judul, penulis, dan abstrak)
- **Catatan tambahan:** Eksperimen di paper menunjukkan solusi lebih koheren/akurat dibanding metode multi-agent lain yang dites, tapi generasi peran "on the fly" berarti kualitas tim sangat bergantung kemampuan LLM dasar memahami task dari awal — task ambigu berisiko menghasilkan tim agen yang salah arah sejak awal.

---

## Kategori #14 — Proactive & Context-Aware Behavior

### Intent-Aware Dialogue Generation and Multi-Task Contrastive Learning (2024)
- **Lokasi file:** `M17/Intent-Aware Dialogue Generation and Multi-Task Contrastive (2024).pdf`
- **Sprint/Modul terkait:** Sprint 11 (M17); juga modul NLU inti lintas sprint
- **Ide inti:** Model dialog yang memprediksi intent pengguna dan menghasilkan respons secara joint (multi-task learning), memakai contrastive learning memperkuat representasi intent agar lebih selaras konteks percakapan.
- **Relevansi ke F.R.I.D.A.Y:** Memperkuat intent classification/NLU sebelum routing ke tool-use — joint training intent+response membedakan "user butuh aksi" vs "user hanya ngobrol", penting untuk keputusan proactive/reactive.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan, konten dikonfirmasi cocok dengan judul
- **Catatan tambahan:** Fokus riset NLP akademik, belum tentu langsung deployable — perlu adaptasi ke domain command/tool-use F.R.I.D.A.Y yang lebih terbatas dibanding open-domain chit-chat.

### Proactive Conversational Agents with Inner Thoughts (2025) — ✅ terverifikasi 2026-08-12
- **Lokasi file:** `M17/Proactive Conversational Agents with Inner Thoughts (2025).pdf`
- **Sprint/Modul terkait:** Sprint 11 (M17) — ⭐ Sangat relevan
- **Ide inti:** CHI'25 paper. Mengusulkan **Inner Thoughts** — AI menjaga "aliran pikiran" paralel yang terus jalan bersamaan percakapan (terinspirasi arsitektur kognitif SOAR/ACT-R: retrieve memori → bentuk pikiran → evaluasi respons, siklus terus-menerus), lalu memutuskan sendiri kapan pikiran itu "layak diucapkan" berdasarkan skor motivasi intrinsik. Studi formatif (24 partisipan, think-aloud) mengidentifikasi 8 heuristik kenapa manusia memilih bicara atau diam saat ngobrol (mis. dampak yang diharapkan, urgensi) — dipakai sebagai metrik evaluasi. Dibuktikan lewat 2 implementasi: simulasi multi-agent dan chatbot nyata ("Swimmy"). Poin penting: strategi umum "next-speaker prediction" TERBUKTI tidak cukup untuk proaktivitas — bagus kalau ada cue eksplisit (misal ditanya balik), tapi gagal di kasus "self-selection" (spontan, tidak ada cue) yang justru paling relevan untuk momen F.R.I.D.A.Y perlu nyeletuk duluan.
- **Relevansi ke F.R.I.D.A.Y:** Paper paling konkret untuk M17 — bukan cuma "kapan proaktif" tapi kerangka teknis nyata: agent punya proses background yang terus mengevaluasi apakah momen ini "layak" diinterupsi dengan skor motivasi, bukan aturan if-else statis. 8 heuristik manusia (urgensi, dampak, redundansi) bisa langsung dijadiin prompt/kriteria evaluator M17. Relevan juga untuk M14 (arsitektur multi-agent/paralel thought-stream) dan M2 (long-term memory dipakai buat bentuk pikiran).
- **Sumber informasi:** Ekstraksi mendalam — sebelumnya "Gagal dibaca" (poppler/render PDF tidak tersedia), sekarang berhasil diekstrak penuh via `pdftotext` (fallback yang ternyata tersedia di environment ini) dan dikonfirmasi isinya cocok 1:1 dengan judul (CHI '25, Liu et al., UCLA/Tokyo/Northeastern/Salesforce).
- **Catatan tambahan:** Ekstraksi teks di bagian figure/diagram agak berantakan (teks tumpang tindih karena PDF figure kompleks), tapi bagian abstract/intro/metodologi/limitasi terbaca bersih. Limitasi yang diakui sendiri oleh penulis relevan buat F.R.I.D.A.Y: threshold proaktivitas masih trial-and-error (belum data-driven), dan AI kadang salah menaksir "urgency" pikirannya sendiri — jangan adopsi threshold mentah-mentah, perlu tuning ulang untuk domain F.R.I.D.A.Y (rumah/IoT, bukan casual chat).

### A Survey of Personalization: From RAG to Agent (2025)
- **Lokasi file:** `M17/A Survey of Personalization- From RAG to Agent (2025).pdf`
- **Sprint/Modul terkait:** Sprint 11 (M17); juga Sprint 2 (M2, karena personalisasi berbasis RAG/memori) — ditambahkan user 2026-08-12
- **Ide inti:** Survei personalisasi lintas 3 tahap RAG (pre-retrieval, retrieval, generation) lalu diperluas ke **Personalized LLM-based Agent** (menambah kapabilitas agentic: user understanding, personalized planning & execution, dynamic generation). Menyediakan definisi formal, dataset, dan metrik evaluasi untuk tiap tahap.
- **Relevansi ke F.R.I.D.A.Y:** Peta paling lengkap untuk membuat F.R.I.D.A.Y terasa "kenal" penggunanya — bukan cuma reaktif proaktif (M17), tapi personalisasi cara jawab/rencana berdasarkan preferensi historis (M2 + M15 persona). Struktur "pre-retrieval → retrieval → generation" bisa dipetakan ke pipeline memory-injection M2: kapan filter preferensi user diterapkan (sebelum atau saat retrieval).
- **Sumber informasi:** Ekstraksi mendalam — abstract & intro dibaca langsung via pdftotext
- **Catatan tambahan:** Cakupan sangat luas (25 halaman survei RAG+agent) — worth dipakai sebagai indeks rujukan silang saat M2/M17 mulai desain detail, bukan dibaca linear sekali duduk.

### ContextAgent: Context-Aware Proactive LLM Agents with Open-World Sensory Perceptions (2025)
- **Lokasi file:** `M17/ContextAgent- Context-Aware Proactive LLM Agents with Open-World Sensory Perceptions (2025).pdf`
- **Sprint/Modul terkait:** Sprint 11 (M17) — ⭐ Sangat relevan, ditambahkan user 2026-08-12
- **Ide inti:** NeurIPS 2025. Agent proaktif pertama yang pakai sensor wearable dunia-nyata (video, audio dari kacamata pintar/earphone/smartwatch) untuk memahami konteks pengguna, bukan cuma observasi terbatas di desktop UI atau notifikasi rule-based. Ekstrak konteks multi-dimensi dari sensor mentah → prediksi perlu-tidaknya bantuan proaktif (pakai histori persona) → panggil tool yang relevan secara otomatis dan tidak mengganggu. Dibuat benchmark baru ContextAgentBench (1000 sampel, 9 skenario harian, 20 tool); ContextAgent unggul 8.5% (prediksi proaktif) dan 6.0% (tool-calling) dari baseline.
- **Relevansi ke F.R.I.D.A.Y:** Paling dekat dengan visi jangka panjang F.R.I.D.A.Y yang sadar konteks fisik (bukan cuma teks chat) — kalau nanti ada sensor rumah/wearable, pola "ekstrak konteks sensor → skor perlu-proaktif-tidak → panggil tool" ini langsung jadi blueprint M17. Juga isi gap yang selama ini dicari kategori #14 (konteks-awareness) yang paper mismatch-nya belum ketemu — walau bukan pengganti 1:1 paper yang mismatch, topiknya jauh lebih relevan & konkret.
- **Sumber informasi:** Ekstraksi mendalam — abstract & intro dibaca langsung via pdftotext
- **Catatan tambahan:** Bergantung hardware wearable (kacamata/earphone pintar) yang F.R.I.D.A.Y belum punya di roadmap eksplisit — realistiknya baru applicable kalau nanti ada modul sensor tambahan; untuk sekarang, prinsip arsitekturnya (context extraction → proactivity scoring → tool call) tetap portable ke sensor rumah/IoT biasa.

### Enabling Personalized Long-term Interactions in LLM-based Agents through Persistent Memory and User Profiles (2025)
- **Lokasi file:** `M17/Enabling Personalized Long-term Interactions in LLM-based Agents through Persistent Memory and User Profiles (2025).pdf`
- **Sprint/Modul terkait:** Sprint 11 (M17); juga Sprint 2 (M2) — ditambahkan user 2026-08-12
- **Ide inti:** Mercedes-Benz AG + Ulm University. Framework personalisasi jangka panjang yang menggabungkan 6 pola agentic (Central Coordination, Planning, Multi-Source Retrieval, Multi-Agent Collaboration, Reflection, Persistent Memory) dengan memori persisten (long-term via embedding + short-term untuk konteks terbaru) dan user profile yang terus berkembang. Dievaluasi di 3 dataset publik + studi pilot user 5 hari. Memakai MCP (Model Context Protocol) sebagai interface standar buat Operator agent mengakses memori/sumber eksternal — konkret contoh MCP dipakai di luar konteks tool-calling murni.
- **Relevansi ke F.R.I.D.A.Y:** Blueprint arsitektur konkret yang menggabungkan M2 (persistent memory + user profile) dengan M1/M14 (Coordinator + Operator agent, mirip pola orchestrator-executor) — dan penting, memakai **MCP untuk akses memori**, bukan cuma tool-calling, memperkuat keputusan M0 pakai MCP sebagai format kontrak. Studi pilot 5 hari (walau kecil) beri sinyal awal nyata soal persepsi personalisasi pengguna, berguna sebagai referensi metodologi evaluasi M16.
- **Sumber informasi:** Ekstraksi mendalam — abstract & intro dibaca langsung via pdftotext
- **Catatan tambahan:** Studi user hanya 5 hari/skala kecil (pilot, bukan validasi besar) — treat temuan UX-nya sebagai indikasi awal, bukan bukti kuat. Arsitektur Coordinator→Operator-nya paling langsung dicontoh.

### Proactive Agent: Shifting LLM Agents from Reactive Responses to Active Assistance (2024)
- **Lokasi file:** `M17/Proactive Agent- Shifting LLM Agents from Reactive Responses to Active Assistance (2024).pdf`
- **Sprint/Modul terkait:** Sprint 11 (M17) — ⭐ Sangat relevan, ditambahkan user 2026-08-12
- **Ide inti:** Tsinghua/Renmin University. Pendekatan data-driven untuk melatih proaktivitas: kumpulkan aktivitas manusia nyata → generate prediksi task proaktif → dilabeli manusia (diterima/ditolak) → data ini melatih **reward model** yang mensimulasikan judgment manusia sebagai evaluator otomatis proaktivitas agent. Menghasilkan dataset ProactiveBench (6.790 event); fine-tuning pakai dataset ini secara signifikan meningkatkan proaktivitas agent (F1-Score 66.47%, mengalahkan semua model open/closed-source yang dites).
- **Relevansi ke F.R.I.D.A.Y:** Pendekatan berbeda dari Inner Thoughts (yang berbasis heuristik/skor saat inference) — ini berbasis **data collection + reward model + fine-tuning**. Relevan kalau nanti F.R.I.D.A.Y mau melatih model lokal (M12) khusus mendeteksi momen proaktif dari histori aktivitas user asli, bukan cuma prompting. Reward model-nya juga bisa dipakai sebagai automatic evaluator M16 untuk menilai kualitas keputusan proaktif tanpa perlu makhluk manusia menilai tiap kali.
- **Sumber informasi:** Ekstraksi mendalam — abstract & intro dibaca langsung via pdftotext
- **Catatan tambahan:** Butuh data aktivitas manusia nyata berlabel untuk melatih reward model — investasi data collection yang tidak murah; untuk F.R.I.D.A.Y skala personal (1 pengguna utama), volume data historis mungkin tidak akan sebesar 6.790 event, perlu strategi data augmentasi atau reward model yang sudah dilatih di corpus lebih besar.

### A Comprehensive Survey on Context-Aware Multi-Agent Systems: Techniques, Applications, Challenges and Future Directions (2024/2025) — ✅ diganti & terverifikasi 2026-08-13
- **Lokasi file:** `M17/Context-Awareness in Modern Conversational Agents.pdf` — file lama yang mismatch (isi kriptografi citra medis) sudah dihapus, diganti user dengan file yang benar
- **Sprint/Modul terkait:** Sprint 11 (M17) — ⭐ Sangat relevan, mengisi gap yang selama ini dicari kategori #14
- **Ide inti:** Du, Thudumu, Nguyen, Vasa, Mouzakis (Deakin University, arXiv:2402.01968). Survei komprehensif yang menyatukan dua bidang yang biasanya diteliti terpisah — context-awareness dan multi-agent systems (MAS) — jadi satu arsitektur & taksonomi terpadu (Context-Aware Multi-Agent Systems/CA-MAS), diorganisir sekitar 5 kapabilitas agen inti: **Sense → Learn → Reason → Predict → Act**. Perception mencakup sensor visual/auditory/dll; Memory menyimpan state lampau/sekarang/prediksi masa depan (dengan mekanisme experience replay untuk "melupakan" info yang tidak relevan lagi).
- **Relevansi ke F.R.I.D.A.Y:** Kerangka Sense-Learn-Reason-Predict-Act bisa langsung dipetakan ke pipeline M17: sensor/input rumah (Sense) → update model preferensi user (Learn) → putuskan relevansi situasi (Reason) → prediksi kebutuhan proaktif (Predict) → panggil tool (Act). Berguna sebagai kerangka tingkat-tinggi yang melengkapi paper lain di kategori ini (Inner Thoughts, ContextAgent) yang lebih fokus ke satu bagian pipeline saja.
- **Sumber informasi:** Ekstraksi mendalam — abstract, intro, dan bagian taksonomi kapabilitas agen dibaca via `pdftotext`, dikonfirmasi cocok dengan judul & arXiv ID
- **Catatan tambahan:** Ini survei tentang multi-agent systems secara umum (bukan khusus asisten personal/rumah), jadi banyak contoh kasusnya dari domain lain (kendaraan otonom, robotika bawah air) — perlu filter bagian yang relevan ke konteks single-user smart-home F.R.I.D.A.Y.

> **Catatan kategori [2026-08-13]:** File mismatch lama sudah diganti dengan paper survei di atas — kategori #14/M17 sekarang lengkap tanpa file bermasalah tersisa.

---

## Kategori #15 — Personality & Persona Design

### Exploring Users' Mental Models for Anthropomorphized Voice Assistants through Psychological Approaches
- **Lokasi file:** `M15/Exploring Users' Mental Models for Anthropomorphized Voice Assistants through Psychological Approaches.pdf`
- **Sprint/Modul terkait:** Sprint 10 (M15) — ✅ Punya
- **Ide inti:** Meneliti bagaimana pengguna membentuk model mental terhadap voice assistant yang dianggap ber-"kepribadian" (anthropomorphized), memakai kerangka psikologis (misal Computers-As-Social-Actors) untuk menjelaskan proyeksi sifat manusiawi ke asisten AI.
- **Relevansi ke F.R.I.D.A.Y:** Landasan psikologis batas anthropomorphism yang membuat interaksi natural vs uncanny-valley/ekspektasi berlebihan — penting menentukan seberapa "manusiawi" nada bicara F.R.I.D.A.Y.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan, konten dikonfirmasi cocok dengan judul
- **Catatan tambahan:** Worth direvisit saat menulis system prompt/persona guideline — rujukan menghindari over-anthropomorphizing yang memicu ekspektasi tidak realistis.

### Humanizing Machines: Rethinking LLM Anthropomorphism Through a Multi-Level Framework of Design (2025) — ✅ diganti & terverifikasi 2026-08-13
- **Lokasi file:** `M15/Form Follows Function Anthropomorphism in AI-Mediated Interactions.pdf` — nama file dipertahankan (warisan), file lama yang mismatch (isi serangan privasi federated learning) sudah dihapus, diganti user dengan file yang benar. **Catatan lokasi:** file sempat salah ditaruh user di `M17/` terlebih dulu, sudah dipindah ke `M15/` di sesi ini karena isinya soal anthropomorphism (Persona), bukan context-awareness.
- **Sprint/Modul terkait:** Sprint 10 (M15)
- **Ide inti:** Xiao, Ng, Liu, Diab (Carnegie Mellon University, arXiv:2508.17573). Mengusulkan kerangka anthropomorphism LLM yang bukan cuma soal risiko (over-trust, deception), tapi sebagai **konsep desain** yang bisa disetel sengaja untuk mendukung tujuan pengguna. Interaksi human-AI dipetakan jadi 4 komponen: **Artifacts** (sistem AI-nya sendiri), **Cues** (sinyal perceptual/linguistic/behavioral/cognitive yang membuat sesuatu terasa "manusiawi" — silhouette humanoid, nada simpatik, kata ganti orang pertama), **Designers** (yang menanamkan cue), **Interpreters** (pengguna yang memproyeksikan respons kognitif ke cue tersebut). Anthropomorphism didefinisikan sebagai fenomena resiprokal: designer menanam cue, interpreter memproyeksikan makna manusiawi ke situ.
- **Relevansi ke F.R.I.D.A.Y:** Kerangka 4 kategori cue (perceptual/linguistic/behavioral/cognitive) langsung actionable untuk desain persona M15 — bisa dipakai sebagai checklist eksplisit saat menentukan seberapa "manusiawi" F.R.I.D.A.Y terdengar (nada bicara = linguistic cue, respon empati = behavioral cue, dst), bukan cuma insting. Melengkapi paper "Exploring Users' Mental Models" yang lebih fokus ke sisi psikologi persepsi pengguna — paper ini menambahkan sisi desain/produksi cue-nya.
- **Sumber informasi:** Ekstraksi mendalam — abstract, intro, dan bagian kerangka 4-komponen dibaca via `pdftotext`, dikonfirmasi cocok dengan judul & arXiv ID
- **Catatan tambahan:** Paper eksplisit mengkritik riset anthropomorphism yang selama ini "risk-focused" — relevan sebagai pengingat bahwa tujuan F.R.I.D.A.Y menambahkan cue manusiawi harus jelas (mis. usability/trust), bukan sekadar ikut-ikutan tren, karena cue yang tidak sengaja ("inadvertently built in") bisa memicu ekspektasi tidak realistis.

### A Mixed-Methods Approach to Understanding User Trust after Voice Assistant Failures (2023) — ✅ pengganti file mismatch, terverifikasi 2026-08-13
- **Lokasi file:** `M15/A Mixed-Methods Approach to Understanding User Trust after Voice Assistant Failures (2023).pdf` — file baru, menggantikan file lama `Voice Assistants in Everyday Life; An Exploratory Study on User Experience and Trust.pdf` (folder tematik lama, dihapus) yang isinya ternyata mismatch total (paper computer vision klasifikasi land cover). Judul aslinya tidak ditemukan; paper ini dipilih sebagai pengganti tematik terdekat.
- **Sprint/Modul terkait:** Sprint 10 (M15)
- **Ide inti:** Baughan, Mercurio, Liu, Wang, Chen, Ma (University of Washington + Google Research, CHI'23, arXiv:2303.00164). Studi mixed-methods (wawancara + survei) soal bagaimana kegagalan voice assistant memengaruhi trust pengguna. Berkontribusi dataset crowdsourced 199 kegagalan voice assistant, dikategorikan ke 12 sumber kegagalan. Temuan: sebagian jenis kegagalan (misal overcapturing input — asisten menangkap lebih dari yang diucapkan user) merusak trust jauh lebih parah dibanding jenis kegagalan lain.
- **Relevansi ke F.R.I.D.A.Y:** Taksonomi 12 sumber kegagalan bisa langsung dipakai sebagai checklist desain M15/M8 — tahu kegagalan mana yang paling merusak trust (misal overcapturing) membantu prioritas mana yang harus dicegah lebih ketat (misal endpoint detection M7, confirmation-before-action M11) dibanding yang cukup di-log saja.
- **Sumber informasi:** Ekstraksi mendalam — abstract & intro dibaca via `pdftotext`, dikonfirmasi cocok 100% dengan judul, penulis, dan arXiv ID
- **Catatan tambahan:** Data dikumpulkan dari voice assistant komersial umum (Google Assistant, Siri, dll), bukan dari asisten custom seperti F.R.I.D.A.Y — taksonomi kegagalannya portable, tapi frekuensi/skala dampak trust bisa beda di skala personal 1-pengguna.

> **Catatan kategori [2026-08-13]:** File mismatch lama sudah diganti dengan paper di atas — kategori #15/M15 sekarang lengkap dengan 3 paper, sesuai status "✅ Punya" yang tadinya keliru diklaim sebelum audit ditemukan mismatch-nya.

---

## Kategori #16 — Evaluation & Benchmarking

### A Strategy Framework to Boost Conversational AI Performance
- **Lokasi file:** `M16/A Strategy Framework to Boost Conversational AI Performance.pdf`
- **Sprint/Modul terkait:** Sprint 12 (M16)
- **Ide inti:** Kerangka strategi berupa pilar/best-practice meningkatkan performa conversational AI secara menyeluruh — desain arsitektur, pengukuran kualitas respons, iterasi berbasis feedback pengguna.
- **Relevansi ke F.R.I.D.A.Y:** Checklist/kerangka acuan menyusun rencana evaluasi end-to-end F.R.I.D.A.Y — mengukur & meningkatkan performa secara sistematis (akurasi, latensi, kepuasan pengguna).
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan, konten dikonfirmasi cocok dengan judul
- **Catatan tambahan:** Level strategis/manajerial, bukan teknis mendalam — referensi tambahan dokumen evaluasi, bukan sumber implementasi kode.

### IntellAgent: A Multi-Agent Framework for Evaluating (Conversational AI)
- **Lokasi file:** `M16/IntellAgent; A Multi-Agent Framework for Evaluating.pdf`
- **Sprint/Modul terkait:** Sprint 12 (M16) — ✅ Punya
- **Ide inti:** Framework evaluasi otomatis berbasis multi-agent — satu set agen simulasi persona/skenario pengguna untuk menguji conversational AI, agen lain menilai kepatuhan policy/behavior graph, evaluasi skalabel tanpa human annotator manual.
- **Relevansi ke F.R.I.D.A.Y:** Sangat relevan membangun test-harness otomatis Sprint 12 — agen simulator sebagai "pengguna sintetis" menjalankan skenario uji tool-use/memory recall/proactive behavior, agen evaluator menilai kepatuhan policy keamanan/perilaku.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan, konten dikonfirmasi cocok dengan judul
- **Catatan tambahan:** Perlu policy graph/definisi perilaku F.R.I.D.A.Y eksplisit dulu sebelum framework ini efektif — worth direvisit setelah modul keamanan (#6) punya permission model jelas.

### Voice Assistants Thesis - The University of Manchester
- **Lokasi file:** `M16/Voice Assistants Thesis - The University of Manchester.pdf`
- **Sprint/Modul terkait:** Sprint 10 (M15) dan Sprint 12 (M16)
- **Ide inti:** Tesis akademik meneliti voice assistant dari sisi desain, penggunaan, dan evaluasi — tinjauan arsitektur voice assistant komersial/eksperimental serta studi persepsi & interaksi pengguna.
- **Relevansi ke F.R.I.D.A.Y:** Sumber referensi akademik lebih dalam untuk landasan teori desain persona dan metodologi evaluasi user study di Sprint 12.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan (tesis panjang, bagian metodologi detail belum ditinjau mendalam)
- **Catatan tambahan:** Kalau butuh detail teknis spesifik dari metodologi, perlu ditinjau ulang lebih dalam.

### Evaluation of a Smart Audio System Based on the ViP Principle and the Analytic Hierarchy Process (Human–Computer Interaction Design)
- **Lokasi file:** `M16/Evaluation of a Smart Audio System Based on the ViP Principle and the Analytic Hierarchy Process Human–Computer Interaction Design.pdf`
- **Sprint/Modul terkait:** Sprint 12 (M16)
- **Ide inti:** Mengevaluasi sistem smart audio menggunakan kombinasi prinsip desain ViP (Vision in Product design) dan Analytic Hierarchy Process (AHP) — metode pengambilan keputusan multi-kriteria — untuk menilai/memprioritaskan aspek desain HCI.
- **Relevansi ke F.R.I.D.A.Y:** Metodologi AHP bisa diadaptasi menyusun kriteria evaluasi multi-aspek F.R.I.D.A.Y (trade-off latensi vs akurasi vs privasi) secara terstruktur dan terbobot, bukan sekadar checklist kualitatif.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan, konten dikonfirmasi cocok dengan judul
- **Catatan tambahan:** Fokus paper ke hardware/perangkat audio fisik — yang diambil sebaiknya metodologi evaluasinya (AHP), bukan temuan spesifik produknya.

### A Systematic Review on Fostering Appropriate Trust in Human-AI Interaction (2023) — ✅ pengganti file mismatch, terverifikasi 2026-08-13
- **Lokasi file:** `M16/A Systematic Review on Fostering Appropriate Trust in Human-AI Interaction (2023).pdf` — file baru, menggantikan file lama `Building Trust in Human-AI Collaboration; A Survey.pdf` (folder tematik lama, dihapus) yang isinya ternyata mismatch total (paper virtual try-on diffusion model). Judul aslinya tidak ditemukan; paper ini dipilih sebagai pengganti tematik terdekat.
- **Sprint/Modul terkait:** Sprint 12 (M16) — juga relevan Sprint 10 (M15, persona/trust)
- **Ide inti:** Mehrotra, Degachi, Vereschak, Jonker, Tielman (Delft University of Technology, arXiv:2311.06305). Systematic review yang memetakan praktik membangun **appropriate trust** (bukan sekadar "trust setinggi mungkin") pada sistem AI — meninjau pendekatan seperti confidence score, explanation, trustworthiness cue, dan komunikasi uncertainty. Mengidentifikasi jenis task yang dipakai riset trust, cara mengukur trust, dan tantangan utama (kurangnya definisi tunggal "appropriate trust" lintas disiplin).
- **Relevansi ke F.R.I.D.A.Y:** Kerangka evaluasi trust yang bisa dipakai M16 menyusun metrik "apakah user percaya F.R.I.D.A.Y secara wajar" (bukan over-trust yang berbahaya untuk aksi kritis M11, bukan juga under-trust yang bikin fitur proaktif M17 tidak dipakai). Confidence score/uncertainty communication relevan langsung ke cara F.R.I.D.A.Y menyampaikan keraguan (misal saat tool-call gagal atau ambigu).
- **Sumber informasi:** Ekstraksi mendalam — abstract & intro dibaca via `pdftotext`, dikonfirmasi cocok 100% dengan judul, penulis, dan arXiv ID
- **Catatan tambahan:** Fokus review ke *taksonomi pendekatan* (bukan resep implementasi tunggal) — perlu dikombinasikan dengan paper trust-spesifik lain (mis. "A Mixed-Methods Approach... Voice Assistant Failures" di M15) untuk actionable ke domain voice assistant.

### OSWorld 2.0: Benchmarking Computer Use Agents on Long-Horizon Real-World Tasks (2026)
- **Lokasi file:** `M6/OSWorld 2.0 Benchmarking Computer Use Agents on Long-Horizon Real-World Tasks (2026).pdf`
- **Sprint/Modul terkait:** Sprint 4 (M11, safety analysis); evaluasi umum lintas roadmap; dipakai lagi di Sprint 12
- **Ide inti:** Benchmark 108 task komputer jangka-panjang (median ~1.6 jam manusia, ~250+ langkah agent), jauh lebih realistis dari OSWorld 1.0 — agent frontier terbaik hanya menyelesaikan 20.6% task penuh; kegagalan utama bukan kontrol GUI dasar, tapi menjaga state/constraint sepanjang task panjang, gagal bertanya saat ambigu, dan hampir tidak pernah self-correction (<7% budget).
- **Relevansi ke F.R.I.D.A.Y:** Acuan realistis keterbatasan agent computer-use saat ini — jangan berharap F.R.I.D.A.Y menuntaskan task rumit 100% otonom tanpa checkpoint/verifikasi. Bagian "Agent Safety Analysis" (§4.2): agent sering mengabaikan efek samping berbahaya dan memakai cara agresif/bypass UI saat menemui kendala — bahan langsung untuk M11 (guardrail side-effect checking, bukan hanya menilai keberhasilan task akhir). Prinsip "proactive interaction" (bertanya saat kurang info) relevan untuk kategori #14.
- **Sumber informasi:** Ekstraksi parsial — file >20MB, diekstrak sebagian besar (abstrak, metodologi, hasil eksperimen, safety analysis) via pdftotext; bagian appendix/case-study detail tidak diekstrak
- **Catatan tambahan:** Dipakai lagi di Sprint 12 (Evaluation) — simpan paper ini.

---

## File Bermasalah / Perlu Tindakan Manual

Daftar semua isu integritas file yang ditemukan selama proses ini — file dengan nama yang tidak cocok dengan isinya, file yang gagal dibaca, dan file yang sengaja dilewati. Semua ini butuh tindakan dari user (unduh ulang, rename, atau baca manual) sebelum bisa dipercaya sepenuhnya sebagai referensi riset.

> **[2026-08-12] 4 baris DILEWATI dihapus dari tabel ini** — semuanya berhasil dibaca pakai `pdftotext` (lihat entry lengkap masing-masing di kategori #6/M11 di atas). Ternyata bukan masalah konten yang memicu safety-filter, melainkan tool render PDF (`pdftoppm`) yang tidak tersedia — begitu dicoba pakai ekstraksi teks murni, semua terbaca normal tanpa hambatan.
>
> **[2026-08-13] 4 baris resolved dihapus dari tabel ini** — M7 (duplikat DS-CNN 2022 dihapus, tidak ada paper terpisah), M14 (AutoAgents diganti file benar), M17 (Context-Awareness diganti file benar), M15 (Form Follows Function diganti file benar, sempat salah taruh di M17 lalu dipindah). Juga 1 baris "Inner Thoughts — Gagal dibaca" dihapus karena sudah terverifikasi penuh sejak 2026-08-12 (tabel ini sempat tidak disinkronkan saat itu). Detail masing-masing ada di entry kategori terkait di atas.
>
> **[2026-08-13] Update kedua — 3 baris terakhir mismatch selesai, 2 folder tematik lama dihapus:** Pencarian judul persis "Recent Advances in Conversational AI", "Voice Assistants in Everyday Life", dan "Building Trust in Human-AI Collaboration" di web tidak menemukan paper aslinya (kemungkinan judul itu memang bukan judul asli paper, melainkan parafrase/ringkasan dari daftar bacaan lama). Diputuskan pakai paper pengganti tematik terdekat (dicari & diverifikasi isinya via `pdftotext`): "A Survey of Large Language Models" (arXiv:2303.18223) → dipindah ke `M1/`, "A Mixed-Methods Approach to Understanding User Trust after Voice Assistant Failures" (arXiv:2303.00164) → dipindah ke `M15/`, "A Systematic Review on Fostering Appropriate Trust in Human-AI Interaction" (arXiv:2311.06305) → dipindah ke `M16/`. Ketiga file mismatch lama dihapus. Folder `Arsitektur & Evaluasi Sistem Asisten AI (Teknik & Komputasi)/` dan `Interaksi Manusia-Komputer & Psikologi AI (Human-Computer Interaction)/` sudah kosong sepenuhnya, ikut dihapus — migrasi ke skema M0-M17 sekarang genap 100% (kecuali folder `1/Nggak dulu/` yang memang sengaja dikecualikan sejak awal).

| Folder | Nama File | Masalah |
|---|---|---|
| `M11/` | "Not What You've Signed Up For..." (2 file, satu tanpa tahun di nama) | **Duplikat** — konten identik, bukan error. Hapus salah satu kalau mau declutter folder. |
| `M7/` | "Deep Spoken Keyword Spotting: An Overview" (arXiv 2021 & IEEE Access 2022) | **Duplikat/versi lain** — arXiv preprint vs jurnal resmi, konten sama. Bukan error, tidak perlu tindakan kecuali mau declutter. |

Tidak ada lagi file mismatch tersisa di seluruh koleksi. 2 baris di atas murni duplikat/versi-lain yang isinya identik, bukan masalah integritas.

**Total paper diproses:** ~117 file per 2026-08-14 (108 per 2026-08-13, ditambah 9 paper baru di M2 soal forgetting/consolidation — lihat update di bawah). Dari total ini, semua sudah punya sumber terverifikasi (Teks penuh/Ekstraksi mendalam/Ekstraksi parsial) — **0** entry berstatus "Pengetahuan umum", dan **0** file mismatch tersisa di seluruh koleksi. Semua 16 kategori sudah terisi kuat. Migrasi ke skema folder per-modul `M0`-`M17` sudah genap 100% (2 folder tematik lama terakhir sudah dihapus karena kosong) — hanya folder `1/Nggak dulu/` yang tersisa di luar skema, sengaja dikecualikan sejak awal.

**[2026-08-14] Update tambahan #4 — 10 file baru user di M2, 1 duplikat + 1 mismatch ditemukan & diperbaiki:** User menambahkan 10 file PDF baru ke folder `M2/` (topik forgetting/consolidation/memory-organization untuk M2c, menjawab gap yang teridentifikasi saat diskusi kecukupan paper M2). Diverifikasi satu-satu via `pdftotext`: **9 cocok isi vs judul** (A Survey on the Memory Mechanism of LLM-based Agents, A-Mem, FSFM, MemoryBank, Recursively Summarizing, plus 4 paper neurosains dasar — Roscow/replay, Kirkpatrick/EWC, McClelland/Complementary Learning Systems, dan 1 paper sleep). **2 masalah ditemukan:** (1) file "Generative Agents...— Park et al. (2023), UIST.pdf" 100% duplikat (md5 identik) dengan file lama yang sudah ada — dihapus karena versi lama sudah tracked di git, versi baru untracked; (2) file "The Memory Function of Sleep — Diekelmann & Born (2010), Nature Reviews Neuroscience.pdf" isinya **bukan** paper itu — isi aslinya "About Sleep's Role in Memory" oleh Rasch & Born (2013), *Physiological Reviews* — nama file diperbaiki menyesuaikan isi asli (bukan dicari paper penggantinya, karena isinya tetap relevan). Juga ditemukan 1 salah atribusi nama file (bukan mismatch konten): "Recursively Summarizing...— Qian et al." seharusnya "— Wang et al." (penulis asli tidak ada nama Qian) — diperbaiki. Detail lengkap tiap paper ada di entry masing-masing di atas.

**[2026-08-12] Update tambahan:** Struktur folder dirombak dari angka (`1/`-`5/`) + tematik jadi per-modul `M0/`-`M17/` (lihat catatan di bagian atas dokumen). `pdftotext` ternyata tersedia di environment ini — dipakai untuk 9 paper baru + berhasil membuka ulang 1 paper yang sebelumnya berstatus "Gagal dibaca" (Proactive Conversational Agents with Inner Thoughts).

**[2026-08-12] Update tambahan #2 — upgrade massal status sumber:** Ke-11 dari 12 entry lama berstatus "Pengetahuan umum" (kategori #7-#10, ditambah 1 di #13) berhasil diupgrade jadi "Ekstraksi mendalam" pakai `pdftotext` — sekarang cuma tersisa **1** entry "Pengetahuan umum" di seluruh dokumen (AutoAgents, karena file fisiknya memang salah unduh — dikonfirmasi ulang, bukan masalah tool). Ditemukan 1 **koreksi penting**: entry "ASVspoof (2017)" ternyata selama ini salah — deskripsi lama ("replay attack, corpus RedDots") sebenarnya menggambarkan edisi ASVspoof 2017, sedangkan file fisiknya isinya laporan ASVspoof **2015** (fokus TTS/voice-conversion spoofing, bukan replay) — sudah diperbaiki di entry terkait. Juga ditemukan 1 koreksi metodologi: entry "Building Accurate Low Latency ASR" sebelumnya diasumsikan pakai "two-pass decoding", ternyata pakai pendekatan berbeda (hierarchical CTC + joint EOS detection) — sudah diperbaiki.

**[2026-08-13] Update tambahan #3 — 3 file mismatch diganti user, 1 duplikat dibersihkan:** User menambahkan file pengganti untuk M14 (AutoAgents), M17 (Context-Awareness survey), dan M15 (Form Follows Function → ternyata paper "Humanizing Machines" soal anthropomorphism) — ketiganya diverifikasi via `pdftotext` isinya cocok dengan judul, entry lengkap ditulis ulang. File "Form Follows Function" sempat salah ditaruh di folder `M17/`, dipindah ke `M15/` di sesi ini. Untuk M7, user sempat menambahkan file yang diberi nama "(2022)" tapi setelah dicek full-text diff, isinya 100% identik dengan paper Sørensen (2020) yang sudah ada — bukan paper terpisah, jadi file duplikatnya dihapus (2 kali muncul karena delay sinkronisasi OneDrive) dan file mismatch asli (yang isinya Sub-mW) juga dihapus karena kontennya sudah ada dengan nama benar. Kesimpulan: tidak ada paper "DS-CNN Keyword Spotting 2022" yang berdiri sendiri — kategori #7 tetap dianggap lengkap dengan Sørensen (2020).
