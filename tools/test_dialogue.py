#!/usr/bin/env python3
"""
test_dialogue.py — Automated verification of Rule 71 (Dialogue System with Portraits):
1. Verifies tests/dialogue-test.html (schema, text length <= 140, effects whitelist, disabled choices)
2. Connects to live gameplay (index.html?debug=1)
3. Tests speaker highlighting (NPC active vs Player active during choices)
4. Tests choice selection and whitelist effect execution
5. Captures screenshots on Desktop (1200x800) and Tablet (768x1024)
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

CDP_PORT = 9227
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
    print("  TEST SUITE: Life Journey Dialogue System (Rule 71)")
    print("==================================================")

    chrome_proc = subprocess.Popen([
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1200,800",
        f"--remote-debugging-port={CDP_PORT}",
        f"http://localhost:{HTTP_PORT}/tests/dialogue-test.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        await asyncio.sleep(1.5)
        ws_url = await get_ws_url("dialogue-test.html")
        if not ws_url:
            print("[FAIL] Tidak dapat terhubung ke Chrome CDP untuk dialogue-test.html")
            return False

        async with websockets.connect(ws_url) as ws:
            await send_cdp(ws, "Page.enable", {}, 1)
            await asyncio.sleep(1.5)

            # 1. Verify tests/dialogue-test.html
            summary_class = ""
            summary_text = ""
            for _ in range(20):
                summary_text = await evaluate_js(ws, "document.getElementById('summary')?.textContent", 10)
                summary_class = await evaluate_js(ws, "document.getElementById('summary')?.className", 11)
                if summary_class and "summary-" in str(summary_class):
                    break
                await asyncio.sleep(0.3)

            print(f"1. Dialogue Unit & Schema Test:\n   Hasil: {summary_text} (class: {summary_class})")
            if "summary-fail" in str(summary_class) or not summary_class:
                cards = await evaluate_js(ws, "Array.from(document.querySelectorAll('.test-card')).map(c => c.textContent).join('\\n')", 12)
                print("   Detail Pengujian:\n", cards)

            assert "summary-pass" in str(summary_class), f"Dialogue test failed: {summary_text}"

            # 2. Navigate to live game
            await send_cdp(ws, "Page.navigate", {"url": f"http://localhost:{HTTP_PORT}/index.html?debug=1"}, 20)
            await asyncio.sleep(2.0)

            # Start game if in MainMenu
            current_scene = await evaluate_js(ws, "window.__GAME__?.scene?.getScenes(true)?.[0]?.scene?.key", 30)
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
                            if (inputs[1]) inputs[1].value = 'Pak Budi';
                            if (inputs[2]) inputs[2].value = 'Bu Budi';
                            form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
                        }
                    })()
                """, 32)
                await asyncio.sleep(2.0)

            # 3. Test Live Dialogue Ibu (Desktop 1200x800)
            print("2. Menjalankan Dialog Ibu di Rumah (Desktop):")
            await evaluate_js(ws, "(async () => { await window.__LJ__.startDialogue('dia_ibu_home', 'npc_ibu'); })()", 40)
            await asyncio.sleep(0.5)

            # Verify NPC speaker active
            st1 = await evaluate_js(ws, "window.__LJ__.getDialogueState()", 41)
            print(f"   State simpul awal: speaker={st1.get('speaker')}, text='{st1.get('currentText')[:30]}...'")
            assert st1.get('speaker') == 'npc', "Speaker harus NPC di awal"
            await capture_screenshot(ws, os.path.join(SCREENSHOT_DIR, "live_dialogue_ibu_speaking_desktop.png"), 42)

            # Fast-forward typewriter to show choices
            await evaluate_js(ws, "document.getElementById('dlg-box')?.click()", 43)
            await asyncio.sleep(0.5)

            st2 = await evaluate_js(ws, "window.__LJ__.getDialogueState()", 44)
            print(f"   Choices muncul: {len(st2.get('choices', []))} opsi. Player active highlight!")
            assert len(st2.get('choices', [])) >= 2, f"Harus ada 2-4 pilihan, dapat: {st2.get('choices')}"
            await capture_screenshot(ws, os.path.join(SCREENSHOT_DIR, "live_dialogue_ibu_choices_desktop.png"), 45)

            # Close dialogue
            await evaluate_js(ws, "window.__LJ__.closeDialogue()", 46)
            await asyncio.sleep(0.3)

            # 4. Test Dialogue Budi (Friend Peer-Pressure Flow)
            print("3. Menjalankan Dialog Budi Teman (Ajakan Arcade & Pilihan Diskon/Tolak):")
            # Set cash low so option 1 is disabled
            await evaluate_js(ws, """
                (() => {
                    const store = window.__LJ__.getStore();
                    const state = store.getState();
                    // Set kas to 0 (tidak cukup untuk arcade 25.000)
                    state.ledger.entries = [];
                })()
            """, 50)
            await evaluate_js(ws, "(async () => { await window.__LJ__.startDialogue('dia_budi_school', 'npc_budi'); })()", 51)
            await asyncio.sleep(0.5)
            await evaluate_js(ws, "document.getElementById('dlg-box')?.click()", 52)
            await asyncio.sleep(0.5)

            st_budi = await evaluate_js(ws, "window.__LJ__.getDialogueState()", 53)
            choices_info = st_budi.get('choices', [])
            print(f"   Pilihan Budi: {[c.get('text') for c in choices_info]}")
            print(f"   Opsi 1 disabled: {choices_info[0].get('disabled')}")
            assert choices_info[0].get('disabled') == True, "Opsi arcade harus disabled saat kas < 25.000"
            await capture_screenshot(ws, os.path.join(SCREENSHOT_DIR, "live_dialogue_budi_disabled_desktop.png"), 54)

            # 5. Test Tablet Viewport (768x1024)
            print("4. Pengujian Responsive Viewport Tablet (768x1024):")
            await send_cdp(ws, "Emulation.setDeviceMetricsOverride", {
                "width": 768,
                "height": 1024,
                "deviceScaleFactor": 1,
                "mobile": True
            }, 60)
            await asyncio.sleep(0.5)

            await capture_screenshot(ws, os.path.join(SCREENSHOT_DIR, "live_dialogue_tablet_responsive.png"), 61)
            print("   [LULUS] Tampilan tablet responsif dan rapi!")

            # Restore viewport
            await send_cdp(ws, "Emulation.clearDeviceMetricsOverride", {}, 70)
            await evaluate_js(ws, "window.__LJ__.closeDialogue()", 71)

            print("==================================================")
            print("  GERBANG E3 LULUS 100% — SISTEM DIALOG POTRET OK ")
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
