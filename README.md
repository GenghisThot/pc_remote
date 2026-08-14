# PC Remote

Turn your phone, tablet, or another computer into a wireless mouse and keyboard for your Windows PC in the style of a remote.

- **Touchpad** for mouse movement
- **Scroll rails** on both sides
- **Left / Right click buttons**
- **Media play/pause button**
- **Text input bar** — type anything and it appears on your PC
- **Adjustable mouse sensitivity slider**

---

## Quick Start

### 1. Install Python

If you don't have Python:

1. Go to [python.org](https://www.python.org/downloads/)
2. Download the latest **Python 3.x** for Windows
3. Run the installer — make sure **"Add Python to PATH"** is checked, then click **Install**


### 2. Get PC Remote

Download the file named [pc_remote.py](https://github.com/GenghisThot/pc_remote/blob/main/pc_remote.py).



### 3. Install dependencies

```powershell
pip install --upgrade flask-socketio flask
```

### 4. Start the server

```powershell
python pc_remote.py
```

You should see at the bottom of the terminal:

```
Port 5000 now open
```

### 5. Connect from your phone or tablet

Open a browser (Chrome, Safari, etc.) and go to the local IP address of the device that is running the script (step 4),
> `<host.local.ip.address>:5000` e.g. `192.168.1.?:5000` or `192.168.0.?:5000`

You need to use the **local network IP** (the one that starts with `192.` or `10.`), not `127.0.0.1` which is your loopback address.

That's all, it should be operational now. 
> Some FAQ can be answered below.

---

## How to use the controls

| Control | What it does |
|---------|-------------|
| **Touchpad (center area)** | Drag your finger to move the mouse cursor |
| **Double-tap touchpad** | Left click |
| **Left scroll rail** | Scroll up / down |
| **Right scroll rail** | Scroll up / down |
| ◁ Left button | Left click |
| Right ▷ button | Right click |
| ▶ Play button | Sends media play/pause key |
| Text bar (bottom) | Type anything, press Enter — it types on your PC |
| Sensitivity slider | Adjust how far the cursor moves (1 = slow, 10 = fast) |

---

## FAQ for beginners

### How do I find my local IP address?

Open PowerShell or Command Prompt on the PC and run:

```powershell
ipconfig
```

Look for **IPv4 Address** under your active adapter (Wi-Fi or Ethernet).

### My phone can't connect

- Make sure your phone is on the **same Wi-Fi network** as the PC
- The Windows firewall might block it. If so, try:
  ```powershell
  netsh advfirewall firewall add rule name="PC Remote" dir=in action=allow protocol=TCP localport=5000
  ```
- Use `http://` not `https://`

### How do I stop the server?

Press **Ctrl + C** in the terminal where you ran it.

---

### Requirements

| | |
|--|--|
| OS | Windows 10 / 11 (uses `user32.dll`) |
| Python | 3.8 or higher |
| Dependencies | `flask`, `flask-socketio` |
| Async engine | Auto-detected by flask-socketio (no eventlet/gevent needed) |

> You should get everything you need if you follow the steps above.


### Architecture

```
Phone browser (Socket.IO client)
        ↓  WSS / HTTP long-polling
  pc_remote.py (Flask + python-socketio server)
        ↓
  ctypes → user32.dll (mouse_event, keybd_event, VkKeyScanW)
```

All input events are injected directly into the Windows desktop. No virtual machine or remote-desktop protocol is used — just raw `user32` calls.

### Ports and binding

- Binds to `0.0.0.0:5000` (all interfaces on port 5000)
- CORS is set to `*` for LAN access from any device
- The Werkzeug dev server is used intentionally — this is a local-LAN tool, not an internet-facing app

### Socket.IO events

| Event | Direction | Payload |
|-------|-----------|---------|
| `move` | client → server | `{ dx: number, dy: number }` |
| `scroll` | client → server | `{ dy: number }` |
| `left` | client → server | *(none)* |
| `right` | client → server | *(none)* |
| `play` | client → server | *(none)* |
| `type` | client → server | `{ text: string }` |

### Security

This app has **no authentication**. Anyone on the same network who knows the IP can control your mouse and keyboard.

- It is designed for **trusted local networks only**
- Do **not** expose port 5000 to the internet (no port forwarding)

---

## Deployment beyond localhost (would NOT recommend)

This is built for local use. If you need remote or always-on hosting:

1. **Tailscale / ZeroTier** — create an encrypted overlay network between your PC and phone (recommended, no extra server config needed)
2. **Railway / Render / Fly.io** — deploy the Python server with a production runner like `gunicorn -k gthread`
3. **VPS + Gunicorn/Uvicorn** — full control; add a reverse proxy (Caddy / Nginx) in front

---
