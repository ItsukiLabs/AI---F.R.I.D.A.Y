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

### Paper yang DILEWATI (belum dibaca — perlu ditinjau manual oleh user)

Empat paper berikut berulang kali memicu error/safety-filter otomatis saat dibaca oleh agent (kemungkinan karena kontennya memuat detail teknik serangan yang membuat sistem safeguard curiga), jadi sengaja **tidak dibuka sama sekali** oleh proses ini:

- `M11/Breaking the Code Security Assessment of AI Code Agents Through Systematic Jailbreaking Attacks (2025).pdf`
- `M11/Breaking the Protocol Security Analysis of the Model Context Protocol Specification and Prompt Injection Vulnerabilities in Tool-Integrated LLM Agents (2026).pdf`
- `M11/Quantifying Frontier LLM Capabilities for Container Sandbox Escape (2026).pdf`
- `M11/Optimizing Safety Alignment and Jailbreak Defense for Large Language Models (2025).pdf`

**Sumber informasi:** DILEWATI. Kalau kamu (user) mau isinya masuk ke catatan ini, cara paling aman adalah membacanya sendiri secara manual dan meringkas poin-poin arsitekturalnya (bukan detail teknik serangan) untuk ditambahkan ke sini — terutama yang kedua (soal MCP) karena langsung relevan untuk M11 & M0.

---

## Kategori #7 — Wake Word Detection

### A Depthwise Separable CNN for Keyword Spotting on an Embedded System (2020)
- **Lokasi file:** `M7/A Depthwise Separable CNN for Keyword Spotting on an Embedded System (2020).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M7)
- **Ide inti:** Sørensen, Epp & May (EURASIP JASMP 2020) mengganti convolution biasa dengan depthwise-separable convolution pada DS-CNN untuk keyword spotting, memangkas parameter/MAC signifikan sambil menjaga akurasi tinggi di Google Speech Commands, dengan pengukuran deployment nyata di embedded system.
- **Relevansi ke F.R.I.D.A.Y:** Kandidat arsitektur inti untuk M7 ("Hey Friday") yang harus always-on di edge/embedded dengan power sangat terbatas.
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF
- **Catatan tambahan:** Trade-off klasik: parameter/MAC lebih rendah menekan akurasi sedikit dibanding CNN penuh, tapi power/memori jauh lebih hemat — baseline sebelum eksperimen model lain.

### Accurate Detection of Wake Word Start and End Using a CNN (2020)
- **Lokasi file:** `M7/Accurate Detection of Wake Word Start and End Using a CNN (2020).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M7, endpointing/boundary detection)
- **Ide inti:** Berfokus pada endpointing — bukan hanya mendeteksi APAKAH wake word terucap, tapi KAPAN tepatnya mulai/berakhir, menggunakan CNN, agar audio dipotong akurat sebelum diteruskan ke STT.
- **Relevansi ke F.R.I.D.A.Y:** Krusial untuk handoff M7→M8 — endpoint tidak presisi bisa memotong sebagian wake word atau menyisakan silence berlebih, menambah latensi dan menurunkan akurasi STT.
- **Sumber informasi:** Pengetahuan umum — ekstraksi teks gagal berulang kali, isi berdasarkan pengetahuan model tentang paper ini, belum terverifikasi dari file lokal
- **Catatan tambahan:** Disarankan membaca ulang manual untuk metrik akurasi endpoint spesifik.

