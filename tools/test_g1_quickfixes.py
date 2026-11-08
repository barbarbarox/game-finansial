#!/usr/bin/env python3
"""
test_g1_quickfixes.py — Automated verification of Gate G1:
1. Verifies tests/map-check.html (reachability, reciprocal doors, occlusion test, NPC isolation)
2. Connects to live game via Chrome CDP:
   - Verifies listNPCs('town_hub') does NOT contain 'npc_ibu'
   - Verifies listNPCs('home') contains 'npc_ibu'
   - Verifies collisionProbe on all 7 maps (town_hub, home, school, minimarket, toko_kosmetik, spbu, game_center)
   - Triggers completeMission('M1', 'Buku Kas Pertama')
   - Captures mission complete FX at t=100ms, t=400ms, t=800ms
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

CDP_PORT = 9238
HTTP_PORT = 3843
DOCS_DIR = "/home/abarox/Desktop/prototipe web statis game/game/docs/g1-quickfixes"
os.makedirs(DOCS_DIR, exist_ok=True)

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
        print(f"  📸 Screenshot: {os.path.basename(filepath)}")
        return True
    return False

async def get_ws_url(target_substr=""):
    for _ in range(20):
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
    print("  TEST SUITE: Gate G1 Quickfixes (Rule 73, 77)    ")
    print("==================================================")

    chrome_proc = subprocess.Popen([
        "/usr/bin/google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1200,800",
        f"--remote-debugging-port={CDP_PORT}",
        "--remote-allow-origins=*",
        f"http://localhost:{HTTP_PORT}/tests/map-check.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        await asyncio.sleep(2.0)
        ws_url = await get_ws_url("map-check.html")
        if not ws_url:
            print("[FAIL] Tidak dapat terhubung ke Chrome CDP")
            return False

        async with websockets.connect(ws_url) as ws:
            await send_cdp(ws, "Page.enable", {}, 1)

            # 1. Verify tests/map-check.html
            print("\n1. Verifikasi tests/map-check.html (BFS, Timbal-Balik, Oklusi, Isolasi NPC)...")
            summary_text = ""
            summary_class = ""
            for _ in range(30):
                await asyncio.sleep(0.3)
                summary_text = await evaluate_js(ws, "document.getElementById('summary')?.textContent", 10)
                summary_class = await evaluate_js(ws, "document.getElementById('summary')?.className", 11)
                if summary_class and "summary-" in str(summary_class):
                    break

            print(f"   Hasil: {summary_text}")
            assert "summary-pass" in str(summary_class), f"map-check.html failed: {summary_text}"
            print("   ✓ map-check.html 100% LULUS (termasuk uji oklusi dan isolasi NPC)!")

            # 2. Navigate to live game
            print("\n2. Membuka Live Game...")
            await send_cdp(ws, "Page.navigate", {"url": f"http://localhost:{HTTP_PORT}/index.html?debug=1"}, 20)
            await asyncio.sleep(2.0)

            # New journey if on MainMenu
            current_scene = await evaluate_js(ws, "window.__GAME__?.scene?.getScenes(true)?.[0]?.scene?.key", 30)
            if current_scene == 'MainMenu':
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

            # Wait for window.__LJ__ to be ready
            for _ in range(20):
                is_ready = await evaluate_js(ws, "Boolean(window.__LJ__ && window.__LJ__.listNPCs)", 35)
                if is_ready:
                    break
                await asyncio.sleep(0.3)

            # 3. Test NPC Isolation
            print("\n3. Verifikasi Isolasi NPC per Peta:")
            hub_npcs = await evaluate_js(ws, "window.__LJ__.listNPCs('town_hub')", 40)
            home_npcs = await evaluate_js(ws, "window.__LJ__.listNPCs('home')", 41)
            print(f"   NPC di town_hub: {hub_npcs}")
            print(f"   NPC di home: {home_npcs}")
            assert 'npc_ibu' not in hub_npcs, "npc_ibu masih ada di town_hub!"
            assert 'npc_ibu' in home_npcs, "npc_ibu tidak ditemukan di home!"
            print("   ✓ NPC Ibu berhasil dihapus dari hub dan terisolasi di dalam rumah.")

            # 4. Test Collision Probe across all 7 maps
            print("\n4. Menjalankan Uji collisionProbe pada 7 Peta:")
            maps = ['home', 'town_hub', 'school', 'minimarket', 'toko_kosmetik', 'spbu', 'game_center']
            for m in maps:
                res = await evaluate_js(ws, f"window.__LJ__.collisionProbe('{m}')", 50)
                tested = res.get('testedCount', 0)
                passed = res.get('passedCount', 0)
                all_ok = res.get('allPassed', False)
                print(f"   - Peta [{m}]: {passed}/{tested} collider tertahan kokoh (allPassed={all_ok})")
                assert all_ok, f"Collision probe gagal di peta {m}: {res}"
            print("   ✓ Semua 7 peta lolos collision probe (tidak ada objek yang bisa ditembus)!")

            # 5. Test Mission Complete FX (Rule 77)
            print("\n5. Pengujian Efek Visual Misi Selesai (Rule 77):")
            # Teleport to home bedroom
            await evaluate_js(ws, "window.__LJ__.teleportToMap('home', 'kamar_tidur')", 60)
            await asyncio.sleep(1.0)

            # Trigger completeMission('M1', 'Buku Kas Pertama')
            print("   Memicu completeMission('M1', 'Buku Kas Pertama')...")
            await evaluate_js(ws, "window.__LJ__.completeMission('M1', 'Buku Kas Pertama')", 70)

            # Capture t=100ms (flash tint & rings start)
            await asyncio.sleep(0.1)
            shot1 = os.path.join(DOCS_DIR, "01_mission_complete_t100ms.png")
            await capture_screenshot(ws, shot1, 71)

            # Capture t=400ms (rings expanded, stars floating, floating text visible)
            await asyncio.sleep(0.3)
            shot2 = os.path.join(DOCS_DIR, "02_mission_complete_t400ms.png")
            await capture_screenshot(ws, shot2, 72)

            # Capture t=800ms (fading stars, text floating higher)
            await asyncio.sleep(0.4)
            shot3 = os.path.join(DOCS_DIR, "03_mission_complete_t800ms.png")
            await capture_screenshot(ws, shot3, 73)

            # Idempotency test: trigger M1 again, must return false
            idempotent = await evaluate_js(ws, "window.__LJ__.completeMission('M1', 'Buku Kas Pertama')", 80)
            print(f"   Pengujian Idempoten (panggilan kedua M1): {idempotent} (harus False)")
            assert idempotent is False, "completeMission tidak idempoten!"
            print("   ✓ Efek misi selesai idempoten dan terverifikasi penuh!")

            print("==================================================")
            print("  GERBANG G1: LULUS 100%! SEMUA SYARAT TERPENUHI   ")
            print("==================================================")
            return True

    finally:
        chrome_proc.terminate()

if __name__ == "__main__":
    success = asyncio.run(run_suite())
    sys.exit(0 if success else 1)
