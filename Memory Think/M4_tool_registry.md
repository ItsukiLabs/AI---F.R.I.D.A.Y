# M4 — Tool Registry

> Status: **M4 v1 selesai diimplementasi (2026-09-11), belum di-commit.** 210 test lulus (136 lama tanpa diubah + 74 baru), 3 skip platform-specific di Windows. Belum ada smoke test dengan API key asli.
> Paper rujukan: **MCP-Zero** (agent meminta tool), **ScaleMCP** (sync via hash), **Tool-to-Agent Retrieval** (indeks gabungan domain↔tool), **EasyTool** (contoh skenario di deskripsi tool), **ToolLLM** (jalan keluar jujur saat tidak ada tool), **Sasha** (false positive dinilai paling buruk). Detail di `Memory Think/PAPER_NOTES.md` kategori #4/#5.

---

## Kegunaan

M4 adalah **daftar alat** F.R.I.D.A.Y dan cara agent menemukannya. Sebelum M4, semua tool selalu disodorkan ke LLM tiap iterasi. Itu wajar untuk 4 tool, tapi M5 akan menambah tool per device (tiap device 3-10 tool, bertambah saat device dicolok). Menyuntik semuanya ke prompt boros konteks dan menurunkan akurasi pemilihan tool (MCP-Zero: GitHub MCP server saja 4.600+ token untuk 26 tool).

M4 memisahkan dua hal yang dulu satu:

- **Katalog** (`ToolCatalog`, `backend/registry/`) — semua tool yang *ada*, dikelompokkan per domain, punya sidik jari, bisa dicari.
- **Registry per turn** (`ToolRegistry`, `backend/agent_core/tool_registry.py`) — tool yang *terpasang* untuk satu turn, yaitu yang dilihat LLM.

M4 harus ada **sebelum** adapter M5 pertama, karena adapter akan mendaftar ke katalog ini.

## Pendekatan

1. **MCP-Zero → meta-tool `find_tools`.** Turn dimulai dengan tool *pinned* + `find_tools`. Kalau permintaan butuh kemampuan lain, LLM mencari di katalog; tool yang ketemu langsung di-*bind* ke registry turn itu dan bisa dipanggil di langkah berikutnya. Kalau hasil tidak cocok, LLM mencari lagi dengan kata lain (iterative capability extension).
2. **ScaleMCP → `ToolCatalog.sync(provider, tools)`.** Penyedia tool (sekarang aplikasi, nanti tiap adapter M5) adalah sumber kebenaran untuk tool miliknya. Sync membandingkan `content_hash` tiap kontrak dengan yang tersimpan: tambah, ganti, atau hapus seperlunya, tanpa restart. Katalog tidak dipersist; dibangun ulang dari penyedia tiap start.
3. **Tool-to-Agent Retrieval → satu indeks untuk tool dan domain.** Hit pada ringkasan domain ("lampu ruang tamu") diperluas jadi semua tool domain itu; hit pada satu operasi ("redupkan") hanya mengembalikan tool itu. Tidak perlu menebak domain dulu baru tool.
4. **EasyTool + ScaleMCP → field `examples` di kontrak.** Satu artefak dua kegunaan: ditampilkan ke LLM di deskripsi tool (supaya argumen diisi benar), dan diindeks katalog sebagai bahan pencarian (seperti synthetic questions ScaleMCP).
5. **ToolLLM + Sasha → "tidak ketemu" adalah jawaban, bukan kegagalan.** Hasil kosong `find_tools` menyuruh LLM bilang terus terang bahwa F.R.I.D.A.Y tidak bisa, dan system prompt melarang mengaku sudah melakukan sesuatu atau memakai tool yang tidak relevan.

**Kenapa FTS5, bukan embedding:** katalog berisi puluhan tool, dan arsip M2b sudah membuktikan FTS5 cukup di skala ini tanpa dependensi atau layanan eksternal. Contoh skenario di kontrak menutup sebagian besar celah sinonim (ScaleMCP: synthetic questions konsisten menaikkan retrieval). Ditinjau ulang kalau tool > beberapa ratus.

## Ringkasan Teknis

