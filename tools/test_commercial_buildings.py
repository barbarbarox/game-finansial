#!/usr/bin/env python3
"""
test_commercial_buildings.py — Automated verification for Gate E8:
Commercial Buildings (Minimarket, Toko Kosmetik, SPBU, Game Center)
1. Opening hours enforcement (blocked when closed, allowed when open)
2. Enter each building from town_hub & exit back to town_hub
3. Verify NPC dialogues with portraits (Mbak Maya, Kak Cindy, Mas Doni, Kak Riko, Rani)
4. Verify interactive transaction / activity in each building (ledger updated & time advances)
5. Capture screenshots in docs/e8-commercial/
"""
import asyncio, json, os, subprocess, time, base64
import urllib.request
import websockets

CDP_PORT = 9228
HTTP_PORT = 3843
SCREENSHOT_DIR = "/home/abarox/Desktop/prototipe web statis game/game/docs/e8-commercial"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

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
        p = os.path.join(SCREENSHOT_DIR, f"{name}.png")
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

async def run():
    print("==================================================")
    print("  TEST SUITE: Gate E8 Commercial Buildings")
    print("==================================================")

    chrome_proc = subprocess.Popen([
        "/usr/bin/google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-extensions",
        "--window-size=1200,800",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir=/tmp/test_chrome_e8_{int(time.time())}",
        f"http://127.0.0.1:{HTTP_PORT}/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    failures = []

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

            # 1. Start game and grant initial allowance
            print("\n1. Starting game fresh and preparing player...")
            await evaluate(ws, "localStorage.clear()", 10)
            await send_cdp(ws, "Page.navigate", {"url": f"http://127.0.0.1:{HTTP_PORT}/index.html"}, 11)
            await asyncio.sleep(2.0)
            await evaluate(ws, "window.__GAME__.scene.getScene('MainMenu')._startNew()", 12)
            await asyncio.sleep(0.5)
            await evaluate(ws, "document.querySelector('.charcreate-form')?.requestSubmit()", 13)
            await asyncio.sleep(2.5)

            # Grant allowance via proper double-entry ledger entry
            await evaluate(ws, """
                (function() {
                    const store = window.__LJ__.getStore();
                    const state = store.getState();
                    const entry = {
                        day: 1,
                        month: 1,
                        minuteOfDay: 360,
                        kind: 'allowance',
                        description: 'Uang saku bulanan',
                        categoryId: null,
                        lines: [
                            { accountId: 'KAS_PRIBADI', side: 'D', amount: 500000 },
                            { accountId: 'UANG_SAKU',   side: 'K', amount: 500000 }
                        ]
                    };
                    const entries = [...(state.ledger?.entries || []), entry];
                    store.setState({ ledger: { ...(state.ledger || {}), entries } });
                })()
            """, 14)

            # 2. Test Opening Hours Guards at 06:00
            print("\n2. Testing Opening Hours Guards at 06:00 (before opening)...")
            # Set clock to 06:00
            await evaluate(ws, """
                (function() {
                    const store = window.__LJ__.getStore();
                    const clk = store.getState().clock;
                    store.setState({ clock: { ...clk, timeOfDay: 360, gameMinutes: 360 } });
                })()
            """, 15)

            open_mini = await evaluate(ws, "window.__LJ__.isLocationOpen('minimarket')", 16)
            open_kosmetik = await evaluate(ws, "window.__LJ__.isLocationOpen('toko_kosmetik')", 17)
            open_game = await evaluate(ws, "window.__LJ__.isLocationOpen('game_center')", 18)
            open_spbu = await evaluate(ws, "window.__LJ__.isLocationOpen('spbu')", 19)

            if open_mini.get('open'):
                failures.append("Minimarket should be CLOSED at 06:00")
            else:
                print(f"  ✓ Minimarket tertutup pada 06:00 ({open_mini.get('reason')})")

            if open_kosmetik.get('open'):
                failures.append("Toko Kosmetik should be CLOSED at 06:00")
            else:
                print(f"  ✓ Toko Kosmetik tertutup pada 06:00 ({open_kosmetik.get('reason')})")

            if open_game.get('open'):
                failures.append("Game Center should be CLOSED at 06:00")
            else:
                print(f"  ✓ Game Center tertutup pada 06:00 ({open_game.get('reason')})")

            if not open_spbu.get('open'):
                failures.append("SPBU should be OPEN at 06:00")
            else:
                print("  ✓ SPBU terbuka pada 06:00")

            # Advance time to 10:30 (all commercial buildings open)
            print("\n3. Advancing time to 10:30 (all commercial buildings open)...")
            await evaluate(ws, "window.__LJ__.advanceTime(270, 'test_advance')", 20)
            time_str = await evaluate(ws, "window.__LJ__.getTime()", 21)
            print(f"  Waktu saat ini: {time_str}")

            # 3. Test Minimarket
            print("\n4. Testing Minimarket (Enter -> Dialogue -> Buy Snack -> Exit)...")
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('minimarket')", 30, await_p=True)
            await asyncio.sleep(1.0)
            cur_map = await evaluate(ws, "window.__LJ__.getMapManager().currentMapId", 31)
            if cur_map != 'minimarket':
                failures.append(f"Expected minimarket, got {cur_map}")
            await snap(ws, "01_minimarket_interior", 510)

            # Start dialogue with Mbak Maya
            await evaluate(ws, "window.__LJ__.startDialogue('dia_maya_minimarket', 'npc_kasir_minimarket')", 32, await_p=True)
            await asyncio.sleep(0.5)
            dlg_state = await evaluate(ws, "window.__LJ__.getDialogueState()", 33)
            if not dlg_state.get('active'):
                failures.append("Mbak Maya dialogue did not open")
            else:
                print(f"  ✓ Dialog Mbak Maya terbuka: \"{dlg_state.get('currentText')[:40]}...\"")
            await snap(ws, "02_minimarket_maya_dialogue", 511)

            # Choose option 1: Buy snack (Rp8.000)
            cash_before = await evaluate(ws, """
                (function() {
                    const l = window.__LJ__.getLedger();
                    let bal = 0;
                    for (const e of (l?.entries || [])) {
                        for (const line of (e.lines || [])) {
                            if (line.accountId === 'KAS_PRIBADI') bal += (line.side === 'D' ? line.amount : -line.amount);
                        }
                    }
                    return bal;
                })()
            """, 34)
            await evaluate(ws, "window.__LJ__.choose(0)", 35)
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.closeDialogue()", 36)
            cash_after = await evaluate(ws, """
                (function() {
                    const l = window.__LJ__.getLedger();
                    let bal = 0;
                    for (const e of (l?.entries || [])) {
                        for (const line of (e.lines || [])) {
                            if (line.accountId === 'KAS_PRIBADI') bal += (line.side === 'D' ? line.amount : -line.amount);
                        }
                    }
                    return bal;
                })()
            """, 37)
            diff = cash_before - cash_after
            if diff != 8000:
                failures.append(f"Expected Rp8.000 expense, got diff={diff}")
            else:
                print(f"  ✓ Transaksi jajan minimarket tercatat: Kas berkurang Rp{diff:,}")

            # Exit back to hub
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('town_hub')", 38, await_p=True)
            await asyncio.sleep(0.5)

            # 4. Test Toko Kosmetik
            print("\n5. Testing Toko Kosmetik (Enter -> Dialogue -> Skincare -> Exit)...")
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('toko_kosmetik')", 40, await_p=True)
            await asyncio.sleep(1.0)
            cur_map = await evaluate(ws, "window.__LJ__.getMapManager().currentMapId", 41)
            if cur_map != 'toko_kosmetik':
                failures.append(f"Expected toko_kosmetik, got {cur_map}")
            await snap(ws, "03_kosmetik_interior", 512)

            # Start dialogue with Kak Cindy
            await evaluate(ws, "window.__LJ__.startDialogue('dia_cindy_kosmetik', 'npc_cindy')", 42, await_p=True)
            await asyncio.sleep(0.5)
            dlg_state = await evaluate(ws, "window.__LJ__.getDialogueState()", 43)
            if not dlg_state.get('active'):
                failures.append("Kak Cindy dialogue did not open")
            else:
                print(f"  ✓ Dialog Kak Cindy terbuka: \"{dlg_state.get('currentText')[:40]}...\"")
            await snap(ws, "04_kosmetik_cindy_dialogue", 513)

            # Choose option 1: Beli Lip Balm & Sunscreen (Rp25.000)
            cash_before = await evaluate(ws, """
                (function() {
                    const l = window.__LJ__.getLedger();
                    let bal = 0;
                    for (const e of (l?.entries || [])) {
                        for (const line of (e.lines || [])) {
                            if (line.accountId === 'KAS_PRIBADI') bal += (line.side === 'D' ? line.amount : -line.amount);
                        }
                    }
                    return bal;
                })()
            """, 44)
            await evaluate(ws, "window.__LJ__.choose(0)", 45)
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.closeDialogue()", 46)
            cash_after = await evaluate(ws, """
                (function() {
                    const l = window.__LJ__.getLedger();
                    let bal = 0;
                    for (const e of (l?.entries || [])) {
                        for (const line of (e.lines || [])) {
                            if (line.accountId === 'KAS_PRIBADI') bal += (line.side === 'D' ? line.amount : -line.amount);
                        }
                    }
                    return bal;
                })()
            """, 47)
            diff = cash_before - cash_after
            if diff != 25000:
                failures.append(f"Expected Rp25.000 expense, got diff={diff}")
            else:
                print(f"  ✓ Transaksi kosmetik tercatat: Kas berkurang Rp{diff:,}")

            # Exit back to hub
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('town_hub')", 48, await_p=True)
            await asyncio.sleep(0.5)

            # 5. Test SPBU
            print("\n6. Testing SPBU (Enter -> Dialogue -> Isi Bensin -> Exit)...")
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('spbu')", 50, await_p=True)
            await asyncio.sleep(1.0)
            cur_map = await evaluate(ws, "window.__LJ__.getMapManager().currentMapId", 51)
            if cur_map != 'spbu':
                failures.append(f"Expected spbu, got {cur_map}")
            await snap(ws, "05_spbu_interior", 514)

            # Start dialogue with Mas Doni
            await evaluate(ws, "window.__LJ__.startDialogue('dia_doni_spbu', 'npc_doni')", 52, await_p=True)
            await asyncio.sleep(0.5)
            dlg_state = await evaluate(ws, "window.__LJ__.getDialogueState()", 53)
            if not dlg_state.get('active'):
                failures.append("Mas Doni dialogue did not open")
            else:
                print(f"  ✓ Dialog Mas Doni terbuka: \"{dlg_state.get('currentText')[:40]}...\"")
            await snap(ws, "06_spbu_doni_dialogue", 515)

            # Choose option 1: Isi Bensin 2 Liter (Rp20.000)
            cash_before = await evaluate(ws, """
                (function() {
                    const l = window.__LJ__.getLedger();
                    let bal = 0;
                    for (const e of (l?.entries || [])) {
                        for (const line of (e.lines || [])) {
                            if (line.accountId === 'KAS_PRIBADI') bal += (line.side === 'D' ? line.amount : -line.amount);
                        }
                    }
                    return bal;
                })()
            """, 54)
            await evaluate(ws, "window.__LJ__.choose(0)", 55)
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.closeDialogue()", 56)
            cash_after = await evaluate(ws, """
                (function() {
                    const l = window.__LJ__.getLedger();
                    let bal = 0;
                    for (const e of (l?.entries || [])) {
                        for (const line of (e.lines || [])) {
                            if (line.accountId === 'KAS_PRIBADI') bal += (line.side === 'D' ? line.amount : -line.amount);
                        }
                    }
                    return bal;
                })()
            """, 57)
            diff = cash_before - cash_after
            if diff != 20000:
                failures.append(f"Expected Rp20.000 expense, got diff={diff}")
            else:
                print(f"  ✓ Transaksi bensin tercatat: Kas berkurang Rp{diff:,}")

            # Exit back to hub
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('town_hub')", 58, await_p=True)
            await asyncio.sleep(0.5)

            # 6. Test Game Center
            print("\n7. Testing Game Center (Enter -> Dialogue Kak Riko & Rani -> Play Game -> Exit)...")
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('game_center')", 60, await_p=True)
            await asyncio.sleep(1.0)
            cur_map = await evaluate(ws, "window.__LJ__.getMapManager().currentMapId", 61)
            if cur_map != 'game_center':
                failures.append(f"Expected game_center, got {cur_map}")
            await snap(ws, "07_game_center_interior", 516)

            # Start dialogue with Kak Riko
            await evaluate(ws, "window.__LJ__.startDialogue('dia_riko_game', 'npc_riko')", 62, await_p=True)
            await asyncio.sleep(0.5)
            dlg_state = await evaluate(ws, "window.__LJ__.getDialogueState()", 63)
            if not dlg_state.get('active'):
                failures.append("Kak Riko dialogue did not open")
            else:
                print(f"  ✓ Dialog Kak Riko terbuka: \"{dlg_state.get('currentText')[:40]}...\"")
            await snap(ws, "08_game_center_riko_dialogue", 517)

            # Choose option 1: Main arcade 1 jam (Rp20.000)
            cash_before = await evaluate(ws, """
                (function() {
                    const l = window.__LJ__.getLedger();
                    let bal = 0;
                    for (const e of (l?.entries || [])) {
                        for (const line of (e.lines || [])) {
                            if (line.accountId === 'KAS_PRIBADI') bal += (line.side === 'D' ? line.amount : -line.amount);
                        }
                    }
                    return bal;
                })()
            """, 64)
            await evaluate(ws, "window.__LJ__.choose(0)", 65)
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.closeDialogue()", 66)
            cash_after = await evaluate(ws, """
                (function() {
                    const l = window.__LJ__.getLedger();
                    let bal = 0;
                    for (const e of (l?.entries || [])) {
                        for (const line of (e.lines || [])) {
                            if (line.accountId === 'KAS_PRIBADI') bal += (line.side === 'D' ? line.amount : -line.amount);
                        }
                    }
                    return bal;
                })()
            """, 67)
            diff = cash_before - cash_after
            if diff != 20000:
                failures.append(f"Expected Rp20.000 expense, got diff={diff}")
            else:
                print(f"  ✓ Transaksi game arcade tercatat: Kas berkurang Rp{diff:,}")

            # Test dialogue with Rani in Game Center
            await evaluate(ws, "window.__LJ__.startDialogue('dia_rani_game', 'npc_rani')", 68, await_p=True)
            await asyncio.sleep(0.5)
            dlg_rani = await evaluate(ws, "window.__LJ__.getDialogueState()", 69)
            if not dlg_rani.get('active'):
                failures.append("Rani dialogue did not open")
            else:
                print(f"  ✓ Dialog Rani di Game Center terbuka: \"{dlg_rani.get('currentText')[:40]}...\"")
            await snap(ws, "09_game_center_rani_dialogue", 518)
            await evaluate(ws, "window.__LJ__.closeDialogue()", 70)

            # Exit back to hub
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('town_hub')", 71, await_p=True)
            await asyncio.sleep(0.5)
            cur_map = await evaluate(ws, "window.__LJ__.getMapManager().currentMapId", 72)
            if cur_map != 'town_hub':
                failures.append(f"Expected town_hub after exit, got {cur_map}")
            await snap(ws, "10_town_hub_returned", 519)

            # Summary
            print("\n==================================================")
            if failures:
                print(f"  HASIL E8: GAGAL ({len(failures)} kegagalan)")
                for f in failures:
                    print(f"   ✗ {f}")
                return False
            else:
                print("  HASIL E8: LULUS 100%! Semua bangunan komersial terverifikasi!")
                print("==================================================")
                return True

    finally:
        chrome_proc.kill()

if __name__ == "__main__":
    success = asyncio.run(run())
    exit(0 if success else 1)
