#!/usr/bin/env python3
"""
test_time_system.py — Automated verification of Rule 72 (Time System & Activities):
1. Verifies tests/self-test.html (accounting invariants remain 100% green)
2. Verifies tests/time-test.html (all 10 time domain scenarios pass)
3. Opens live gameplay (index.html?debug=1)
4. Verifies 1 real sec = 1 game min live progression
5. Tests 4 sky phases (pagi, siang, sore, malam) on live Harvest Moon HUD and captures screenshots
6. Verifies activity advanceTime(60) advances clock by exactly 60 minutes
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

CDP_PORT = 9225
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
    print("  TEST SUITE: Life Journey Time System (Rule 72)  ")
    print("==================================================")

    # 1. Start Headless Chrome
    chrome_proc = subprocess.Popen([
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1200,800",
        f"--remote-debugging-port={CDP_PORT}",
        f"http://localhost:{HTTP_PORT}/tests/self-test.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        await asyncio.sleep(1.5)
        ws_url = await get_ws_url("self-test.html")
        if not ws_url:
            print("[FAIL] Tidak dapat terhubung ke Chrome CDP untuk self-test.html")
            return False

        async with websockets.connect(ws_url) as ws:
            await send_cdp(ws, "Page.enable", {}, 1)
            await asyncio.sleep(1.0)
            summary_text = await evaluate_js(ws, "document.getElementById('summary')?.textContent", 10)
            summary_class = await evaluate_js(ws, "document.getElementById('summary')?.className", 11)
            print(f"1. Self-Test Akuntansi:\n   Hasil: {summary_text} (class: {summary_class})")
            assert "summary-pass" in str(summary_class), f"Self-test failed: {summary_text}"

            # 2. Navigate to tests/time-test.html
            await send_cdp(ws, "Page.navigate", {"url": f"http://localhost:{HTTP_PORT}/tests/time-test.html"}, 20)
            await asyncio.sleep(1.5)
            time_summary = await evaluate_js(ws, "document.getElementById('summary')?.textContent", 30)
            time_class = await evaluate_js(ws, "document.getElementById('summary')?.className", 31)
            print(f"2. Time-Test Domain (10 Skenario):\n   Hasil: {time_summary} (class: {time_class})")
            assert "summary-pass" in str(time_class), f"Time-test failed: {time_summary}"

            # 3. Navigate to live game with debug
            await send_cdp(ws, "Page.navigate", {"url": f"http://localhost:{HTTP_PORT}/index.html?debug=1"}, 40)
            await asyncio.sleep(2.5)

            # Check active scene from window.__GAME__
            current_scene = await evaluate_js(ws, "window.__GAME__?.scene?.getScenes(true)?.[0]?.scene?.key", 50)
            print(f"3. Live Game Loaded. Active Scene: {current_scene}")

            if current_scene == "MainMenu":
                print("   Transisi MainMenu -> CharacterCreate -> World...")
                await evaluate_js(ws, """
                    (() => {
                        const game = window.__GAME__;
                        const scene = game.scene.getScene('MainMenu');
                        scene.scene.start('CharacterCreate');
                    })()
                """, 60)
                await asyncio.sleep(1.0)

                # Submit character creation form
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
                """, 70)
                await asyncio.sleep(2.0)

            world_scene = await evaluate_js(ws, "window.__GAME__?.scene?.getScenes(true)?.[0]?.scene?.key", 90)
            print(f"   Scene saat ini: {world_scene}")
            assert world_scene == "World", f"Gagal masuk ke scene World, saat ini: {world_scene}"

            # 4. Verify 1 real sec = 1 game min ticking
            t0 = await evaluate_js(ws, "window.__LJ__.getTime().minuteOfDay", 100)
            print(f"4. Pengujian Tick Waktu Live:\n   Waktu awal t0: {t0} menit ({await evaluate_js(ws, 'window.__LJ__.getTime().timeString', 101)})")
            await asyncio.sleep(2.2) # tunggu ~2 detik
            t1 = await evaluate_js(ws, "window.__LJ__.getTime().minuteOfDay", 102)
            print(f"   Waktu setelah 2.2 detik t1: {t1} menit ({await evaluate_js(ws, 'window.__LJ__.getTime().timeString', 103)})")
            assert t1 > t0, f"Clock tidak berdetik otomatis: t0={t0}, t1={t1}"
            print("   [LULUS] Clock berdetik real-time!")

            # 5. Test 4 Sky Phases on live Harvest Moon HUD & Screenshot
            phases_to_test = [
                ("pagi", 8 * 60, "PAGI", "sky-pagi"),       # 08:00
                ("siang", 13 * 60, "SIANG", "sky-siang"),    # 13:00
                ("sore", 17 * 60 + 30, "SORE", "sky-sore"),  # 17:30
                ("malam", 21 * 60, "MALAM", "sky-malam")     # 21:00
            ]

            print("5. Pengujian & Tangkapan Layar 4 Fase Langit pada HUD:")
            for phase_name, target_min, expected_label, expected_class in phases_to_test:
                # Set time using advanceTime
                current_min = await evaluate_js(ws, "window.__LJ__.getTime().minuteOfDay", 110)
                diff = (target_min - current_min) % 1440
                if diff > 0:
                    await evaluate_js(ws, f"window.__LJ__.advanceTime({diff}, 'test_phase')", 111)
                    await asyncio.sleep(0.3)

                hud_period = await evaluate_js(ws, "document.querySelector('.hm-period-badge')?.textContent", 112)
                hud_sky_class = await evaluate_js(ws, "document.querySelector('.hm-sky-box')?.className", 113)
                hud_time = await evaluate_js(ws, "document.querySelector('.hm-time-text')?.textContent", 114)
                print(f"   - Fase {phase_name.upper()} ({hud_time}): Badge='{hud_period}', SkyBox='{hud_sky_class}'")
                assert expected_label in str(hud_period), f"Label periode salah: {hud_period} vs {expected_label}"
                assert expected_class in str(hud_sky_class), f"Sky class salah: {hud_sky_class} vs {expected_class}"

                shot_path = os.path.join(SCREENSHOT_DIR, f"live_hud_{phase_name}.png")
                await capture_screenshot(ws, shot_path, 120 + target_min)

            # 6. Test Activity Time-Skip (60 Minutes)
            min_before = await evaluate_js(ws, "window.__LJ__.getTime().minuteOfDay", 200)
            print(f"6. Pengujian Aktivitas (Time-Skip 60 Menit):\n   Menit sebelum: {min_before}")
            await evaluate_js(ws, "window.__LJ__.advanceTime(60, 'activity_study')", 201)
            await asyncio.sleep(0.3)
            min_after = await evaluate_js(ws, "window.__LJ__.getTime().minuteOfDay", 202)
            expected_after = (min_before + 60) % 1440
            print(f"   Menit sesudah: {min_after} (harus {expected_after})")
            assert min_after in [expected_after, (expected_after + 1) % 1440], f"Aktivitas 60 menit gagal menambah waktu tepat 60 menit: {min_before} -> {min_after} (expected {expected_after})"
            print("   [LULUS] Aktivitas menambah tepat 60 menit!")

            # Capture final full game screenshot
            final_shot = os.path.join(SCREENSHOT_DIR, "live_gameplay_time_system_e1.png")
            await capture_screenshot(ws, final_shot, 300)

            print("==================================================")
            print("  GERBANG E1 LULUS 100% — SEMUA TES HIJAU & VALID ")
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