### Deep Spoken Keyword Spotting: An Overview (2021, arXiv) / (IEEE Access, 2022)
- **Lokasi file:** `M7/Deep Spoken Keyword Spotting An Overview (2021).pdf` dan `M7/Deep Spoken Keyword Spotting An Overview (IEEE Access, 2022).pdf` — **duplikat/versi lain satu sama lain** (preprint arXiv vs jurnal terbit resmi, penulis & konten sama: López-Espejo, Tan, Hansen, Jensen)
- **Sprint/Modul terkait:** Sprint 5 (M7)
- **Ide inti:** Overview komprehensif keyword spotting berbasis deep learning — front-end feature extraction, taksonomi arsitektur (CNN/RNN/attention/hybrid), teknik small-footprint, dataset standar, tantangan terbuka (noise robustness, far-field, personalisasi, efisiensi energi).
- **Relevansi ke F.R.I.D.A.Y:** Peta literatur paling lengkap untuk M7 — dipakai sebagai "index" memilih arsitektur mana (dari paper lain di folder ini) yang paling sesuai kebutuhan power/akurasi, dan daftar open problem jadi checklist risiko.
- **Sumber informasi:** Pengetahuan umum — ekstraksi teks gagal berulang kali, belum terverifikasi dari file lokal
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
- **Lokasi file:** `M7/Sub-mW Keyword Spotting on an MCU Analog Binary Feature Extraction and Binary Neural Networks (2022).pdf` — **konten ini juga "tersembunyi" di bawah nama file** `M7/A Depthwise Separable CNN for Keyword Spotting on an Embedded System (2022).pdf` (lihat File Bermasalah)
- **Sprint/Modul terkait:** Sprint 5 (M7, ekstrem low-power always-on)
- **Ide inti:** Cerutti et al.: pipeline KWS konsumsi <1mW, menggabungkan ekstraksi fitur biner analog (sebelum digitalisasi) dengan Binary Neural Network (bobot/aktivasi -1/+1, MAC diganti XNOR+popcount).
- **Relevansi ke F.R.I.D.A.Y:** Titik ekstrem paling agresif untuk M7 always-on 24/7 dengan baterai kecil/energy harvesting.
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF (dari salinan bernama benar)
- **Catatan tambahan:** Trade-off akurasi vs power sangat tajam — cocok untuk stage pertama "trigger kasar" pada arsitektur cascade dua-tahap (BNN sub-mW selalu jalan, model lebih besar hanya jalan saat trigger).

---

## Kategori #8 — Real-Time Speech Pipeline

### A Low-Latency Streaming On-Device Automatic Speech Recognition System Using a CNN Acoustic Model on FPGA and a Language Model on Smartphone (2022)
- **Lokasi file:** `M8/A Low-Latency Streaming On-Device Automatic Speech Recognition System Using a CNN Acoustic Model on FPGA and a Language Model on Smartphone.pdf`
- **Sprint/Modul terkait:** Sprint 5 (M8)
- **Ide inti:** Park et al. (Electronics 2022, POSTECH): acoustic model CNN TDS ramping (9.3M weight, dari 115M) di FPGA, input unit 80ms tanpa future context, dipasangkan LM 3-gram di smartphone; latency worst-case 125.5ms, RTF 0.57, WER AM 13.2%/WER+LM 9.1% (LibriSpeech test-clean).
- **Relevansi ke F.R.I.D.A.Y:** Blueprint split acoustic-model (edge) + language-model (device lebih kuat) untuk M8 hybrid edge-cloud (lihat juga kategori #12).
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF
- **Catatan tambahan:** 0ms lookahead demi latensi minimal menaikkan WER ~3% absolut; LM dictionary 1.3GB jadi bottleneck memori untuk perangkat sangat kecil.

### Building Accurate Low Latency ASR for Streaming Voice Search (2023)
- **Lokasi file:** `M8/Building Accurate Low Latency ASR for Streaming Voice Search (2023).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M8)
- **Ide inti:** Teknik praktis ASR streaming (voice search) yang menyeimbangkan akurasi & latensi — two-pass decoding (first-pass cepat + second-pass rescoring), endpointer, strategi training menekan WER tanpa menambah delay.
- **Relevansi ke F.R.I.D.A.Y:** Pola two-pass bisa diadaptasi supaya F.R.I.D.A.Y terasa responsif saat user bicara panjang, tetap akurat pada hasil final.
- **Sumber informasi:** Pengetahuan umum — ekstraksi teks gagal berulang kali, belum terverifikasi dari file lokal
- **Catatan tambahan:** Detail arsitektur/metrik spesifik perlu diverifikasi ulang manual.

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

### A Survey on Speech Deepfake Detection (2025)
- **Lokasi file:** `M9/A Survey on Speech Deepfake Detection (2025).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M9)
- **Ide inti:** Survei 2025 memetakan lanskap deteksi deepfake suara pasca-generasi TTS/voice-conversion neural modern (diffusion, zero-shot cloning) — deteksi berbasis fitur akustik klasik, embedding self-supervised, model end-to-end (RawNet2, AASIST), tantangan generalisasi ke generator suara belum pernah dilihat.
- **Relevansi ke F.R.I.D.A.Y:** Karena F.R.I.D.A.Y juga akan punya modul voice cloning/TTS (M10), survei ini penting untuk risiko "deepfake" pada M9 sendiri — desain M9 harus tahan generator TTS generasi terbaru, bukan cuma dataset lama.
- **Sumber informasi:** Pengetahuan umum — ekstraksi teks gagal, belum terverifikasi dari file lokal
- **Catatan tambahan:** Rincian metrik/metode spesifik perlu dibaca ulang langsung oleh user sebelum dikutip presisi.

