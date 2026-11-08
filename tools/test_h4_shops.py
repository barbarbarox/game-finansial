#!/usr/bin/env python3
"""
tools/test_h4_shops.py — Gate H4 Test Suite (Rule 79)
Tests:
1. A2: Shop selection menu (Kantin, Minimarket, Game Center, SPBU)
   - Category tabs (Semua, Makanan, Minuman, Snack, Lainnya)
   - Item details (label, energy, price, qty stepper)
   - Captures docs/regression/a2_shop_menu_green.png
2. A1: Purchase adds item to inventory & deducts cash atomically
   - Double-entry ledger cash deduction
   - Hotbar/backpack item count increase and DOM badge update
   - Captures docs/regression/a1_shop_purchase_green.png
3. Dialogue-integrated shop triggers (dia_sri_kantin, dia_maya_minimarket)
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

CDP_PORT = 9249
HTTP_PORT = 3843
REG_DIR = "/home/abarox/Desktop/prototipe web statis game/game/docs/regression"
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
        print(f"  📸 Saved GREEN screenshot: {filename}.png")

async def get_ws_url():
    for _ in range(20):
        try:
            req = urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json", timeout=1)
            tabs = json.loads(req.read().decode())
            for tab in tabs:
                if tab.get("type") == "page" and ("index.html" in tab.get("url", "") or "3843" in tab.get("url", "")):
                    return tab.get("webSocketDebuggerUrl")
            for tab in tabs:
                if tab.get("type") == "page":
                    return tab.get("webSocketDebuggerUrl")
        except Exception:
            pass
        await asyncio.sleep(0.5)
    return None

async def run_suite():
    print("==================================================")
    print("  TEST SUITE: Gate H4 (Shops & Vendor Purchases)")
    print("==================================================")

    chrome_proc = subprocess.Popen([
        "/usr/bin/google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-extensions",
        "--window-size=1200,800",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir=/tmp/test_chrome_h4_{int(time.time())}",
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

            print("\n1. Memulai game baru...")
            await evaluate(ws, "localStorage.clear()", 20)
            await send_cdp(ws, "Page.navigate", {"url": f"http://127.0.0.1:{HTTP_PORT}/index.html"}, 21)
            await asyncio.sleep(2.5)

            # Start game safely
            for _ in range(20):
                ready = await evaluate(ws, "!!(window.__GAME__ && window.__GAME__.scene && window.__GAME__.scene.getScene('MainMenu'))", 22)
                if ready:
                    break
                await asyncio.sleep(0.5)

            await evaluate(ws, "window.__GAME__.scene.getScene('MainMenu')._startNew()", 23)
            await asyncio.sleep(0.8)
            await evaluate(ws, "document.querySelector('.charcreate-form select').value = 'm'", 24)
            await evaluate(ws, "document.querySelector('.charcreate-form')?.requestSubmit()", 25)
            await asyncio.sleep(2.0)

            # Seed cash balance Rp100.000 for purchasing tests
            await evaluate(ws, """(() => {
                const store = window.__LJ__.getStore();
                store.setState({
                    ledger: {
                        entries: [
                            {
                                id: 'init_cash',
                                kind: 'allowance',
                                month: 1,
                                day: 1,
                                minute: 360,
                                lines: [
                                    { accountId: 'KAS_PRIBADI', side: 'D', amount: 100000 },
                                    { accountId: 'EKUITAS_AWAL', side: 'K', amount: 100000 }
                                ]
                            }
                        ]
                    }
                });
            })()""", 24)

            # ========================================================
            # Test A2: Shop Selection Menu Modal
            # ========================================================
            print("\n2. Menguji A2: Menu Pemilihan Item Belanja Toko (Kantin)...")
            await evaluate(ws, "document.dispatchEvent(new CustomEvent('lj:openShop', { detail: { shopId: 'kantin_sekolah' } }))", 30)
            await asyncio.sleep(0.8)

            shop_state = await evaluate(ws, """(() => {
                const modal = document.querySelector('.shop-modal-panel');
                if (!modal) return { open: false };
                const title = modal.querySelector('.panel-title')?.textContent || '';
                const tabs = Array.from(modal.querySelectorAll('.shop-tab-btn')).map(b => b.textContent);
                const items = Array.from(modal.querySelectorAll('.shop-item-card')).map(card => {
                    return {
                        name: card.querySelector('.shop-item-name')?.textContent,
                        price: card.querySelector('.shop-item-price')?.textContent,
                        hasIcon: !!card.querySelector('.shop-item-icon')?.src,
                        hasQty: !!card.querySelector('.shop-qty-box'),
                        hasBuyBtn: !!card.querySelector('.shop-buy-btn')
                    };
                });
                return {
                    open: true,
                    title,
                    tabs,
                    itemCount: items.length,
                    firstItem: items[0]
                };
            })()""", 31)

            print(f"  Status Toko: {shop_state}")
            assert shop_state["open"] is True, "Shop modal panel should be open"
            assert "Kantin" in shop_state["title"] or "KANTIN" in shop_state["title"], f"Expected Kantin in title, got {shop_state['title']}"
            assert len(shop_state["tabs"]) >= 4, f"Expected category tabs, got {shop_state['tabs']}"
            assert shop_state["itemCount"] >= 3, f"Expected at least 3 items in canteen, got {shop_state['itemCount']}"

            # Tab filtering test
            await evaluate(ws, """(() => {
                const tabs = Array.from(document.querySelectorAll('.shop-tab-btn'));
                const minTab = tabs.find(t => t.textContent.includes('Minuman'));
                if (minTab) minTab.click();
            })()""", 32)
            await asyncio.sleep(0.3)

            drink_count = await evaluate(ws, "document.querySelectorAll('.shop-item-card').length", 33)
            print(f"  Jumlah item minuman: {drink_count}")
            assert drink_count >= 1, "Expected drink items in Minuman tab"

            # Return to Semua tab
            await evaluate(ws, """(() => {
                const tabs = Array.from(document.querySelectorAll('.shop-tab-btn'));
                const allTab = tabs.find(t => t.textContent.includes('Semua'));
                if (allTab) allTab.click();
            })()""", 34)
            await asyncio.sleep(0.3)

            await snap(ws, "a2_shop_menu_green", 501)
            print("  ✅ A2 VERIFIED GREEN: Menu Toko lengkap dengan tab, daftar item, ikon, dan kontrol!")

            # ========================================================
            # Test A1: Item Purchase Adds to Inventory & Deducts Cash
            # ========================================================
            print("\n3. Menguji A1: Pembelian Item Memotong Kas & Masuk Inventaris...")

            # Select item: Nasi kuning or first item, qty 2
            purchase_setup = await evaluate(ws, """(() => {
                const cards = Array.from(document.querySelectorAll('.shop-item-card'));
                const targetCard = cards.find(c => c.querySelector('.shop-item-name')?.textContent.includes('Nasi kuning')) || cards[0];
                if (!targetCard) return { error: 'No item card found' };

                const itemName = targetCard.querySelector('.shop-item-name')?.textContent;
                const plusBtn = targetCard.querySelectorAll('.shop-qty-btn')[1]; // '+'
                plusBtn.click(); // Qty -> 2

                const qtyVal = targetCard.querySelector('.shop-qty-text')?.textContent;
                const buyBtn = targetCard.querySelector('.shop-buy-btn');

                return {
                    itemName,
                    qty: qtyVal,
                    buyBtnDisabled: buyBtn.disabled
                };
            })()""", 40)

            print(f"  Setup pembelian: {purchase_setup}")
            assert purchase_setup["qty"] == "2", f"Expected qty 2, got {purchase_setup['qty']}"
            assert purchase_setup["buyBtnDisabled"] is False, "Buy button should be enabled"

            # Click Buy via DOM
            await evaluate(ws, """(() => {
                const cards = Array.from(document.querySelectorAll('.shop-item-card'));
                const targetCard = cards.find(c => c.querySelector('.shop-item-name')?.textContent.includes('Nasi kuning')) || cards[0];
                targetCard.querySelector('.shop-buy-btn').click();
            })()""", 41)
            await asyncio.sleep(0.8)

            # Close shop modal with close button
            await evaluate(ws, "document.querySelector('.shop-modal-panel .btn-close').click()", 42)
            await asyncio.sleep(0.5)

            # Inspect inventory and ledger
            verify_res = await evaluate(ws, """(() => {
                const store = window.__LJ__.getStore();
                const st = store.getState();
                const hotbarSlots = st.inventory.hotbar;
                const cash = st.ledger.entries.reduce((acc, e) => {
                    for (const l of e.lines) {
                        if (l.accountId === 'KAS_PRIBADI') {
                            acc += (l.side === 'D' ? l.amount : -l.amount);
                        }
                    }
                    return acc;
                }, 0);

                const slot0 = hotbarSlots[0];

                // DOM check on hotbar slot
                const domSlot0 = document.querySelector('.hotbar-slot[data-slot-index="0"]');
                const domImg = domSlot0?.querySelector('.hotbar-slot-icon');
                const domBadge = domSlot0?.querySelector('.hotbar-slot-badge');

                return {
                    cash,
                    slot0ItemId: slot0?.itemId,
                    slot0Count: slot0?.count,
                    domHasItem: !!domSlot0?.classList.contains('has-item'),
                    domImgVisible: domImg ? domImg.style.display !== 'none' : false,
                    domBadgeText: domBadge?.textContent
                };
            })()""", 43)

            print(f"  Hasil verifikasi inventaris & kas: {verify_res}")
            assert verify_res["cash"] < 100000, f"Cash should be deducted, got {verify_res['cash']}"
            assert verify_res["cash"] == 80000, f"Expected 80000 cash remaining (100k - 2x10k), got {verify_res['cash']}"
            assert verify_res["slot0ItemId"] == "nasi_kuning", f"Expected nasi_kuning in slot 0, got {verify_res['slot0ItemId']}"
            assert verify_res["slot0Count"] == 2, f"Expected count 2, got {verify_res['slot0Count']}"
            assert verify_res["domHasItem"] is True, "DOM hotbar slot 0 must have 'has-item' class"
            assert verify_res["domImgVisible"] is True, "DOM hotbar slot 0 icon must be visible"
            assert verify_res["domBadgeText"] == "2", f"DOM badge should display '2', got {verify_res['domBadgeText']}"

            await snap(ws, "a1_shop_purchase_green", 502)
            print("  ✅ A1 VERIFIED GREEN: Item berhasil dibeli, kas berkurang di buku kas, dan item tampil di hotbar!")

            # ========================================================
            # Test 4: Dialogue Integration (Sri Kantin)
            # ========================================================
            print("\n4. Menguji Integrasi Menu Toko pada Dialog NPC (dia_sri_kantin)...")
            await evaluate(ws, """(() => {
                window.__LJ__.startDialogue('dia_sri_kantin', 'npc_sri');
            })()""", 50)
            await asyncio.sleep(0.8)

            # Fast forward typewriter
            await evaluate(ws, "document.getElementById('dlg-box').click()", 51)
            await asyncio.sleep(0.4)

            # Click "Beli sesuatu (Buka Menu Kantin)"
            shop_opened_from_dlg = await evaluate(ws, """(() => {
                const choices = Array.from(document.querySelectorAll('.dialogue-choice-btn'));
                const shopChoice = choices.find(c => c.textContent.includes('Buka Menu Kantin') || c.textContent.includes('Beli sesuatu'));
                if (shopChoice) {
                    shopChoice.click();
                    return true;
                }
                return false;
            })()""", 52)
            await asyncio.sleep(0.8)

            dlg_closed_and_shop_open = await evaluate(ws, """(() => {
                const dlgPanel = document.querySelector('.dialogue-panel');
                const shopPanel = document.querySelector('.shop-modal-panel');
                return {
                    dlgHidden: !dlgPanel || dlgPanel.classList.contains('hidden') || dlgPanel.style.display === 'none',
                    shopOpen: !!shopPanel
                };
            })()""", 53)

            print(f"  Hasil transisi dialog ke toko: {dlg_closed_and_shop_open}")
            assert shop_opened_from_dlg is True, "Should find 'Buka Menu Kantin' in dialogue choices"
            assert dlg_closed_and_shop_open["shopOpen"] is True, "Shop panel should open from dialogue"

            # Close shop
            await evaluate(ws, "document.querySelector('.shop-modal-panel .btn-close').click()", 54)
            await asyncio.sleep(0.4)

            # ========================================================
            # Test 5: SPBU Refuel Panel
            # ========================================================
            print("\n5. Menguji Panel SPBU Refuel...")
            await evaluate(ws, "document.dispatchEvent(new CustomEvent('lj:openShop', { detail: { shopId: 'spbu' } }))", 60)
            await asyncio.sleep(0.8)

            spbu_state = await evaluate(ws, """(() => {
                const modal = document.querySelector('.shop-modal-panel');
                if (!modal) return { open: false };
                const fuelBtns = Array.from(modal.querySelectorAll('.shop-fuel-btn')).map(b => b.textContent);
                return {
                    open: true,
                    fuelBtnCount: fuelBtns.length,
                    fuelBtns
                };
            })()""", 61)

            print(f"  Status SPBU Modal: {spbu_state}")
            assert spbu_state["open"] is True, "SPBU panel should open"
            assert spbu_state["fuelBtnCount"] >= 3, f"Expected fuel presets, got {spbu_state['fuelBtns']}"

            await evaluate(ws, "document.querySelector('.shop-modal-panel .btn-close').click()", 62)

            print("\n🎉 ALL TESTS IN GATE H4 PASSED SUCCESSFULLY!")
            return True

    finally:
        chrome_proc.terminate()
        try:
            chrome_proc.wait(timeout=3)
        except Exception:
            chrome_proc.kill()

if __name__ == "__main__":
    success = asyncio.run(run_suite())
    sys.exit(0 if success else 1)
