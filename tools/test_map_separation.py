#!/usr/bin/env python3
"""
test_map_separation.py
Launches Chrome, tests game startup, interior rendering, and map transition.
Saves screenshots to docs/e8-mapsep/
"""
import asyncio, json, os, subprocess, time, base64
import urllib.request
import websockets

CDP_PORT = 9225
HTTP_PORT = 3843
SCREENSHOT_DIR = "/home/abarox/Desktop/prototipe web statis game/game/docs/e8-mapsep"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

async def send_cdp(ws, method, params=None, msg_id=1):
    msg = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(msg))
    while True:
        raw = await ws.recv()
        res = json.loads(raw)
        if res.get("id") == msg_id:
            return res

async def evaluate(ws, expr, msg_id=100, await_promise=False):
    res = await send_cdp(ws, "Runtime.evaluate", {
        "expression": expr,
        "returnByValue": True,
        "awaitPromise": await_promise
    }, msg_id)
    if "exceptionDetails" in res.get("result", {}):
        exc = res["result"]["exceptionDetails"]
        raise RuntimeError(f"JS Error: {exc.get('text')} | {exc.get('exception',{}).get('description','')}")
    return res.get("result", {}).get("result", {}).get("value")

async def screenshot(ws, path, msg_id=500):
    res = await send_cdp(ws, "Page.captureScreenshot", {"format": "png"}, msg_id)
    data = res.get("result", {}).get("data")
    if data:
        with open(path, "wb") as f:
            f.write(base64.b64decode(data))
        print(f"  📸 Saved -> {path}")

async def get_ws_url():
    for _ in range(20):
        try:
            req = urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json", timeout=1)
            tabs = json.loads(req.read().decode())
            for tab in tabs:
                if "index.html" in tab.get("url", "") or "localhost" in tab.get("url", ""):
                    return tab.get("webSocketDebuggerUrl")
            if tabs:
                return tabs[0].get("webSocketDebuggerUrl")
        except Exception:
            pass
        await asyncio.sleep(0.5)
    return None

async def run():
    print("=== Testing Map Separation & Interior Rendering ===")
    chrome_proc = subprocess.Popen([
        "/usr/bin/google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1200,800",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir=/tmp/test_chrome_mapsep_{int(time.time())}",
        f"http://127.0.0.1:{HTTP_PORT}/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        await asyncio.sleep(2.0)
        ws_url = await get_ws_url()
        if not ws_url:
            print("ERROR: Could not get Chrome WebSocket URL")
            return False

        async with websockets.connect(ws_url, max_size=10**7) as ws:
            await send_cdp(ws, "Page.enable", {}, 1)
            await send_cdp(ws, "Runtime.enable", {}, 2)
            await asyncio.sleep(1.0)

            # Check console errors
            print("1. Clear localStorage and navigate to fresh start...")
            await evaluate(ws, "localStorage.clear()", 10)
            await send_cdp(ws, "Page.navigate", {"url": f"http://127.0.0.1:{HTTP_PORT}/index.html"}, 11)
            await asyncio.sleep(2.5)

            # Screenshot MainMenu
            await screenshot(ws, os.path.join(SCREENSHOT_DIR, "01_main_menu.png"), 501)

            # Click Mulai Petualangan Baru
            print("2. Starting New Game...")
            # In MainMenu, space or enter activates selected (default index 0 = Mulai Baru)
            await evaluate(ws, """
                (function() {
                    const scene = window.__LJ__?.scene || window.Phaser?.GAMES?.[0]?.scene?.getScene('MainMenu');
                    if (scene && scene._startNew) {
                        scene._startNew();
                        return 'scene._startNew called';
                    }
                    const btn = document.querySelector('button');
                    if (btn) { btn.click(); return 'button clicked'; }
                    return 'none';
                })()
            """, 12)
            await asyncio.sleep(1.5)

            await screenshot(ws, os.path.join(SCREENSHOT_DIR, "02_char_create.png"), 502)

            # Submit character creation modal
            print("3. Submitting character creation...")
            await evaluate(ws, """
                (function() {
                    const nameInput = document.getElementById('char-name') || document.querySelector('input[type="text"]');
                    if (nameInput) nameInput.value = 'Budi Santoso';
                    const form = document.querySelector('form');
                    if (form) {
                        form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
                        return 'form submitted';
                    }
                    const btn = document.querySelector('.btn-primary') || document.querySelector('button[type="submit"]');
                    if (btn) { btn.click(); return 'btn clicked'; }
                    return 'no form found';
                })()
            """, 13)
            await asyncio.sleep(3.0) # Wait for World scene and MapManager

            await screenshot(ws, os.path.join(SCREENSHOT_DIR, "03_game_world_start.png"), 503)

            # Check World scene & MapManager status
            print("4. Inspecting game world scene...")
            info = await evaluate(ws, """
                (function() {
                    const store = window.__LJ__?.getState?.();
                    const mm = window.__LJ__?.getMapManager?.();
                    const scene = window.__LJ__?.scene;
                    const children = scene?.children?.list || [];
                    
                    const textures = [];
                    let grassCount = 0;
                    children.forEach(c => {
                        if (c.texture?.key) {
                            textures.push(c.texture.key);
                            if (c.texture.key === 'tile_rumput') grassCount++;
                        }
                    });

                    return {
                        currentMap: store?.currentMap,
                        mapManagerCurrentId: mm?.currentMapId,
                        mapObjectsCount: mm?._mapObjects?.length || 0,
                        colliderBodiesCount: mm?._colliderBodies?.length || 0,
                        totalSceneChildren: children.length,
                        grassCount: grassCount,
                        playerPos: { x: window.__LJ__?.getPlayer?.()?.sprite?.x, y: window.__LJ__?.getPlayer?.()?.sprite?.y },
                        interactablesCount: window.__LJ__?.listInteractables?.()?.length || 0
                    };
                })()
            """, 14)
            print("  Scene state:", json.dumps(info, indent=2))

            # Test transition to town_hub
            print("5. Testing transition to town_hub...")
            await evaluate(ws, """
                (async () => {
                    await window.__LJ__?.getMapManager?.()?.loadMap('town_hub');
                })()
            """, 15, await_promise=True)
            await asyncio.sleep(2.0)
            await screenshot(ws, os.path.join(SCREENSHOT_DIR, "04_town_hub.png"), 504)

            # Test transition back to home
            print("6. Testing transition back to home...")
            await evaluate(ws, """
                (async () => {
                    await window.__LJ__?.getMapManager?.()?.loadMap('home');
                })()
            """, 16, await_promise=True)
            await asyncio.sleep(2.0)
            await screenshot(ws, os.path.join(SCREENSHOT_DIR, "05_home_returned.png"), 505)

            print("=== Test complete! ===")
            return True

    finally:
        chrome_proc.kill()

if __name__ == "__main__":
    asyncio.run(run())
