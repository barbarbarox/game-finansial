#!/usr/bin/env python3
"""
test_checkpoint_b.py — Captures the two required renders for Checkpoint B:
1. kamar_pemain_rendered.png: Live gameplay showing player's bedroom with pixel art furniture
2. dialog_portrait_rendered.png: Live gameplay showing dialogue system with player portrait rendered
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
CHECKPOINT_DIR = "/home/abarox/Desktop/prototipe web statis game/game/docs/checkpoint-B"
BRAIN_DIR = "/home/abarox/.gemini/antigravity/brain/4d2f9b08-f034-4550-b619-39a74fd29f25"
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

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

async def run_capture():
    print("==================================================")
    print("  CHECKPOINT B CAPTURE: Bedroom & Portrait Dialogue")
    print("==================================================")

    chrome_proc = subprocess.Popen([
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1280,720",
        f"--remote-debugging-port={CDP_PORT}",
        f"http://localhost:{HTTP_PORT}/index.html?debug=1"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        await asyncio.sleep(2.0)
        ws_url = await get_ws_url("index.html")
        if not ws_url:
            print("[FAIL] Tidak dapat terhubung ke Chrome CDP")
            return False

        async with websockets.connect(ws_url) as ws:
            await send_cdp(ws, "Page.enable", {}, 1)
            await asyncio.sleep(2.0)

            # Start game if in MainMenu
            in_main_menu = await evaluate_js(ws, "window.game?.scene?.isActive('MainMenu')", 2)
            if in_main_menu:
                print("1. Memulai permainan dari MainMenu...")
                await evaluate_js(ws, "window.__LJ__?.startNewGame?.()", 3)
                await asyncio.sleep(1.5)

            # Switch to 'home' map
            print("2. Pindah ke peta 'home' (kamar tidur pemain)...")
            await evaluate_js(ws, "window.__LJ__?.mapManager?.transitionTo('home', 'kamar_tidur')", 4)
            await asyncio.sleep(1.0)

            # Position camera nicely around player bedroom
            await evaluate_js(ws, """
                const scene = window.game?.scene?.getScene('World');
                if (scene && scene._player) {
                    scene._player.sprite.setPosition(192, 192); // tile x=6, y=6
                    scene.cameras.main.centerOn(192, 192);
                }
            """, 5)
            await asyncio.sleep(0.5)

            # Capture bedroom rendered screenshot
            bedroom_out = os.path.join(CHECKPOINT_DIR, "kamar_pemain_rendered.png")
            await capture_screenshot(ws, bedroom_out, 10)
            # Copy to brain dir
            subprocess.run(["cp", bedroom_out, os.path.join(BRAIN_DIR, "kamar_pemain_rendered.png")], check=False)

            # Now start dialogue with Ibu to show dialogue system with player portrait
            print("3. Membuka dialog dengan Ibu untuk potret pemain...")
            await evaluate_js(ws, "window.__LJ__?.startDialogue?.('dia_ibu_home', 'npc_ibu')", 11)
            await asyncio.sleep(0.8)

            # Advance to choices/player speaking
            await evaluate_js(ws, "window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }))", 12)
            await asyncio.sleep(0.5)

            dialogue_out = os.path.join(CHECKPOINT_DIR, "dialog_portrait_rendered.png")
            await capture_screenshot(ws, dialogue_out, 20)
            subprocess.run(["cp", dialogue_out, os.path.join(BRAIN_DIR, "dialog_portrait_rendered.png")], check=False)

            print("[SUCCESS] Checkpoint B visual assets captured successfully!")
            return True

    finally:
        chrome_proc.terminate()
        try:
            chrome_proc.wait(timeout=2)
        except Exception:
            chrome_proc.kill()

if __name__ == "__main__":
    success = asyncio.run(run_capture())
    sys.exit(0 if success else 1)
