# F.R.I.D.A.Y — Peta Sprint ↔ Kategori Riset ↔ Paper

> Dokumen rujukan cepat: sprint mana ambil kategori riset nomor berapa, dan paper apa saja.
> Pakai ini saat mencari/upload paper agar tidak tersesat.

---

## Daftar 16 Kategori Riset (Referensi)

| No | Kategori | Tier |
|---|---|---|
| 1 | Agentic AI / Tool Use & Function Calling | 1 |
| 2 | Memory Architecture & Long-Term Context | 1 |
| 3 | Task Planning & Decomposition | 1 |
| 4 | Device Orchestration & OS-Level Control | 2 |
| 5 | IoT Integration & Protocol | 2 |
| 6 | Security, Sandboxing & Permission Model | 2 |
| 7 | Wake Word Detection (always-on) | 3 |
| 8 | Real-Time Speech Pipeline | 3 |
| 9 | Speaker Identification & Voice Authentication | 3 |
| 10 | Expressive TTS | 3 |
| 11 | Local LLM Inference & Optimization | 4 |
| 12 | Hybrid Cloud–Edge Routing | 4 |
| 13 | Multi-Agent Orchestration | 4 |
| 14 | Proactive & Context-Aware Behavior | 5 |
| 15 | Personality & Persona Design | 5 |
| 16 | Evaluation & Benchmarking | 5 |

---

## Tabel Induk: Sprint → Kategori

| Sprint | Modul | Kategori | Nama Kategori | Jml Paper |
|---|---|---|---|---|
| **1** | M0 + M1 | **#1** | Agentic AI / Tool Use | 5 |
| **2** | M2 | **#2** | Memory Architecture | 3 |
| **3** | M4 + M5 | **#4** + **#5** | Device Orchestration + IoT | 5 |
| **4** | M11 ⚠️ | **#6** | Security & Permission | 4 |
| **5** | M7–M10 | **#7** + **#8** + **#9** + **#10** | Voice Layer (4 kategori) | 5 |
| **6** | M3 | **#3** | Task Planning | 3 |
| **7** | M6 | **#4** (lanjutan) | OS-Level Control | 3 |
| **8** | M12 + M13 | **#11** + **#12** | Local Inference + Routing | 3 |
| **9** | M14 | **#13** | Multi-Agent Orchestration | 3 |
| **10** | M15 | **#15** | Persona Design | 2 |
| **11** | M17 | **#14** | Proactive & Context-Aware | 2 |
| **12** | M16 | **#16** | Evaluation & Benchmarking | 4 |

---

## SPRINT 1 — Agent Core

**Kategori: #1** — Agentic AI / Tool Use & Function Calling
**Modul:** M0 (Contract) + M1 (Agent Core)

| # | Paper | Kategori | Prioritas | Fungsi di Modul Ini |
|---|---|---|---|---|
| 1 | **ReAct** | #1 | ⭐ Wajib | Loop Thought→Action→Observation |
| 2 | **Toolformer** | #1 | ⭐ Wajib | Kapan model panggil tool |
| 3 | **MCP** | #4 | ⭐ Wajib | Format tool manifest & schema |
| 4 | **LLM Agent Survey** | #1 | Penting | Peta arsitektur agent |
| 5 | **AgentOS** | #13 | Penting | Versioned contract, plugin model |
| — | *Gorilla* | #1 | Opsional | Halusinasi nama fungsi |