### ASVspoof: The Automatic Speaker Verification Spoofing and Countermeasures Challenge (2017)
- **Lokasi file:** `M9/ASVspoof The Automatic Speaker Verification Spoofing and Countermeasures Challenge (2017).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M9)
- **Ide inti:** Kinnunen et al.: challenge fokus REPLAY ATTACK "in the wild" (corpus RedDots) — baseline CQCC+GMM EER 30.6%, sistem terbaik peserta EER 6.73% via fusion; performa terburuk pada rekaman ulang kualitas tinggi.
- **Relevansi ke F.R.I.D.A.Y:** Dataset/protokol acuan standar industri menguji M9 terhadap replay attack — serangan paling realistis/mudah dilakukan siapa saja.
- **Sumber informasi:** Pengetahuan umum — ekstraksi teks gagal, belum terverifikasi dari file lokal (angka metrik di atas adalah angka publik yang umum dikutip untuk challenge ini)
- **Catatan tambahan:** Replay attack kualitas tinggi jauh lebih sulit dideteksi dibanding speech-synthesis/voice-conversion — countermeasure tidak boleh hanya dioptimasi untuk TTS/voice-clone palsu.

### ECAPA-TDNN: Emphasized Channel Attention, Propagation and Aggregation in TDNN Based Speaker Verification (2020)
- **Lokasi file:** `M9/ECAPA-TDNN Emphasized Channel Attention, Propagation and Aggregation in TDNN Based Speaker Verification (2020).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M9, arsitektur inti speaker embedding)
- **Ide inti:** Desplanques, Thienpondt & Demuynck (Ghent University, Interspeech 2020): menyempurnakan x-vector/TDNN dengan SE-Res2Net 1D, multi-layer feature aggregation, attentive statistics pooling — EER 0.87% di VoxCeleb1, ~19% perbaikan relatif dari baseline.
- **Relevansi ke F.R.I.D.A.Y:** Salah satu arsitektur speaker-embedding paling kuat & populer — kandidat utama backbone speaker verification M9 (bedakan suara pemilik vs orang lain sebelum eksekusi perintah sensitif).
- **Sumber informasi:** Teks penuh — dibaca langsung dari file PDF
- **Catatan tambahan:** Varian 512-channel (6.2M parameter) tetap mengungguli baseline lama dengan parameter jauh lebih hemat dari varian 1024-channel — pilihan lebih baik untuk device kecil.

