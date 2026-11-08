import subprocess
import time
import json
import urllib.request
import websocket
import base64
import os

CDP_PORT = 9226
HTTP_PORT = 3843
DOCS_DIR = "game/docs/g8-fixes"
os.makedirs(DOCS_DIR, exist_ok=True)

chrome_proc = subprocess.Popen([
    "/usr/bin/google-chrome",
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--remote-allow-origins=*",
    f"--remote-debugging-port={CDP_PORT}",
    f"--user-data-dir=/tmp/test_chrome_fixes_{int(time.time())}",
    f"http://127.0.0.1:{HTTP_PORT}/index.html"
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

time.sleep(2.0)

try:
    tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json").read().decode("utf-8"))
    ws_url = tabs[0]["webSocketDebuggerUrl"]
    ws = websocket.create_connection(ws_url, timeout=15)

    msg_id = 0
    def send(method, params=None):
        global msg_id
        msg_id += 1
        payload = {"id": msg_id, "method": method}
        if params: payload["params"] = params
        ws.send(json.dumps(payload))
        while True:
            resp = json.loads(ws.recv())
            if resp.get("id") == msg_id:
                return resp.get("result", {})

    def evaluate(expr):
        res = send("Runtime.evaluate", {
            "expression": expr,
            "returnByValue": True,
            "awaitPromise": True
        })
        if "exceptionDetails" in res.get("result", {}):
            print("JS Error:", res["result"]["exceptionDetails"])
        return res.get("result", {}).get("result", {}).get("value")

    def snap(name):
        shot = send("Page.captureScreenshot", {"format": "png"})
        data = shot.get("data")
        if data:
            with open(os.path.join(DOCS_DIR, f"{name}.png"), "wb") as f:
                f.write(base64.b64decode(data))
            print(f"  📸 Saved screenshot: {name}.png")

    send("Page.enable")
    time.sleep(2.0)

    print("\n--- 1. Testing New Game Flow as Female Character ('f') ---")
    evaluate("""(() => {
        const mm = window.__GAME__.scene.getScene('MainMenu');
        mm._startNew();
    })()""")
    time.sleep(1.0)

    evaluate("""(() => {
        const sel = document.querySelector('.charcreate-form select');
        if (sel) {
            sel.value = 'f';
            sel.dispatchEvent(new Event('change'));
        }
        const inputs = document.querySelectorAll('.charcreate-form input');
        if (inputs[0]) inputs[0].value = 'Siti';
        if (inputs[1]) inputs[1].value = 'Pak Joko';
        if (inputs[2]) inputs[2].value = 'Bu Siti';
        const form = document.querySelector('.charcreate-form');
        if (form) {
            form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
        }
    })()""")
    time.sleep(2.5)

    # Verify state gender
    gender = evaluate("window.__LJ__?.getState()?.character?.gender")
    print(f"Character gender in state: '{gender}'")
    assert gender == 'f', f"Expected gender 'f', got {gender}"

    # Interact with Ayah
    print("\n--- 2. Interacting with Ayah (Testing Female Player Portrait) ---")
    evaluate("""(() => {
        const world = window.__GAME__.scene.getScene('World');
        const ayah = world._npcManager.npcs.find(n => n.def.id === 'npc_ayah');
        if (ayah) {
            world._player.sprite.setPosition(ayah.x, ayah.y + 20);
            world._npcManager.openDialog(ayah, document.body);
        }
    })()""")
    time.sleep(1.0)
    snap("01_female_player_dialogue_ayah")

    player_img_src = evaluate("document.querySelector('#dlg-player-portrait .portrait-img')?.src")
    npc_img_src = evaluate("document.querySelector('#dlg-npc-portrait .portrait-img')?.src")
    dlg_visible = evaluate("document.getElementById('dialogue-overlay')?.classList.contains('visible')")
    print(f"Dialogue visible: {dlg_visible}")
    print(f"Player portrait src: {player_img_src}")
    print(f"NPC portrait src: {npc_img_src}")
    assert "portrait_player_f.png" in str(player_img_src), f"Expected female portrait, got {player_img_src}"
    assert "portrait_ayah.png" in str(npc_img_src), f"Expected ayah portrait, got {npc_img_src}"

    # Close dialogue
    evaluate("document.querySelector('#dlg-choices-menu button:last-child')?.click()")
    time.sleep(0.5)

    print("\n--- 3. Testing Home Furniture (Clock, Frame, Dining Set) ---")
    snap("02_home_dining_and_decor")

    # Check 0 placeholders across all 6 maps
    maps = ['home', 'school', 'game_center', 'minimarket', 'toko_kosmetik', 'spbu']
    for m in maps:
        print(f"\n--- Checking Map: {m} ---")
        evaluate(f"window.__LJ__.teleportToMap('{m}', 'default')")
        time.sleep(1.2)
        
        info = evaluate("""(() => {
            const world = window.__GAME__.scene.getScene('World');
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
                map: world._currentMapId,
                total: mapObjs.length,
                placeholdersCount: placeholders.length,
                placeholders,
                spritesCount: sprites.length
            };
        })()""")
        print(f"  Map: {info.get('map')} | Total Objects: {info.get('total')} | Sprites: {info.get('spritesCount')} | Placeholders: {info.get('placeholdersCount')}")
        if info.get('placeholdersCount') > 0:
            print("  ⚠️ Placeholders found:", info.get('placeholders'))
        assert info.get('placeholdersCount') == 0, f"Map {m} has {info.get('placeholdersCount')} placeholders!"
        snap(f"map_{m}_verified")

    print("\n--- 4. Testing Non-Family NPC Portrait Dialogues ---")
    npc_tests = [
        ('school', 'npc_sri', 'portrait_penjual_kantin.png'),
        ('minimarket', 'npc_kasir_mini', 'portrait_kasir_minimarket.png'),
        ('game_center', 'npc_operator_game', 'portrait_penjaga_game.png'),
        ('toko_kosmetik', 'npc_mbak_maya', 'portrait_penjaga_kosmetik.png'),
        ('spbu', 'npc_bang_dodi', 'portrait_petugas_spbu.png'),
        ('town_hub', 'npc_pak_anto', 'portrait_petugas_spbu.png')
    ]
    for map_id, npc_id, expected_portrait in npc_tests:
        evaluate(f"window.__LJ__.teleportToMap('{map_id}', 'default')")
        time.sleep(1.0)
        res = evaluate(f"""(() => {{
            const world = window.__GAME__.scene.getScene('World');
            const target = world._npcManager.npcs.find(n => n.def.id === '{npc_id}');
            if (!target) return {{ error: 'NPC not found: {npc_id}' }};
            world._npcManager.openDialog(target, document.body);
            return {{
                opened: true,
                playerImg: document.querySelector('#dlg-player-portrait .portrait-img')?.src,
                npcImg: document.querySelector('#dlg-npc-portrait .portrait-img')?.src,
                visible: document.getElementById('dialogue-overlay')?.classList.contains('visible')
            }};
        }})()""")
        print(f"  NPC {npc_id} on {map_id}: {res}")
        assert res.get('visible') is True, f"Dialogue overlay did not open for {npc_id}!"
        assert "portrait_player_f.png" in (res.get('playerImg') or ''), f"Female player portrait missing for {npc_id}!"
        assert expected_portrait in (res.get('npcImg') or ''), f"Expected {expected_portrait} for {npc_id}, got {res.get('npcImg')}!"
        snap(f"dialogue_{npc_id}")
        # Close dialogue
        evaluate("document.querySelector('#dialogue-overlay')?.classList.remove('visible')")
        evaluate("document.querySelector('#dialogue-overlay')?.classList.add('hidden')")
        time.sleep(0.3)

    print("\n🎉 ALL TESTS PASSED! 100% SUCCESSFUL FIXES!")

finally:
    chrome_proc.terminate()
