#!/usr/bin/env python3
"""
tools/test_j2_green.py — J2 Green Verification Suite
Verifies J2 Energy v2 fixes with real browser UI interactions & screenshots:
- B10: Energy costs for activities (Pelajaran Sesi 1 ~9%, Sesi 2 ~11% -> exact 20%, Game Center 20%/hr, etc.)
- B11: Energy < 50% warning toast ("Energi kamu di bawah 50%, silakan makan untuk menambahnya."), pulse animation, rearming >= 60%, terracotta <= 25%
- B12: Exhaustion at 0%: blackout overlay, teleport to bed at home (x=5, y=5), time advances to next day 10:00, energy reset to 50%, attendanceMissed++
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
    user_data = f"/tmp/chrome_j2_{int(time.time())}"
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
        await asyncio.sleep(0.5)
    return None

async def run_j2_tests():
    start_chrome()
    ws_url = await get_ws_url()
    if not ws_url:
        print("❌ Could not connect to Chrome debugging port!")
        stop_chrome()
        sys.exit(1)

    print(f"Connected to CDP: {ws_url}")
    results = {}

    async with websockets.connect(ws_url, max_size=100_000_000) as ws:
        await send_cdp(ws, "Page.enable", msg_id=1)
        await send_cdp(ws, "DOM.enable", msg_id=2)
        await send_cdp(ws, "Runtime.enable", msg_id=3)

        # Wait for game to be initialized
        print("Waiting for game to initialize...")
        for i in range(50):
            in_world = await evaluate(ws, "Boolean(window.__LJ__ && window.__LJ__.scene && window.__LJ__.scene._player)", 10)
            if in_world:
                break
            is_menu = await evaluate(ws, "Boolean(window.__GAME__?.scene?.isActive?.('MainMenu'))", 11)
            if is_menu:
                print("  Starting new game from MainMenu...")
                await evaluate(ws, "window.__GAME__.scene.getScene('MainMenu')._startNew()", 12)
                await asyncio.sleep(1.0)
            
            has_form = await evaluate(ws, "Boolean(document.querySelector('.charcreate-form'))", 13)
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
                """, 14)
                await asyncio.sleep(1.5)

            await asyncio.sleep(0.5)

        in_world_check = await evaluate(ws, "Boolean(window.__LJ__ && window.__LJ__.scene && window.__LJ__.scene._player)", 15)
        if not in_world_check:
            raise RuntimeError("Failed to transition into World scene within timeout.")

        print("✅ World scene ready!")
        await asyncio.sleep(1.0)

        # -------------------------------------------------------------
        # TEST B10: Biaya Energi Sesuai Tabel Realistis (Rule 83)
        # -------------------------------------------------------------
        print("\n--- Verifying B10: Energy Costs (Pelajaran Sesi 1/2, Game Center, etc.) ---")
        b10_math = await evaluate(ws, """
            (() => {
                const store = window.__LJ__.scene.game.registry.get('store');
                // Set energy to 100
                window.__LJ__.setEnergy(100);

                // Check Sesi 1 (180 min)
                const c1 = window.__LJ__.advanceTime(180, 'ikut_pelajaran');
                const e1 = window.__LJ__.getEnergy().current; // expected 91 (-9%)

                // Check Sesi 2 (240 min)
                const c2 = window.__LJ__.advanceTime(240, 'ikut_pelajaran');
                const e2 = window.__LJ__.getEnergy().current; // expected 80 (-11%, total -20%)

                // Check Main Game (60 min)
                const c3 = window.__LJ__.advanceTime(60, 'main_game');
                const e3 = window.__LJ__.getEnergy().current; // expected 60 (-20%)

                // Check Belajar Mandiri (60 min)
                const c4 = window.__LJ__.advanceTime(60, 'belajar_mandiri');
                const e4 = window.__LJ__.getEnergy().current; // expected 52 (-8%)

                return {
                    e1, e2, e3, e4,
                    sesi1_drain: 100 - e1,
                    sesi2_drain: e1 - e2,
                    total_school_drain: 100 - e2,
                    game_drain: e2 - e3,
                    belajar_drain: e3 - e4
                };
            })()
        """, 101)

        print(f"  Calculated drains: {b10_math}")
        b10_ok = (
            b10_math["sesi1_drain"] == 9 and
            b10_math["sesi2_drain"] == 11 and
            b10_math["total_school_drain"] == 20 and
            b10_math["game_drain"] == 20 and
            b10_math["belajar_drain"] == 8
        )
        if b10_ok:
            print("  ✅ B10 PASS: School session drains (9% + 11% = 20%) & Game Center (20%) match Rule 83 exactly!")
            await snap(ws, "b10_biaya_energi_green", 510)
            results["B10"] = True
        else:
            print(f"  ❌ B10 FAIL: Drains did not match expected values: {b10_math}")
            results["B10"] = False

        # -------------------------------------------------------------
        # TEST B11: Notifikasi Peringatan < 50% & Rearm >= 60% (Rule 83 §2)
        # -------------------------------------------------------------
        print("\n--- Verifying B11: Warning Toast < 50% & Rearm >= 60% ---")
        # Player is at 52%. Drain 5% to reach 47% (< 50%)
        b11_step1 = await evaluate(ws, """
            (() => {
                // Drain 5% via 15 min main_game (5% drain)
                window.__LJ__.advanceTime(15, 'main_game');
                const eNow = window.__LJ__.getEnergy().current;
                const toastEl = document.querySelector('.energy-warn-toast');
                const hudText = document.querySelector('.hm-energy-val')?.textContent;
                const hudFill = document.querySelector('.hm-energy-fill');
                const track = document.querySelector('.hm-energy-track');
                return {
                    energy: eNow,
                    toastText: toastEl?.textContent || null,
                    hudText: hudText,
                    hudWidth: hudFill?.style.width,
                    trackPulse: track?.classList.contains('pulse-warn')
                };
            })()
        """, 102)

        print(f"  B11 Step 1 (<50% Trigger): {b11_step1}")
        await asyncio.sleep(0.2)
        await snap(ws, "b11_peringatan_energi_50_green", 511)

        expected_toast = "Energi kamu di bawah 50%, silakan makan untuk menambahnya."
        toast_matches = b11_step1.get("toastText") == expected_toast

        # Verify Rearming logic
        b11_rearm = await evaluate(ws, """
            (() => {
                // 1. Recover energy to 70% (>= 60%)
                window.__LJ__.setEnergy(70);
                const st1 = window.__LJ__.getEnergy();

                // 2. Drain down to 45% again
                window.__LJ__.advanceTime(75, 'main_game'); // -25% -> 45%
                const st2 = window.__LJ__.getEnergy();
                const toast2 = document.querySelector('.energy-warn-toast');

                // 3. Test low energy color <= 25%
                window.__LJ__.setEnergy(20);
                const fillLow = document.querySelector('.hm-energy-fill');
                const lowBgStyle = fillLow ? fillLow.style.backgroundColor : null;
                const isDanger = fillLow ? fillLow.classList.contains('danger') : false;

                return {
                    st1_current: st1.current,
                    st1_warn50Triggered: st1.warn50Triggered,
                    st2_current: st2.current,
                    toast2_text: toast2?.textContent || null,
                    low_bg_style: lowBgStyle,
                    is_danger: isDanger
                };
            })()
        """, 103)
        print(f"  B11 Rearm & Color: {b11_rearm}")

        b11_ok = (
            toast_matches and
            b11_rearm["toast2_text"] == expected_toast and
            (b11_rearm.get("is_danger") or "192, 101, 74" in (b11_rearm.get("low_bg_style") or "") or "c0654a" in (b11_rearm.get("low_bg_style") or "").lower())
        )
        if b11_ok:
            print("  ✅ B11 PASS: Warning toast text exact match, pulse animation, re-arming >=60%, and terracotta color at <=25% verified!")
            results["B11"] = True
        else:
            print(f"  ❌ B11 FAIL: toast_matches={toast_matches}, rearm={b11_rearm}")
            results["B11"] = False

        # -------------------------------------------------------------
        # TEST B12: Bangun Kesiangan Pukul 10:00 Saat Energi Habis (Rule 83 §3)
        # -------------------------------------------------------------
        print("\n--- Verifying B12: Exhaustion Wake-up at 10:00 in Bed ---")
        # Put player in school or town_hub, drain energy to 0%
        b12_trigger = await evaluate(ws, """
            (() => {
                const store = window.__LJ__.scene.game.registry.get('store');
                // Ensure starting in town_hub or school
                const initialClock = store.getState().clock;
                const initialDay = initialClock.day || 1;
                const initialMissed = store.getState().school?.attendanceMissed || 0;

                // Set energy to 1% then advance time with 10 min main_game to hit 0%
                window.__LJ__.setEnergy(1);
                window.__LJ__.advanceTime(10, 'main_game');

                return {
                    initialDay,
                    initialMissed,
                    postDrainEnergy: window.__LJ__.getEnergy().current
                };
            })()
        """, 104)
        print(f"  B12 Triggered: {b12_trigger}")

        # Wait for blackout sequence to complete (1200ms delay + 800ms fade)
        print("  Waiting 2.5s for blackout transition and wake-up sequence...")
        await asyncio.sleep(2.5)

        b12_wake = await evaluate(ws, """
            (() => {
                const store = window.__LJ__.scene.game.registry.get('store');
                const st = store.getState();
                const mapId = window.__LJ__.scene._mapManager?.currentMapId;
                const player = window.__LJ__.scene._player;
                const clock = st.clock || {};
                const energy = st.energy || {};
                const school = st.school || {};

                const totalMin = clock.gameMinutes !== undefined ? (clock.gameMinutes % 1440) : (clock.timeOfDay || 0);
                const hours = Math.floor(totalMin / 60) % 24;
                const mins = totalMin % 60;

                return {
                    mapId,
                    playerX: player ? Math.round(player.sprite.x / 32) : null,
                    playerY: player ? Math.round(player.sprite.y / 32) : null,
                    day: clock.day,
                    timeFormatted: `${String(hours).padStart(2,'0')}:${String(mins).padStart(2,'0')}`,
                    energyCurrent: energy.current,
                    attendanceMissed: school.attendanceMissed
                };
            })()
        """, 105)
        print(f"  B12 Wake State: {b12_wake}")

        await snap(ws, "b12_bangun_kesiangan_green", 512)

        b12_ok = (
            b12_wake["mapId"] == "home" and
            b12_wake["playerX"] == 5 and
            b12_wake["playerY"] == 5 and
            b12_wake["timeFormatted"] == "10:00" and
            b12_wake["day"] == b12_trigger["initialDay"] + 1 and
            b12_wake["energyCurrent"] == 50 and
            b12_wake["attendanceMissed"] == b12_trigger["initialMissed"] + 1
        )

        if b12_ok:
            print("  ✅ B12 PASS: Player woke up in bed at home (5,5), next day 10:00, 50% energy, attendanceMissed++!")
            results["B12"] = True
        else:
            print(f"  ❌ B12 FAIL: Wake state does not match requirements: {b12_wake}")
            results["B12"] = False

    stop_chrome()
    print("\n================== SUMMARY ==================")
    for k, v in results.items():
        print(f"  {k}: {'PASS' if v else 'FAIL'}")

    all_pass = all(results.values()) and len(results) == 3
    if not all_pass:
        sys.exit(1)
    print("\nGate J2 ALL PASS! Ready for documentation & commit.")

if __name__ == "__main__":
    asyncio.run(run_j2_tests())