### Speaker-Aware Anti-Spoofing (2023)
- **Lokasi file:** `M9/Speaker-Aware Anti-Spoofing (2023).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M9)
- **Ide inti:** Mengusulkan anti-spoofing yang "sadar identitas pembicara" — memasukkan embedding speaker ke pipeline countermeasure spoof-detection sehingga deteksi dikondisikan pada karakteristik suara pengguna terdaftar.
- **Relevansi ke F.R.I.D.A.Y:** Sangat relevan karena F.R.I.D.A.Y biasanya punya satu/segelintir pengguna terdaftar — countermeasure lebih personal & presisi terhadap profil suara pemilik, alih-alih model generic populasi umum.
- **Sumber informasi:** Pengetahuan umum — ekstraksi teks gagal, belum terverifikasi dari file lokal
- **Catatan tambahan:** Perlu baca ulang manual untuk arsitektur joint training ASV+CM spesifik sebelum implementasi.

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

### EmoKnob: Enhance Voice Cloning with Fine-Grained Emotion Control (2024)
- **Lokasi file:** `M10/EmoKnob Enhance Voice Cloning with Fine-Grained Emotion Control (2024).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M10)
- **Ide inti:** Menambahkan "knob" kontrol emosi berbutir halus (bukan kategori diskrit) ke atas voice cloning zero/few-shot existing — mengekstrak vektor emosi dari sedikit sampel referensi, memungkinkan interpolasi/skala intensitas emosi tanpa retrain model TTS dasar.
- **Relevansi ke F.R.I.D.A.Y:** Relevan untuk M10 + M15 (Persona) — suara F.R.I.D.A.Y bisa punya "dial" intensitas emosi (ceria saat menyapa, tegas saat peringatan) di atas satu identitas suara persona konsisten.
- **Sumber informasi:** Pengetahuan umum — ekstraksi teks gagal, belum terverifikasi dari file lokal
- **Catatan tambahan:** Detail arsitektur teknis (base model TTS, metode ekstraksi vektor emosi) perlu dikonfirmasi ulang sebelum implementasi.

### Emotional Prosody Control for Speech Generation (2021)
- **Lokasi file:** `M10/Emotional Prosody Control for Speech Generation (2021).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M10)
- **Ide inti:** Kontrol prosodi emosional pada TTS — atribut prosodik (pitch, durasi, energi) yang berkorelasi ekspresi emosi diatur terpisah dari konten linguistik, biasanya lewat embedding kondisi tambahan.
- **Relevansi ke F.R.I.D.A.Y:** Fondasi konseptual M10 ekspresif — kontrol prosodi terpisah dari identitas suara memungkinkan F.R.I.D.A.Y menyesuaikan nada bicara sesuai konteks (urgent vs santai) sambil konsisten dengan suara dasarnya.
- **Sumber informasi:** Pengetahuan umum — ekstraksi teks gagal, belum terverifikasi dari file lokal
- **Catatan tambahan:** Detail arsitektur presisi perlu verifikasi manual sebelum jadi referensi kode.

### Expressive Neural Voice Cloning (2021)
- **Lokasi file:** `M10/Expressive Neural Voice Cloning (2021).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M10)
- **Ide inti:** Voice cloning neural yang mempertahankan/mengontrol ekspresivitas selain hanya meniru timbre — biasanya mendisentangle representasi speaker identity dari representasi gaya/prosodi.
- **Relevansi ke F.R.I.D.A.Y:** Relevan jika F.R.I.D.A.Y ingin fitur "clone suara pengguna sebagai persona" namun bisa mengatur gaya bicara secara independen — disentanglement identity vs style penting untuk fleksibilitas ini.
- **Sumber informasi:** Pengetahuan umum — ekstraksi teks gagal, belum terverifikasi dari file lokal
- **Catatan tambahan:** Detail metode presisi perlu baca manual untuk data requirement sebelum implementasi.