| File | Isi |
|---|---|
| `backend/schemas/tool_contract.py` | Kontrak **1.1.0**: `domain` (default `"general"`, snake_case), `examples: list[ToolExample]` (tiap `arguments` divalidasi ke `input_schema` saat kontrak dibuat), `content_hash` (SHA-256 JSON kanonik semua field **kecuali** `version`/`contract_version`), `validate_identifier()` publik. |
| `backend/schemas/versioning.py` | `CONTRACT_VERSION = "1.1.0"` + riwayat versi. Perubahan aditif: kontrak gaya 1.0.0 tetap valid. |
| `backend/registry/catalog.py` | `ToolCatalog`: `register()` (satu tool, default pinned, provider `app`), `sync()` (ScaleMCP, validasi dulu baru mutasi), `describe_domain()`, `search()` (FTS5 in-memory, semua kata dulu lalu fallback OR, hit domain → semua tool domain), `pinned_tools()`, `discoverable_domains()`. Dataclass `CatalogEntry`, `CatalogHit`, `SyncReport`. |
| `backend/registry/discovery_tool.py` | `find_tools`: kontrak dibuat per turn (deskripsi memuat daftar domain + ringkasan, argumen `domain` dibatasi `enum`), `make_discovery_tool(catalog, turn_registry)`. Mengembalikan nama, domain, deskripsi, `permission_tier`, satu contoh, status `loaded`/`already_available`. |
| `backend/agent_core/tool_registry.py` | `bind()` (idempoten untuk tool yang sama, raise kalau nama sama tapi hash beda) dan `has()`. `register()` tidak berubah. |
| `backend/agent_core/loop.py` | `to_llm_tools()` dibaca ulang **tiap iterasi** (tanpa ini tool hasil `find_tools` tidak terlihat). System prompt + 1 kalimat anti-klaim-palsu. |
| `backend/agent_core/llm_client.py` | `examples` ditambahkan ke deskripsi tool yang dikirim ke LLM (format tool Anthropic tidak punya slot contoh). Kontrak tanpa contoh dikonversi persis seperti dulu. |
| `backend/orchestrator/orchestrator.py` | Parameter baru `catalog`; `registry` jadi opsional. Registry per turn = tool `registry` + pinned katalog + tool memori + `find_tools` (hanya kalau katalog punya tool discoverable). Nama ganda antara `registry` dan katalog → raise. |
| `backend/dal/fts.py` | Helper FTS5 bersama (`TOKENIZER`, `TOKEN_PATTERN`, `tokens()`, `fts_query()`), dipindah dari `archive_store.py`. Arsip M2b hanya ganti impor. |
| `backend/agent_core/tools/*` | 4 tool lama diberi `domain` (`time`, `memory`) + 1-2 contoh berbahasa Indonesia/Inggris — sekaligus contoh standar untuk adapter M5. |

**Test baru (74):** `test_tool_contract_examples.py`, `test_tool_catalog.py`, `test_discovery_tool.py`, `test_agent_loop_discovery.py`, `test_orchestrator_catalog.py`. File test lama **tidak diubah sebaris pun** (regression guard, konvensi sejak M2a). Semua pakai `FakeLLMClient`, tidak ada panggilan API asli.

### Alur satu turn dengan katalog

1. `Orchestrator.run_turn()` membuat registry per turn: pinned + memori + `find_tools`.
2. LLM melihat daftar itu. Tool device (discoverable) belum ada.
3. LLM memanggil `find_tools(query="turn on lamp")` → katalog mencari → tool lampu di-`bind` ke registry turn.
4. Iterasi berikutnya `run_agent()` membaca ulang registry → LLM melihat `lamp_set_power` → memanggilnya.
5. Turn selesai. Registry per turn dibuang; katalog tidak berubah. Turn berikutnya mulai lagi dari pinned.

## Bahasa Awam

Bayangkan F.R.I.D.A.Y bekerja di **meja kerja** yang ada di depan **gudang alat**.

- **Gudang** (katalog) menyimpan semua alat yang dimiliki, disusun per rak (domain: "waktu", "memori", "lampu ruang tamu"). Tiap rak punya label singkat.
- **Meja** (registry per turn) hanya berisi alat yang sedang dipakai. Beberapa alat selalu ada di meja (pinned), misalnya jam.
- Kalau butuh alat yang tidak ada di meja, F.R.I.D.A.Y **minta ke penjaga gudang** (`find_tools`) dengan menyebut kebutuhannya: "alat untuk menyalakan lampu". Penjaga mencari berdasarkan nama alat, keterangan, contoh pemakaian, dan label rak, lalu menaruh alat yang cocok di meja.
- Kalau gudang tidak punya alatnya, penjaga bilang "tidak ada", dan F.R.I.D.A.Y wajib jujur ke user, bukan pura-pura atau memakai alat lain yang tidak nyambung.
- Tiap alat punya **sidik jari** (hash). Saat pemasok (nanti: adapter device) datang membawa daftar alat terbaru, gudang cukup membandingkan sidik jari: alat baru ditambah, alat yang berubah diganti, alat yang sudah tidak dibawa dibuang.
- Selesai satu tugas, meja dibereskan. Gudangnya tetap.

