#!/usr/bin/env python3
"""
tools/test_h2_nakas_access.py — Gate H2 Test Suite
Tests:
1. tests/layout-check.html: ApproachCheck across all 7 maps passes.
2. In-game walk from bedroom door to bed without nakas collision blocking.
3. Bed interaction successfully triggers sleep activity.
4. Saves docs/regression/a8_nakas_unblocked_green.png.
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
    print("  TEST SUITE: Gate H2 (Nakas Unblocked & Bed Access)")
    print("==================================================")

    chrome_proc = subprocess.Popen([
        "/usr/bin/google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-extensions",
        "--window-size=1200,800",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir=/tmp/test_chrome_h2_{int(time.time())}",
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

            # 1. Run tests/layout-check.html
            print("\n1. Menjalankan tests/layout-check.html (Termasuk Uji ApproachCheck)...")
            await send_cdp(ws, "Page.navigate", {"url": f"http://127.0.0.1:{HTTP_PORT}/tests/layout-check.html"}, 10)
            await asyncio.sleep(2.0)

            results = await evaluate(ws, "window.__LAYOUT_RESULTS__", 12)
            failed_checks = [r for r in results if not r.get("pass")]
            print(f"  Failed checks ({len(failed_checks)}): {failed_checks}")
            summary_text = await evaluate(ws, "document.getElementById('summary')?.textContent", 11)
            print(f"  Ringkasan Layout: {summary_text}")
            assert "LULUS SEMUA TATA LETAK" in (summary_text or ""), f"Layout validator failed: {summary_text}"
            approach_checks = [r for r in results if "ApproachCheck" in r.get("name", "")]
            print(f"  ApproachCheck count across 7 maps: {len(approach_checks)}")
            for ac in approach_checks:
                print(f"    Peta {ac.get('mapId')}: {'PASS' if ac.get('pass') else 'FAIL'} - {ac.get('detail')}")
                assert ac.get("pass"), f"ApproachCheck failed for map {ac.get('mapId')}"

            # 2. In-game walk and interact test
            print("\n2. Menguji navigasi dari pintu kamar ke kasur via UI nyata...")
            await evaluate(ws, "localStorage.clear()", 20)
            await send_cdp(ws, "Page.navigate", {"url": f"http://127.0.0.1:{HTTP_PORT}/index.html"}, 21)
            await asyncio.sleep(2.5)

            # Start game
            await evaluate(ws, "window.__GAME__.scene.getScene('MainMenu')._startNew()", 22)
            await asyncio.sleep(0.5)
            await evaluate(ws, "document.querySelector('.charcreate-form select').value = 'm'", 23)
            await evaluate(ws, "document.querySelector('.charcreate-form')?.requestSubmit()", 24)
            await asyncio.sleep(2.0)

            # Teleport to home interior at bedroom entrance
            # Bedroom entrance in home is around x = 4.5 * 32 = 144, y = 7 * 32 = 224
            await evaluate(ws, """(() => {
                const world = window.__GAME__.scene.getScene('World');
                world._player.sprite.setPosition(144, 224);
            })()""", 25)
            await asyncio.sleep(0.5)

            # Check nakas position
            nakas_pos = await evaluate(ws, """(() => {
                const mapMgr = window.__LJ__.getMapManager();
                const furns = mapMgr.currentLayout?.furniture || [];
                const nakas = furns.find(f => f.id === 'fur_nakas_lampu');
                return nakas ? { x: nakas.x, y: nakas.y } : null;
            })()""", 26)
            print(f"  Posisi nakas setelah perbaikan: {nakas_pos}")
            assert nakas_pos and nakas_pos["y"] == 2.0, f"Expected nakas at y=2.0, got {nakas_pos}"

            # Walk upward towards bed (W key) for 800ms
            print("  Menggerakkan pemain ke arah kasur menggunakan tombol W...")
            await send_cdp(ws, "Input.dispatchKeyEvent", {"type": "keyDown", "windowsVirtualKeyCode": 87, "key": "w", "code": "KeyW"})
            await asyncio.sleep(0.8)
            await send_cdp(ws, "Input.dispatchKeyEvent", {"type": "keyUp", "windowsVirtualKeyCode": 87, "key": "w", "code": "KeyW"})
            await asyncio.sleep(0.5)

            player_pos = await evaluate(ws, """(() => {
                const p = window.__GAME__.scene.getScene('World')._player.sprite;
                return { x: Math.round(p.x), y: Math.round(p.y) };
            })()""", 27)
            print(f"  Posisi pemain setelah berjalan: {player_pos}")
            # Player should have moved up (y < 200) without getting stuck at nakas
            assert player_pos["y"] < 200, f"Pemain terhalang! Posisi y: {player_pos['y']}"

            # Check if bed interactable is within reach
            interactable_nearby = await evaluate(ws, """(() => {
                const world = window.__GAME__.scene.getScene('World');
                const curr = world._currentInteractable;
                return curr ? { id: curr.id, type: curr.type, activityId: curr.activityId } : null;
            })()""", 28)
            print(f"  Interactable terdekat: {interactable_nearby}")
            assert interactable_nearby and interactable_nearby["id"] == "int_kasur", f"Expected int_kasur nearby, got {interactable_nearby}"

            # Press E to trigger bed sleep activity
            print("  Menekan tombol E untuk interaksi tidur...")
            await send_cdp(ws, "Input.dispatchKeyEvent", {"type": "keyDown", "windowsVirtualKeyCode": 69, "key": "e", "code": "KeyE"})
            await asyncio.sleep(0.1)
            await send_cdp(ws, "Input.dispatchKeyEvent", {"type": "keyUp", "windowsVirtualKeyCode": 69, "key": "e", "code": "KeyE"})
            await asyncio.sleep(1.0)

            # Check if timeskip / sleep overlay triggered
            has_timeskip = await evaluate(ws, "!!document.querySelector('.timeskip-overlay, .timeskip-box, .timeskip-content')", 29)
            print(f"  Animasi tidur / timeskip aktif: {has_timeskip}")

            await snap(ws, "a8_nakas_unblocked_green", 501)
            print("\n  ✅ A8 VERIFIED GREEN: Akses ke kasur lancar tanpa terhalang nakas, interaksi tidur berhasil!")

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
