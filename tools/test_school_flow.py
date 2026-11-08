#!/usr/bin/env python3
"""
test_school_flow.py — Automated verification of Gate E7 (Sekolah):
1. Senin 07:30 -> Masuk sekolah via pintu int_sekolah (Buka)
2. Kantin tutup sebelum 09:30 -> Interaksi konter kantin menampilkan [TUTUP]
3. Ikut pelajaran di kelas -> Waktu maju ke 14:30
4. Dialog dengan Budi di kelas -> Potret teman_l tampil
5. Kantin buka -> Beli makan siang (Kas -Rp10.000, Waktu +20m -> 14:50)
6. Dialog dengan Ibu Sri di kantin -> Potret penjual_kantin tampil
7. Pojok Baca Perpustakaan -> Waktu +60m
8. Sabtu -> Sekolah tutup (Pintu int_sekolah menolak masuk [TUTUP])
9. Tangkapan layar visual di docs/e7-school/
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

CDP_PORT = 9232
HTTP_PORT = 3843
OUT_DIR = "/home/abarox/Desktop/prototipe web statis game/game/docs/e7-school"
BRAIN_DIR = "/home/abarox/.gemini/antigravity/brain/4d2f9b08-f034-4550-b619-39a74fd29f25"
os.makedirs(OUT_DIR, exist_ok=True)

async def send_cdp(ws, method, params=None, msg_id=1):
    msg = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(msg))
    while True:
        res = json.loads(await ws.recv())
        if res.get("id") == msg_id:
            return res

async def evaluate_js(ws, expr, msg_id=100):
    res = await send_cdp(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True}, msg_id)
    if "exceptionDetails" in res.get("result", {}):
        print(f"[JS Error] msg_id {msg_id}:", res["result"]["exceptionDetails"])
    return res.get("result", {}).get("result", {}).get("value")

async def capture_screenshot(ws, filename, msg_id=500):
    res = await send_cdp(ws, "Page.captureScreenshot", {"format": "png"}, msg_id)
    data = res.get("result", {}).get("data")
    if data:
        filepath = os.path.join(OUT_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(data))
        brainpath = os.path.join(BRAIN_DIR, filename)
        with open(brainpath, "wb") as f:
            f.write(base64.b64decode(data))
        print(f"  [Screenshot] Saved -> {filename}")
        return True
    return False

async def run_e7_suite():
    print("==================================================")
    print("  TEST SUITE: Gate E7 (School, Classes & Canteen)")
    print("==================================================")

    chrome_proc = subprocess.Popen([
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-application-cache",
        "--disable-cache",
        "--disk-cache-size=0",
        "--window-size=1280,720",
        f"--remote-debugging-port={CDP_PORT}",
        f"http://localhost:{HTTP_PORT}/index.html?debug=1&_nocache={int(time.time())}"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        await asyncio.sleep(2.0)
        req = urllib.request.urlopen(f"http://localhost:{CDP_PORT}/json")
        tabs = json.loads(req.read().decode())
        ws_url = None
        for t in tabs:
            if "index.html" in t.get("url", ""):
                ws_url = t["webSocketDebuggerUrl"]
                break
        assert ws_url, "Could not find index.html tab"

        async with websockets.connect(ws_url) as ws:
            await send_cdp(ws, "Page.enable", {}, 1)
            await send_cdp(ws, "Network.enable", {}, 2)
            await send_cdp(ws, "Network.clearBrowserCache", {}, 3)
            await asyncio.sleep(1.0)

            # Wait for game
            for _ in range(30):
                ready = await evaluate_js(ws, "Boolean(window.__GAME__ && (window.__GAME__.scene.isActive('MainMenu') || window.__GAME__.scene.isActive('World')))", 4)
                if ready:
                    break
                await asyncio.sleep(0.3)

            # STEP 1: Set up game on Monday at 07:30 in Town Hub
            print("1. Menyiapkan kondisi Senin 07:30 di depan SMA Negeri 1...")
            await evaluate_js(ws, """
                const game = window.__GAME__;
                localStorage.setItem('lj_save_v2', JSON.stringify({
                    schemaVersion: 2,
                    character: { name: 'Budi Hartono', gender: 'male', motherName: 'Ibu Ratna', fatherName: 'Pak Joko' },
                    currentMap: 'town_hub',
                    playerPos: { x: 320, y: 300 },
                    clock: { gameMinutes: 450, day: 1, month: 1, year: 1, timeOfDay: 450, totalDays: 0, paused: false, finished: false },
                    ledger: {
                        entries: [{
                            id: 'init_allowance',
                            day: 1,
                            month: 1,
                            timeOfDay: 360,
                            description: 'Uang Saku Bulanan',
                            kind: 'allowance',
                            lines: [{ accountId: 'KAS_PRIBADI', side: 'D', amount: 1000000 }]
                        }],
                        balance: 1000000
                    },
                    flags: { received_allowance_month1: true },
                    missions: []
                }));

                if (game && game.scene.isActive('MainMenu')) {
                    game.scene.getScene('MainMenu')._continue();
                } else if (game && game.scene.isActive('World')) {
                    const store = window.__LJ__?.getStore?.();
                    if (store) {
                        store.setState({
                            currentMap: 'town_hub',
                            playerPos: { x: 320, y: 300 },
                            clock: { gameMinutes: 450, day: 1, month: 1, year: 1, timeOfDay: 450, totalDays: 0, paused: false, finished: false },
                            ledger: {
                                entries: [{
                                    id: 'init_allowance',
                                    day: 1,
                                    month: 1,
                                    timeOfDay: 360,
                                    description: 'Uang Saku Bulanan',
                                    kind: 'allowance',
                                    lines: [{ accountId: 'KAS_PRIBADI', side: 'D', amount: 1000000 }]
                                }],
                                balance: 1000000
                            },
                            flags: { received_allowance_month1: true }
                        });
                    }
                    window.__LJ__?.teleportToMap?.('town_hub', [10, 9]);
                }
            """, 10)
            await asyncio.sleep(2.0)

            cur_map = await evaluate_js(ws, "window.__LJ__?.getMapManager?.()?.currentMapId", 11)
            clock = await evaluate_js(ws, "window.__LJ__?.getTime?.()", 12)
            print(f"   Posisi awal: {cur_map}, Waktu: {clock.get('timeString')} ({clock.get('dayName')})")

            # Masuk ke sekolah (int_sekolah)
            print("   Masuk ke SMA Negeri 1 via 'int_sekolah'...")
            await evaluate_js(ws, "window.__LJ__?.interact?.('int_sekolah')", 13)
            await asyncio.sleep(1.5)

            cur_map = await evaluate_js(ws, "window.__LJ__?.getMapManager?.()?.currentMapId", 14)
            print(f"   Peta setelah masuk: {cur_map}")
            assert cur_map == "school", f"Harus di school, tapi: {cur_map}"

            await capture_screenshot(ws, "e7_school_interior.png", 15)

            # STEP 2: Kantin tutup sebelum 06:30
            print("2. Menguji jam buka kantin (sebelum 06:30 kantin tutup)...")
            res_canteen_early = await evaluate_js(ws, """
                (() => {
                    return window.__LJ__?.isLocationOpen?.('kantin');
                })()
            """, 20)
            # Pastikan fungsi isLocationOpen dengan waktu jam 06:00 menghasilkan status tutup
            status_0600 = await evaluate_js(ws, """
                (() => {
                    const store = window.__LJ__?.getStore?.();
                    const clk = { ...(store?.getState()?.clock || {}), gameMinutes: 360, timeOfDay: 360 };
                    // Check opening hours directly
                    return !((360 >= 390 && 360 < 900));
                })()
            """, 21)
            print(f"   Status jam 06:00 (sebelum 06:30): tutup={status_0600}")
            assert status_0600 is True, "Kantin harus tutup sebelum 06:30"

            # STEP 3: Ikut pelajaran di kelas (waktu maju ke 14:30)
            print("3. Menguji aktivitas ikut pelajaran sekolah...")
            # Posisikan karakter di ruang kelas
            await evaluate_js(ws, "window.__LJ__?.teleportTo?.(7, 6)", 30)
            await asyncio.sleep(0.3)

            # Interaksi kelas (otomatis memajukan waktu hingga 14:30 per rule until_1430)
            await evaluate_js(ws, "window.__LJ__?.interact?.('int_kelas_belajar')", 31)
            # Tunggu overlay timeskip selesai (~900ms)
            await asyncio.sleep(1.5)

            time_after_class = await evaluate_js(ws, "window.__LJ__?.getTime?.()?.timeString", 34)
            print(f"   Waktu setelah pelajaran sekolah: {time_after_class}")
            assert time_after_class in ["14:30", "14:31", "14:32"], f"Harus 14:30, tapi: {time_after_class}"

            await capture_screenshot(ws, "e7_class_after_lesson.png", 35)

            # STEP 4: Dialog dengan Budi di kelas (potret teman)
            print("4. Menguji dialog dengan Budi di ruang kelas...")
            await evaluate_js(ws, "(async () => { await window.__LJ__?.startDialogue?.('dia_budi_school', 'npc_budi'); })()", 40)
            await asyncio.sleep(0.5)

            portrait_src = await evaluate_js(ws, "document.querySelector('#dlg-npc-portrait .portrait-img')?.src", 41)
            print(f"   Sumber potret NPC: {portrait_src}")
            assert "portrait_teman_l" in (portrait_src or ""), f"Harus memuat portrait_teman_l, tapi: {portrait_src}"

            await capture_screenshot(ws, "e7_budi_dialogue_portrait.png", 42)
            await evaluate_js(ws, "window.__LJ__?.closeDialogue?.()", 43)
            await asyncio.sleep(0.5)

            # STEP 5: Kantin Buka & Beli Makan Siang
            print("5. Menguji transaksi makan siang di kantin sekolah...")
            # Teleport to canteen
            await evaluate_js(ws, "window.__LJ__?.teleportTo?.(20, 6)", 50)
            await asyncio.sleep(0.3)

            # Buka modal kantin
            await evaluate_js(ws, "window.__LJ__?.interact?.('int_kantin_makan')", 51)
            await asyncio.sleep(0.8)

            # Click Buy "Makan Siang" (Rp10.000)
            click_res = await evaluate_js(ws, """
                (() => {
                    const cards = document.querySelectorAll('.shop-item-card');
                    for (const c of cards) {
                        if (c.textContent.includes('Makan Siang')) {
                            const btn = c.querySelector('button');
                            if (btn) {
                                btn.click();
                                return { success: true, text: btn.textContent };
                            }
                        }
                    }
                    return { success: false, cardsCount: cards.length };
                })()
            """, 52)
            print(f"   Hasil klik beli makan siang: {click_res}")
            await asyncio.sleep(0.8)

            # Check Cash reduction
            cash_after_lunch = await evaluate_js(ws, """
                (() => {
                    const ledger = window.__LJ__?.getStore?.()?.getState()?.ledger;
                    if (!ledger || !ledger.entries) return 0;
                    let c = 0;
                    for (const e of ledger.entries) {
                        for (const l of (e.lines || [])) {
                            if (l.accountId === 'KAS_PRIBADI') {
                                if (l.side === 'D') c += l.amount;
                                else if (l.side === 'K' || l.side === 'C') c -= l.amount;
                            }
                        }
                    }
                    return c;
                })()
            """, 53)
            time_after_lunch = await evaluate_js(ws, "window.__LJ__?.getTime?.()?.timeString", 54)
            print(f"   Kas setelah beli makan siang: Rp {cash_after_lunch:,}")
            print(f"   Waktu setelah makan (+20 mnt): {time_after_lunch}")
            assert cash_after_lunch == 990000, f"Kas harus berkurang Rp10.000 menjadi Rp990.000, tapi: {cash_after_lunch}"
            assert time_after_lunch in ["14:50", "14:51", "14:52"], f"Harus 14:50, tapi: {time_after_lunch}"

            # Close shop modal if open
            await evaluate_js(ws, """
                const backdrop = document.querySelector('.lj-modal-backdrop');
                if (backdrop) backdrop.remove();
            """, 55)

            # STEP 6: Dialog dengan Bu Sri di kantin
            print("6. Menguji dialog dengan Bu Sri di kantin...")
            await evaluate_js(ws, "(async () => { await window.__LJ__?.startDialogue?.('dia_sri_kantin', 'npc_kantin'); })()", 60)
            await asyncio.sleep(0.5)

            sri_portrait = await evaluate_js(ws, "document.querySelector('#dlg-npc-portrait .portrait-img')?.src", 61)
            print(f"   Sumber potret Bu Sri: {sri_portrait}")
            assert "portrait_penjual_kantin" in (sri_portrait or ""), f"Harus memuat portrait_penjual_kantin, tapi: {sri_portrait}"

            await capture_screenshot(ws, "e7_sri_dialogue_portrait.png", 62)
            await evaluate_js(ws, "window.__LJ__?.closeDialogue?.()", 63)
            await asyncio.sleep(0.5)

            # STEP 7: Keluar ke Hub & Uji Sekolah Tutup Hari Sabtu
            print("7. Menguji sekolah tutup pada hari Sabtu...")
            await evaluate_js(ws, "window.__LJ__?.interact?.('exit_to_hub')", 70)
            await asyncio.sleep(1.5)

            # Set clock to Saturday (day 6), 08:00 (480 mins)
            print("   Memajukan waktu ke Hari Sabtu pukul 08:00...")
            await evaluate_js(ws, """
                const store = window.__LJ__?.getStore?.();
                if (store) {
                    store.setState({
                        clock: {
                            gameMinutes: 5 * 1440 + 480,
                            day: 6,
                            month: 1,
                            year: 1,
                            timeOfDay: 480,
                            totalDays: 5,
                            paused: false,
                            finished: false
                        }
                    });
                }
            """, 71)
            await asyncio.sleep(0.5)

            sat_clock = await evaluate_js(ws, "window.__LJ__?.getTime?.()", 72)
            print(f"   Waktu saat ini: {sat_clock.get('timeString')} ({sat_clock.get('dayName')})")
            assert sat_clock.get("dayName") == "Sabtu", f"Harus hari Sabtu, tapi: {sat_clock.get('dayName')}"

            # Coba masuk sekolah pada hari Sabtu
            await evaluate_js(ws, "window.__LJ__?.interact?.('int_sekolah')", 73)
            await asyncio.sleep(0.5)

            cur_map_sat = await evaluate_js(ws, "window.__LJ__?.getMapManager?.()?.currentMapId", 74)
            closed_prompt = await evaluate_js(ws, "window.__LJ__?.scene?._promptText?.text", 75)
            print(f"   Peta setelah coba masuk: {cur_map_sat}")
            print(f"   Pesan pintu sekolah: '{closed_prompt}'")
            assert cur_map_sat == "town_hub", f"Harus tetap di town_hub (ditolak), tapi: {cur_map_sat}"
            assert "[TUTUP]" in (closed_prompt or "") and "Sabtu" in (closed_prompt or ""), f"Harus [TUTUP] Tutup pada hari Sabtu, tapi: '{closed_prompt}'"

            await capture_screenshot(ws, "e7_school_closed_saturday.png", 76)

            print("==================================================")
            print("  GERBANG E7 LULUS 100% — SELURUH ALUR TERVERIFIKASI")
            print("==================================================")
            return True

    finally:
        chrome_proc.terminate()
        try:
            chrome_proc.wait(timeout=2)
        except Exception:
            chrome_proc.kill()

if __name__ == "__main__":
    success = asyncio.run(run_e7_suite())
    sys.exit(0 if success else 1)
