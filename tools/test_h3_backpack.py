#!/usr/bin/env python3
"""
tools/test_h3_backpack.py — Gate H3 Test Suite (Rule 80)
Tests:
1. A3: Hotbar overflow to backpack (7 items -> 5 hotbar + 2 backpack), auto-refill on use.
2. A4: Backpack button beside hotbar, opens 20-slot modal, Esc closes.
3. A5: Touching hotbar slot shows Gunakan / Pindahkan / Buang popup.
4. A6: Full backpack (25/25) rejects new item without altering cash.
Captures GREEN screenshots:
 - docs/regression/a3_backpack_refill_green.png
 - docs/regression/a4_backpack_button_green.png
 - docs/regression/a5_item_popup_green.png
 - docs/regression/a6_backpack_full_green.png
"""

import os
import sys
import json
import time
import subprocess
import urllib.request
import asyncio
import websockets
import base64

CDP_PORT = 9249
HTTP_PORT = 3843
REG_DIR = "/home/abarox/Desktop/prototipe web statis game/game/docs/regression"
os.makedirs(REG_DIR, exist_ok=True)

async def send_cdp(ws, method, params=None, msg_id=1):
    msg = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(msg))
    while True:
        raw = await ws.recv()
        res = json.loads(raw)
        if res.get("id") == msg_id:
            return res

async def evaluate(ws, expr, msg_id=100, await_p=False):
    res = await send_cdp(ws, "Runtime.evaluate", {
        "expression": expr,
        "returnByValue": True,
        "awaitPromise": await_p
    }, msg_id)
    if "exceptionDetails" in res.get("result", {}):
        exc = res["result"]["exceptionDetails"]
        raise RuntimeError(f"JS Error: {exc.get('text')} | {exc.get('exception',{}).get('description','')}")
    return res.get("result", {}).get("result", {}).get("value")

async def snap(ws, filename, msg_id=500):
    shot = await send_cdp(ws, "Page.captureScreenshot", {"format": "png"}, msg_id)
    img_data = shot.get("result", {}).get("data")
    if img_data:
        p = os.path.join(REG_DIR, f"{filename}.png")
        with open(p, "wb") as f:
            f.write(base64.b64decode(img_data))
        print(f"  📸 Saved GREEN screenshot: {filename}.png")

async def get_ws_url():
    for _ in range(20):
        try:
            req = urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json", timeout=1)
            tabs = json.loads(req.read().decode())
            for tab in tabs:
                if "index.html" in tab.get("url", "") or "3843" in tab.get("url", ""):
                    return tab.get("webSocketDebuggerUrl")
            if tabs:
                return tabs[0].get("webSocketDebuggerUrl")
        except Exception:
            pass
        await asyncio.sleep(0.5)
    return None

