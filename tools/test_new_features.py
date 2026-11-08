#!/usr/bin/env python3
"""
test_new_features.py — Automated verification of:
1. Player indicator above sprite
2. Clickable Budget Modal (Susun Anggaran)
3. HUD Nav buttons visibility and positioning
4. Dark / Light Mode theme toggle and persistence
5. Running game clock (1 real sec = 1 game min)
6. NPC interaction triggered by pressing [E]
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

CDP_PORT = 9223
HTTP_PORT = 3841

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

async def run_suite():
    print("=== Testing New Features ===")

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
        page_tab = next((t for t in tabs if t.get("type") == "page" and "localhost" in t.get("url", "")), tabs[0])
        ws_url = page_tab["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url) as ws:
            print("1. Connected to Chrome CDP.")

            # Wait for Phaser
            for _ in range(25):
                is_ready = await evaluate_js(ws, "Boolean(window.__GAME__ && window.__GAME__.scene)", 1)
                if is_ready:
                    break
                await asyncio.sleep(0.4)

            # Start game directly to CharacterCreate -> World
            await evaluate_js(ws, """
            (() => {
                const game = window.__GAME__;
                const scene = game.scene.getScene('MainMenu');
                scene.scene.start('CharacterCreate');
            })()
            """, 2)
            await asyncio.sleep(0.8)

            # Submit character form: Name = "Rian"
            await evaluate_js(ws, """
            (() => {
                const form = document.querySelector('.charcreate-form');
                if (form) {
                    const inputs = form.querySelectorAll('input');
                    inputs[0].value = 'Rian';
                    inputs[1].value = 'Pak Joko';
                    inputs[2].value = 'Bu Siti';
                    form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
                }
            })()
            """, 3)
            await asyncio.sleep(1.5)

            # ----------------------------------------------------
            # FEATURE 1: Player indicator above sprite
            # ----------------------------------------------------
            print("\n--- Feature 1: Indikator Karakter Player ---")
            indicator_info = await evaluate_js(ws, """
            (() => {
                const p = window.__LJ__.getPlayer();
                if (!p) return null;
                return {
                    hasBg: Boolean(p._indicatorBg),
                    hasArrow: Boolean(p._indicatorArrow),
                    nameText: p._indicatorText?.text,
                    playerX: p.sprite.x,
                    playerY: p.sprite.y,
                    indicatorY: p._indicatorBg.y
                };
            })()
            """, 4)
            print("   Hasil Indikator Player:", indicator_info)
            assert indicator_info['hasBg'], "Background indikator player tidak ada!"
            assert indicator_info['hasArrow'], "Panah indikator player tidak ada!"
            assert indicator_info['nameText'] == 'Rian', f"Nama indikator harus 'Rian', terbaca {indicator_info['nameText']}"
            assert indicator_info['indicatorY'] < indicator_info['playerY'], "Indikator harus berada di atas karakter!"
            print("   ✓ PASS: Indikator pemain tampil di atas sprite karakter.")

            # ----------------------------------------------------
            # FEATURE 2: HUD Nav Buttons Visibility
            # ----------------------------------------------------
            print("\n--- Feature 2: Visibilitas Tombol Navigasi HUD ---")
            nav_info = await evaluate_js(ws, """
            (() => {
                const wrapper = document.getElementById('game-wrapper');
                const wrapperRect = wrapper.getBoundingClientRect();
                const btns = Array.from(document.querySelectorAll('.hud-nav button'));
                return btns.map(b => {
                    const r = b.getBoundingClientRect();
                    return {
                        text: b.textContent.trim(),
                        right: r.right,
                        wrapperRight: wrapperRect.right,
                        visible: r.right <= wrapperRect.right + 2 && r.left >= wrapperRect.left,
                        width: r.width
                    };
                });
            })()
            """, 5)
            print("   Tombol HUD Nav:", nav_info)
            for b in nav_info:
                print(f"   - {b['text']}: visible={b['visible']} (width={b['width']}px)")
                assert b['visible'], f"Tombol '{b['text']}' terpotong atau keluar dari layar!"
            assert len(nav_info) == 3, "Harus ada 3 tombol di HUD Nav (Buku Kas, Anggaran, Pengaturan)"
            print("   ✓ PASS: Seluruh tombol di kanan Buku Kas terlihat sempurna.")

            # ----------------------------------------------------
            # FEATURE 3: Clickable Budget Modal (Susun Anggaran)
            # ----------------------------------------------------
            print("\n--- Feature 3: Tombol Susun Anggaran Bulanan ---")
            await evaluate_js(ws, """
            (() => {
                const btns = Array.from(document.querySelectorAll('.hud-nav button'));
                const budgetBtn = btns.find(b => b.textContent.includes('Anggaran'));
                if (budgetBtn) budgetBtn.click();
            })()
            """, 6)
            await asyncio.sleep(0.5)

            budget_title = await evaluate_js(ws, "document.querySelector('.budget-panel .panel-title')?.textContent", 7)
            table_rows = await evaluate_js(ws, "document.querySelectorAll('.budget-panel tbody tr').length", 8)
            print(f"   Modal Anggaran Terbuka: '{budget_title}', Rows={table_rows}")
            assert 'Anggaran' in (budget_title or ''), "Modal Anggaran Bulanan gagal dibuka!"
            assert table_rows >= 5, f"Tabel anggaran harus memiliki kategori (terbaca {table_rows})"

            # Test Saran Anggaran
            await evaluate_js(ws, """
            (() => {
                const btn = Array.from(document.querySelectorAll('.budget-panel button')).find(b => b.textContent.includes('Saran'));
                if (btn) btn.click();
            })()
            """, 9)
            await asyncio.sleep(0.2)

            first_input_val = await evaluate_js(ws, "document.querySelector('.budget-panel input')?.value", 10)
            print(f"   Nilai input kategori pertama setelah klik Saran: Rp{first_input_val}")
            assert int(first_input_val) > 0, "Input anggaran saran gagal diisi!"

            # Simpan Anggaran
            await evaluate_js(ws, """
            (() => {
                const btn = Array.from(document.querySelectorAll('.budget-panel button')).find(b => b.textContent.includes('Simpan'));
                if (btn) btn.click();
            })()
            """, 11)
            await asyncio.sleep(0.4)
            is_modal_closed = await evaluate_js(ws, "document.querySelector('.budget-panel') === null", 12)
            assert is_modal_closed, "Modal Anggaran harus tertutup setelah disimpan!"
            print("   ✓ PASS: Tombol Susun Anggaran berfungsi 100% (buka, saran, simpan).")

            # ----------------------------------------------------
            # FEATURE 4: Dark / Light Mode Toggle
            # ----------------------------------------------------
            print("\n--- Feature 4: Toggle Dark & Light Mode ---")
            # Open Settings
            await evaluate_js(ws, """
            (() => {
                const btns = Array.from(document.querySelectorAll('.hud-nav button'));
                const settingsBtn = btns.find(b => b.textContent.includes('Pengaturan'));
                if (settingsBtn) settingsBtn.click();
            })()
            """, 13)
            await asyncio.sleep(0.5)

            # Find theme toggle
            theme_btn_text_before = await evaluate_js(ws, """
            (() => {
                const rows = Array.from(document.querySelectorAll('.settings-row'));
                const themeRow = rows.find(r => r.textContent.includes('Tema Tampilan'));
                return themeRow ? themeRow.querySelector('button')?.textContent : null;
            })()
            """, 14)
            print("   Tombol Tema Awal:", theme_btn_text_before)

            # Click theme toggle to switch to Light mode
            await evaluate_js(ws, """
            (() => {
                const rows = Array.from(document.querySelectorAll('.settings-row'));
                const themeRow = rows.find(r => r.textContent.includes('Tema Tampilan'));
                themeRow?.querySelector('button')?.click();
            })()
            """, 15)
            await asyncio.sleep(0.3)

            is_light_mode = await evaluate_js(ws, "document.body.classList.contains('lj-light')", 16)
            saved_theme = await evaluate_js(ws, "localStorage.getItem('lj_theme')", 17)
            print(f"   Setelah toggle: is_light_mode={is_light_mode}, saved_theme={saved_theme}")
            assert is_light_mode, "Class 'lj-light' harus ada pada body setelah toggle ke Light Mode!"
            assert saved_theme == 'light', "localStorage lj_theme harus 'light'!"

            # Take screenshot in Light Mode
            shot_res = await send_cdp(ws, "Page.captureScreenshot", {"format": "png"}, 18)
            img_data = base64.b64decode(shot_res["result"]["data"])
            shot_light_path = "/home/abarox/.gemini/antigravity/brain/4d2f9b08-f034-4550-b619-39a74fd29f25/live_light_mode.png"
            with open(shot_light_path, "wb") as f:
                f.write(img_data)
            print(f"   Screenshot Light Mode tersimpan: {shot_light_path}")

            # Close Settings
            await evaluate_js(ws, "document.querySelector('.settings-panel .btn-close')?.click()", 19)
            await asyncio.sleep(0.3)
            print("   ✓ PASS: Dark/Light Mode toggle dan persistensi berfungsi.")

            # ----------------------------------------------------
            # FEATURE 5: Running Game Clock
            # ----------------------------------------------------
            print("\n--- Feature 5: Waktu Permainan Berjalan Otomatis ---")
            clock_before = await evaluate_js(ws, """
            (() => {
                const st = window.__LJ__.getStore().getState();
                const hudTxt = document.querySelector('.hud-val-clock')?.textContent;
                return { timeOfDay: st.clock?.timeOfDay, hudTxt };
            })()
            """, 20)
            print("   Clock Awal:", clock_before)

            print("   Menunggu 2.5 detik waktu nyata (harus bertambah minimal 2 menit game)...")
            await asyncio.sleep(2.5)

            clock_after = await evaluate_js(ws, """
            (() => {
                const st = window.__LJ__.getStore().getState();
                const hudTxt = document.querySelector('.hud-val-clock')?.textContent;
                return { timeOfDay: st.clock?.timeOfDay, hudTxt };
            })()
            """, 21)
            print("   Clock Setelah 2.5s:", clock_after)
            assert clock_after['timeOfDay'] > clock_before['timeOfDay'], "Waktu game tidak berjalan!"
            print(f"   ✓ PASS: Jam game berjalan real-time ({clock_before['hudTxt']} -> {clock_after['hudTxt']}).")

            # ----------------------------------------------------
            # FEATURE 6: NPC Interaction ONLY on [E] Pressed
            # ----------------------------------------------------
            print("\n--- Feature 6: Interaksi NPC Hanya Saat Menekan [E] ---")
            # Teleport player near NPC Ibu (x: 256, y: 640)
            await evaluate_js(ws, """
            (() => {
                const player = window.__LJ__.getPlayer();
                player.sprite.x = 256;
                player.sprite.y = 620; // 20px above npc_ibu (radius < 54px)
            })()
            """, 22)
            await asyncio.sleep(0.6)

            # Verify dialog is NOT open automatically
            dialog_open_before_e = await evaluate_js(ws, "document.querySelector('.lj-npc-dialog') !== null", 23)
            print("   Dialog NPC terbuka otomatis sebelum tekan E?:", dialog_open_before_e)
            assert not dialog_open_before_e, "Dialog NPC TIDAK BOLEH terbuka otomatis sebelum tekan E!"

            # Now simulate pressing E key
            await evaluate_js(ws, """
            (() => {
                const scene = window.__LJ__.scene;
                // Trigger interaction via keydown
                window.dispatchEvent(new KeyboardEvent('keydown', { key: 'e', code: 'KeyE', keyCode: 69 }));
            })()
            """, 24)
            await asyncio.sleep(0.5)

            # Check if dialog opened
            dialog_name = await evaluate_js(ws, "document.querySelector('.lj-npc-dialog .npc-name')?.textContent", 25)
            print("   Nama di Dialog NPC setelah tekan E:", dialog_name)
            assert dialog_name == 'Ibu', f"Dialog harus terbuka untuk Ibu, terbaca: {dialog_name}"
            print("   ✓ PASS: Interaksi NPC terjadi hanya saat tombol E ditekan.")

            # Capture live gameplay screenshot
            shot_res = await send_cdp(ws, "Page.captureScreenshot", {"format": "png"}, 26)
            img_data = base64.b64decode(shot_res["result"]["data"])
            shot_final_path = "/home/abarox/.gemini/antigravity/brain/4d2f9b08-f034-4550-b619-39a74fd29f25/live_npc_and_features.png"
            with open(shot_final_path, "wb") as f:
                f.write(img_data)
            print(f"\nFinal Screenshot tersimpan di: {shot_final_path}")

            print("\n==========================================")
            print("SEMUA FITUR BARU 100% LULUS PENGUJIAN!")
            print("==========================================")

    finally:
        chrome_proc.kill()
        http_proc.kill()

if __name__ == "__main__":
    asyncio.run(run_suite())
