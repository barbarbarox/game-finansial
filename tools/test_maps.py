#!/usr/bin/env python3
"""
test_maps.py — Automated verification of Rule 70 (Interior Maps & Buildings):
1. Verifies tests/map-check.html (all 7 maps pass JSON, bounds, colliders, reciprocal doors, and BFS reachability)
2. Connects to live gameplay (index.html?debug=1)
3. Teleports to all 7 maps and captures screenshots:
   - home (kamar pemain & rumah)
   - town_hub (overworld)
   - school (sekolah & kelas & kantin)
   - minimarket
   - toko_kosmetik
   - spbu
   - game_center
4. Verifies physical door transition hub <-> interior
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

CDP_PORT = 9226
HTTP_PORT = 3843
SCREENSHOT_DIR = "/home/abarox/Desktop/prototipe web statis game/game/tests/screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

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
        print(f"[JS Error] msg_id {msg_id}:", res["result"]["exceptionDetails"])
    return res.get("result", {}).get("result", {}).get("value")

async def capture_screenshot(ws, filepath, msg_id=500):
    res = await send_cdp(ws, "Page.captureScreenshot", {"format": "png"}, msg_id)
    data = res.get("result", {}).get("data")
    if data:
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(data))
        print(f"  [Screenshot] Saved -> {filepath}")
        return True
    return False

async def get_ws_url(target_substr=""):
    for _ in range(15):
        try:
            req = urllib.request.urlopen(f"http://localhost:{CDP_PORT}/json", timeout=1)
            tabs = json.loads(req.read().decode())
            for tab in tabs:
                if target_substr in tab.get("url", ""):
                    return tab.get("webSocketDebuggerUrl")
            if tabs and not target_substr:
                return tabs[0].get("webSocketDebuggerUrl")
        except Exception:
            pass
        await asyncio.sleep(0.5)
    return None

async def run_suite():
    print("==================================================")
    print("  TEST SUITE: Life Journey Interior Maps (Rule 70)")
    print("==================================================")

    chrome_proc = subprocess.Popen([
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1200,800",
        f"--remote-debugging-port={CDP_PORT}",
        f"http://localhost:{HTTP_PORT}/tests/map-check.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        await asyncio.sleep(1.5)
        ws_url = await get_ws_url("map-check.html")
        if not ws_url:
            print("[FAIL] Tidak dapat terhubung ke Chrome CDP untuk map-check.html")
            return False

        async with websockets.connect(ws_url) as ws:
            await send_cdp(ws, "Page.enable", {}, 1)
            await asyncio.sleep(1.5)

            # 1. Verify tests/map-check.html (wait until finished)
            summary_text = ""
            summary_class = ""
            for _ in range(20):
                summary_text = await evaluate_js(ws, "document.getElementById('summary')?.textContent", 10)
                summary_class = await evaluate_js(ws, "document.getElementById('summary')?.className", 11)
                if summary_class and "summary-" in str(summary_class):
                    break
                await asyncio.sleep(0.3)

            print(f"1. Map-Check BFS & Verifikasi Peta:\n   Hasil: {summary_text} (class: {summary_class})")
            if "summary-fail" in str(summary_class) or not summary_class:
                # Print cards to see details
                cards = await evaluate_js(ws, "Array.from(document.querySelectorAll('.map-card')).map(c => c.textContent).join('\\n')", 12)
                print("   Detail Pengujian:\n", cards)

            assert "summary-pass" in str(summary_class), f"Map check failed: {summary_text}"

            # 2. Navigate to live game
            await send_cdp(ws, "Page.navigate", {"url": f"http://localhost:{HTTP_PORT}/index.html?debug=1"}, 20)
            await asyncio.sleep(2.0)

            # Start game if in MainMenu
            current_scene = await evaluate_js(ws, "window.__GAME__?.scene?.getScenes(true)?.[0]?.scene?.key", 30)
            print(f"2. Live Game Loaded. Active Scene: {current_scene}")

            if current_scene == "MainMenu":
                await evaluate_js(ws, """
                    (() => {
                        const game = window.__GAME__;
                        const scene = game.scene.getScene('MainMenu');
                        scene.scene.start('CharacterCreate');
                    })()
                """, 31)
                await asyncio.sleep(1.0)
                await evaluate_js(ws, """
                    (() => {
                        const form = document.querySelector('.charcreate-form');
                        if (form) {
                            const inputs = form.querySelectorAll('input');
                            if (inputs[0]) inputs[0].value = 'Budi';
                            if (inputs[1]) inputs[1].value = 'Ayah';
                            if (inputs[2]) inputs[2].value = 'Ibu';
                            form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
                        }
                    })()
                """, 32)
                await asyncio.sleep(2.0)

            world_scene = await evaluate_js(ws, "window.__GAME__?.scene?.getScenes(true)?.[0]?.scene?.key", 40)
            assert world_scene == "World", f"Gagal masuk ke scene World: {world_scene}"

            # 3. Teleport & screenshot all 7 maps
            maps_to_test = [
                ("home", "kamar_tidur", "live_map_home.png"),
                ("town_hub", "default", "live_map_town_hub.png"),
                ("school", "default", "live_map_school.png"),
                ("minimarket", "default", "live_map_minimarket.png"),
                ("toko_kosmetik", "default", "live_map_toko_kosmetik.png"),
                ("spbu", "default", "live_map_spbu.png"),
                ("game_center", "default", "live_map_game_center.png")
            ]

            print("3. Teleportasi & Tangkapan Layar Seluruh 7 Peta:")
            for map_id, spawn, shot_name in maps_to_test:
                print(f"   - Teleportasi ke peta '{map_id}'...")
                await evaluate_js(ws, f"window.__LJ__.teleportToMap('{map_id}', '{spawn}')", 100)
                await asyncio.sleep(0.6)

                active_map = await evaluate_js(ws, "window.__LJ__.getMapManager()?.currentMapId", 101)
                assert active_map == map_id, f"Gagal teleport ke {map_id}, active: {active_map}"

                shot_path = os.path.join(SCREENSHOT_DIR, shot_name)
                await capture_screenshot(ws, shot_path, 110)

            # 4. Test physical door transition: Hub -> School -> Hub
            print("4. Pengujian Transisi Timbal-Balik Pintu (Hub <-> School):")
            await evaluate_js(ws, "window.__LJ__.teleportToMap('town_hub')", 200)
            await asyncio.sleep(0.5)

            # Advance clock to 08:00 (jam sekolah buka: 07:00 - 15:00)
            curr_min = await evaluate_js(ws, "window.__LJ__.getTime().minuteOfDay", 201)
            target_min = 8 * 60
            diff = (target_min - curr_min) % 1440
            if diff > 0:
                await evaluate_js(ws, f"window.__LJ__.advanceTime({diff}, 'school_hours')", 202)
                await asyncio.sleep(0.3)

            await evaluate_js(ws, "window.__LJ__.teleportTo(10, 8.5)", 203)
            await asyncio.sleep(0.3)

            # Interact with school door
            await evaluate_js(ws, """
                (() => {
                    const scene = window.__LJ__.scene;
                    const door = scene._interactables?.find(i => i.id === 'int_sekolah');
                    if (door) scene._openInteraction(door);
                })()
            """, 204)
            await asyncio.sleep(1.2) # wait for fade

            current_map_after_enter = await evaluate_js(ws, "window.__LJ__.getMapManager()?.currentMapId", 205)
            print(f"   Setelah interaksi pintu sekolah pada 08:00: Map='{current_map_after_enter}'")
            assert current_map_after_enter == "school", f"Gagal masuk ke sekolah: {current_map_after_enter}"

            # Interact with exit door to return to Hub
            await evaluate_js(ws, """
                (() => {
                    const scene = window.__LJ__.scene;
                    const exit = scene._interactables?.find(i => i.id === 'exit_to_hub');
                    if (exit) scene._openInteraction(exit);
                })()
            """, 206)
            await asyncio.sleep(1.2)

            current_map_after_exit = await evaluate_js(ws, "window.__LJ__.getMapManager()?.currentMapId", 207)
            print(f"   Setelah keluar pintu sekolah: Map='{current_map_after_exit}'")
            assert current_map_after_exit == "town_hub", f"Gagal kembali ke hub: {current_map_after_exit}"
            print("   [LULUS] Transisi timbal balik pintu berhasil mulus!")

            print("==================================================")
            print("  GERBANG E2 LULUS 100% — SEMUA PETA & FITUR VALID")
            print("==================================================")
            return True

    finally:
        chrome_proc.terminate()
        try:
            chrome_proc.wait(timeout=2)
        except Exception:
            chrome_proc.kill()

if __name__ == "__main__":
    success = asyncio.run(run_suite())
    sys.exit(0 if success else 1)
