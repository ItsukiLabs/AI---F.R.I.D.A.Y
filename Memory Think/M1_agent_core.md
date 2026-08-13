# M1 — Agent Core

> Status: **Implementasi awal selesai (2026-08-13)** — loop ReAct jalan, 8 test baru lulus (19 total termasuk M0). Sprint 1, Kategori riset #1 (Agentic AI / Tool Use & Function Calling).
> Paper rujukan: ReAct, Toolformer, Reflexion, LLM Agent Survey. Detail lengkap di `Memory Think/PAPER_NOTES.md`.

---

## Kegunaan

M1 adalah **"otak" pengambil keputusan** F.R.I.D.A.Y — bagian yang bikin F.R.I.D.A.Y jadi *agent* beneran, bukan sekadar chatbot yang jawab teks. Ini loop inti yang:

1. Mikir soal apa yang harus dilakukan (reasoning)
2. Mutusin apakah butuh manggil tool (dari daftar tool yang sudah punya `ToolContract` dari M0) atau langsung jawab
3. Kalau manggil tool, lihat hasilnya (observation)
4. Mikir lagi berdasarkan hasil itu — ulang sampai task selesai atau menyerah

M1 bergantung langsung ke M0: setiap tool yang bisa dipanggil loop ini **harus** sudah punya `ToolContract` yang valid, karena manifest itulah yang di-"tunjukkan" ke LLM supaya dia tahu tool apa saja yang tersedia dan kapan boleh dipakai.

## Pendekatan

Tiga paper jadi kerangka utama:

1. **ReAct** — pola loop `Thought → Action → Observation → Thought → ...`. "Thought" adalah reasoning verbal (bantu agent lacak progres & sesuaikan rencana), "Action" adalah pemanggilan tool nyata (ambil info dari luar, kurangi halusinasi dibanding cuma mikir tanpa cek fakta). Ini kerangka loop utama M1.
2. **Toolformer** — prinsip *kapan* tool sebaiknya dipanggil: tool dipanggil hanya kalau benar-benar mengurangi ketidakpastian/berguna, bukan asal panggil semua tool yang ada. Penting buat efisiensi biaya & latensi kalau F.R.I.D.A.Y punya banyak tool IoT/OS sekaligus.
3. **Reflexion** — mekanisme "belajar dari gagal" tanpa training ulang model: kalau satu percobaan gagal, agent bikin refleksi verbal (bahasa biasa, bukan update bobot) dan simpan sebagai konteks tambahan buat percobaan berikutnya. Ini yang bikin loop ReAct tidak cuma "coba-gagal-coba lagi tanpa belajar", tapi makin pintar tiap percobaan dalam sesi yang sama.

Risiko yang harus diantisipasi (dicatat di paper notes): loop ReAct bisa terjebak berulang tanpa progres — perlu guard/timeout/batas iterasi, bukan dibiarkan jalan tanpa henti.

## Ringkasan Teknis (implementasi nyata, 2026-08-13)

Keputusan desain kunci: **native tool-calling Claude**, bukan text-parsing manual seperti paper ReAct asli (2022, sebelum tool-calling API ada). Model mengembalikan teks (= Thought) diikuti `tool_use` block terstruktur (= Action) dalam satu response; tool result dikirim balik sebagai pesan berikutnya (= Observation). Sama persis secara semantik dengan pola ReAct, tapi jauh lebih robust dibanding parsing regex teks bebas.

Struktur file (`backend/agent_core/`):