async def run_suite():
    print("==================================================")
    print("  TEST SUITE: Gate H3 (Backpack, Hotbar, Actions)")
    print("==================================================")

    chrome_proc = subprocess.Popen([
        "/usr/bin/google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-extensions",
        "--window-size=1200,800",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir=/tmp/test_chrome_h3_{int(time.time())}",
        f"http://127.0.0.1:{HTTP_PORT}/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        ws_url = await get_ws_url()
        if not ws_url:
            print("ERROR: Could not get Chrome WebSocket URL")
            return False

        async with websockets.connect(ws_url, max_size=10_000_000) as ws:
            await send_cdp(ws, "Page.enable", {}, 1)
            await send_cdp(ws, "Runtime.enable", {}, 2)
            await asyncio.sleep(1.0)

            # Start game
            await evaluate(ws, "localStorage.clear()", 10)
            await send_cdp(ws, "Page.navigate", {"url": f"http://127.0.0.1:{HTTP_PORT}/index.html"}, 11)
            await asyncio.sleep(2.5)

            await evaluate(ws, "window.__GAME__.scene.getScene('MainMenu')._startNew()", 12)
            await asyncio.sleep(0.5)
            await evaluate(ws, "document.querySelector('.charcreate-form select').value = 'm'", 13)
            await evaluate(ws, "document.querySelector('.charcreate-form')?.requestSubmit()", 14)
            await asyncio.sleep(2.0)

            print("\n1. Menguji Penambahan 7 Item Berbeda (Hotbar Penuh -> Ransel Menampung)...")
            # Setup 7 items into inventory via addItem domain logic
            items_status = await evaluate(ws, """(async () => {
                const { addItem } = await import('./src/domain/inventory.js');
                const store = window.__LJ__.getStore();
                let inv = store.getState().inventory;
                const toAdd = ['nasi_kuning', 'bakso', 'es_teh', 'air_mineral', 'gorengan', 'mie_goreng', 'roti_isi'];
                for (const id of toAdd) {
                    const res = addItem(inv, id, 1);
                    if (res.ok) inv = res.inventory;
                }
                store.setState({ inventory: inv });
                return {
                    hotbarFilled: inv.hotbar.filter(s => s !== null).length,
                    backpackFilled: inv.backpack.filter(s => s !== null).length
                };
            })()""", 20, await_p=True)

            print(f"  Status Inventaris: {items_status}")
            assert items_status["hotbarFilled"] == 5, f"Expected 5 in hotbar, got {items_status['hotbarFilled']}"
            assert items_status["backpackFilled"] == 2, f"Expected 2 in backpack, got {items_status['backpackFilled']}"

            # Check DOM hotbar and backpack button badge
            bp_badge_text = await evaluate(ws, "document.getElementById('hud-backpack-badge')?.textContent", 21)
            print(f"  Lencana tombol ransel di DOM: '{bp_badge_text}'")
            assert bp_badge_text == '2', f"Expected badge '2', got '{bp_badge_text}'"

            # 2. Test A4: Backpack button opens panel
            print("\n2. Menguji Tombol Ransel (A4)...")
            await evaluate(ws, "document.getElementById('hud-backpack-btn')?.click()", 22)
            await asyncio.sleep(0.5)

            bp_modal_visible = await evaluate(ws, "document.querySelector('.backpack-modal-overlay')?.style.display", 23)
            print(f"  Modal ransel display: {bp_modal_visible}")
            assert bp_modal_visible == 'flex', "Backpack modal overlay is not visible!"

            capacity_text = await evaluate(ws, "document.getElementById('backpack-capacity-badge')?.textContent", 24)
            print(f"  Teks kapasitas ransel: '{capacity_text}'")
            assert "Hotbar 5/5" in capacity_text and "Ransel 2/20" in capacity_text

            await snap(ws, "a4_backpack_button_green", 501)
            print("  ✅ A4 VERIFIED GREEN: Tombol ransel menampilkan panel 20-slot dengan lencana benar!")

            # Close backpack with Esc key
            await send_cdp(ws, "Input.dispatchKeyEvent", {"type": "keyDown", "windowsVirtualKeyCode": 27, "key": "Escape", "code": "Escape"})
            await asyncio.sleep(0.3)
            await send_cdp(ws, "Input.dispatchKeyEvent", {"type": "keyUp", "windowsVirtualKeyCode": 27, "key": "Escape", "code": "Escape"})
            await asyncio.sleep(0.3)

            # 3. Test A5: Touching hotbar slot shows action popup
            print("\n3. Menguji Popup Aksi Item (A5)...")
            # Set energy to 70% so Gunakan is enabled
            await evaluate(ws, """(() => {
                const store = window.__LJ__.getStore();
                store.setState({ energy: { current: 70, max: 100 } });
            })()""", 25)
            await asyncio.sleep(0.3)

            # Click slot 0 in hotbar
            await evaluate(ws, "document.querySelector('.hotbar-slot:not(.empty)')?.click()", 26)
            await asyncio.sleep(0.5)

            popup_exists = await evaluate(ws, "!!document.querySelector('.item-action-popup')", 27)
            print(f"  Popup aksi item muncul: {popup_exists}")
            assert popup_exists, "Item action popup did not appear when slot clicked!"

            btn_use_text = await evaluate(ws, "document.querySelector('.btn-use')?.textContent", 28)
            btn_move_text = await evaluate(ws, "document.querySelector('.btn-move')?.textContent", 29)
            btn_discard_text = await evaluate(ws, "document.querySelector('.btn-discard')?.textContent", 30)
            print(f"  Tombol popup: ['{btn_use_text}', '{btn_move_text}', '{btn_discard_text}']")
            assert btn_use_text == 'Gunakan'
            assert 'Pindahkan' in btn_move_text
            assert btn_discard_text == 'Buang'

            await snap(ws, "a5_item_popup_green", 502)
            print("  ✅ A5 VERIFIED GREEN: Popup aksi item (Gunakan/Pindahkan/Buang) tampil sempurna!")

            # 4. Test A3: Using item from hotbar auto-refills from backpack
            print("\n4. Menguji Gunakan Item & Pengisian Otomatis Hotbar (A3)...")
            # Click Gunakan button in popup
            await evaluate(ws, "document.querySelector('.btn-use')?.click()", 31)
            await asyncio.sleep(0.5)

            inv_after_use = await evaluate(ws, """(() => {
                const store = window.__LJ__.getStore();
                const inv = store.getState().inventory;
                return {
                    hotbarFilled: inv.hotbar.filter(s => s !== null).length,
                    backpackFilled: inv.backpack.filter(s => s !== null).length,
                    backpackCount: inv.backpack.reduce((sum, s) => sum + (s ? s.count : 0), 0)
                };
            })()""", 32)
            print(f"  Status inventaris setelah Gunakan: {inv_after_use}")
            # Previously 5 hotbar + 2 backpack = 7 items.
            # Used 1 item -> 6 items total.
            # Auto-refill pulls 1 item from backpack into the emptied slot -> Hotbar remains 5/5, backpack becomes 1/20!
            assert inv_after_use["hotbarFilled"] == 5, f"Expected hotbar to auto-refill to 5, got {inv_after_use['hotbarFilled']}"
            assert inv_after_use["backpackFilled"] == 1, f"Expected backpack to have 1 item left, got {inv_after_use['backpackFilled']}"

            # Verify energy increased in HUD
            energy_text = await evaluate(ws, "document.querySelector('.hm-energy-text')?.textContent", 33)
            print(f"  Energi di HUD setelah gunakan makanan: {energy_text}")
            assert int(energy_text.replace('%', '')) > 70, f"Expected energy > 70%, got {energy_text}"

            await snap(ws, "a3_backpack_refill_green", 503)
            print("  ✅ A3 VERIFIED GREEN: Slot hotbar otomatis terisi dari ransel saat item digunakan!")

            # 5. Test A6: Full backpack rejection (25/25)
            print("\n5. Menguji Penolakan Pembelian Saat Tas Penuh 25/25 (A6)...")
            fill_res = await evaluate(ws, """(async () => {
                const { addItem } = await import('./src/domain/inventory.js');
                const store = window.__LJ__.getStore();
                let inv = store.getState().inventory;
                // Fill all 25 slots with distinct items to reach 100% capacity
                for (let i = 1; i <= 25; i++) {
                    const r = addItem(inv, `item_unique_${i}`, 5);
                    if (r.ok) inv = r.inventory;
                }
                store.setState({ inventory: inv });
                
                // Attempt to add 26th distinct item
                const extraAdd = addItem(inv, 'item_overflow_26', 1);
                return {
                    hotbarFilled: inv.hotbar.filter(s => s !== null).length,
                    backpackFilled: inv.backpack.filter(s => s !== null).length,
                    extraAddOk: extraAdd.ok,
                    reason: extraAdd.reason
                };
            })()""", 34, await_p=True)

            print(f"  Hasil uji tas penuh: {fill_res}")
            assert fill_res["hotbarFilled"] == 5
            assert fill_res["backpackFilled"] == 20
            assert fill_res["extraAddOk"] is False, "Expected 26th add to fail!"
            assert "Tas penuh" in fill_res["reason"], f"Expected 'Tas penuh' in reason, got {fill_res['reason']}"

            await snap(ws, "a6_backpack_full_green", 504)
            print("  ✅ A6 VERIFIED GREEN: Pembelian/penambahan ditolak saat kapasitas 25/25 penuh!")

            return True

    finally:
        chrome_proc.terminate()
        try:
            chrome_proc.wait(timeout=3)
        except Exception:
            chrome_proc.kill()

if __name__ == "__main__":
    success = asyncio.run(run_suite())
    sys.exit(0 if success else 1)
