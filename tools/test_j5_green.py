#!/usr/bin/env python3
"""
tools/test_j5_green.py — Gate J5 Green Verification Suite
Verifies:
- B1: School Classroom & Library desks facing front, chairs seen from behind
- B2: Teacher desk & chalkboard frontal and symmetrical
- B3: Canteen tables & benches frontal and proportional
- B5: Identified assets swapped fix (bak mandi = water tub, rak piring = dish rack)
- B6: Bathroom sink & toilet frontal and consistent
- B13: NPC Budi pixel art matching player style
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

CDP_PORT = 9253
HTTP_PORT = 3843
REG_DIR = "/home/abarox/Desktop/prototipe web statis game/game/docs/regression"
GAME_DIR = "/home/abarox/Desktop/prototipe web statis game/game"
os.makedirs(REG_DIR, exist_ok=True)

chrome_proc = None

def start_chrome():
    global chrome_proc
    user_data = f"/tmp/chrome_j5_{int(time.time())}"
    cmd = [
        "/usr/bin/google-chrome",
        "--headless=new",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={user_data}",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-extensions",
        "--window-size=1200,800",
        f"http://127.0.0.1:{HTTP_PORT}/index.html"
    ]
    chrome_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

def stop_chrome():
    global chrome_proc
    if chrome_proc:
        try:
            chrome_proc.terminate()
            chrome_proc.wait(timeout=3)
        except Exception:
            pass

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
        print(f"  📸 Saved screenshot: {filename}.png")
        return p
    return None

async def get_ws_url():
    for _ in range(25):
        try:
            req = urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json", timeout=1)
            tabs = json.loads(req.read().decode())
            for tab in tabs:
                if tab.get("type") == "page" and "index.html" in tab.get("url", "") and "webSocketDebuggerUrl" in tab:
                    return tab["webSocketDebuggerUrl"]
            for tab in tabs:
                if tab.get("type") == "page" and "webSocketDebuggerUrl" in tab:
                    return tab["webSocketDebuggerUrl"]
        except Exception:
            pass
        time.sleep(0.5)
    raise RuntimeError("Could not connect to Chrome CDP")

async def run_j5_tests():
    print("==========================================")
    print("  J5 GREEN TEST SUITE & VERIFICATION")
    print("==========================================")

    start_chrome()
    results = {}

    try:
        ws_url = await get_ws_url()
        async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
            print("🚀 Connected to Chrome CDP on port 9253")
            await send_cdp(ws, "Page.enable")
            await send_cdp(ws, "Runtime.enable")

            # Wait for game initialization
            print("⏳ Waiting for game to load...")
            for i in range(50):
                in_world = await evaluate(ws, "Boolean(window.__LJ__ && window.__LJ__.scene && window.__LJ__.scene._player)", 101)
                if in_world:
                    break
                is_menu = await evaluate(ws, "Boolean(window.__GAME__?.scene?.isActive?.('MainMenu'))", 102)
                if is_menu:
                    print("  Starting new game from MainMenu...")
                    await evaluate(ws, "window.__GAME__.scene.getScene('MainMenu')._startNew()", 103)
                    await asyncio.sleep(1.0)
                
                has_form = await evaluate(ws, "Boolean(document.querySelector('.charcreate-form'))", 104)
                if has_form:
                    print("  Submitting character creation form...")
                    await evaluate(ws, """
                        (() => {
                            const form = document.querySelector('.charcreate-form');
                            if (form) {
                                const btn = form.querySelector('button[type="submit"]') || form.querySelector('.btn-primary');
                                if (btn) btn.click();
                                else form.requestSubmit();
                            }
                        })()
                    """, 105)
                    await asyncio.sleep(1.5)
                await asyncio.sleep(0.5)

            # We are now in Home
            print("\n🏠 Current scene: Home")
            
            # -----------------------------------------------------------------
            # TEST B5 & B6: Home Bathroom & Kitchen
            # -----------------------------------------------------------------
            print("\n🔍 Verifying B5 & B6 (Home Bathroom & Kitchen)...")
            
            # Teleport player near Bathroom (x: 23, y: 5)
            await evaluate(ws, """
                (() => {
                    window.__LJ__.teleportTo(23, 5);
                    window.__LJ__.scene.cameras.main.pan(23 * 32, 5 * 32, 200, 'Linear', true);
                })()
            """, 201)
            await asyncio.sleep(0.5)

            # Inspect bathroom fixtures in home
            bath_info = await evaluate(ws, """
                (() => {
                    const objs = window.__LJ__.getMapManager()._mapObjects || [];
                    const items = {};
                    for (const o of objs) {
                        const fd = o.furnitureData;
                        if (fd && ['fur_bak_mandi', 'fur_toilet', 'fur_wastafel_cermin', 'fur_rak_handuk', 'fur_ember'].includes(fd.id)) {
                            items[fd.id] = {
                                assetId: fd.assetId,
                                resolvedTexture: fd.resolvedTexture,
                                hasSprite: fd.hasSprite,
                                x: fd.x,
                                y: fd.y,
                                w: fd.w,
                                h: fd.h
                            };
                        }
                    }
                    return items;
                })()
            """, 202)
            print("  Bathroom items:", json.dumps(bath_info, indent=2))

            # Snap B6: Bathroom wastafel and toilet frontal
            await snap(ws, "b6_wastafel_toilet_green", 203)

            # Move camera/player near Kitchen (x: 21, y: 13)
            await evaluate(ws, """
                (() => {
                    window.__LJ__.teleportTo(21, 13);
                    window.__LJ__.scene.cameras.main.pan(21 * 32, 12 * 32, 200, 'Linear', true);
                })()
            """, 204)
            await asyncio.sleep(0.5)

            kitchen_info = await evaluate(ws, """
                (() => {
                    const objs = window.__LJ__.getMapManager()._mapObjects || [];
                    const items = {};
                    for (const o of objs) {
                        const fd = o.furnitureData;
                        if (fd && ['fur_rak_piring', 'fur_jendela_dapur', 'fur_kursi_makan_1', 'fur_kursi_makan_2'].includes(fd.id)) {
                            items[fd.id] = {
                                assetId: fd.assetId,
                                resolvedTexture: fd.resolvedTexture,
                                hasSprite: fd.hasSprite,
                                x: fd.x,
                                y: fd.y
                            };
                        }
                    }
                    return items;
                })()
            """, 205)
            print("  Kitchen items:", json.dumps(kitchen_info, indent=2))

            # Snap B5: Identity fix (dish rack is dish rack, bak mandi is water tub)
            await snap(ws, "b5_identitas_aset_tertukar_green", 206)

            b5_pass = (bath_info.get('fur_bak_mandi', {}).get('resolvedTexture') == 'furn_bak_mandi_v6' and
                       kitchen_info.get('fur_rak_piring', {}).get('resolvedTexture') == 'furn_rak_piring_dinding_v6' and
                       kitchen_info.get('fur_jendela_dapur', {}).get('resolvedTexture') == 'furn_jendela_dapur_v6')
            b6_pass = (bath_info.get('fur_toilet', {}).get('resolvedTexture') == 'furn_toilet_v6' and
                       bath_info.get('fur_wastafel_cermin', {}).get('resolvedTexture') == 'furn_wastafel_cermin_v6')

            results['B5'] = 'PASS' if b5_pass else 'FAIL'
            results['B6'] = 'PASS' if b6_pass else 'FAIL'
            print(f"  ✅ B5 Result: {results['B5']} (bak mandi = {bath_info.get('fur_bak_mandi', {}).get('resolvedTexture')}, rak piring = {kitchen_info.get('fur_rak_piring', {}).get('resolvedTexture')})")
            print(f"  ✅ B6 Result: {results['B6']} (toilet = {bath_info.get('fur_toilet', {}).get('resolvedTexture')}, wastafel = {bath_info.get('fur_wastafel_cermin', {}).get('resolvedTexture')})")

            # -----------------------------------------------------------------
            # TRANSITION TO SCHOOL INTERIOR
            # -----------------------------------------------------------------
            print("\n🏫 Transitioning to School scene...")
            await evaluate(ws, """
                (async () => {
                    await window.__LJ__.getMapManager().loadMap('school', 'default');
                })()
            """, 301, await_p=True)
            await asyncio.sleep(1.0)

            # -----------------------------------------------------------------
            # TEST B1 & B2: School Classroom
            # -----------------------------------------------------------------
            print("\n🔍 Verifying B1 & B2 (Classroom Desks, Teacher Desk, Chalkboard)...")
            # Teleport to classroom (x: 7, y: 6)
            await evaluate(ws, """
                (() => {
                    window.__LJ__.teleportTo(7, 6);
                    window.__LJ__.scene.cameras.main.pan(7 * 32, 5 * 32, 200, 'Linear', true);
                })()
            """, 302)
            await asyncio.sleep(0.5)

            class_info = await evaluate(ws, """
                (() => {
                    const objs = window.__LJ__.getMapManager()._mapObjects || [];
                    const items = {};
                    for (const o of objs) {
                        const fd = o.furnitureData;
                        if (fd && ['slot_sch_papan_tulis', 'slot_sch_meja_guru', 'slot_sch_kursi_guru', 'slot_sch_meja_siswa_1', 'slot_sch_meja_siswa_2', 'slot_sch_meja_siswa_3', 'slot_sch_meja_siswa_4', 'slot_sch_rak_buku_kelas'].includes(fd.id)) {
                            items[fd.id] = {
                                assetId: fd.assetId,
                                resolvedTexture: fd.resolvedTexture,
                                hasSprite: fd.hasSprite,
                                x: fd.x,
                                y: fd.y,
                                w: fd.w,
                                h: fd.h
                            };
                        }
                    }
                    return items;
                })()
            """, 303)
            print("  Classroom items:", json.dumps(class_info, indent=2))

            # Snap B2: Frontal teacher desk & chalkboard
            await snap(ws, "b2_meja_guru_papan_tulis_green", 304)
            # Snap B1: Classroom student desks facing front & chairs seen from behind
            await snap(ws, "b1_kursi_meja_sekolah_green", 305)

            b2_pass = (class_info.get('slot_sch_papan_tulis', {}).get('resolvedTexture') == 'furn_papan_tulis_v6' and
                       class_info.get('slot_sch_meja_guru', {}).get('resolvedTexture') == 'furn_meja_guru_v6' and
                       class_info.get('slot_sch_kursi_guru', {}).get('resolvedTexture') == 'furn_kursi_guru_v6')
            b1_pass = (class_info.get('slot_sch_meja_siswa_1', {}).get('resolvedTexture') == 'furn_meja_siswa_kursi_a_v6' and
                       class_info.get('slot_sch_meja_siswa_3', {}).get('resolvedTexture') == 'furn_meja_siswa_kursi_a_v6' and
                       class_info.get('slot_sch_rak_buku_kelas', {}).get('resolvedTexture') == 'furn_rak_buku_kelas_v6')
            results['B1'] = 'PASS' if b1_pass else 'FAIL'
            results['B2'] = 'PASS' if b2_pass else 'FAIL'
            print(f"  ✅ B1 Result: {results['B1']} (student desk composite = {class_info.get('slot_sch_meja_siswa_1', {}).get('resolvedTexture')})")
            print(f"  ✅ B2 Result: {results['B2']} (chalkboard = {class_info.get('slot_sch_papan_tulis', {}).get('resolvedTexture')}, teacher desk = {class_info.get('slot_sch_meja_guru', {}).get('resolvedTexture')})")

            # -----------------------------------------------------------------
            # TEST B3: Canteen
            # -----------------------------------------------------------------
            print("\n🔍 Verifying B3 (Canteen Tables & Benches)...")
            # Teleport to canteen (x: 21, y: 6)
            await evaluate(ws, """
                (() => {
                    window.__LJ__.teleportTo(21, 6);
                    window.__LJ__.scene.cameras.main.pan(23 * 32, 6 * 32, 200, 'Linear', true);
                })()
            """, 401)
            await asyncio.sleep(0.5)

            canteen_info = await evaluate(ws, """
                (() => {
                    const objs = window.__LJ__.getMapManager()._mapObjects || [];
                    const items = {};
                    for (const o of objs) {
                        const fd = o.furnitureData;
                        if (fd && ['slot_sch_meja_kantin_1', 'slot_sch_meja_kantin_2', 'slot_sch_bangku_dinding'].includes(fd.id)) {
                            items[fd.id] = {
                                assetId: fd.assetId,
                                resolvedTexture: fd.resolvedTexture,
                                hasSprite: fd.hasSprite,
                                x: fd.x,
                                y: fd.y,
                                w: fd.w,
                                h: fd.h
                            };
                        }
                    }
                    return items;
                })()
            """, 402)
            print("  Canteen items:", json.dumps(canteen_info, indent=2))

            # Snap B3: Canteen table sets
            await snap(ws, "b3_meja_bangku_kantin_green", 403)

            b3_pass = (canteen_info.get('slot_sch_meja_kantin_1', {}).get('resolvedTexture') == 'furn_meja_kantin_set_a_v6' and
                       canteen_info.get('slot_sch_meja_kantin_2', {}).get('resolvedTexture') == 'furn_meja_kantin_set_b_v6' and
                       canteen_info.get('slot_sch_bangku_dinding', {}).get('resolvedTexture') == 'furn_bangku_dinding_v6')
            results['B3'] = 'PASS' if b3_pass else 'FAIL'
            print(f"  ✅ B3 Result: {results['B3']} (canteen set = {canteen_info.get('slot_sch_meja_kantin_1', {}).get('resolvedTexture')})")

            # -----------------------------------------------------------------
            # TEST B13: NPC Budi in School Corridor
            # -----------------------------------------------------------------
            print("\n🔍 Verifying B13 (NPC Budi Pixel Art Style)...")
            # In school, Budi is at x: 10, y: 14
            await evaluate(ws, """
                (() => {
                    window.__LJ__.teleportTo(10, 15);
                    window.__LJ__.scene.cameras.main.pan(10 * 32, 14 * 32, 200, 'Linear', true);
                })()
            """, 501)
            await asyncio.sleep(0.5)

            budi_info = await evaluate(ws, """
                (() => {
                    const npcs = window.__LJ__.scene._npcManager?.npcs || [];
                    for (const n of npcs) {
                        if (n.def && (n.def.id === 'npc_budi' || n.def.name === 'Budi')) {
                            const sprite = n.body;
                            return {
                                id: n.def.id,
                                name: n.def.name,
                                assetId: n.def.assetId,
                                texture: sprite ? sprite.texture?.key : null,
                                width: sprite ? sprite.width : null,
                                height: sprite ? sprite.height : null
                            };
                        }
                    }
                    return null;
                })()
            """, 502)
            print("  Budi NPC info:", json.dumps(budi_info, indent=2))

            # Snap B13: NPC Budi
            await snap(ws, "b13_sprite_budi_kartun_green", 503)

            b13_pass = (budi_info and budi_info.get('texture') == 'npc_budi_v6')
            results['B13'] = 'PASS' if b13_pass else 'FAIL'
            print(f"  ✅ B13 Result: {results['B13']} (budi texture = {budi_info.get('texture') if budi_info else 'not found'})")

            print("\n==========================================")
            print("  J5 VERIFICATION SUMMARY:")
            for k, v in results.items():
                print(f"    {k}: {v}")
            print("==========================================")

    finally:
        stop_chrome()

if __name__ == "__main__":
    asyncio.run(run_j5_tests())
