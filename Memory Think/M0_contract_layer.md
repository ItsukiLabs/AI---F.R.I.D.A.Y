# M0 — Contract Layer

> Status: **Sedang digarap.** Sprint 1, Kategori riset #1 (Agentic AI / Tool Use & Function Calling).
> Paper rujukan: MCP (Model Context Protocol), Agent-OS. Detail lengkap di `Memory Think/PAPER_NOTES.md`.

---

## Kegunaan

M0 adalah **lapisan kontrak/skema** — bukan logika agent itu sendiri, tapi aturan main tentang bagaimana segala sesuatu yang bisa dipakai agent (tool/skill) *harus dideskripsikan* sebelum boleh didaftarkan ke sistem.

Tanpa M0, setiap modul lain (M1 agent core, M4 tool registry, M5 device layer, dst.) akan mendeskripsikan tool dengan caranya sendiri-sendiri — tidak konsisten, rawan salah paham antara kode dan LLM, dan susah divalidasi otomatis. M0 memastikan **satu bentuk baku** dipakai di semua tempat.

Ini juga fondasi buat modul keamanan (M11) nanti — karena kontrak ini sudah membawa label tingkat risiko (`permission_tier`) sejak awal, bukan ditambah belakangan.

## Pendekatan

Dua sumber ide utama:

1. **MCP (Model Context Protocol)** — tool dideskripsikan dengan `name`, `description`, `input_schema`/`output_schema` (JSON Schema), dan "annotation hints" yang memberi tahu sifat tool: apakah cuma baca (`read_only_hint`), apakah bisa merusak/tidak bisa dibatalkan (`destructive_hint`), apakah aman dipanggil berulang (`idempotent_hint`), apakah menyentuh sistem luar (`open_world_hint`).
2. **Agent-OS (versioned plugin/contract model)** — konsep "kontrak berversi" ala driver/ABI di sistem operasi: `contract_version` (bentuk skemanya) dipisah dari `version` (versi tool itu sendiri), supaya kalau bentuk skema berubah di masa depan, tool lama tidak otomatis rusak.

Implementasi teknis pakai **Pydantic v2** (Python) — setiap field divalidasi otomatis saat objek dibuat (nama harus `snake_case`, versi harus semver `x.y.z`, deskripsi tidak boleh kosong). Kalau ada yang coba daftarin tool asal-asalan, ditolak di titik ini juga, bukan menyusul jadi bug aneh pas agent lagi jalan.

## Ringkasan Teknis (yang sudah ada)

| File | Isi |
|---|---|
| `backend/schemas/versioning.py` | Konstanta `CONTRACT_VERSION` — versi bentuk skema kontrak, bukan versi tool. |
| `backend/schemas/tool_contract.py` | `ToolAnnotations` (4 hint di atas), `PermissionTier` enum (`read_only` / `standard` / `critical` — cuma label, logic penegakannya nanti di M11), `ToolContract` (model utama + validator). |
| `backend/schemas/__init__.py` | Re-export simbol utama. |
| `backend/tests/test_tool_contract.py` | 11 test — validasi default value, penolakan nama/versi/deskripsi tidak valid, serialisasi ke JSON. Semua **passed**. |

Scope M0 sengaja dipersempit ke **Tool Contract dulu** (paling kritis dan dipakai lintas modul). Kontrak lain yang disebut di README (`Task`, `Event`, `Memory`, `Device`) sengaja **ditunda** sampai modul terkait benar-benar digarap (Task di M3, Device di M4/M5, dst.) — supaya tidak mendesain skema untuk sesuatu yang belum jelas kebutuhannya.

## Bahasa Awam

Bayangkan M0 itu seperti **formulir pendaftaran alat baru**. Setiap kali ada "alat" (tool) baru yang mau dikasih ke F.R.I.D.A.Y — entah itu `cek_cuaca`, `nyalain_lampu`, atau `cari_lukisan` — alat itu wajib diisi formulirnya dulu:

- Namanya apa (rapi, konsisten)
- Fungsinya buat apa (dijelasin jelas, karena F.R.I.D.A.Y "baca" penjelasan ini buat mutusin kapan alat ini dipakai)
- Butuh input apa
- Hasilnya berupa apa
- Apakah alat ini cuma "lihat-lihat" doang atau bisa "bikin perubahan beneran" (misal ngunci pintu — itu beda level bahaya sama sekadar baca suhu ruangan)

Kalau formulirnya nggak lengkap atau ngasal, alat itu **ditolak, nggak boleh masuk sistem**. Ini penting supaya nanti pas F.R.I.D.A.Y punya puluhan/ratusan alat, semuanya tetap rapi dan bisa dipercaya — dan kalau ada alat yang "berbahaya" (bisa merusak/nggak bisa dibatalkan), itu sudah ketauan dari awal, bukan pas kejadian.

---

**[2026-09-11] Kontrak naik ke 1.1.0 (M4, Sprint 3).** Tiga tambahan aditif, kontrak lama tetap valid: `domain` (pengelompokan ala server MCP-Zero, default `"general"`), `examples: list[ToolExample]` (skenario + argumen, divalidasi ke `input_schema` saat kontrak dibuat, ditampilkan ke LLM di deskripsi tool dan diindeks katalog), dan `content_hash` (SHA-256 semua field kecuali nomor versi, dipakai `ToolCatalog.sync` untuk mendeteksi perubahan isi). Aturan snake_case dipindah ke `validate_identifier()` publik supaya dipakai juga untuk domain dan provider katalog. Detail dan alasan di `Memory Think/M4_tool_registry.md`.
