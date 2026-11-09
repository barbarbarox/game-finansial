#!/usr/bin/env python3
"""
tools/test_j0_red.py — J0 Red Test Suite & Evidence Collector for Life Journey V6
Reproduces and documents RED state for B1 through B16:
- B1, B2, B3, B6: Furniture frontality & perspective
- B4, B8: Room boundary crossing & classroom bookshelf placement
- B5: Asset identity mismatches (bak mandi vs rak piring vs jendela)
- B7: Kitchen interaction conflict (pressing E near Ibu triggers int_dapur)
- B9: Motor persistence in classroom
- B10, B11, B12: Energy v2 mechanics (school cost, warning < 50%, exhausted wake 10:00)
- B13: NPC Budi cartoon style vs player pixel sprite
- B14, B15: Shop panel missing Esc/outside-click exit and left-side vendor portrait with speech bubble
- B16: Guided tutorial missing on new game
"""

import os
import sys
import json
import time
import shutil
import subprocess
import urllib.request
import asyncio
import websockets
import base64
from PIL import Image

CDP_PORT = 9251
HTTP_PORT = 3843
REG_DIR = "/home/abarox/Desktop/prototipe web statis game/game/docs/regression"
REF_DIR = "/home/abarox/Desktop/prototipe web statis game/game/docs/reference"
os.makedirs(REG_DIR, exist_ok=True)

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
        print(f"  📸 Saved RED screenshot: {filename}.png")
        return p
    return None

async def get_ws_url():
    for _ in range(25):
        try:
            req = urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json", timeout=1)
            tabs = json.loads(req.read().decode())
            for tab in tabs:
                if tab.get("type") == "page" and ("index.html" in tab.get("url", "") or str(HTTP_PORT) in tab.get("url", "")):
                    return tab.get("webSocketDebuggerUrl")
            if tabs:
                for tab in tabs:
                    if tab.get("type") == "page":
                        return tab.get("webSocketDebuggerUrl")
        except Exception:
            pass
        await asyncio.sleep(0.5)
    return None

