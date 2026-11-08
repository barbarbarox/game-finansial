import subprocess
import time
import json
import urllib.request
import websocket

# Start chrome headless
chrome_cmd = [
    "google-chrome",
    "--headless=new",
    "--remote-debugging-port=9222",
    "--remote-allow-origins=*",
    "--no-sandbox",
    "--disable-gpu",
    "--window-size=1200,800"
]
proc = subprocess.Popen(chrome_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)

try:
    tabs = json.loads(urllib.request.urlopen("http://localhost:9222/json").read().decode("utf-8"))
    ws_url = tabs[0]["webSocketDebuggerUrl"]
    ws = websocket.create_connection(ws_url, timeout=10)

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

    send("Page.enable")
    maps = ['home', 'school', 'game_center', 'minimarket', 'toko_kosmetik', 'spbu']
    for m in maps:
        send("Page.navigate", {"url": f"http://localhost:3843/?scene=World&map={m}"})
        time.sleep(2.0)
        
        js = """(() => {
            const world = window.__GAME__.scene.getScene('World');
            if (!world) return { error: 'No World scene' };
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
                        placeholders.push({
                            label: textObj ? textObj.text : 'Unknown',
                            x: obj.x,
                            y: obj.y
                        });
                    } else if (hasSprite) {
                        const sp = obj.list.find(c => c.type === 'Sprite');
                        sprites.push(sp.texture.key);
                    }
                }
            }
            return {
                map: world._currentMapId,
                totalObjects: mapObjs.length,
                placeholdersCount: placeholders.length,
                placeholders,
                spritesCount: sprites.length,
                sprites: sprites.slice(0, 5)
            };
        })()"""
        res = send("Runtime.evaluate", {"expression": js, "returnByValue": True})
        val = res.get("result", {}).get("value", {})
        print(f"=== MAP: {m} ===")
        print(f"Placeholders ({val.get('placeholdersCount')}): {val.get('placeholders')}")
        print(f"Sprites ({val.get('spritesCount')}): {val.get('sprites')}")

finally:
    proc.terminate()