### Meta-Voice: Fast Few-Shot Style Transfer for Expressive Voice Cloning Using Meta Learning (2021)
- **Lokasi file:** `M10/Meta-Voice Fast Few-Shot Style Transfer for Expressive Voice Cloning Using Meta Learning (2021).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M10)
- **Ide inti:** Pendekatan meta-learning (mirip MAML) agar model voice cloning beradaptasi cepat ke speaker/style baru hanya dari sedikit contoh, karena "dilatih untuk belajar cepat" di banyak tugas adaptasi selama meta-training.
- **Relevansi ke F.R.I.D.A.Y:** Relevan untuk fitur "voice cloning instan" dari sedikit sampel (5-10 detik) untuk personalisasi cepat tanpa fine-tuning lama — cocok untuk onboarding cepat di M10.
- **Sumber informasi:** Pengetahuan umum — ekstraksi teks gagal, belum terverifikasi dari file lokal
- **Catatan tambahan:** Butuh proses meta-training awal yang mahal (banyak speaker/style) — cocok dilakukan sekali di cloud/training pipeline, model hasilnya dipakai ringan di edge.

### Prosody-TTS: Improving Prosody with Masked Autoencoder and Conditional Diffusion Model for Expressive Text-to-Speech (2023)
- **Lokasi file:** `M10/Prosody-TTS Improving Prosody with Masked Autoencoder and Conditional Diffusion Model for Expressive Text-to-Speech (2023).pdf`
- **Sprint/Modul terkait:** Sprint 5 (M10)
- **Ide inti:** Menggabungkan masked autoencoder (pre-training representasi prosodi self-supervised) dengan conditional diffusion model (generate prosodi natural saat sintesis) — meningkatkan ekspresivitas dibanding prediksi prosodi deterministik biasa.
- **Relevansi ke F.R.I.D.A.Y:** Diffusion-based prosody generation adalah SOTA kualitas ekspresi suara sintetis — referensi upgrade M10 dari TTS netral ke TTS natural secara prosodik sesuai konteks percakapan.
- **Sumber informasi:** Pengetahuan umum — ekstraksi teks gagal, belum terverifikasi dari file lokal
- **Catatan tambahan:** Diffusion model lebih mahal komputasi (multiple denoising steps) — mungkin lebih cocok mode "high-quality narration" daripada respons cepat sehari-hari.

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

### AutoAgents: A Framework for Automatic Agent Generation (2024) — ⚠️ file lokal bermasalah
- **Lokasi file:** `M14/AutoAgents A Framework for Automatic Agent Generation (2024).pdf` — **isi file sebenarnya adalah paper fisika kuantum tidak terkait ("Quantum Codes from Twisted Unitary t-groups", arXiv:2402.01638)**
- **Sprint/Modul terkait:** Sprint 9 (M14)
- **Ide inti (dari pengetahuan umum, BUKAN dari file lokal):** Mengotomatisasi pembuatan peran dan agen berdasarkan task yang diberikan (bukan peran statis) — sistem men-generate profil agen "on the fly" lengkap deskripsi peran, dikoordinasikan via tahap perencanaan-eksekusi-observasi dengan self-refleksi/drop agen tidak relevan.
- **Relevansi ke F.R.I.D.A.Y:** Berguna untuk skenario task pengguna tak terduga — sistem membentuk "tim" agen ad-hoc (agent cuaca + kalender + smart-home) otomatis daripada daftar agent statis hardcoded.
- **Sumber informasi:** Pengetahuan umum — file lokal isinya paper lain (tidak terkait sama sekali), catatan ini ditulis dari pengetahuan model tentang paper AutoAgents (Chen et al. 2024, arXiv:2309.17288), **belum terverifikasi dari file lokal**
- **Catatan tambahan:** File perlu diunduh ulang. Lihat juga bagian "File Bermasalah" di akhir dokumen.

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

> **Catatan kategori:** Kategori #14 tadinya kekurangan 1 paper karena "Context-Awareness in Modern Conversational Agents and Large Language Models" ternyata file-nya **mismatch** (isi sebenarnya paper kriptografi citra medis) — file itu MASIH mismatch dan belum diganti (lihat bagian **File Bermasalah**). Tapi per 2026-08-12, kategori ini sudah diperkuat signifikan oleh 4 paper baru di atas (Inner Thoughts kini terverifikasi penuh, plus 3 paper baru soal personalisasi & context-aware proactive agent) — jadi walau file mismatch itu belum terganti secara harfiah, gap konten untuk M17 sudah jauh lebih tertutup dibanding sebelumnya. Rename/cari file pengganti masih worth dilakukan untuk kerapian, tapi tidak lagi mendesak/blocking.

---

## Kategori #15 — Personality & Persona Design

### Exploring Users' Mental Models for Anthropomorphized Voice Assistants through Psychological Approaches
- **Lokasi file:** `M15/Exploring Users' Mental Models for Anthropomorphized Voice Assistants through Psychological Approaches.pdf`
- **Sprint/Modul terkait:** Sprint 10 (M15) — ✅ Punya
- **Ide inti:** Meneliti bagaimana pengguna membentuk model mental terhadap voice assistant yang dianggap ber-"kepribadian" (anthropomorphized), memakai kerangka psikologis (misal Computers-As-Social-Actors) untuk menjelaskan proyeksi sifat manusiawi ke asisten AI.
- **Relevansi ke F.R.I.D.A.Y:** Landasan psikologis batas anthropomorphism yang membuat interaksi natural vs uncanny-valley/ekspektasi berlebihan — penting menentukan seberapa "manusiawi" nada bicara F.R.I.D.A.Y.
- **Sumber informasi:** Ekstraksi parsial — abstract/intro/kesimpulan, konten dikonfirmasi cocok dengan judul
- **Catatan tambahan:** Worth direvisit saat menulis system prompt/persona guideline — rujukan menghindari over-anthropomorphizing yang memicu ekspektasi tidak realistis.