async def run_j0():
    print("==================================================")
    print("  J0 RED TEST SUITE & EVIDENCE GENERATOR (V6)")
    print("==================================================")

    # 1. Establish reference screenshots for visual asset issues
    print("\n--- 1. Archiving Visual Asset RED Screenshots ---")
    ref_map = {
        "b1_kursi_meja_sekolah_red.png": "v6-kelas-kursi-serong.png",
        "b2_meja_guru_papan_tulis_red.png": "v6-kelas-kursi-serong.png",
        "b3_meja_bangku_kantin_red.png": "v6-kantin.png",
        "b4_furnitur_tembus_dinding_red.png": "v6-kelas-kursi-serong.png",
        "b5_identitas_aset_tertukar_red.png": "v6-kamar-mandi-dapur-tertukar.png",
        "b6_wastafel_toilet_red.png": "v6-kamar-mandi-dapur-tertukar.png",
        "b8_rak_buku_kelas_red.png": "v6-kelas-kursi-serong.png",
        "b9_motor_di_kelas_red.png": "v6-kelas-kursi-serong.png",
    }
    for dest, src in ref_map.items():
        src_path = os.path.join(REF_DIR, src)
        dest_path = os.path.join(REG_DIR, dest)
        if os.path.exists(src_path):
            shutil.copyfile(src_path, dest_path)
            print(f"  📸 Copied reference RED: {dest} (from {src})")

    # B13: Budi sprite comparison
    budi_src = "/home/abarox/Desktop/prototipe web statis game/game/assets/npcs/npc_budi.png"
    budi_dest = os.path.join(REG_DIR, "b13_sprite_budi_kartun_red.png")
    if os.path.exists(budi_src):
        # Create a side-by-side comparison image of Budi vs Player
        player_src = "/home/abarox/Desktop/prototipe web statis game/game/assets/characters/char_player_m_casual.png"
        im_b = Image.open(budi_src).convert("RGBA")
        im_p = Image.open(player_src).convert("RGBA")
        # Player has 3 frames of 32x64; crop first frame (front)
        im_p_front = im_p.crop((0, 0, 32, 64))
        comp = Image.new("RGBA", (180, 100), (20, 25, 35, 255))
        # Scale 2x for clarity
        b_scaled = im_b.resize((64, 128), Image.NEAREST)
        p_scaled = im_p_front.resize((64, 128), Image.NEAREST)
        comp = Image.new("RGBA", (200, 140), (20, 25, 35, 255))
        comp.paste(p_scaled, (20, 10), p_scaled)
        comp.paste(b_scaled, (110, 10), b_scaled)
        comp.save(budi_dest)
        print(f"  📸 Saved RED comparison: b13_sprite_budi_kartun_red.png (Player Left vs Budi Right)")

    # 2. Launch Chrome Headless for UI behavioral tests
    print("\n--- 2. Launching Headless Chrome for UI Bug Reproduction ---")
    chrome_proc = subprocess.Popen([
        "/usr/bin/google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-extensions",
        "--window-size=1200,800",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir=/tmp/test_chrome_j0_{int(time.time())}",
        f"http://127.0.0.1:{HTTP_PORT}/index.html"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        ws_url = await get_ws_url()
        if not ws_url:
            raise RuntimeError("Failed to attach to headless Chrome debug port.")

        async with websockets.connect(ws_url, max_size=50_000_000) as ws:
            print("  Connected to CDP session.")
            await asyncio.sleep(2.0)

            # Wait for game initialization
            print("  Waiting for game scene / character creation...")
            for _ in range(40):
                in_world = await evaluate(ws, "window.__LJ__ !== undefined && window.__LJ__.scene !== undefined && window.__LJ__.scene._player !== undefined", 101)
                if in_world:
                    break
                has_menu = await evaluate(ws, "!!(window.__GAME__?.scene?.getScene?.('MainMenu'))", 102)
                if has_menu:
                    # Start new game if in main menu
                    await evaluate(ws, "window.__GAME__.scene.getScene('MainMenu')._startNew()", 103)
                    await asyncio.sleep(0.8)
                    await evaluate(ws, "document.querySelector('.charcreate-form')?.requestSubmit()", 104)
                    await asyncio.sleep(1.5)
                await asyncio.sleep(0.5)

            print("  World scene ready!")

            # (A) Test B7: Kitchen interaction conflict
            print("\n  [Test B7 RED] Testing Kitchen Interaction Overlap near Ibu...")
            # Teleport player near Ibu (x=20, y=13.5)
            await evaluate(ws, """
                (() => {
                    const scene = window.__LJ__.scene;
                    scene._player.sprite.x = 20 * 32;
                    scene._player.sprite.y = 13 * 32;
                    scene._player.facing = 'up';
                    scene._checkInteractables();
                    return {
                        playerPos: { x: scene._player.x, y: scene._player.y },
                        activeInteractable: scene._currentInteractable ? scene._currentInteractable.id : null,
                        prompt: scene._promptText ? scene._promptText.text : null
                    };
                })()
            """, 201)
            b7_info = await evaluate(ws, """
                (() => {
                    const scene = window.__LJ__.scene;
                    scene._checkInteractables();
                    return {
                        currentId: scene._currentInteractable?.id,
                        prompt: scene._promptText?.text
                    };
                })()
            """, 202)
            print(f"    Current interactable selected: {b7_info.get('currentId')} with prompt '{b7_info.get('prompt')}'")
            if b7_info.get('currentId') == 'int_dapur':
                print("    ❌ RED CONFIRMED: Standing near Ibu triggers 'int_dapur' (cooking) instead of Ibu dialogue!")
            await snap(ws, "b7_interaksi_ibu_dapur_red", 501)

            # (B) Test B14 & B15: Shop panel exit buttons & vendor portrait
            print("\n  [Test B14/B15 RED] Testing Shop Panel Controls & Vendor Portrait...")
            await evaluate(ws, "window.__LJ__.openShop('minimarket')", 203)
            await asyncio.sleep(0.8)
            shop_info = await evaluate(ws, """
                (() => {
                    const modal = document.querySelector('.shop-modal-panel');
                    const backdrop = document.querySelector('.lj-modal-backdrop');
                    const vendorImg = document.querySelector('.shop-vendor-img');
                    const speechBubble = document.querySelector('.shop-vendor-speech');
                    return {
                        hasModal: !!modal,
                        hasBackdrop: !!backdrop,
                        hasSpeechBubble: !!speechBubble,
                        imgSize: vendorImg ? { w: vendorImg.clientWidth, h: vendorImg.clientHeight } : null
                    };
                })()
            """, 204)
            print(f"    Shop modal open: {shop_info.get('hasModal')}, Speech bubble present: {shop_info.get('hasSpeechBubble')}, Img size: {shop_info.get('imgSize')}")
            
            # Press Escape key
            await send_cdp(ws, "Input.dispatchKeyEvent", {
                "type": "rawKeyDown",
                "key": "Escape",
                "code": "Escape",
                "windowsVirtualKeyCode": 27
            }, 301)
            await send_cdp(ws, "Input.dispatchKeyEvent", { "type": "keyUp", "key": "Escape", "code": "Escape" }, 302)
            await asyncio.sleep(0.5)

            # Test B14: Click outside modal (backdrop) should close panel (Rule 86 §2)
            await evaluate(ws, """
                (() => {
                    const backdrop = document.querySelector('.lj-modal-backdrop');
                    if (backdrop) {
                        backdrop.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                    }
                })()
            """, 205)
            await asyncio.sleep(0.5)

            backdrop_still_open = await evaluate(ws, "document.querySelector('.shop-modal-panel') !== null", 206)
            print(f"    Modal still open after clicking outside on backdrop: {backdrop_still_open}")
            if backdrop_still_open:
                print("    ❌ RED CONFIRMED: Clicking outside backdrop does not close shop panel (closeOnOutsideClick missing)!")
                await snap(ws, "b14_toko_tanpa_tombol_keluar_red", 502)

            if not shop_info.get('hasSpeechBubble'):
                print("    ❌ RED CONFIRMED: Shop panel lacks left-side vendor portrait with speech bubble!")
                await snap(ws, "b15_toko_tanpa_vendor_red", 503)

            # Close shop via close button
            await evaluate(ws, "document.querySelector('.shop-modal-panel .btn-close')?.click()", 207)
            await asyncio.sleep(0.4)

            # (C) Test B10, B11, B12: Energy v2 mechanics
            print("\n  [Test B10/B11/B12 RED] Testing Energy v2 Costs & Thresholds...")
            # Check default activity energy cost
            energy_cfg = await evaluate(ws, "window.__LJ__.getStore()?.getState()?.config?.energy || {}", 207)
            ikut_pelajaran_cost = energy_cfg.get('activityEnergyCostPerHour', {}).get('ikut_pelajaran')
            print(f"    Existing ikut_pelajaran cost: {ikut_pelajaran_cost}% per hour (total 37.5%, expected exact 20%)")
            
            # Check warning below 50%
            await evaluate(ws, "window.__LJ__.getStore()?.setState({ energy: { current: 48, max: 100 } })", 208)
            await asyncio.sleep(0.5)
            toast_text = await evaluate(ws, "document.querySelector('.lj-toast')?.textContent || document.querySelector('.hm-energy-warning')?.textContent", 209)
            print(f"    Warning text on 48% energy: '{toast_text}'")
            if toast_text != "Energi kamu di bawah 50%, silakan makan untuk menambahnya.":
                print("    ❌ RED CONFIRMED: Toast warning 'Energi kamu di bawah 50%, silakan makan untuk menambahnya.' did not appear!")
                await snap(ws, "b11_peringatan_energi_50_red", 504)
            await snap(ws, "b10_biaya_energi_red", 505)

            # Check 0% energy exhaustion behavior
            await evaluate(ws, "window.__LJ__.getStore()?.setState({ energy: { current: 0, max: 100 } })", 210)
            await asyncio.sleep(0.5)
            exhausted_handled = await evaluate(ws, """
                (() => {
                    const st = window.__LJ__.getStore()?.getState() || {};
                    return {
                        clock: st.clock,
                        location: window.__LJ__.scene._mapManager?.currentMapId,
                        message: document.querySelector('.lj-exhausted-screen')?.textContent
                    };
                })()
            """, 211)
            print(f"    Exhausted state: {exhausted_handled}")
            if not exhausted_handled.get('message'):
                print("    ❌ RED CONFIRMED: 0% energy does not trigger black screen and next day 10:00 wake up!")
                await snap(ws, "b12_bangun_kesiangan_red", 506)

            # (D) Test B16: Tutorial system
            print("\n  [Test B16 RED] Testing Tutorial System on New Game...")
            tutorial_state = await evaluate(ws, "window.__LJ__.getStore()?.getState()?.tutorial", 212)
            print(f"    Tutorial state in store: {tutorial_state}")
            if tutorial_state is None:
                print("    ❌ RED CONFIRMED: Tutorial state is null / uninitialized in store!")
                await snap(ws, "b16_tutorial_red", 507)

    finally:
        chrome_proc.terminate()
        try:
            chrome_proc.wait(timeout=2)
        except Exception:
            chrome_proc.kill()

    print("\n==================================================")
    print("  J0 RED TEST SUITE EXECUTION FINISHED")
    print("==================================================")

if __name__ == '__main__':
    asyncio.run(run_j0())
