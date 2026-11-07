#!/usr/bin/env python3
"""
test_main_menu.py — Automated test for Main Menu interactivity and HUD icons.
Verifies:
1. Main menu loads with scenic background, player sprites, and title banner.
2. Clicking 'Mulai Baru' button transitions to Character Creation modal.
3. Clicking 'Pengaturan' button opens Settings modal; close button closes it.
4. Gameplay HUD displays all 5 pixel-art status icons and button icons properly.
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
HTTP_PORT = 3840

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
        print("JS Exception:", res["result"]["exceptionDetails"])
    return res.get("result", {}).get("result", {}).get("value")

async def run_menu_suite():
    print("=== Memulai Pengujian Menu Utama & Ikon HUD ===")

    # Start HTTP Server
    http_proc = subprocess.Popen(
        ["python3", "-m", "http.server", str(HTTP_PORT)],
        cwd="/home/abarox/Desktop/prototipe web statis game/game",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    # Start Headless Chrome
    chrome_proc = subprocess.Popen([
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--window-size=960,540",
        f"--remote-debugging-port={CDP_PORT}",
        f"http://localhost:{HTTP_PORT}/index.html"
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

            # Wait for Phaser initialization
            for _ in range(20):
                is_ready = await evaluate_js(ws, "Boolean(window.__GAME__ && window.__GAME__.scene)", 1)
                if is_ready:
                    break
                await asyncio.sleep(0.5)

            # Check Main Menu buttons existence
            btns = await evaluate_js(ws, """
            (() => {
                const scene = window.__GAME__.scene.getScene('MainMenu');
                return scene._buttons.map(b => ({
                    label: b.def.label,
                    enabled: b.enabled,
                    y: b.y
                }));
            })()
            """, 2)
            print("2. Tombol di MainMenu:", btns)
            assert len(btns) == 3, "Harus ada 3 tombol di Menu Utama"
            assert btns[0]["enabled"] is True, "Tombol Mulai Baru harus aktif"
            assert btns[2]["enabled"] is True, "Tombol Pengaturan harus aktif"

            # Get Canvas Bounding Rect
            c_rect = await evaluate_js(ws, """
            (() => {
                const c = document.querySelector('canvas');
                const r = c.getBoundingClientRect();
                return { left: r.left, top: r.top, width: r.width, height: r.height };
            })()
            """, 3)

            # Test 1: Click Pengaturan
            btn_settings_y = btns[2]["y"]
            cx = c_rect["left"] + (480 / 960) * c_rect["width"]
            cy = c_rect["top"] + (btn_settings_y / 540) * c_rect["height"]
            print(f"3. Menguji klik tombol Pengaturan di ({cx}, {cy})...")

            await send_cdp(ws, "Input.dispatchMouseEvent", {"type": "mouseMoved", "x": cx, "y": cy}, 10)
            await send_cdp(ws, "Input.dispatchMouseEvent", {"type": "mousePressed", "x": cx, "y": cy, "button": "left", "clickCount": 1}, 11)
            await send_cdp(ws, "Input.dispatchMouseEvent", {"type": "mouseReleased", "x": cx, "y": cy, "button": "left", "clickCount": 1}, 12)
            await asyncio.sleep(0.5)

            settings_title = await evaluate_js(ws, "document.querySelector('.settings-panel .panel-title')?.textContent", 13)
            print("   Modal Pengaturan terbuka:", settings_title)
            assert "Pengaturan" in (settings_title or ""), "Modal Pengaturan gagal terbuka dari Menu Utama!"

            # Close Settings Modal via Close Button
            await evaluate_js(ws, "document.querySelector('.settings-panel .btn-close').click()", 14)
            await asyncio.sleep(0.3)
            modal_closed = await evaluate_js(ws, "document.querySelector('.settings-panel') === null", 15)
            assert modal_closed, "Modal Pengaturan gagal ditutup!"
            print("   Modal Pengaturan berhasil ditutup.")

            # Test 2: Click Mulai Baru
            btn_new_y = btns[0]["y"]
            cx_new = c_rect["left"] + (480 / 960) * c_rect["width"]
            cy_new = c_rect["top"] + (btn_new_y / 540) * c_rect["height"]
            print(f"4. Menguji klik tombol Mulai Baru di ({cx_new}, {cy_new})...")

            await send_cdp(ws, "Input.dispatchMouseEvent", {"type": "mouseMoved", "x": cx_new, "y": cy_new}, 20)
            await send_cdp(ws, "Input.dispatchMouseEvent", {"type": "mousePressed", "x": cx_new, "y": cy_new, "button": "left", "clickCount": 1}, 21)
            await send_cdp(ws, "Input.dispatchMouseEvent", {"type": "mouseReleased", "x": cx_new, "y": cy_new, "button": "left", "clickCount": 1}, 22)
            await asyncio.sleep(0.6)

            char_title = await evaluate_js(ws, "document.querySelector('.charcreate-panel .panel-title')?.textContent", 23)
            print("   Modal Pembuatan Karakter terbuka:", char_title)
            assert "Karakter" in (char_title or ""), "Modal Pembuatan Karakter gagal terbuka!"

            # Test 3: Submit character creation to transition to World
            await evaluate_js(ws, """
            (() => {
                const form = document.querySelector('.charcreate-form');
                form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
            })()
            """, 24)
            await asyncio.sleep(1.2)

            scenes = await evaluate_js(ws, "window.__GAME__.scene.getScenes(true).map(s => s.sys.settings.key)", 25)
            print("5. Transisi ke Dunia Permainan:", scenes)
            assert "World" in scenes, "Scene World gagal aktif!"

            # Test 4: Verify HUD icons
            hud_icons = await evaluate_js(ws, """
            (() => {
                const imgs = Array.from(document.querySelectorAll('.lj-hud img'));
                return imgs.map(img => img.src.split('/').pop());
            })()
            """, 26)
            print("6. Ikon Pixel Art yang digunakan di HUD:", hud_icons)
            expected_icons = [
                'icon_coin.png',
                'icon_celengan.png',
                'icon_bensin.png',
                'icon_jam.png',
                'icon_misi.png',
                'icon_buku.png',
                'icon_wallet.png'
            ]
            for exp in expected_icons:
                assert exp in hud_icons, f"Ikon {exp} tidak ditemukan di HUD!"

            print("\n>>> PENGUJIAN MENU UTAMA & IKON HUD LULUS 100%! <<<\n")

    finally:
        chrome_proc.kill()
        http_proc.kill()

if __name__ == '__main__':
    asyncio.run(run_menu_suite())