- `config.py` — baca `.env` (`LLM_PROVIDER`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_MODEL` default `claude-haiku-4-5` untuk development yang murah).
- `llm_client.py` — `LLMClient` (Protocol provider-agnostic), `ToolCallRequest`/`LLMResponse` (dataclass provider-agnostic), `AnthropicLLMClient` (implementasi nyata pakai SDK `anthropic`), `tool_contract_to_anthropic_tool()` (konversi `ToolContract` M0 → format tool Anthropic, 1:1 karena M0 memang dirancang mengikuti primitif MCP), `get_llm_client(provider)` factory — `"openai"` sengaja `raise NotImplementedError` (slot Sprint 8, bukan dibangun sekarang).
- `tool_registry.py` — `ToolRegistry`: `register()`, `get()`, `to_llm_tools()`.
- `loop.py` — `run_agent(user_input, registry, llm, max_iterations=6)`: tiap iterasi kirim riwayat+tools ke LLM → kalau ada tool_calls, validasi argumen ke `input_schema` pakai `jsonschema` → eksekusi tool nyata → exception/validasi gagal jadi **observation refleksi** (`is_error: true`, pesan verbal) disisipkan balik ke riwayat, bukan silent retry → lanjut iterasi. Kalau LLM jawab final (tanpa tool_calls), loop selesai. Guard `max_iterations`: kalau kelewat, `AgentResult.exceeded_max_iterations=True` dengan pesan jujur, bukan infinite loop.
- `tools/time_tool.py` — satu tool contoh (`get_current_time`, read-only) untuk menguji loop end-to-end secara nyata tanpa butuh integrasi IoT/OS yang belum ada (M4/M5).

**Reflexion di-scope minimal**: refleksi kegagalan cuma hidup di riwayat pesan satu sesi run — persistensi lintas-sesi itu ranah M2 (Memory), belum digarap di sini.

**Test** (`backend/tests/test_tool_registry.py`, `test_agent_loop.py`) — 8 test baru, semua pakai `FakeLLMClient` (test double), tidak ada yang memanggil API Anthropic asli (hindari biaya/flakiness saat CI/dev iteration). Cover: jawaban final tanpa tool, satu tool call sukses, argumen invalid → refleksi → retry sukses, melebihi `max_iterations`.

**Verifikasi nyata (2026-08-13):** smoke test manual dengan `ANTHROPIC_API_KEY` asli user berhasil — `run_agent("jam berapa sekarang?", ...)` memanggil `get_current_time` di iterasi 1, jawab final pakai hasilnya di iterasi 2 ("Waktu sekarang adalah 08:42:06 UTC, Kamis 13 Agustus 2026"). Bukti loop ReAct benar-benar nyambung end-to-end (console API key → `.env` → `config.py` → `AnthropicLLMClient` → `loop.py`), bukan cuma lulus test dengan fake LLM.

**Belum digarap / TODO lanjutan:**
- Provider `"openai"` belum diimplementasi (sengaja, Sprint 8).
- Belum ada tool nyata untuk IoT/OS (M4/M5) — `get_current_time` cuma contoh untuk menguji loop.
- Reflexion belum persisten lintas sesi (M2).

## Bahasa Awam

Kalau M0 itu "formulir pendaftaran alat", M1 itu **orangnya yang mikir dan pakai alat itu**.

Bayangkan kamu minta tolong F.R.I.D.A.Y: *"nyalain lampu kamar terus kasih tau suhu di luar."* M1 ini yang:

1. **Mikir dulu**: "oke, ada dua hal yang harus gua lakuin — nyalain lampu, sama cek cuaca."
2. **Bertindak**: manggil alat `nyalain_lampu` (yang sudah terdaftar di M0), lihat hasilnya — berhasil apa nggak.
3. **Mikir lagi**: "oke lampu udah nyala, sekarang gua panggil alat `cek_cuaca`."
4. **Bertindak lagi**: manggil `cek_cuaca`, dapat hasilnya.
5. **Selesai**: gabungin semua hasil jadi jawaban ke kamu: "Lampu kamar udah nyala. Suhu di luar 28°C."

Kalau di tengah jalan ada yang gagal (misal alat `nyalain_lampu` error), F.R.I.D.A.Y nggak langsung nyerah atau ngulang percis sama caranya — dia "mencatat" apa yang salah (refleksi), terus coba pendekatan lain berdasarkan catatan itu. Ini bedanya F.R.I.D.A.Y sama chatbot biasa yang cuma jawab teks: F.R.I.D.A.Y benar-benar **melakukan** sesuatu, mikir sebelum dan sesudah tiap aksi, dan bisa memperbaiki diri di tengah proses.
