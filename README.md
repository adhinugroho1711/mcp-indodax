# Indodax MCP Server 🚀

Expose semua *Private REST API* Indodax sebagai **MCP tools** (bisa dipakai Claude Code atau agen AI lain). Fokus: cepat dipakai, mudah dipahami.

---

## 1. Persiapan Cepat
```bash
# clone & masuk repo
git clone https://github.com/adhinugroho1711/mcp-indodax.git
cd mcp-indodax

# (opsional) buat virtual-env
python -m venv .venv && source .venv/bin/activate

# install paket
pip install -r requirements.txt
```

## 2. Isi Kredensial
Buat `.env` (file ini tidak akan ke-push):
```ini
INDODAX_API_KEY=YOUR_API_KEY
INDODAX_API_SECRET=YOUR_SECRET
```

## 3. Jalankan
```bash
python server.py              # mode stdio (default MCP)
# atau HTTP:
uvicorn server:mcp.app --reload
```

## 4. Contoh Pakai Tool
```python
from server import get_info, trade
import asyncio, json

async def demo():
    print(json.dumps(await get_info(), indent=2))
    # order beli BTC 50k IDR
    # await trade("btc_idr", "buy", price=500000000, idr=50000)
asyncio.run(demo())
```

## 5. Integrasi Editor (Claude Code)
- **VS Code**: letakkan `mcp_servers.json` di root ➜ *Command Palette* ➜ `Claude: Start MCP Server`.
- **JetBrains**: taruh `mcp_servers.json` di root atau `.claude/` ➜ Tools ➜ Claude ➜ *Start MCP Server*.
- **Neovim**: simpan `mcp_servers.json` di `~/.config/claude/` ➜ `:ClaudeStartServer indodax`.

Contoh `mcp_servers.json`:
```json
{
  "mcpServers": {
    "indodax": {
      "command": "uv",
      "args": ["--directory", "/ABSOLUTE/PATH/TO/mcp-indodax", "run", "server.py"]
    }
  }
}
```

---
### Struktur Singkat
```
server.py          # semua MCP tools
requirements.txt   # dependensi
mcp_servers.json   # config runner (contoh)
```

MIT 2025 Prihanantho Adhi Nugroho

## Integrasi Editor / Claude Code

Berikut cara mendaftarkan *MCP server* di beberapa editor / plugin umum. Pastikan `mcp_servers.json` Anda sudah berisi path absolut proyek.

### VS Code (Claude Code Extension)
1. Install extension "Claude Code".
2. Letakkan `mcp_servers.json` di root proyek, contoh:
   ```json
   {
     "mcpServers": {
       "indodax": {
         "command": "uv",
         "args": [
           "--directory",
           "/ABSOLUTE/PATH/TO/mcp-indodax",
           "run",
           "server.py"
         ]
       }
     }
   }
   ```
3. Buka Command Palette → `Claude: Start MCP Server…` → pilih `indodax`.

### JetBrains IDE (IntelliJ / PyCharm) + Plugin Claude Code
1. Taruh `mcp_servers.json` di direktori `.claude/` atau root proyek.
2. Tools → Claude → **Start MCP Server** → pilih `indodax`.

### Neovim (`claude.nvim`)
1. Simpan `mcp_servers.json` di `$HOME/.config/claude/`.
2. Jalankan `:ClaudeStartServer indodax`.

### CLI Langsung
```bash
uv --directory /ABSOLUTE/PATH/TO/mcp-indodax run server.py   # atau python server.py
```

---

## Contoh Pemanggilan Alat

```python
import asyncio, json
from server import get_info, trade

async def main():
    info = await get_info()
    print(json.dumps(info, indent=2))

    # Contoh order beli BTC senilai 50.000 IDR
    # res = await trade("btc_idr", "buy", price=500000000, idr=50000)

asyncio.run(main())
```

## Struktur Proyek

```
├── server.py          # Implementasi MCP tools
├── requirements.txt   # Dependensi Python
├── mcp_servers.json   # Contoh konfigurasi runner MCP
├── .gitignore         # Mengabaikan file sensitif & artefak
└── README.md          # Dokumentasi ini
```

## Lisensi

MIT © 2025 Prihanantho Adhi Nugroho
