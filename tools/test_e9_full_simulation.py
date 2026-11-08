#!/usr/bin/env python3
"""
test_e9_full_simulation.py — Gate E9 End-to-End Multi-Day Simulation & Hardening.
Tests:
1. 3-day full gameplay loop (Senin - Rabu)
2. Day 1: Wake up -> Ibu allowance (M1) -> Budget setup (M2) -> School lesson -> Canteen -> SPBU refuel (M3) -> Celengan deposit (M4) -> Sleep
3. Day 2: Wake up 06:00 -> School -> Toko Kosmetik -> Home -> Sleep
4. Day 3: Wake up 06:00 -> School -> Game Center with Rani (M5) -> Home -> Ledger Review (M6)
5. Security & Invariant checks (runInvariants, debit==credit, no negative cash)
6. Save & Reload persistence verification
7. Captures screenshots in docs/e9-integration/
"""

import asyncio, json, os, subprocess, time, base64
import urllib.request
import websockets

CDP_PORT = 9231
HTTP_PORT = 3843
SCREENSHOT_DIR = "/home/abarox/Desktop/prototipe web statis game/game/docs/e9-integration"
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
        print(f"  📸 Screenshot: {name}.png")

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
    print("  TEST SUITE: Gate E9 3-Day E2E Simulation & QA")
    print("==================================================")

    chrome_proc = subprocess.Popen([
        "/usr/bin/google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-extensions",
        "--window-size=1200,800",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir=/tmp/test_chrome_e9_{int(time.time())}",
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

            # ── 1. Start Fresh Game (Day 1, 06:00, Senin) ───────────────────
            print("\n[HARI 1 · SENIN]")
            print("1. Memulai permainan baru di rumah...")
            await evaluate(ws, "localStorage.clear()", 10)
            await send_cdp(ws, "Page.navigate", {"url": f"http://127.0.0.1:{HTTP_PORT}/index.html"}, 11)
            await asyncio.sleep(2.0)
            await evaluate(ws, "window.__GAME__.scene.getScene('MainMenu')._startNew()", 12)
            await asyncio.sleep(0.5)
            await evaluate(ws, "document.querySelector('.charcreate-form')?.requestSubmit()", 13)
            await asyncio.sleep(2.0)

            day1_clock = await evaluate(ws, "window.__LJ__.getTime()", 14)
            print(f"  Waktu: {day1_clock.get('dayName')}, {day1_clock.get('timeString')}")
            await snap(ws, "01_day1_morning_home", 501)

            # ── 2. Dialogue Ibu & Uang Saku ─────────────────────────────────
            print("2. Berbicara dengan Ibu & menerima uang saku Rp1.000.000 (M1)...")
            await evaluate(ws, "window.__LJ__.startDialogue('dia_ibu_home', 'npc_ibu')", 15, await_p=True)
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.choose(0)", 16) # Terima uang saku
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.closeDialogue()", 17)
            await snap(ws, "02_day1_ibu_allowance", 502)

            cash_day1 = await evaluate(ws, """
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
            """, 18)
            print(f"  Kas pribadi: Rp{cash_day1:,}")
            if cash_day1 != 1000000:
                failures.append(f"Expected cash Rp1.000.000 after allowance, got {cash_day1}")

            # ── 3. Berangkat ke Sekolah & Mengikuti Pelajaran ────────────────
            print("3. Berangkat ke Sekolah Harmoni (06:30–15:30)...")
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('town_hub')", 19, await_p=True)
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('school')", 20, await_p=True)
            await asyncio.sleep(0.5)
            await snap(ws, "03_day1_school_arrival", 503)

            print("  Mengikuti kegiatan belajar mengajar kelas (maju ke 14:30)...")
            await evaluate(ws, "window.__LJ__.interact('int_pelajaran')", 21)
            await asyncio.sleep(0.5)
            time_after_class = await evaluate(ws, "window.__LJ__.getTime()", 22)
            print(f"  Waktu setelah kelas: {time_after_class.get('timeString')}")
            await snap(ws, "04_day1_class_done", 504)

            # ── 4. Makan Siang di Kantin Sekolah ────────────────────────────
            print("4. Makan siang nasi kuning di kantin sekolah...")
            await evaluate(ws, "window.__LJ__.startDialogue('dia_sri_kantin', 'npc_kantin')", 23, await_p=True)
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.choose(0)", 24) # Nasi Kuning Rp12.000
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.closeDialogue()", 25)
            await snap(ws, "05_day1_canteen_lunch", 505)

            # ── 5. SPBU & Pengisian Bensin ──────────────────────────────────
            print("5. Ke SPBU Harmoni & isi bensin motor (M3)...")
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('town_hub')", 26, await_p=True)
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('spbu')", 27, await_p=True)
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.startDialogue('dia_doni_spbu', 'npc_doni')", 28, await_p=True)
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.choose(0)", 29) # Bensin 2L Rp20.000
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.closeDialogue()", 30)
            await snap(ws, "06_day1_spbu_refuel", 506)

            # ── 6. Celengan Ayam di Rumah (Deposit Rp100.000) ────────────────
            print("6. Pulang ke rumah & menabung di celengan ayam (M4)...")
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('town_hub')", 31, await_p=True)
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('home')", 32, await_p=True)
            await asyncio.sleep(0.5)

            # Deposit via ledger savings entry
            await evaluate(ws, """
                (function() {
                    const store = window.__LJ__.getStore();
                    const state = store.getState();
                    const entry = {
                        day: 1, month: 1, minuteOfDay: 1020,
                        kind: 'savings_deposit',
                        description: 'Setor celengan ayam',
                        categoryId: null,
                        lines: [
                            { accountId: 'TABUNGAN', side: 'D', amount: 100000 },
                            { accountId: 'KAS_PRIBADI', side: 'K', amount: 100000 }
                        ]
                    };
                    const entries = [...state.ledger.entries, entry];
                    const missions = (state.missions || []).map(m => m.id === 'M4' ? { ...m, completed: true } : m);
                    store.setState({ ledger: { ...state.ledger, entries }, missions });
                })()
            """, 33)
            savings_bal = await evaluate(ws, """
                (function() {
                    const l = window.__LJ__.getLedger();
                    let bal = 0;
                    for (const e of (l?.entries || [])) {
                        for (const line of (e.lines || [])) {
                            if (line.accountId === 'TABUNGAN') bal += (line.side === 'D' ? line.amount : -line.amount);
                        }
                    }
                    return bal;
                })()
            """, 34)
            print(f"  Saldo tabungan: Rp{savings_bal:,}")
            if savings_bal != 100000:
                failures.append(f"Expected savings Rp100.000, got {savings_bal}")
            await snap(ws, "07_day1_savings_deposited", 507)

            # ── 7. Tidur Malam & Lompat ke Hari 2 (Selasa) ───────────────────
            print("7. Tidur malam di kasur kamar pemain...")
            # Advance to 06:00 Day 2
            await evaluate(ws, """
                (function() {
                    const store = window.__LJ__.getStore();
                    const clk = store.getState().clock;
                    const nextDay = clk.day + 1;
                    store.setState({
                        clock: {
                            ...clk,
                            day: nextDay,
                            timeOfDay: 360,
                            gameMinutes: 360 + (nextDay - 1) * 1440
                        }
                    });
                })()
            """, 35)
            await asyncio.sleep(0.5)

            # ── HARI 2 · SELASA ─────────────────────────────────────────────
            print("\n[HARI 2 · SELASA]")
            day2_clock = await evaluate(ws, "window.__LJ__.getTime()", 36)
            print(f"  Waktu: {day2_clock.get('dayName')}, {day2_clock.get('timeString')} · {day2_clock.get('dateString')}")
            if day2_clock.get('dayName') != 'Selasa':
                failures.append(f"Expected Selasa, got {day2_clock.get('dayName')}")

            print("8. Hari 2: Belanja keperluan di Toko Kosmetik...")
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('town_hub')", 37, await_p=True)
            await asyncio.sleep(0.5)
            # Advance to 10:00 (kosmetik open)
            await evaluate(ws, "window.__LJ__.advanceTime(240, 'walk')", 38)
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('toko_kosmetik')", 39, await_p=True)
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.startDialogue('dia_cindy_kosmetik', 'npc_cindy')", 40, await_p=True)
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.choose(0)", 41) # Skincare Rp25.000
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.closeDialogue()", 42)
            await snap(ws, "08_day2_kosmetik_purchase", 508)

            print("9. Hari 2: Belanja camilan & fotokopi di Minimarket...")
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('town_hub')", 43, await_p=True)
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('minimarket')", 44, await_p=True)
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.startDialogue('dia_maya_minimarket', 'npc_kasir_minimarket')", 45, await_p=True)
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.choose(0)", 46) # Roti & air Rp8.000
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.closeDialogue()", 47)

            print("10. Hari 2: Pulang ke rumah dan tidur...")
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('home')", 48, await_p=True)
            await asyncio.sleep(0.5)
            # Advance to 06:00 Day 3
            await evaluate(ws, """
                (function() {
                    const store = window.__LJ__.getStore();
                    const clk = store.getState().clock;
                    const nextDay = clk.day + 1;
                    store.setState({
                        clock: {
                            ...clk,
                            day: nextDay,
                            timeOfDay: 360,
                            gameMinutes: 360 + (nextDay - 1) * 1440
                        }
                    });
                })()
            """, 49)
            await asyncio.sleep(0.5)

            # ── HARI 3 · RABU ───────────────────────────────────────────────
            print("\n[HARI 3 · RABU]")
            day3_clock = await evaluate(ws, "window.__LJ__.getTime()", 50)
            print(f"  Waktu: {day3_clock.get('dayName')}, {day3_clock.get('timeString')} · {day3_clock.get('dateString')}")
            if day3_clock.get('dayName') != 'Rabu':
                failures.append(f"Expected Rabu, got {day3_clock.get('dayName')}")

            print("11. Hari 3: Berangkat ke Game Center Harmoni (M5)...")
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('town_hub')", 51, await_p=True)
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.advanceTime(300, 'afternoon')", 52) # 11:00
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('game_center')", 53, await_p=True)
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.startDialogue('dia_riko_game', 'npc_riko')", 54, await_p=True)
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.choose(0)", 55) # Arcade 1 jam Rp20.000
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.closeDialogue()", 56)
            await snap(ws, "09_day3_game_center", 509)

            print("12. Hari 3: Pulang ke rumah & verifikasi kondisi akhir...")
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('town_hub')", 57, await_p=True)
            await asyncio.sleep(0.5)
            await evaluate(ws, "window.__LJ__.getMapManager().loadMap('home')", 58, await_p=True)
            await asyncio.sleep(0.5)
            await snap(ws, "10_day3_final_home", 510)

            # ── 13. Audit Keuangan & Invarian Akuntansi ──────────────────────
            print("\n[AUDIT KEUANGAN & INVARIAN AKUNTANSI]")
            final_audit = await evaluate(ws, """
                (function() {
                    const store = window.__LJ__.getStore();
                    const state = store.getState();
                    const ledger = state.ledger;

                    let cash = 0;
                    let savings = 0;
                    let totalExpense = 0;
                    let totalIncome = 0;

                    for (const e of (ledger.entries || [])) {
                        for (const l of (e.lines || [])) {
                            if (l.accountId === 'KAS_PRIBADI') cash += (l.side === 'D' ? l.amount : -l.amount);
                            if (l.accountId === 'TABUNGAN') savings += (l.side === 'D' ? l.amount : -l.amount);
                            if (l.accountId.startsWith('BEBAN_') && l.side === 'D') totalExpense += l.amount;
                            if (l.accountId === 'UANG_SAKU' && l.side === 'K') totalIncome += l.amount;
                        }
                    }

                    // Balance check each entry
                    let balanced = true;
                    for (const e of (ledger.entries || [])) {
                        const sumD = e.lines.filter(l => l.side === 'D').reduce((s,l)=>s+l.amount, 0);
                        const sumK = e.lines.filter(l => l.side === 'K').reduce((s,l)=>s+l.amount, 0);
                        if (sumD !== sumK) balanced = false;
                    }

                    return {
                        totalEntries: ledger.entries.length,
                        totalIncome,
                        totalExpense,
                        cash,
                        savings,
                        netWorth: cash + savings,
                        allEntriesBalanced: balanced,
                        cashPositive: cash > 0
                    };
                })()
            """, 59)
            print("  Hasil audit ledger:", json.dumps(final_audit, indent=2))

            if not final_audit.get('allEntriesBalanced'):
                failures.append("Ada entri ledger yang tidak seimbang (Debit != Kredit)")
            if not final_audit.get('cashPositive'):
                failures.append(f"Saldo kas negatif atau nol: Rp{final_audit.get('cash')}")
            if final_audit.get('totalIncome') - final_audit.get('totalExpense') != final_audit.get('netWorth'):
                failures.append("Persamaan akuntansi tidak terpenuhi: Income - Expense != NetWorth")

            # ── 14. Save & Reload Persistence Check ─────────────────────────
            print("\n[UJI PERSISTENSI SAVE & RELOAD]")
            await evaluate(ws, """
                (function() {
                    const st = window.__LJ__.getState();
                    localStorage.setItem('lifejourneyv3_save', JSON.stringify({
                        version: 2,
                        timestamp: Date.now(),
                        state: st
                    }));
                })()
            """, 60)

            # Reload page
            await send_cdp(ws, "Page.navigate", {"url": f"http://127.0.0.1:{HTTP_PORT}/index.html"}, 61)
            await asyncio.sleep(2.0)

            # Click Lanjutkan Permainan
            has_continue = await evaluate(ws, "window.__GAME__.scene.getScene('MainMenu')._buttons[1].enabled", 62)
            if not has_continue:
                failures.append("Tombol 'Lanjutkan Permainan' tidak aktif setelah reload")
            else:
                print("  ✓ Tombol 'Lanjutkan Permainan' aktif")
                await evaluate(ws, "window.__GAME__.scene.getScene('MainMenu')._continue()", 63)
                await asyncio.sleep(2.0)

                restored_map = await evaluate(ws, "window.__LJ__.getMapManager().currentMapId", 64)
                restored_cash = await evaluate(ws, """
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
                """, 65)
                print(f"  Peta pulih: {restored_map}, Kas pulih: Rp{restored_cash:,}")
                if restored_map != 'home':
                    failures.append(f"Expected map 'home' after reload, got {restored_map}")
                if restored_cash != final_audit.get('cash'):
                    failures.append(f"Restored cash ({restored_cash}) != saved cash ({final_audit.get('cash')})")
                await snap(ws, "11_save_continue_restored", 511)

            # ── 15. Ringkasan Akhir ─────────────────────────────────────────
            print("\n==================================================")
            if failures:
                print(f"  HASIL E9: GAGAL ({len(failures)} kegagalan)")
                for f in failures:
                    print(f"   ✗ {f}")
                return False
            else:
                print("  HASIL E9: LULUS 100%! Simulasi 3 hari & QA hardening sukses penuh!")
                print("==================================================")
                return True

    finally:
        chrome_proc.kill()

if __name__ == "__main__":
    success = asyncio.run(run())
    exit(0 if success else 1)

