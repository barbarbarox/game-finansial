#!/usr/bin/env python3
"""
tools/test_h1_hud_fuel.py — Gate H1 Test Suite
Tests:
1. tests/hud-sync.html (DOM latency <= 200ms, >= 1 subscriber per event)
2. In-game SPBU refuel via real UI clicks:
   - fuel bar updates instantly to 80%
   - state.gasoline is 80
   - saves docs/regression/a9_gas_bar_green.png
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
    print("  TEST SUITE: Gate H1 (HUD Sync & Fuel Bar Fix)")
    print("==================================================")

    chrome_proc = subprocess.Popen([
        "/usr/bin/google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-extensions",
        "--window-size=1200,800",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir=/tmp/test_chrome_h1_{int(time.time())}",
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

            # Part 1: Run tests/hud-sync.html
            print("\n1. Menjalankan tests/hud-sync.html...")
            await send_cdp(ws, "Page.navigate", {"url": f"http://127.0.0.1:{HTTP_PORT}/tests/hud-sync.html"}, 10)
            await asyncio.sleep(1.5)

            hud_test_result = await evaluate(ws, "window.__TEST_RESULTS__", 11)
            assert hud_test_result, "hud-sync.html did not produce __TEST_RESULTS__"
            all_passed = hud_test_result.get("allPassed")
            print(f"  hud-sync.html allPassed: {all_passed}")
            for r in hud_test_result.get("results", []):
                print(f"    {'PASS' if r.get('passed') else 'FAIL'}: {r.get('name')} ({r.get('detail')})")
            assert all_passed, "tests/hud-sync.html had failing tests!"

            # Part 2: Real in-game test at SPBU
            print("\n2. Menguji alur isi bensin SPBU lewat UI nyata...")
            await evaluate(ws, "localStorage.clear()", 20)
            await send_cdp(ws, "Page.navigate", {"url": f"http://127.0.0.1:{HTTP_PORT}/index.html"}, 21)
            await asyncio.sleep(2.5)

            # Character creation
            await evaluate(ws, "window.__GAME__.scene.getScene('MainMenu')._startNew()", 22)
            await asyncio.sleep(0.5)
            await evaluate(ws, "document.querySelector('.charcreate-form select').value = 'm'", 23)
            await evaluate(ws, "document.querySelector('.charcreate-form')?.requestSubmit()", 24)
            await asyncio.sleep(2.0)

            # Setup initial state: 40% fuel and 100,000 cash for testing
            await evaluate(ws, """(() => {
                const store = window.__LJ__.getStore();
                const state = store.getState();
                const entry = {
                    id: 'init_cash',
                    kind: 'allowance',
                    day: 1,
                    month: 1,
                    minuteOfDay: 480,
                    description: 'Uang awal tes',
                    categoryId: null,
                    lines: [
                        { accountId: 'KAS_PRIBADI', side: 'D', amount: 100000 },
                        { accountId: 'UANG_SAKU', side: 'K', amount: 100000 }
                    ]
                };
                const newLedger = {
                    ...state.ledger,
                    entries: [...(state.ledger?.entries || []), entry]
                };
                store.setState({ gasoline: 40, ledger: newLedger });
            })()""", 25)
            await asyncio.sleep(0.5)

            # Teleport to SPBU
            await evaluate(ws, "window.__LJ__.getMapManager().transitionTo('spbu', 'default')", 26)
            await asyncio.sleep(1.5)

            # Open dialogue with Bang Dodi / Mas Doni in SPBU
            await evaluate(ws, """(() => {
                const world = window.__GAME__.scene.getScene('World');
                const doni = world._npcManager.npcs.find(n => n.def.id === 'npc_bang_dodi' || n.def.id === 'npc_doni');
                if (doni) {
                    world._player.sprite.setPosition(doni.x, doni.y + 24);
                    world._npcManager.openDialog(doni, document.body);
                }
            })()""", 27)
            await asyncio.sleep(2.0)

            # Complete typewriter animation by clicking dialogue box
            await evaluate(ws, """(() => {
                const box = document.getElementById('dlg-box');
                if (box) box.click();
            })()""", 28)
            await asyncio.sleep(0.5)

            fuel_text_before = await evaluate(ws, "document.querySelector('.hm-fuel-text')?.textContent", 29)
            print(f"  Bensin sebelum isi: {fuel_text_before}")
            assert fuel_text_before == '40%', f"Expected 40%, got {fuel_text_before}"

            # Real DOM click on "Isi Bensin Pertalite 2 Liter (Rp20.000)"
            print("  Mengklik pilihan 'Isi Bensin Pertalite 2 Liter' lewat DOM click...")
            clicked = await evaluate(ws, """(() => {
                const btn = document.querySelector('.dialogue-choice-btn, .choice-btn, button.selected');
                if (btn) {
                    btn.click();
                    return true;
                }
                return false;
            })()""", 30)
            print(f"  Tombol diklik: {clicked}")
            assert clicked, "Gagal menemukan tombol dialog yang aktif!"
            await asyncio.sleep(2.0)

            fuel_text_after = await evaluate(ws, "document.querySelector('.hm-fuel-text')?.textContent", 30)
            fuel_width_after = await evaluate(ws, "document.querySelector('.hm-fuel-fill')?.style.width", 31)
            fuel_state_after = await evaluate(ws, "window.__LJ__.getState().gasoline", 32)
            print(f"  Bensin setelah isi di DOM: text={fuel_text_after}, width={fuel_width_after}, state={fuel_state_after}")

            assert fuel_text_after == '80%', f"Expected '80%', got {fuel_text_after}"
            assert fuel_width_after == '80%', f"Expected '80%', got {fuel_width_after}"
            assert fuel_state_after == 80, f"Expected state.gasoline 80, got {fuel_state_after}"

            # Capture Green screenshot
            await snap(ws, "a9_gas_bar_green", 501)
            print("\n  ✅ A9 VERIFIED GREEN: Bar bensin dan state terupdate seketika menjadi 80%!")

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

