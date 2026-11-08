#!/usr/bin/env python3
"""
capture_checkpoint_d.py - Capture all Checkpoint D verification screenshots for Gate G7:
1. 01_persimpangan_4arah.png (Intersection)
2. 02_pintu_rumah.png (Home entrance)
3. 03_pintu_sekolah.png (School entrance)
4. 04_pintu_minimarket_kosmetik.png (Shops sidewalk)
5. 05_pintu_spbu.png (Gas station)
6. 06_pintu_game_center.png (New Game Center)
7. 07_tampilan_bermotor.png (Mounted motorcycle)
8. 08_perbandingan_sebelum_sesudah.png (Before/After comparison)
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
from PIL import Image

CDP_PORT = 9245
HTTP_PORT = 3843
OUT_DIR = "/home/abarox/Desktop/prototipe web statis game/game/docs/checkpoint-D"
os.makedirs(OUT_DIR, exist_ok=True)

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

async def capture_screenshot(ws, filename, msg_id=500):
    path = os.path.join(OUT_DIR, filename)
    res = await send_cdp(ws, "Page.captureScreenshot", {"format": "png"}, msg_id)
    data = res.get("result", {}).get("data")
    if data:
        with open(path, "wb") as f:
            f.write(base64.b64decode(data))
        print(f"  📸 Saved screenshot: {filename}")
        return True
    return False

async def get_ws_url():
    for _ in range(20):
        try:
            req = urllib.request.urlopen(f"http://localhost:{CDP_PORT}/json", timeout=1)
            tabs = json.loads(req.read().decode())
            for tab in tabs:
                if "localhost" in tab.get("url", ""):
                    return tab.get("webSocketDebuggerUrl")
            if tabs:
                return tabs[0].get("webSocketDebuggerUrl")
        except Exception:
            pass
        await asyncio.sleep(0.5)
    return None

async def run_captures():
    print("==================================================")
    print("  CAPTURING CHECKPOINT D SCREENSHOTS (Gate G7)    ")
    print("==================================================")

    url = f"http://localhost:{HTTP_PORT}/?scene=World&map=town_hub"
    chrome_proc = subprocess.Popen([
        "/usr/bin/google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=960,540",
        f"--remote-debugging-port={CDP_PORT}",
        url
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        ws_url = await get_ws_url()
        if not ws_url:
            print("Failed to get Chrome WebSocket URL!")
            return False

        async with websockets.connect(ws_url, max_size=10_000_000) as ws:
            await send_cdp(ws, "Page.enable")
            await send_cdp(ws, "Runtime.enable")

            # Wait for Phaser scene to load
            print("Waiting for World scene to load in town_hub...")
            for _ in range(30):
                is_ready = await evaluate_js(ws, "!!(window.__GAME__ && window.__GAME__.scene && window.__GAME__.scene.getScene('World') && window.__GAME__.scene.getScene('World')._player)")
                if is_ready:
                    break
                await asyncio.sleep(0.5)

            await asyncio.sleep(1.5)

            # 1. 01_persimpangan_4arah.png: Player at intersection (tile 21, 16 -> px 672, 512)
            print("Capturing 01_persimpangan_4arah.png...")
            await evaluate_js(ws, """(() => {
                const world = window.__GAME__.scene.getScene('World');
                const x = 21 * 32, y = 16 * 32;
                world._player.x = x; world._player.y = y;
                world._player.sprite.setPosition(x, y);
                world.cameras.main.pan(x, y, 0);
            })()""")
            await asyncio.sleep(0.5)
            await capture_screenshot(ws, "01_persimpangan_4arah.png", 101)

            # 2. 02_pintu_rumah.png: Player at home door (tile 6, 21 -> px 192, 672)
            print("Capturing 02_pintu_rumah.png...")
            await evaluate_js(ws, """(() => {
                const world = window.__GAME__.scene.getScene('World');
                const x = 6 * 32, y = 21 * 32;
                world._player.x = x; world._player.y = y;
                world._player.sprite.setPosition(x, y);
                world.cameras.main.pan(x, y, 0);
            })()""")
            await asyncio.sleep(0.5)
            await capture_screenshot(ws, "02_pintu_rumah.png", 102)

            # 3. 03_pintu_sekolah.png: Player at school door (tile 10, 9 -> px 320, 288)
            print("Capturing 03_pintu_sekolah.png...")
            await evaluate_js(ws, """(() => {
                const world = window.__GAME__.scene.getScene('World');
                const x = 10 * 32, y = 9 * 32;
                world._player.x = x; world._player.y = y;
                world._player.sprite.setPosition(x, y);
                world.cameras.main.pan(x, y, 0);
            })()""")
            await asyncio.sleep(0.5)
            await capture_screenshot(ws, "03_pintu_sekolah.png", 103)

            # 4. 04_pintu_minimarket_kosmetik.png: Player between minimarket and cosmetic (tile 31, 8 -> px 992, 256)
            print("Capturing 04_pintu_minimarket_kosmetik.png...")
            await evaluate_js(ws, """(() => {
                const world = window.__GAME__.scene.getScene('World');
                const x = 31 * 32, y = 8 * 32;
                world._player.x = x; world._player.y = y;
                world._player.sprite.setPosition(x, y);
                world.cameras.main.pan(x, y, 0);
            })()""")
            await asyncio.sleep(0.5)
            await capture_screenshot(ws, "04_pintu_minimarket_kosmetik.png", 104)

            # 5. 05_pintu_spbu.png: Player at SPBU (tile 36, 14 -> px 1152, 448)
            print("Capturing 05_pintu_spbu.png...")
            await evaluate_js(ws, """(() => {
                const world = window.__GAME__.scene.getScene('World');
                const x = 36 * 32, y = 14 * 32;
                world._player.x = x; world._player.y = y;
                world._player.sprite.setPosition(x, y);
                world.cameras.main.pan(x, y, 0);
            })()""")
            await asyncio.sleep(0.5)
            await capture_screenshot(ws, "05_pintu_spbu.png", 105)

            # 6. 06_pintu_game_center.png: Player at Game Center (tile 30, 21 -> px 960, 672)
            print("Capturing 06_pintu_game_center.png...")
            await evaluate_js(ws, """(() => {
                const world = window.__GAME__.scene.getScene('World');
                const x = 30 * 32, y = 21 * 32;
                world._player.x = x; world._player.y = y;
                world._player.sprite.setPosition(x, y);
                world.cameras.main.pan(x, y, 0);
            })()""")
            await asyncio.sleep(0.5)
            await capture_screenshot(ws, "06_pintu_game_center.png", 106)

            # 7. 07_tampilan_bermotor.png: Player mounted on motorcycle on the main road
            print("Capturing 07_tampilan_bermotor.png...")
            await evaluate_js(ws, """(() => {
                const world = window.__GAME__.scene.getScene('World');
                const x = 15 * 32, y = 16 * 32;
                world._player.x = x; world._player.y = y;
                world._player.sprite.setPosition(x, y);
                world.cameras.main.pan(x, y, 0);
                if (!world._player.isMounted) {
                    world._toggleVehicle();
                }
            })()""")
            await asyncio.sleep(0.8)
            await capture_screenshot(ws, "07_tampilan_bermotor.png", 107)

            # 8. Before / After procedural comparison
            print("Capturing procedural ground comparison...")
            await evaluate_js(ws, """(() => {
                const world = window.__GAME__.scene.getScene('World');
                if (world._player.isMounted) world._toggleVehicle();
                const x = 21 * 32, y = 16 * 32;
                world._player.x = x; world._player.y = y;
                world._player.sprite.setPosition(x, y);
                world.cameras.main.pan(x, y, 0);
                world._mapManager.currentLayout.terrain = { mode: 'procedural' };
                world._mapManager.loadMap('town_hub', 'default');
            })()""")
            await asyncio.sleep(1.0)
            await capture_screenshot(ws, "procedural_temp.png", 108)

            # Revert to plate
            await evaluate_js(ws, """(() => {
                const world = window.__GAME__.scene.getScene('World');
                world._mapManager.currentLayout.terrain = { mode: 'plate' };
                world._mapManager.loadMap('town_hub', 'default');
            })()""")
            await asyncio.sleep(1.0)

    finally:
        chrome_proc.terminate()
        try:
            chrome_proc.wait(timeout=2)
        except Exception:
            chrome_proc.kill()

    # Generate 08_perbandingan_sebelum_sesudah.png side-by-side
    p_proc = os.path.join(OUT_DIR, "procedural_temp.png")
    p_plate = os.path.join(OUT_DIR, "01_persimpangan_4arah.png")
    p_comp = os.path.join(OUT_DIR, "08_perbandingan_sebelum_sesudah.png")

    if os.path.exists(p_proc) and os.path.exists(p_plate):
        img_proc = Image.open(p_proc)
        img_plate = Image.open(p_plate)
        W, H = img_proc.size
        comp = Image.new("RGB", (W * 2 + 10, H), (20, 25, 35))
        comp.paste(img_proc, (0, 0))
        comp.paste(img_plate, (W + 10, 0))
        comp.save(p_comp)
        os.remove(p_proc)
        print(f"  📸 Generated side-by-side comparison: 08_perbandingan_sebelum_sesudah.png")

    print("\nCheckpoint D capture sequence completed!")
    return True

if __name__ == "__main__":
    asyncio.run(run_captures())
