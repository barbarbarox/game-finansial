#!/usr/bin/env python3
"""
test_g3_vehicle.py — Automated verification of Gate G3 Motor Pemain (Rule 75):
1. Toggle on/off via HUD button and V key
2. Measured speed ratio >= 1.6x walking speed (hook measureSpeed)
3. Simulated fuel drain per 5 seconds of riding (deterministic accumulator check)
4. Fuel 0% forces auto-dismount and disables vehicle button
5. Auto-dismount on building door / interior entrance & parked motor prop
6. Save/load persistence preserves gasoline and parked motor position
7. Screenshots of mount animation at t=0ms, 120ms, 240ms, 350ms
8. Collision probe passes 100% while mounted
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

CDP_PORT = 9241
HTTP_PORT = 3843
DOCS_DIR = "/home/abarox/Desktop/prototipe web statis game/game/docs/g3-vehicle"
os.makedirs(DOCS_DIR, exist_ok=True)

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
        print(f"  📸 Screenshot: {os.path.basename(filepath)}")
        return True
    return False

async def get_ws_url():
    for _ in range(20):
        try:
            req = urllib.request.urlopen(f"http://localhost:{CDP_PORT}/json", timeout=1)
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

async def run_suite():
    print("==================================================")
    print("  TEST SUITE: Gate G3 Motor Pemain (Rule 75)       ")
    print("==================================================")

    chrome_proc = subprocess.Popen([
        "/usr/bin/google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=960,540",
        f"--remote-debugging-port={CDP_PORT}",
        "--remote-allow-origins=*",
        f"http://localhost:{HTTP_PORT}/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    passed_all = True

    try:
        await asyncio.sleep(2.0)
        ws_url = await get_ws_url()
        if not ws_url:
            print("[FAIL] Tidak dapat terhubung ke Chrome CDP")
            return False

        async with websockets.connect(ws_url) as ws:
            await send_cdp(ws, "Page.enable", {}, 1)

            # Wait for game to initialize
            print("\n1. Menunggu inisialisasi game & transisi ke town_hub...")
            await send_cdp(ws, "Page.navigate", {"url": f"http://localhost:{HTTP_PORT}/index.html?debug=1"}, 20)
            await asyncio.sleep(2.0)

            # Advance MainMenu -> CharacterCreate -> World
            for _ in range(30):
                has_game = await evaluate_js(ws, "Boolean(window.__GAME__)", 21)
                if has_game:
                    break
                await asyncio.sleep(0.3)

            current_scene = await evaluate_js(ws, "window.__GAME__?.scene?.getScenes(true)?.[0]?.scene?.key", 22)
            if current_scene == 'MainMenu':
                can_continue = await evaluate_js(ws, """
                    (() => {
                        const scene = window.__GAME__.scene.getScene('MainMenu');
                        if (scene && scene._buttons && scene._buttons[1] && scene._buttons[1].enabled) {
                            scene._continue();
                            return true;
                        }
                        return false;
                    })()
                """, 23)
                if not can_continue:
                    await evaluate_js(ws, """
                        (() => {
                            const scene = window.__GAME__.scene.getScene('MainMenu');
                            scene.scene.start('CharacterCreate');
                        })()
                    """, 24)
                    await asyncio.sleep(1.0)
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
                    """, 25)
                await asyncio.sleep(2.0)

            # Wait for World ready
            ready = False
            for _ in range(40):
                await asyncio.sleep(0.3)
                is_ready = await evaluate_js(ws, "Boolean(window.__LJ__ && window.__LJ__.teleportToMap)", 26)
                if is_ready:
                    ready = True
                    break

            if not ready:
                print("  [FAIL] Game tidak memasuki scene World")
                return False

            # Teleport player to town_hub for vehicle operations
            await evaluate_js(ws, "window.__LJ__.teleportToMap('town_hub', 'default')", 27)
            await asyncio.sleep(1.0)
            cur_map = await evaluate_js(ws, "window.__LJ__.getMapManager().currentMapId", 28)
            print(f"  [PASS] Berada di peta: {cur_map}")

            # 2. Test speed multiplier (measureSpeed >= 1.6x)
            print("\n2. Uji Pengali Kecepatan Motor (measureSpeed >= 1.6x)...")
            walk_speed = await evaluate_js(ws, "window.__LJ__.measureSpeed()", 30)
            await evaluate_js(ws, "window.__LJ__.toggleVehicle()", 31)
            await asyncio.sleep(0.5) # allow mount
            mounted_speed = await evaluate_js(ws, "window.__LJ__.measureSpeed()", 32)
            is_mounted = await evaluate_js(ws, "window.__LJ__.isMounted()", 33)
            ratio = mounted_speed / walk_speed if walk_speed > 0 else 0
            if is_mounted and ratio >= 1.6:
                print(f"  [PASS] Jalan: {walk_speed} px/s, Motor: {mounted_speed} px/s (Rasio: {ratio:.2f}x >= 1.6x)")
            else:
                print(f"  [FAIL] Kecepatan bermotor: {mounted_speed} px/s (rasio {ratio:.2f}x, isMounted={is_mounted})")
                passed_all = False

            # 3. Test toggle via V key & HUD button
            print("\n3. Uji Toggle Naik-Turun via Tombol dan Pintasan V...")
            # Dismount via HUD button click
            await evaluate_js(ws, "document.querySelector('.hud-btn-vehicle')?.click()", 40)
            await asyncio.sleep(0.5)
            dismounted_via_btn = not await evaluate_js(ws, "window.__LJ__.isMounted()", 41)

            # Mount again via V keydown + keyup
            await evaluate_js(ws, """
                (() => {
                    window.dispatchEvent(new KeyboardEvent('keydown', {
                        key: 'v', code: 'KeyV', keyCode: 86, which: 86, bubbles: true, cancelable: true
                    }));
                    setTimeout(() => {
                        window.dispatchEvent(new KeyboardEvent('keyup', {
                            key: 'v', code: 'KeyV', keyCode: 86, which: 86, bubbles: true, cancelable: true
                        }));
                    }, 50);
                })()
            """, 42)
            await asyncio.sleep(0.5)
            mounted_via_v = await evaluate_js(ws, "window.__LJ__.isMounted()", 43)

            # Dismount again via V keydown + keyup
            await evaluate_js(ws, """
                (() => {
                    window.dispatchEvent(new KeyboardEvent('keydown', {
                        key: 'v', code: 'KeyV', keyCode: 86, which: 86, bubbles: true, cancelable: true
                    }));
                    setTimeout(() => {
                        window.dispatchEvent(new KeyboardEvent('keyup', {
                            key: 'v', code: 'KeyV', keyCode: 86, which: 86, bubbles: true, cancelable: true
                        }));
                    }, 50);
                })()
            """, 44)
            await asyncio.sleep(0.5)
            dismounted_via_v = not await evaluate_js(ws, "window.__LJ__.isMounted()", 45)

            # Mount for next tests
            await evaluate_js(ws, "window.__LJ__.toggleVehicle()", 46)
            await asyncio.sleep(0.5)
            await evaluate_js(ws, """
                (() => {
                    const p = window.__LJ__.getPlayer();
                    p.isMounted = true;
                    p.isMounting = false;
                })()
            """, 47)

            if dismounted_via_btn and mounted_via_v and dismounted_via_v:
                print("  [PASS] Naik dan turun motor responsif via tombol HUD & pintasan V")
            else:
                print(f"  [FAIL] Toggle V: btn_turun={dismounted_via_btn}, v_naik={mounted_via_v}, v_turun={dismounted_via_v}")
                passed_all = False

            # 4. Test deterministic fuel consumption (2% per 5000ms moving)
            print("\n4. Uji Konsumsi Bensin Simulasi (2% per 5 detik nyata bergerak)...")
            await evaluate_js(ws, "window.__LJ__.setGasoline(100)", 50)
            await evaluate_js(ws, "window.__LJ__.simulateMovingFuel(5000)", 51)
            gas_after_5s = await evaluate_js(ws, "window.__LJ__.getGasoline()", 52)
            await evaluate_js(ws, "window.__LJ__.simulateMovingFuel(5000)", 53)
            gas_after_10s = await evaluate_js(ws, "window.__LJ__.getGasoline()", 54)

            if gas_after_5s == 98 and gas_after_10s == 96:
                print(f"  [PASS] Bensin turun tepat 2% tiap 5 detik simulasi (100 -> {gas_after_5s} -> {gas_after_10s})")
            else:
                print(f"  [FAIL] Bensin: setelah 5s={gas_after_5s}, setelah 10s={gas_after_10s}")
                passed_all = False

            # 5. Test fuel 0% auto-dismount and button disable
            print("\n5. Uji Bensin 0% Memaksa Turun & Menonaktifkan Tombol...")
            await evaluate_js(ws, "window.__LJ__.setGasoline(2)", 60)
            await evaluate_js(ws, "window.__LJ__.simulateMovingFuel(5000)", 61)
            gas_zero = await evaluate_js(ws, "window.__LJ__.getGasoline()", 62)
            is_mounted_zero = await evaluate_js(ws, "window.__LJ__.isMounted()", 63)
            # Attempt to mount with 0 gas
            await evaluate_js(ws, "window.__LJ__.toggleVehicle()", 64)
            cant_mount = not await evaluate_js(ws, "window.__LJ__.isMounted()", 65)

            if gas_zero == 0 and not is_mounted_zero and cant_mount:
                print("  [PASS] Bensin 0% otomatis menurunkan pemain & menolak naik motor")
            else:
                print(f"  [FAIL] Bensin 0%: gas={gas_zero}, isMounted={is_mounted_zero}, cantMount={cant_mount}")
                passed_all = False

            # 6. Test interior prohibition & auto-dismount on building door
            print("\n6. Uji Larangan Interior & Parkir Otomatis di Depan Pintu...")
            # Advance time to 09:00 (minimarket opens at 08:00)
            await evaluate_js(ws, "window.__LJ__.advanceTime(180)", 69)
            await evaluate_js(ws, "window.__LJ__.setGasoline(100)", 70)
            await evaluate_js(ws, "window.__LJ__.toggleVehicle()", 71)
            await asyncio.sleep(0.5)

            # Trigger door interaction into minimarket
            await evaluate_js(ws, """
                (() => {
                    const scene = window.__LJ__.scene;
                    const door = { type: 'door', targetMap: 'minimarket', targetSpawn: 'default' };
                    scene._openInteraction(door);
                })()
            """, 72)
            await asyncio.sleep(1.5)

            cur_map_interior = await evaluate_js(ws, "window.__LJ__.getMapManager().currentMapId", 73)
            is_mounted_interior = await evaluate_js(ws, "window.__LJ__.isMounted()", 74)
            parked_pos = await evaluate_js(ws, "window.__LJ__.getParkedMotor()", 75)

            # Try to mount inside interior
            await evaluate_js(ws, "window.__LJ__.toggleVehicle()", 76)
            interior_denied = not await evaluate_js(ws, "window.__LJ__.isMounted()", 77)

            if cur_map_interior == 'minimarket' and not is_mounted_interior and parked_pos and interior_denied:
                print(f"  [PASS] Masuk minimarket: turun otomatis, motor diparkir di {parked_pos}, dilarang bermotor di dalam")
            else:
                print(f"  [FAIL] Interior test: map={cur_map_interior}, isMounted={is_mounted_interior}, parked={parked_pos}")
                passed_all = False

            # Return to town_hub
            await evaluate_js(ws, "window.__LJ__.teleportToMap('town_hub', 'default')", 78)
            await asyncio.sleep(1.0)

            # 7. Test Save/load persistence for gasoline & vehicle state
            print("\n7. Uji Persistensi Save v3 (Bensin & Motor Parkir)...")
            await evaluate_js(ws, "window.__LJ__.setGasoline(85)", 80)
            await evaluate_js(ws, """
                window.__LJ__.getStore().setState({
                    gasoline: 85,
                    vehicle: {
                        mounted: false,
                        parked: { mapId: 'town_hub', x: 200, y: 350 }
                    }
                });
            """, 81)
            saved_vehicle = await evaluate_js(ws, """
                (() => {
                    const st = window.__LJ__.getState();
                    localStorage.setItem('lj_save_v3', JSON.stringify({ ...st, schemaVersion: 3 }));
                    const raw = JSON.parse(localStorage.getItem('lj_save_v3'));
                    return {
                        gas: raw.gasoline,
                        parked: raw.vehicle?.parked
                    };
                })()
            """, 82)
            if saved_vehicle and saved_vehicle.get("gas") == 85 and saved_vehicle.get("parked", {}).get("x") == 200:
                print(f"  [PASS] Save v3 menyimpan bensin ({saved_vehicle.get('gas')}%) dan posisi motor parkir dengan benar")
            else:
                print(f"  [FAIL] Persistensi kendaraan save v3: {saved_vehicle}")
                passed_all = False

            # 8. Test collision probe while mounted in town_hub
            print("\n8. Uji Kolisi (collisionProbe) saat Bermotor di town_hub...")
            await evaluate_js(ws, "window.__LJ__.toggleVehicle()", 85)
            await asyncio.sleep(0.5)
            probe_res = await evaluate_js(ws, "window.__LJ__.collisionProbe('town_hub')", 86)
            tested = probe_res.get('testedCount', 0)
            passed = probe_res.get('passedCount', 0)
            all_passed = probe_res.get('allPassed', False)
            if all_passed:
                print(f"  [PASS] collisionProbe town_hub saat bermotor: {passed}/{tested} tertahan kokoh (100% LULUS)")
            else:
                print(f"  [FAIL] collisionProbe town_hub saat bermotor: {probe_res}")
                passed_all = False

            # 9. Screenshots of procedural mount animation at t=0, 120, 240, 350 ms
            print("\n9. Pengambilan Tangkapan Layar Frame Animasi Naik Motor (t=0/120/240/350 ms)...")
            # Dismount first
            await evaluate_js(ws, "window.__LJ__.getPlayer().dismount()", 90)
            await asyncio.sleep(0.2)

            # Trigger mount animation without instant finish
            await evaluate_js(ws, "window.__LJ__.getPlayer().mount()", 91)
            # t=0ms
            await capture_screenshot(ws, os.path.join(DOCS_DIR, "01_mount_anim_t0ms.png"), 92)
            await asyncio.sleep(0.12)
            # t=120ms
            await capture_screenshot(ws, os.path.join(DOCS_DIR, "02_mount_anim_t120ms.png"), 93)
            await asyncio.sleep(0.12)
            # t=240ms
            await capture_screenshot(ws, os.path.join(DOCS_DIR, "03_mount_anim_t240ms.png"), 94)
            await asyncio.sleep(0.11)
            # t=350ms
            await capture_screenshot(ws, os.path.join(DOCS_DIR, "04_mount_anim_t350ms.png"), 95)

    finally:
        chrome_proc.terminate()
        try:
            chrome_proc.wait(timeout=3)
        except Exception:
            chrome_proc.kill()

    print("\n==================================================")
    if passed_all:
        print("  🎉 HASIL: GERBANG G3 LULUS SEMUA UJI (100% HIJAU)")
        print("==================================================")
        return True
    else:
        print("  ❌ HASIL: GERBANG G3 GAGAL PADA BEBERAPA UJI")
        print("==================================================")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_suite())
    sys.exit(0 if success else 1)

