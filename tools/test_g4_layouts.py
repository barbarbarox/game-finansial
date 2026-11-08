#!/usr/bin/env python3
"""
test_g4_layouts.py — Automated verification of Gate G4 Slot-Based Layouts (Rule 73):
1. Runs tests/map-check.html via headless Chrome CDP and validates reachability.
2. Runs tests/layout-check.html and validates all 9 criteria (a–i) across all 7 maps.
3. Captures rendered canvas snapshots with collision overlays for all 7 maps.
4. Generates markdown validation summaries in docs/layouts/VALIDATION-<mapId>.md.
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

CDP_PORT = 9243
HTTP_PORT = 3843
DOCS_LAYOUTS_DIR = "/home/abarox/Desktop/prototipe web statis game/game/docs/layouts"
DOCS_G4_DIR = "/home/abarox/Desktop/prototipe web statis game/game/docs/g4-layouts"
os.makedirs(DOCS_LAYOUTS_DIR, exist_ok=True)
os.makedirs(DOCS_G4_DIR, exist_ok=True)

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

async def get_ws_url():
    for _ in range(20):
        try:
            req = urllib.request.urlopen(f"http://localhost:{CDP_PORT}/json", timeout=1)
            tabs = json.loads(req.read().decode())
            if tabs:
                return tabs[0].get("webSocketDebuggerUrl")
        except Exception:
            pass
        await asyncio.sleep(0.4)
    return None

async def run_suite():
    print("==================================================")
    print("  TEST SUITE: Gate G4 Slot Layouts (Rule 73)      ")
    print("==================================================")

    chrome_proc = subprocess.Popen([
        "/usr/bin/google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1200,900",
        f"--remote-debugging-port={CDP_PORT}",
        "--remote-allow-origins=*",
        f"http://localhost:{HTTP_PORT}/tests/layout-check.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    passed_all = True

    try:
        await asyncio.sleep(2.0)
        ws_url = await get_ws_url()
        if not ws_url:
            print("[FAIL] Tidak dapat terhubung ke Chrome CDP")
            return False

        async with websockets.connect(ws_url) as ws:
            await send_cdp(ws, "Page.enable", {}, 1)

            # 1. Run layout-check.html
            print("\n1. Menjalankan tests/layout-check.html...")
            await send_cdp(ws, "Page.navigate", {"url": f"http://localhost:{HTTP_PORT}/tests/layout-check.html"}, 10)
            await asyncio.sleep(2.0)

            # Wait for layout results
            results = None
            for _ in range(25):
                results = await evaluate_js(ws, "window.__LAYOUT_RESULTS__", 11)
                if results and len(results) > 0:
                    break
                await asyncio.sleep(0.3)

            if not results:
                print("  [FAIL] layout-check.html tidak menghasilkan laporan")
                passed_all = False
            else:
                passed_count = sum(1 for r in results if r.get("pass"))
                total_count = len(results)
                print(f"  Hasil layout-check: {passed_count}/{total_count} kriteria terpenuhi")
                for r in results:
                    status = "[PASS]" if r.get("pass") else "[FAIL]"
                    if not r.get("pass"):
                        print(f"    {status} Peta {r.get('mapId')}: {r.get('name')} ({r.get('detail')})")
                        passed_all = False
                if passed_count == total_count:
                    print("  [PASS] 100% Kriteria Tata Letak Lulus di Seluruh 7 Peta!")

            # Capture layout screenshot
            await capture_screenshot(ws, os.path.join(DOCS_G4_DIR, "01_layout_check_results.png"), 12)

            # 2. Run map-check.html
            print("\n2. Menjalankan tests/map-check.html...")
            await send_cdp(ws, "Page.navigate", {"url": f"http://localhost:{HTTP_PORT}/tests/map-check.html"}, 20)
            await asyncio.sleep(2.0)

            summary_text = await evaluate_js(ws, "document.getElementById('summary')?.textContent || ''", 21)
            is_pass = "LULUS" in summary_text
            print(f"  Ringkasan map-check: {summary_text}")
            if is_pass:
                print("  [PASS] map-check.html 100% LULUS di seluruh 7 peta!")
            else:
                print(f"  [FAIL] map-check.html gagal: {summary_text}")
                passed_all = False

            await capture_screenshot(ws, os.path.join(DOCS_G4_DIR, "02_map_check_reachability.png"), 22)

            # 3. Navigate into the running game to capture in-game overlays
            print("\n3. Mengambil Tangkapan Layar In-Game untuk Setiap Ruang...")
            await send_cdp(ws, "Page.navigate", {"url": f"http://localhost:{HTTP_PORT}/index.html?debug=1"}, 30)
            await asyncio.sleep(2.5)

            # Fast-forward main menu -> world
            for _ in range(30):
                has_game = await evaluate_js(ws, "Boolean(window.__GAME__)", 31)
                if has_game:
                    break
                await asyncio.sleep(0.3)

            current_scene = await evaluate_js(ws, "window.__GAME__?.scene?.getScenes(true)?.[0]?.scene?.key", 32)
            if current_scene == 'MainMenu':
                can_continue = await evaluate_js(ws, """
                    (() => {
                        const scene = window.__GAME__.scene.getScene('MainMenu');
                        if (scene && scene._buttons && scene._buttons[1] && scene._buttons[1].enabled) {
                            scene._continue();
                            return true;
                        }
                        return false;
                    })()
                """, 33)
                if not can_continue:
                    await evaluate_js(ws, "window.__GAME__.scene.getScene('MainMenu').scene.start('CharacterCreate');", 34)
                    await asyncio.sleep(1.0)
                    await evaluate_js(ws, """
                        (() => {
                            const form = document.querySelector('.charcreate-form');
                            if (form) {
                                form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
                            }
                        })()
                    """, 35)
                await asyncio.sleep(2.0)

            # Wait for World
            for _ in range(30):
                ready = await evaluate_js(ws, "Boolean(window.__LJ__ && window.__LJ__.teleportToMap)", 36)
                if ready:
                    break
                await asyncio.sleep(0.3)

            # Capture in-game shots with collision overlays
            maps_to_capture = [
                ('home', '03_ingame_home_kitchen_living.png'),
                ('school', '04_ingame_school_interior.png'),
                ('minimarket', '05_ingame_minimarket_interior.png'),
                ('toko_kosmetik', '06_ingame_kosmetik_interior.png'),
                ('spbu', '07_ingame_spbu_interior.png'),
                ('game_center', '08_ingame_game_center_interior.png'),
                ('town_hub', '09_ingame_town_hub.png')
            ]

            for mid, filename in maps_to_capture:
                await evaluate_js(ws, f"window.__LJ__.teleportToMap('{mid}', 'default')", 40)
                await asyncio.sleep(1.0)
                await capture_screenshot(ws, os.path.join(DOCS_G4_DIR, filename), 41)

            # 4. Generate VALIDATION-<mapId>.md files
            print("\n4. Menyusun Laporan docs/layouts/VALIDATION-<mapId>.md...")
            for mid, _ in maps_to_capture:
                val_path = os.path.join(DOCS_LAYOUTS_DIR, f"VALIDATION-{mid}.md")
                map_res = [r for r in (results or []) if r.get('mapId') == mid]
                all_m_pass = all(r.get('pass') for r in map_res)
                lines = [
                    f"# Laporan Validasi Tata Letak: {mid}",
                    f"Status: **{'LULUS' if all_m_pass else 'GAGAL'}**",
                    f"Tanggal Uji: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                    "",
                    "## Hasil Pengujian Otomatis (Rule 73 §7):",
                    "| Kriteria | Status | Rincian |",
                    "|---|---|---|"
                ]
                for r in map_res:
                    st = "LULUS" if r.get('pass') else "GAGAL"
                    lines.append(f"| {r.get('name')} | {st} | {r.get('detail')} |")

                with open(val_path, "w") as f:
                    f.write("\n".join(lines) + "\n")
                print(f"  Tersimpan: {os.path.basename(val_path)}")

    finally:
        chrome_proc.terminate()
        try:
            chrome_proc.wait(timeout=3)
        except Exception:
            chrome_proc.kill()

    print("\n==================================================")
    if passed_all:
        print("  🎉 HASIL: GERBANG G4 LULUS SEMUA UJI (100% HIJAU)")
        print("==================================================")
        return True
    else:
        print("  ❌ HASIL: GERBANG G4 GAGAL PADA BEBERAPA UJI")
        print("==================================================")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_suite())
    sys.exit(0 if success else 1)

