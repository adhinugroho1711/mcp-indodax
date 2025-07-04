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

### 1. Mengecek Harga Kripto
```python
import asyncio
from server import ticker, ticker_all

async def check_prices():
    # Dapatkan semua ticker yang tersedia
    all_tickers = await ticker_all()
    
    # Dapatkan harga BTC/IDR
    btc_price = await ticker("btcidr")
    print(f"Harga BTC/IDR: {int(btc_price['last']):,}")
    
    # Dapatkan harga XRP/IDR
    xrp_price = await ticker("xrpidr")
    print(f"Harga XRP/IDR: {int(xrp_price['last']):,}")

asyncio.run(check_prices())
```

### 2. Mengecek Saldo dan Membuat Order
```python
import asyncio, json
from server import get_info, trade

async def main():
    # Dapatkan info akun
    info = await get_info()
    print("Saldo IDR:", info['return']['balance']['idr'])
    
    # Contoh order beli BTC senilai 50.000 IDR
    # res = await trade("btc_idr", "buy", price=500000000, idr=50000)
    # print(json.dumps(res, indent=2))

asyncio.run(main())
```

## Cara Melakukan Trading

### Daftar Perintah Trading

| Perintah | Deskripsi | Contoh Penggunaan |
|----------|-----------|-------------------|
| `ticker("btcidr")` | Melihat harga BTC/IDR terkini | ```python\nfrom server import ticker\nimport asyncio\n\nasync def main():\n    price = await ticker("btcidr")\n    print(f"Harga BTC: {int(price['last']):,} IDR")\n\nasyncio.run(main())\n``` |
| `trade("btcidr", "buy", idr=50000, price=500000000)` | Membeli kripto dengan IDR | ```python\nfrom server import trade\n\nasync def beli_btc():\n    await trade("btcidr", "buy", idr=50000, price=500000000)\n``` |
| `trade("xrpidr", "sell", xrp=100, price=40000)` | Menjual kripto | ```python\nfrom server import trade\n\nasync def jual_xrp():\n    await trade("xrpidr", "sell", xrp=100, price=40000)\n``` |
| `open_orders()` | Melihat daftar order aktif | ```python\nfrom server import open_orders\n\nasync def cek_order():\n    orders = await open_orders()\n    print(orders)\n``` |
| `cancel_order(order_id=12345)` | Membatalkan order | ```python\nfrom server import cancel_order\n\nasync def batal_order():\n    await cancel_order(order_id=12345)\n``` |

### 1. Membuat Order Beli/Jual

```python
import asyncio
from server import trade, get_info

async def place_order():
    # Dapatkan info akun terlebih dahulu
    info = await get_info()
    print("Saldo IDR:", info['return']['balance']['idr'])
    
    # Contoh order beli BTC senilai 50.000 IDR
    buy_order = await trade(
        pair="btcidr",       # pair yang akan ditradingkan
        type="buy",          # 'buy' atau 'sell'
        price=500000000,     # harga per unit (dalam satuan terkecil)
        idr=50000,          # jumlah IDR yang akan dibelanjakan
        # atau gunakan parameter crypto untuk menentukan jumlah koin
        # btc=0.001         # jumlah koin yang akan dibeli/dijual
    )
    print("Order Response:", buy_order)

asyncio.run(place_order())
```

### 2. Membatalkan Order

```python
import asyncio
from server import cancel_order, open_orders

async def cancel_existing_order():
    # Dapatkan daftar order terbuka
    orders = await open_orders()
    
    if 'btc_idr' in orders and orders['btc_idr']:
        # Batalkan order pertama yang ditemukan
        order_id = orders['btc_idr'][0]['order_id']
        result = await cancel_order(order_id=order_id)
        print(f"Order {order_id} dibatalkan:", result)

asyncio.run(cancel_existing_order())
```

### 2. Contoh Lengkap Trading

```python
import asyncio
from server import ticker, trade, open_orders, cancel_order

async def trading_bot():
    # 1. Cek harga BTC/IDR
    btc = await ticker("btcidr")
    print(f"Harga BTC: {int(btc['last']):,} IDR")
    
    # 2. Buat order beli jika harga di bawah 500 juta
    if btc['last'] < 500000000:
        print("Harga menarik, membeli...")
        order = await trade(
            pair="btcidr",
            type="buy",
            price=btc['last'],
            idr=100000  # Beli senilai 100 ribu IDR
        )
        print("Order berhasil:", order)
    
    # 3. Cek order aktif
    print("\nOrder aktif:")
    orders = await open_orders()
    for pair, order_list in orders.items():
        for order in order_list:
            print(f"- {pair}: {order['type']} {order['order_btc']} BTC @ {int(order['price']):,}")

# Jalankan bot
try:
    asyncio.run(trading_bot())
except Exception as e:
    print("Error:", e)
```

### 3. Memeriksa Order yang Aktif

```python
import asyncio
from server import open_orders

async def check_orders():
    orders = await open_orders()
    for pair, order_list in orders.items():
        if order_list:
            print(f"\nOrder aktif untuk {pair}:")
            for order in order_list:
                print(f"- ID: {order['order_id']}")
                print(f"  Tipe: {order['type']}")
                print(f"  Harga: {int(order['price']):,} IDR")
                print(f"  Jumlah: {order.get('order_btc', order.get('order_eth', 'N/A'))}")

asyncio.run(check_orders())
```

## Daftar Pair ID yang Tersedia

Berikut adalah beberapa contoh pair ID yang bisa digunakan:
- `btcidr` - Bitcoin (BTC) ke Rupiah
- `ethidr` - Ethereum (ETH) ke Rupiah
- `xrpidr` - XRP ke Rupiah
- `adaidr` - Cardano (ADA) ke Rupiah
- `bnbidr` - Binance Coin (BNB) ke Rupiah
- `dogeidr` - Dogecoin (DOGE) ke Rupiah

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
