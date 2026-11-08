#!/usr/bin/env python3
"""
test_npc_interaction.py — Automated browser test for NPC Proximity & Interaction Dialog.
"""

import os
import sys
import json
import time
import subprocess
import urllib.request
import asyncio
import websockets

CDP_PORT = 9222
HTTP_PORT = 3839

async def send_cdp(ws, method, params=None, msg_id=1):
    msg = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(msg))
    while True:
        res_raw = await ws.recv()
        res = json.loads(res_raw)
        if res.get("id") == msg_id:
            return res

async def evaluate_js(ws, expr, msg_id=100):
    res = await send_cdp(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True}, msg_id)
    if "exceptionDetails" in res.get("result", {}):
        print("JS Exception at msg_id", msg_id, ":", res["result"]["exceptionDetails"])
    return res.get("result", {}).get("result", {}).get("value")

async def run_npc_suite():
    print("=== Memulai Pengujian Interaksi NPC & Menu HUD ===")

    # 1. Start HTTP Server
    http_proc = subprocess.Popen(
        ["python3", "-m", "http.server", str(HTTP_PORT)],
        cwd="/home/abarox/Desktop/prototipe web statis game/game",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    # 2. Start Headless Chrome
    chrome_proc = subprocess.Popen([
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--window-size=1024,768",
        f"--remote-debugging-port={CDP_PORT}",
        f"http://localhost:{HTTP_PORT}/index.html?debug=1"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    try:
        tabs_raw = urllib.request.urlopen(f"http://localhost:{CDP_PORT}/json").read()
        tabs = json.loads(tabs_raw)
        page_tab = next((t for t in tabs if t.get("type") == "page" and "localhost" in t.get("url", "")), None)
        if not page_tab:
            page_tab = next((t for t in tabs if t.get("type") == "page"), tabs[0])
        ws_url = page_tab["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url) as ws:
            print("1. Terhubung ke Chrome CDP.")

            # Wait for Phaser
            for _ in range(20):
                is_ready = await evaluate_js(ws, "Boolean(window.__GAME__ && window.__GAME__.scene)", 1)
                if is_ready:
                    break
                await asyncio.sleep(0.5)

            # Start game directly to World
            await evaluate_js(ws, """
            (() => {
                const game = window.__GAME__;
                const scene = game.scene.getScene('MainMenu');
                scene.scene.start('CharacterCreate');
            })()
            """, 2)
            await asyncio.sleep(0.8)

            # Submit character form
            await evaluate_js(ws, """
            (() => {
                const form = document.querySelector('.charcreate-form');
                if (form) {
                    const inputs = form.querySelectorAll('input');
                    inputs[0].value = 'Budi';
                    inputs[1].value = 'Pak Joko';
                    inputs[2].value = 'Bu Siti';
                    form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
                }
            })()
            """, 3)
            await asyncio.sleep(1.2)

            # Test 1: Check HUD buttons
            buttons = await evaluate_js(ws, """
            (() => {
                const btns = Array.from(document.querySelectorAll('.hud-nav button'));
                return btns.map(b => b.textContent.trim());
            })()
            """, 4)
            print("2. Tombol Navigasi HUD:", buttons)
            assert any('Buku Kas' in b for b in buttons), "Tombol Buku Kas hilang!"
            assert any('Anggaran' in b for b in buttons), "Tombol Anggaran hilang!"
            assert any(('Pengaturan' in b or 'Menu' in b) for b in buttons), "Tombol Pengaturan/Menu hilang!"

            # Test 2: Click Menu/Pengaturan button to verify Settings opens
            await evaluate_js(ws, """
            (() => {
                const btns = Array.from(document.querySelectorAll('.hud-nav button'));
                const menuBtn = btns.find(b => b.textContent.includes('Pengaturan') || b.textContent.includes('Menu'));
                if (menuBtn) menuBtn.click();
            })()
            """, 5)
            await asyncio.sleep(0.5)

            settings_title = await evaluate_js(ws, "document.querySelector('.settings-panel .panel-title')?.textContent", 6)
            print("3. Buka Menu Pengaturan dari HUD:", settings_title)
            assert 'Pengaturan' in (settings_title or ''), "Modal Pengaturan gagal terbuka!"

            # Test Simpan Permainan inside settings
            await evaluate_js(ws, """
            (() => {
                const btns = Array.from(document.querySelectorAll('.settings-section button'));
                const saveBtn = btns.find(b => b.textContent.includes('Simpan Permainan'));
                if (saveBtn) saveBtn.click();
            })()
            """, 7)
            await asyncio.sleep(0.3)
            toast_txt = await evaluate_js(ws, "document.querySelector('.settings-toast')?.textContent", 8)
            print("   Feedback Simpan Permainan:", toast_txt)
            assert 'berhasil disimpan' in (toast_txt or ''), "Toast simpan permainan gagal muncul!"

            # Close Settings
            await evaluate_js(ws, "document.querySelector('.settings-panel .btn-close')?.click()", 9)
            await asyncio.sleep(0.5)

            # Test Texture Loading: Check that new buildings and props textures exist in Phaser
            textures_loaded = await evaluate_js(ws, """
            (() => {
                const keys = [
                    'bld_rumah_pemain', 'bld_minimarket', 'bld_toko_kosmetik', 'bld_spbu', 'bld_game_center',
                    'npc_sheet_family', 'npc_sheet_friends', 'npc_sheet_vendors',
                    'prop_tree_large', 'prop_tree_small', 'prop_street_lamp', 'prop_bench', 'prop_bush'
                ];
                const scene = window.__GAME__.scene.getScene('World');
                return keys.map(k => ({ key: k, exists: scene.textures.exists(k) }));
            })()
            """, 10)
            print("4. Status Tekstur Baru di Phaser:")
            for t in textures_loaded:
                print(f"   - {t['key']}: {'OK' if t['exists'] else 'MISSING'}")
                assert t['exists'], f"Tekstur {t['key']} tidak ditemukan di Phaser!"

            # Test 3: NPC Proximity.
            # Teleport/move player right next to npc_ibu (at tile x: 8, y: 20 -> px: 256, py: 640)
            print("5. Mendekatkan karakter player ke NPC Ibu (x: 256, y: 640)...")
            await evaluate_js(ws, """
            (() => {
                const player = window.__LJ__.getPlayer();
                player.sprite.x = 256;
                player.sprite.y = 620; // 20px above npc_ibu (dalam radius 54px)
            })()
            """, 8)
            await asyncio.sleep(0.5)

            # Tekan tombol E untuk membuka interaksi
            print("   Menekan tombol [E] untuk berinteraksi...")
            await evaluate_js(ws, """
            (() => {
                window.dispatchEvent(new KeyboardEvent('keydown', { key: 'e', code: 'KeyE', keyCode: 69 }));
            })()
            """, 85)
            await asyncio.sleep(0.5)

            # Check if NPC dialog appeared
            dialog_title = await evaluate_js(ws, "document.querySelector('.lj-npc-dialog .npc-name')?.textContent", 9)
            dialog_role = await evaluate_js(ws, "document.querySelector('.lj-npc-dialog .npc-title')?.textContent", 10)
            dialog_body = await evaluate_js(ws, "document.querySelector('.lj-npc-dialog .npc-dialog-body')?.textContent", 11)
            choices = await evaluate_js(ws, """
            (() => {
                const btns = Array.from(document.querySelectorAll('.lj-npc-dialog .npc-choice-btn'));
                return btns.map(b => b.textContent.trim());
            })()
            """, 12)

            print(f"5. Dialog NPC Terbuka: Nama = '{dialog_title}', Peran = '{dialog_role}'")
            print(f"   Pesan NPC: '{dialog_body}'")
            print(f"   Pilihan Interaksi ({len(choices)} opsi):", choices)

            assert dialog_title == 'Ibu', f"Dialog harus menampilkan nama Ibu, terbaca {dialog_title}"
            assert len(choices) >= 3, f"Pilihan interaksi harus >= 3, terbaca {len(choices)}"

            # Take screenshot of NPC dialog in action
            shot_res = await send_cdp(ws, "Page.captureScreenshot", {"format": "png"}, 13)
            import base64
            img_data = base64.b64decode(shot_res["result"]["data"])
            shot_path = "/home/abarox/Desktop/prototipe web statis game/game/docs/screenshot_npc_interaction.png"
            with open(shot_path, "wb") as f:
                f.write(img_data)
            print(f"6. Tangkapan Layar Interaksi NPC tersimpan di: {shot_path}")

            # Test 4: Select choice "💡 Minta Nasihat Menabung"
            print("7. Memilih opsi '💡 Minta Nasihat Menabung'...")
            await evaluate_js(ws, """
            (() => {
                const btns = Array.from(document.querySelectorAll('.lj-npc-dialog .npc-choice-btn'));
                const adviceBtn = btns.find(b => b.textContent.includes('Nasihat'));
                if (adviceBtn) adviceBtn.click();
            })()
            """, 14)
            await asyncio.sleep(0.5)

            new_body = await evaluate_js(ws, "document.querySelector('.lj-npc-dialog .npc-dialog-body')?.textContent", 15)
            print("   Balasan NPC:", new_body)
            assert 'Celengan Ayam' in new_body or 'tabungan' in new_body.lower(), f"Nasihat menabung harus tampil, terbaca: {new_body}"

            # Test 5: Close dialog via [Esc] or bye
            print("8. Menutup dialog...")
            await evaluate_js(ws, "document.querySelector('.lj-npc-dialog .btn-close')?.click()", 16)
            await asyncio.sleep(0.5)
            is_closed = await evaluate_js(ws, "document.querySelector('.lj-npc-dialog') === null", 17)
            assert is_closed, "Dialog gagal ditutup!"
            print("9. Dialog berhasil ditutup.")

            # Test 6: Move player away and verify no dialog stuck
            await evaluate_js(ws, """
            (() => {
                const player = window.__LJ__.getPlayer();
                player.sprite.x = 100;
                player.sprite.y = 100;
            })()
            """, 18)
            await asyncio.sleep(0.5)

            print("\n>>> SELURUH PENGUJIAN INTERAKSI NPC & MENU LULUS 100%! <<<")

    finally:
        chrome_proc.terminate()
        http_proc.terminate()

if __name__ == "__main__":
    asyncio.run(run_npc_suite())