## Keputusan desain (dan deviasi dari rencana)

- **Hash mencakup semua field kecuali nomor versi.** Rencana awal hanya menyebut sebagian field. Semua field (termasuk `annotations`, `output_schema`) dipilih karena aturan "semua kecuali versi" lebih sederhana dan tidak bisa kelewatan field yang ditambah nanti.
- **`register()` terpisah dari `sync()`.** Rencana awal menyebut `register()` = `sync` satu tool. Ternyata salah: `sync` menghapus tool penyedia yang tidak ditawarkan, jadi mendaftar satu per satu lewat `sync` akan menghapus tool sebelumnya. `register()` sekarang aditif dan raise pada nama ganda, seperti `ToolRegistry.register()`.
- **`sync()` validasi dulu baru mutasi.** Tabrakan nama dengan penyedia lain atau nama ganda dalam satu tawaran → raise, katalog tidak berubah sama sekali.
- **`sync()` selalu menyimpan callable terbaru**, bahkan untuk tool yang tidak berubah: adapter yang reconnect membawa closure baru, yang lama bisa terikat ke koneksi mati.
- **Pinned adalah kebijakan katalog, bukan field kontrak.** Tool yang sama bisa pinned di satu instalasi dan discoverable di instalasi lain.
- **Contoh dikirim ke LLM lewat deskripsi.** Tidak eksplisit di rencana, tapi tanpa ini EasyTool tidak berlaku (LLM tidak pernah melihat contohnya).
- **`find_tools` hanya dipasang kalau ada yang bisa ditemukan.** Kalau semua tool pinned, `find_tools` cuma menambah konteks tanpa guna.
- **Binding tidak memberi izin apa pun.** `permission_tier` hanya dilaporkan; penegakan saat eksekusi adalah tugas M11.
- **Katalog tidak dipersist.** Ia data turunan dari penyedia (prinsip ScaleMCP). Tidak ada file baru di disk, tidak ada migrasi.
- **Test baru di file baru.** File test lama tetap utuh sebagai bukti tidak ada regresi.

## Belum digarap / TODO lanjutan

- **Keputusan A2 (checkpoint wajib).** Diputuskan saat tool device mock pertama dibuat, dengan kasus konkret "lampu nyala tapi turn gagal tersimpan". M4 tidak menyentuh urutan tulis orchestrator.
- **M5:** adapter memanggil `catalog.sync("<adapter_id>", tools)` dan `describe_domain(...)`. Tool device mock pertama pakai pola benchmark SAGE (state awal → perintah → cek state akhir, tanpa hardware).
- **M11:** penegakan `permission_tier` saat eksekusi, minimal konfirmasi untuk `CRITICAL`. Saat ini `find_tools` hanya melaporkan tier.
- **`find_tools` memakan satu iterasi.** `max_iterations` default 6; tugas device multi-langkah bisa mendekati batas. Pantau saat pemakaian nyata.
- **Tool yang di-load tidak bertahan lintas turn.** LLM harus mencari lagi di turn berikutnya. Kalau ini jadi masalah biaya/latensi, rujukan: MemTool (arXiv 2507.21428).
- **Embedding/vector index** kalau katalog tumbuh ke ratusan tool.
- **Belum ada entry point produksi yang memakai katalog.** Belum ada CLI/server yang membangun `Orchestrator`; semua pemakaian masih lewat test.
- **Smoke test dengan API key asli** belum dijalankan: `get_current_time` sebagai tool discoverable, tanya "jam berapa sekarang?", pastikan LLM memanggil `find_tools` lalu `get_current_time`.
- **Metrik evaluasi (M16):** ukur *tool correctness* terpisah dari *task completion* (ScaleMCP), pakai 7 mode kegagalan Sasha untuk tool device.