**Catatan:** MCP dan AgentOS diambil dari kategori lain (#4, #13) karena dipakai lintas modul. Keduanya **jangan dihapus** dari Project Knowledge.

---

## SPRINT 2 — Memory System

**Kategori: #2** — Memory Architecture & Long-Term Context
**Modul:** M2 (M2a short-term, M2b long-term, M2c profile)

| # | Paper | Kategori | Sub-Modul | Fungsi di Modul Ini |
|---|---|---|---|---|
| 1 | **MemGPT** | #2 | M2c | Hirarki memori, paging |
| 2 | **RAG Survey** | #2 | M2b | Pipeline retrieval & embedding |
| 3 | **Lost in the Middle** | #2 | M2a | Kenapa konteks panjang gagal |

---

## SPRINT 3 — Device Control

**Kategori: #4 + #5** — Device Orchestration + IoT Integration
**Modul:** M4 (Tool Registry) + M5 (Device Abstraction Layer)

| # | Paper | Kategori | Modul | Fungsi di Modul Ini |
|---|---|---|---|---|
| 1 | **MCP-Zero** ⭐ | #4 | M4 | Agent minta tool sendiri saat butuh |
| 2 | **ScaleMCP** | #4 | M4 | Auto-sync tool baru tanpa restart |
| 3 | **Enhancing IoT with LLM** ⭐ | #5 | M5 | Blueprint: Home Assistant + MQTT |
| 4 | **HearthNet** ⭐ | #5 | M5 | Adapter tipis, edge orchestration |
| 5 | **Agentic IoT Survey** | #5 | M5 | IoT vs AIoT vs Agentic IoT |
| — | *Tool-to-Agent Retrieval* | #4 | M4 | Opsional — routing saat tool ratusan |

**Link download:**
- MCP-Zero: `arxiv.org/pdf/2506.01056`
- ScaleMCP: `arxiv.org/abs/2505.06416`
- Tool-to-Agent: `arxiv.org/pdf/2511.01854`

---

## SPRINT 4 — Security Gate ⚠️

**Kategori: #6** — Security, Sandboxing & Permission Model
**Modul:** M11

| # | Paper | Kategori | Prioritas | Fungsi di Modul Ini |
|---|---|---|---|---|
| 1 | **HearthNet** (bag. Authorization) ⭐ | #5 | ⭐ Wajib | Root-issued lease model |
| 2 | **AgentOS** (NFR3) ⭐ | #13 | ⭐ Wajib | Capability-scoped access, ≥95% deflection |
| 3 | **Indirect Prompt Injection** | #6 | ⭐ Wajib | Serangan lewat konten yang dibaca |
| 4 | **Security Risk Analysis in IoT** | #6 | Penting | Ancaman hardware |

**Catatan:** HearthNet & AgentOS sudah ada dari sprint sebelumnya — hanya baca **bagian security-nya**. Yang perlu diupload baru: 2 paper.

---

## SPRINT 5 — Voice Layer

**Kategori: #7 + #8 + #9 + #10** — 4 kategori sekaligus
**Modul:** M7 (Wake) + M8 (STT) + M9 (Auth) + M10 (TTS)

| # | Paper | Kategori | Modul | Fungsi di Modul Ini |
|---|---|---|---|---|
| 1 | *Keyword spotting low-power* | **#7** | M7 | Akurasi vs konsumsi daya |
| 2 | **Whisper** (Radford et al.) | **#8** | M8 | Model STT dasar |
| 3 | *Streaming ASR / VAD* | **#8** | M8 | Real-time, bukan batch |
| 4 | *Speaker verification + anti-spoofing* | **#9** | M9 | Bedakan suaramu |
| 5 | *Neural TTS prosody control* | **#10** | M10 | Emosi & intonasi |

**Alternatif hemat:** Kategori #7 dan #10 boleh **skip paper**, langsung baca dokumentasi tool jadi (openWakeWord, Piper). Kualitas tidak turun.

---

## SPRINT 6 — Task Planner

**Kategori: #3** — Task Planning & Decomposition
**Modul:** M3

| # | Paper | Kategori | Prioritas | Fungsi di Modul Ini |
|---|---|---|---|---|
| 1 | **Tree of Thoughts** | #3 | ⭐ Wajib | Eksplorasi multi-cabang |
| 2 | **Reflexion** | #3 | ⭐ Wajib | Self-critique saat gagal |
| 3 | **Chain-of-Thought** | #3 | Penting | Baseline reasoning |
| — | *LLM+P* | #3 | Opsional | Planner klasik (PDDL) |

---

## SPRINT 7 — Computer Control

**Kategori: #4 (lanjutan)** — OS-Level Control
**Modul:** M6

| # | Paper | Kategori | Prioritas | Fungsi di Modul Ini |
|---|---|---|---|---|
| 1 | **Computer Use Agents Survey** | #4 | ⭐ Wajib | Screenshot+VLM vs a11y tree |
| 2 | **GUI Agents Survey** | #4 | ⭐ Wajib | Grounding elemen UI |
| 3 | **OSWorld 2.0** | #4 / #16 | Penting | Benchmark — ukur progres |

**Catatan:** OSWorld dipakai lagi di Sprint 12 (Evaluation). Simpan.

---

## SPRINT 8 — Local Inference & Routing

**Kategori: #11 + #12** — Local Inference + Cloud-Edge Routing
**Modul:** M12 + M13

| # | Paper | Kategori | Modul | Fungsi di Modul Ini |
|---|---|---|---|---|
| 1 | *LLM quantization survey* | **#11** | M12 | Ukuran model vs kualitas |
| 2 | *Model routing / cascade* | **#12** | M13 | Kapan local, kapan cloud |
| 3 | **AI on Edge IoT** ✅ | **#12** | M13 | Strategi offloading (sudah punya) |

---

## SPRINT 9 — Multi-Agent

**Kategori: #13** — Multi-Agent Orchestration
**Modul:** M14

| # | Paper | Kategori | Prioritas | Fungsi di Modul Ini |
|---|---|---|---|---|
| 1 | **AgentVerse** | #13 | ⭐ Wajib | Expert recruitment, evaluator loop |
| 2 | **HearthNet** ✅ | #5 | ⭐ Wajib | Peran root/manager/librarian |
| 3 | **AgentOS** ✅ | #13 | Penting | Blueprint runtime |

**Catatan:** 2 dari 3 sudah ada. Upload baru: 1 paper.

---

## SPRINT 10 — Persona

**Kategori: #15** — Personality & Persona Design
**Modul:** M15

| # | Paper | Kategori | Status | Fungsi di Modul Ini |
|---|---|---|---|---|
| 1 | **Form Follows Function: Anthropomorphism** | #15 | ✅ Punya | Kapan mirip-manusia membantu |
| 2 | **Exploring Users' Mental Models** | #15 | ✅ Punya | Ekspektasi user terhadap AI |

**Catatan:** Kategori #15 **sudah lengkap**. Tidak perlu cari paper baru.

---

## SPRINT 11 — Proactive

**Kategori: #14** — Proactive & Context-Aware Behavior
**Modul:** M17

| # | Paper | Kategori | Status | Fungsi di Modul Ini |
|---|---|---|---|---|
| 1 | **ContextAwareness in Conversational Agents** | #14 | ✅ Punya | Deteksi konteks untuk trigger |
| 2 | **Agentic IoT Survey** (Behavior Model) | #5 | ✅ Punya | Definisi perilaku proaktif |

**Catatan:** Tidak perlu upload paper baru. Keduanya sudah ada.

---

## SPRINT 12 — Evaluation

**Kategori: #16** — Evaluation & Benchmarking
**Modul:** M16

| # | Paper | Kategori | Status | Fungsi di Modul Ini |
|---|---|---|---|---|
| 1 | **IntellAgent** | #16 | ✅ Punya | Framework eval multi-agent |
| 2 | **EvaluationDesign** | #16 | ✅ Punya | Metodologi eksperimen |
| 3 | **OSWorld 2.0** | #4/#16 | ✅ (dari Sprint 7) | Benchmark OS control |
| 4 | *AgentBench* | #16 | Cari | Benchmark umum agent |

**Catatan:** Upload baru: 1 paper (AgentBench, opsional).

---

## Paper Lintas-Sprint (JANGAN HAPUS)

Tiga paper ini dirujuk di banyak modul. Selalu simpan di Project Knowledge:

| Paper | Kategori Asal | Dipakai di Sprint |
|---|---|---|
| **MCP** | #4 | 1, 3 |
| **AgentOS** | #13 | 1, 4, 9 |
| **HearthNet** | #5 | 3, 4, 9 |

---

## Kategori yang BELUM Punya Paper — [STATUS: SUDAH TERISI SEMUA, per 2026-08-12]

> Tabel di bawah ini ditulis 2025-07-14, **sebelum** sesi riset paper besar-besaran 2026-08-06 (lihat `PAPER_NOTES.md`). Per audit 2026-08-12, **semua 6 kategori di tabel ini sudah punya paper** (bahkan lebih dari cukup) — tabel dipertahankan di bawah cuma sebagai riwayat, bukan TODO aktif lagi. Detail lengkap tiap paper ada di `PAPER_NOTES.md` per kategori.

| Kategori | Nama | Status per 2026-08-12 |
|---|---|---|
| **#6** | Security & Permission | ✅ Terisi — 14 paper terbaca (5 di antaranya baru ditambah 2026-08-12) + 4 paper *dilewati* (DILEWATI, masih perlu ditinjau manual, lihat File Bermasalah di `PAPER_NOTES.md`) |
| **#7** | Wake Word | ✅ Terisi — 8 paper |
| **#8** | Real-Time Speech | ✅ Terisi — 7 paper |
| **#9** | Speaker Auth | ✅ Terisi — 7 paper |
| **#10** | Expressive TTS | ✅ Terisi — 6 paper |
| **#11** | Local Inference | ✅ Terisi — 6 paper |
| **#12** | Cloud-Edge Routing | ✅ Terisi — 6 paper |

**Yang MASIH genuinely butuh tindakan (bukan dari tabel ini, tapi dari audit terpisah):**
- 4 paper **DILEWATI** di kategori #6 (jailbreak/sandbox-escape) — belum pernah dibaca sama sekali karena memicu safety-filter otomatis berulang saat proses awal. Baca manual kalau perlu isinya (lihat tabel File Bermasalah di `PAPER_NOTES.md`).
- 3 file **mismatch tanpa kategori jelas** (Recent Advances in Conversational AI, Voice Assistants in Everyday Life, Building Trust in Human-AI Collaboration) — isi filenya salah total, paper aslinya belum ketahuan sama sekali.
- 1 file **mismatch kategori #15** (Form Follows Function) — masih perlu paper pengganti, belum ditaruh user.

---

## Kata Kunci Pencarian (Kategori yang Masih Kosong)

**#6 Security:**
`LLM agent security sandboxing`, `indirect prompt injection defense`, `capability-based permission AI agent`, `agent safety guardrails`

**#7 Wake Word:**
`keyword spotting low power`, `wake word detection on-device`

**#8 Real-Time Speech:**
`streaming ASR low latency`, `Whisper real-time inference`, `voice activity detection`

**#9 Speaker Auth:**
`speaker verification`, `voice biometric authentication`, `anti-spoofing voice`

**#10 Expressive TTS:**
`emotional TTS`, `neural TTS prosody control`

**#11 Local Inference:**
`LLM quantization edge device`, `on-device LLM`, `llama.cpp inference optimization`

**#12 Cloud-Edge Routing:**
`edge cloud offloading LLM`, `model routing cascade`, `adaptive inference offloading`