> **Catatan kategori:** paper "Form Follows Function: Anthropomorphism in AI-Mediated Interactions" yang seharusnya jadi paper kedua di kategori ini (per `sprint-paper-mapping.md`, kategori #15 dianggap "sudah lengkap ✅") ternyata file-nya **mismatch** (isi sebenarnya paper serangan privasi federated learning) — lihat bagian **File Bermasalah**. Berarti kategori #15 sebenarnya **belum lengkap**, perlu cari ulang paper aslinya.

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

> Kolom "Folder" di bawah sudah mengikuti skema folder baru **M0–M17** (per modul, lihat catatan di bagian atas dokumen). Tiga baris mismatch tanpa kategori jelas (Recent Advances, Voice Assistants in Everyday Life, Building Trust) sengaja **belum dipindah** — masih di folder tematik lama, menunggu paper aslinya ditemukan dulu baru ditentukan modul mana yang cocok.

| Folder | Nama File | Masalah |
|---|---|---|
| `M7/` | A Depthwise Separable CNN for Keyword Spotting on an Embedded System (**2022**).pdf | **MISMATCH** — isi sebenarnya = "Sub-mW Keyword Spotting on an MCU" (Cerutti et al.), bukan versi 2022 dari paper Sørensen. Rename/ganti file. |
| `M14/` | AutoAgents A Framework for Automatic Agent Generation (2024).pdf | **MISMATCH** — isi sebenarnya paper fisika kuantum tidak terkait (arXiv:2402.01638). Unduh ulang. |
| `M17/` | Proactive Conversational Agents with Inner Thoughts (2025).pdf | **Gagal dibaca** — ukuran 22MB > limit, tool render PDF tidak tersedia. Baca manual/compress file. |
| `Arsitektur & Evaluasi.../` (belum dipindah) | Recent Advances in Conversational AI; A Review of Large Language Models.pdf | **MISMATCH** — isi sebenarnya paper matematika (Willmore energy). Cari ulang paper aslinya — belum jelas modul mana sampai isi aslinya ketemu. |
| `Arsitektur & Evaluasi.../` (belum dipindah) | Voice Assistants in Everyday Life; An Exploratory Study on User Experience and Trust.pdf | **MISMATCH** — isi sebenarnya paper computer vision (land cover classification). Cari ulang paper aslinya — belum jelas modul mana sampai isi aslinya ketemu. |
| `Interaksi Manusia-Komputer.../` (belum dipindah) | Building Trust in Human-AI Collaboration; A Survey.pdf | **MISMATCH** — isi sebenarnya paper virtual try-on diffusion model. Cari ulang paper aslinya — belum jelas modul mana sampai isi aslinya ketemu. |
| `M17/` | Context-Awareness in Modern Conversational Agents and Large Language Models.pdf | **MISMATCH** — isi sebenarnya paper kriptografi citra medis. **Prioritas cari ulang** — topik ini inti untuk M17 (kategori #14). Paper pengganti taruh langsung di folder `M17/` dengan nama file ini (menggantikan). |
| `M15/` | Form Follows Function Anthropomorphism in AI-Mediated Interactions.pdf | **MISMATCH** — isi sebenarnya paper serangan privasi federated learning. Cari ulang — kategori #15 sempat dianggap "lengkap" di mapping doc, ternyata belum. Paper pengganti taruh langsung di folder `M15/`. |
| `M11/` | Breaking the Code... Systematic Jailbreaking Attacks (2025).pdf | **DILEWATI** — memicu safety-filter otomatis berulang, tidak dibuka. Baca manual kalau perlu isinya. |
| `M11/` | Breaking the Protocol... Prompt Injection Vulnerabilities in Tool-Integrated LLM Agents (2026).pdf | **DILEWATI** — sama seperti di atas. Prioritas baca manual karena bahas MCP (relevan M0/M11). |
| `M11/` | Quantifying Frontier LLM Capabilities for Container Sandbox Escape (2026).pdf | **DILEWATI** — sama seperti di atas. |
| `M11/` | Optimizing Safety Alignment and Jailbreak Defense for Large Language Models (2025).pdf | **DILEWATI** — sama seperti di atas. |
| `M11/` | "Not What You've Signed Up For..." (2 file, satu tanpa tahun di nama) | **Duplikat** — konten identik, bukan error. Hapus salah satu kalau mau declutter folder. |
| `M7/` | "Deep Spoken Keyword Spotting: An Overview" (arXiv 2021 & IEEE Access 2022) | **Duplikat/versi lain** — arXiv preprint vs jurnal resmi, konten sama. Bukan error, tidak perlu tindakan kecuali mau declutter. |

**Total paper diproses:** ~105 file per 2026-08-12 (96 dari sesi awal 2026-08-06 + 9 baru ditambahkan user 2026-08-12 ke `M11/` dan `M17/`, sudah dibaca & dicatat di atas). Semua 16 kategori sudah terisi setidaknya sebagian; kategori #14 (M17) sekarang terisi kuat (5 paper solid termasuk 1 yang berhasil diverifikasi ulang dari status "gagal dibaca"); kategori #15 (M15) masih kekurangan 1 paper karena file mismatch belum diganti.

**[2026-08-12] Update tambahan:** Struktur folder dirombak dari angka (`1/`-`5/`) + tematik jadi per-modul `M0/`-`M17/` (lihat catatan di bagian atas dokumen). `pdftotext` ternyata tersedia di environment ini — dipakai untuk 9 paper baru + berhasil membuka ulang 1 paper yang sebelumnya berstatus "Gagal dibaca" (Proactive Conversational Agents with Inner Thoughts). Sejumlah entry lama di kategori #7-#12 masih berstatus "Pengetahuan umum" (gagal diekstrak saat sesi awal) — berpotensi bisa diupgrade sekarang pakai `pdftotext`, belum dikerjakan di sesi ini karena di luar scope permintaan (lihat rekomendasi di percakapan).
