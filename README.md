# PC Remote

A lightweight web-based remote control for Windows machines. Access it from any device on your local network — tap, swipe, and type to control a PC in real time.

## Features

- **Mouse movement** via an on-screen touchpad
- **Left / right click** buttons (or double-tap the touchpad for left-click)
- **Scroll wheels** with animated visual indicators that follow your swipe direction
- **Keyboard input** — type text and press Enter to send it character by character
- **Media play/pause** button
- **Fullscreen mode** for maximum screen real estate

## Requirements

- Python 3.8+
- Windows (uses `user32.dll` for input injection)

Install dependencies:

```bash
pip install flask flask-socketio eventlet
```

## How to Use

1. Run the server on your PC in PowerShell (make sure you are in the directory pc_remote.py resides in):

   ```bash
   python pc_remote.py
   ```

2. Find your local IP (e.g., `192.168.1.?`).

3. On any phone, tablet, or browser on the same network, open:
    
   ```
   http://<your-local-ip>:5000 
   ```
   (e.g., `http://192.168.1.?:5000`)

4. Use the controls:
   - **Touchpad (center)** — drag to move cursor; double-tap for left-click
   - **Scroll rails (left & right edges)** — swipe up/down to scroll
   - **Buttons (bottom)** — Left, Right click, Play/Pause
   - **Text input** — type and press Enter to send keystrokes

## Controls Layout

```
┌─────────────────────────────┐
│  ◉ PC Remote  [Fullscreen]  │
├──────┬───────────────┬──────|
│      │               │      │
│scroll│   Touchpad    │scroll│
│ pad  │   (cursor)    │ pad  │
│      │               │      │
├──────┴─────────────┬─┴──────┤
│[◁ Left] [▶ Play] [Right ▷] │
│  ┌───────────────────────┐  │
│  │ Type here, press Enter│  │
│  └───────────────────────┘  │
│  Mouse Sensitivity: ◄━━━━━► │
└─────────────────────────────┘
```

## Notes

- The server binds to `0.0.0.0` so it is reachable from any device on the local network.
- **Not encrypted.** Only use on trusted networks.
- If the connection isn't immediately responsive, adjust the mouse sensitivity to force the connection.
