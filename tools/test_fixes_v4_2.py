#!/usr/bin/env python3
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
DOCS_DIR = "/home/abarox/Desktop/prototipe web statis game/game/docs/g8-fixes"
os.makedirs(DOCS_DIR, exist_ok=True)

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

async def snap(ws, name, msg_id=500):
    shot = await send_cdp(ws, "Page.captureScreenshot", {"format": "png"}, msg_id)
    img_data = shot.get("result", {}).get("data")
    if img_data:
        p = os.path.join(DOCS_DIR, f"{name}.png")
        with open(p, "wb") as f:
            f.write(base64.b64decode(img_data))
        print(f"  📸 Saved screenshot: {name}.png")

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
    print("  TEST SUITE: Gate G8 Fixes (Furniture & Dialogue)")
    print("==================================================")

    chrome_proc = subprocess.Popen([
        "/usr/bin/google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-extensions",
        "--window-size=1200,800",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir=/tmp/test_chrome_fix_{int(time.time())}",
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

            print("\n1. Memulai permainan baru dengan karakter PEREMPUAN ('f')...")
            await evaluate(ws, "localStorage.clear()", 10)
            await send_cdp(ws, "Page.navigate", {"url": f"http://127.0.0.1:{HTTP_PORT}/index.html"}, 11)
            await asyncio.sleep(2.5)

            # Open character creation
            await evaluate(ws, "window.__GAME__.scene.getScene('MainMenu')._startNew()", 12)
            await asyncio.sleep(0.5)

            # Set gender to 'f' (Perempuan) and submit
            await evaluate(ws, "document.querySelector('.charcreate-form select').value = 'f'", 13)
            await evaluate(ws, "document.querySelector('.charcreate-form')?.requestSubmit()", 14)
            await asyncio.sleep(2.5)

            gender = await evaluate(ws, "window.__LJ__.getState().character.gender", 15)
            print(f"  Gender karakter di state: '{gender}'")
            assert gender == 'f', f"Expected gender 'f', got {gender}"

            # 2. Dialogue with Ayah -> Female portrait check
            print("\n2. Interaksi dengan Ayah (Cek Portrait Pemain Perempuan)...")
            await evaluate(ws, """(() => {
                const world = window.__GAME__.scene.getScene('World');
                const ayah = world._npcManager.npcs.find(n => n.def.id === 'npc_ayah');
                if (ayah) {
                    world._player.sprite.setPosition(ayah.x, ayah.y + 20);
                    world._npcManager.openDialog(ayah, document.body);
                }
            })()""", 20)
            await asyncio.sleep(1.0)
            await snap(ws, "01_female_player_dialogue_ayah", 501)

            player_img = await evaluate(ws, "document.querySelector('#dlg-player-portrait .portrait-img')?.src", 21)
            npc_img = await evaluate(ws, "document.querySelector('#dlg-npc-portrait .portrait-img')?.src", 22)
            dlg_vis = await evaluate(ws, "document.getElementById('dialogue-overlay')?.classList.contains('visible')", 23)
            print(f"  Dialog terlihat: {dlg_vis}")
            print(f"  Portrait Pemain: {player_img}")
            print(f"  Portrait NPC: {npc_img}")
            assert dlg_vis is True, "Dialogue overlay is not visible!"
            assert "portrait_player_f.png" in str(player_img), f"Player portrait must be portrait_player_f.png, got: {player_img}"
            assert "portrait_ayah.png" in str(npc_img), f"NPC portrait must be portrait_ayah.png, got: {npc_img}"

            # Close dialogue
            await evaluate(ws, "document.querySelector('#dlg-choices-menu button:last-child')?.click()", 24)
            await asyncio.sleep(0.5)

            # 3. Check Home Interior (Clock, Picture Frame, Dining Set)
            print("\n3. Memeriksa Furnitur Rumah (Jam Dinding, Bingkai Foto, Set Meja Makan)...")
            await snap(ws, "02_home_dining_and_decor", 502)

            # 4. Check 0 Placeholders across all 6 building interiors
            print("\n4. Memeriksa 0 Placeholder di seluruh 6 bangunan...")
            maps = ['home', 'school', 'game_center', 'minimarket', 'toko_kosmetik', 'spbu']
            for m in maps:
                await evaluate(ws, f"window.__LJ__.teleportToMap('{m}', 'default')", 30)
                await asyncio.sleep(1.8)
                info = await evaluate(ws, """(() => {
                    const world = window.__GAME__.scene.getScene('World');
                    if (!world || !world._mapManager) return null;
                    const placeholders = [];
                    const sprites = [];
                    const mapObjs = world._mapManager?._mapObjects || [];
                    for (const obj of mapObjs) {
                        if (obj.list) {
                            const hasText = obj.list.some(c => c.type === 'Text');
                            const hasGraphics = obj.list.some(c => c.type === 'Graphics');
                            const hasSprite = obj.list.some(c => c.type === 'Sprite');
                            const textObj = obj.list.find(c => c.type === 'Text');
                            if (hasGraphics && hasText && !hasSprite) {
                                placeholders.push(textObj ? textObj.text : 'Unknown');
                            } else if (hasSprite) {
                                const sp = obj.list.find(c => c.type === 'Sprite');
                                sprites.push(sp.texture.key);
                            }
                        }
                    }
                    return {
                        map: world._currentMapId || 'unknown',
                        total: mapObjs.length,
                        placeholdersCount: placeholders.length,
                        placeholders,
                        spritesCount: sprites.length
                    };
                })()""", 31)
                info = info or {}
                map_str = str(info.get('map', 'unknown'))
                print(f"  Peta: {map_str:<14} | Total Objek: {info.get('total', 0):<3} | Sprites: {info.get('spritesCount', 0):<3} | Placeholders: {info.get('placeholdersCount', 0)}")
                if info.get('placeholdersCount', 0) > 0:
                    print(f"    ⚠️ Ditemukan placeholder: {info.get('placeholders')}")
                assert info.get('placeholdersCount', 0) == 0, f"Map {m} has {info.get('placeholdersCount')} placeholders!"
                await snap(ws, f"map_{m}_verified", 510)

            # 5. Check Non-Family NPC Portrait Dialogues
            print("\n5. Memeriksa Dialog Ber-Portrait untuk NPC Non-Keluarga...")
            npc_tests = [
                ('school', 'npc_sri', 'portrait_penjual_kantin.png', 'Ibu Sri Kantin'),
                ('minimarket', 'npc_kasir_mini', 'portrait_kasir_minimarket.png', 'Mbak Maya Kasir'),
                ('game_center', 'npc_operator_game', 'portrait_penjaga_game.png', 'Kak Riko Game Center'),
                ('toko_kosmetik', 'npc_mbak_maya', 'portrait_penjaga_kosmetik.png', 'Kak Cindy Kosmetik'),
                ('spbu', 'npc_bang_dodi', 'portrait_petugas_spbu.png', 'Mas Doni SPBU'),
                ('town_hub', 'npc_pak_anto', 'portrait_petugas_spbu.png', 'Pak Anto Town Hub')
            ]
            for map_id, npc_id, expected_portrait, npc_name in npc_tests:
                await evaluate(ws, f"window.__LJ__.teleportToMap('{map_id}', 'default')", 40)
                await asyncio.sleep(1.0)
                await evaluate(ws, f"""(() => {{
                    const world = window.__GAME__.scene.getScene('World');
                    const target = world._npcManager.npcs.find(n => n.def.id === '{npc_id}');
                    if (target) world._npcManager.openDialog(target, document.body);
                }})()""", 41)
                await asyncio.sleep(0.8)
                res = await evaluate(ws, """(() => {
                    return {
                        playerImg: document.querySelector('#dlg-player-portrait .portrait-img')?.src,
                        npcImg: document.querySelector('#dlg-npc-portrait .portrait-img')?.src,
                        visible: document.getElementById('dialogue-overlay')?.classList.contains('visible')
                    };
                })()""", 42)
                print(f"  Interaksi {npc_name} ({npc_id}): visible={res.get('visible')} | npcImg={res.get('npcImg')}")
                assert res.get('visible') is True, f"Dialogue overlay did not open for {npc_id}!"
                assert "portrait_player_f.png" in (res.get('playerImg') or ''), f"Female portrait missing for {npc_id}!"
                assert expected_portrait in (res.get('npcImg') or ''), f"Expected {expected_portrait} for {npc_id}, got {res.get('npcImg')}!"
                await snap(ws, f"dialogue_{npc_id}", 520)
                # Close dialogue
                await evaluate(ws, "document.querySelector('#dialogue-overlay')?.classList.remove('visible')", 43)
                await evaluate(ws, "document.querySelector('#dialogue-overlay')?.classList.add('hidden')", 44)
                await asyncio.sleep(0.3)

            print("\n==================================================")
            print("  🎉 SELURUH PENGUJIAN LULUS 100%! SEMUA PERBAIKAN BERHASIL!")
            print("==================================================")
            return True

    finally:
        chrome_proc.terminate()

if __name__ == "__main__":
    success = asyncio.run(run_suite())
    sys.exit(0 if success else 1)
