from flask import Flask, render_template_string
from flask_socketio import SocketIO
import ctypes


# ── FLASK APP SETUP ───────────────────────────────────────

app = Flask(__name__)

socketio = SocketIO(
    app,
    cors_allowed_origins="*"
)


# ── WINDOWS INPUT CONTROL (mouse + keyboard injection) ────

user32 = ctypes.windll.user32


# ── HTML + CSS + JS UI ───────────────────────────────────

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PC Remote</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">

<style>
  /* ── RESET + BASE ─────────────────────── */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  html, body {
    height: 100%; overflow: hidden;
    background: linear-gradient(145deg, #0c0e14, #131622);
    color: #e4e4e7;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    display: flex; flex-direction: column;
    align-items: stretch;
    touch-action: none;
  }

  /* ── TOP BAR ─────────────────────────── */
  .topbar {
    width: 100%; padding: 8px 12px;
    display: flex; justify-content: space-between; align-items: center;
    background: rgba(255,255,255,.03);
    border-bottom: 1px solid rgba(255,255,255,.06);
  }
  .topbar .logo {
    font-size: 14px; font-weight: 600;
    letter-spacing: 3px; text-transform: uppercase;
    background: linear-gradient(90deg,#818cf8,#c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .topbar button {
    padding: 7px 16px; border-radius: 8px;
    background: rgba(255,255,255,.07);
    color:#ccc; font-size:13px; cursor:pointer;
    transition: background .2s;
    border: 1px solid rgba(255,255,255,.08);
  }
  .topbar button:hover { background: rgba(255,255,255,.14); color:#fff; }

  /* ── MAIN GRID ──────────────────────── */
  .main {
    flex: 1;
    display: grid;
    grid-template-columns: 0.4fr 4.8fr 0.4fr;
    gap: 4px;
    align-items: center;
    justify-content: stretch;
    padding: 0 2px;
    width: 100%;
  }

  /* scroll rails */
  .scroll-rail {
    height: 65vh; border-radius: 14px;
    background: linear-gradient(145deg, rgba(255,255,255,.06), rgba(255,255,255,.02));
    border: 1px solid rgba(255,255,255,.08);
    position: relative; overflow: hidden;
    box-shadow: inset 0 0 10px rgba(0,0,0,.2), 0 0 5px rgba(0,0,0,.3);
  }
  .scroll-rail::after {
    content:''; position:absolute;
    width:6px; height:40%; border-radius:3px;
    background: rgba(129,140,248,.5);
    left:50%; transform:translateX(-50%);
    top: var(--indicator-top, 30%);
    transition: top .1s ease-out;
  }

  /* touchpad */
  #touchpad {
    width: 100%; height: 65vh;
    border-radius: 30px;
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,255,255,.07);
    position: relative; overflow:hidden;
    box-shadow: inset 0 0 40px rgba(129,140,248,.06);
  }

  /* cursor dot */
  .cursor-dot {
    width:10px; height:10px; border-radius:50%;
    background:#818cf8;
    position:absolute;
    left:50%; top:50%; transform:translate(-50%,-50%);
    pointer-events:none;
    box-shadow:0 0 12px rgba(129,140,248,.6);
    transition: opacity .3s;
  }

  /* ── BOTTOM BAR — buttons + input ─── */
  .bottom {
    width:100%; padding:8px 6px 12px;
    display:flex; flex-direction:column;
    align-items:center;
    background: rgba(255,255,255,.03);
    border-top: 1px solid rgba(255,255,255,.06);
    gap: 8px;
  }

  .btn-row { display:flex; gap:6px; width:100%; max-width:none; justify-content:center; flex-wrap:wrap; }

  .ctrl-btn {
    flex:1; min-width:72px; padding:13px 0;
    border-radius:12px;
    background: rgba(255,255,255,.06);
    color:#ddd; font-size:14px; cursor:pointer;
    border: 1px solid rgba(255,255,255,.08);
    transition: background .18s, transform .12s;
    user-select:none;
  }
  .ctrl-btn:hover { background:rgba(255,255,255,.13); color:#fff; }
  .ctrl-btn:active {
    transform: scale(.94);
    background: rgba(129,140,248,.25);
  }

  #keyboardInput {
    width:92%; max-width:none;
    padding: 12px 14px; font-size:15px;
    border-radius:12px;
    border: 1px solid rgba(129,140,248,.3);
    background: rgba(255,255,255,.05);
    color:#fff; outline:none;
    transition: border-color .2s;
  }
  #keyboardInput:focus { border-color: rgba(129,140,248,.7); }
  #keyboardInput::placeholder { color:#666; }

  /* ── CONNECTION STATUS TOAST ──────── */
  .toast {
    position: fixed; bottom: 16px; left: 50%; transform: translateX(-50%);
    padding: 6px 14px; border-radius: 8px; font-size: 12px;
    pointer-events:none; opacity:0; transition: opacity .3s;
  }
  .toast.show { opacity:1; }
  .toast.ok   { background:#22c55e3b; color:#4ade80; }
  .toast.fail { background:#ef44443b; color:#f87171; }

</style>
</head>

<body>

<!-- TOP BAR -->
<div class="topbar">
    <span class="logo">◉ PC Remote</span>
    <button onclick="toggleFullscreen()">⛶ Fullscreen</button>
</div>

<!-- MAIN CONTROLS -->
<div class="main">
    <div id="leftscroll"   class="scroll-rail"></div>
    <div id="touchpad"><div class="cursor-dot"></div></div>
    <div id="rightscroll"  class="scroll-rail"></div>
</div>

<!-- BOTTOM BAR -->
<div class="bottom">
    <div class="btn-row">
        <button class="ctrl-btn" onclick="leftClick()">◁ Left</button>
        <button class="ctrl-btn" onclick="playPause()">▶ Play</button>
        <button class="ctrl-btn" onclick="rightClick()">Right ▷</button>
    </div>
    <input id="keyboardInput"
           type="text"
           placeholder="Type here, press Enter …"
           onkeydown="if(event.key==='Enter'){sendKeys()}">
    <div style="margin-top:6px; width:92%; max-width:none;">
        <label for="sensitivitySlider" style="display:block; margin-bottom:4px;">Mouse Sensitivity:</label>
        <input type="range" id="sensitivitySlider" min="1" max="10" step="0.1" value="3.5" 
               oninput="setSensitivity(this.value)" style="width:100%">
    </div>
</div>

<!-- STATUS TOAST -->
<div class="toast" id="toast"></div>

<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>

<script>
const socket = io();


// ── ELEMENT REFERENCES ────────────────

const pad        = document.getElementById("touchpad");
const leftscroll  = document.getElementById("leftscroll");
const rightscroll = document.getElementById("rightscroll");
const cursorDot   = pad.querySelector(".cursor-dot");
const toast       = document.getElementById("toast");


// ── TOAST HELPER ─────────────────────

function showToast(msg, type) {
    toast.textContent = msg;
    toast.className = "toast " + type + " show";
    setTimeout(() => toast.classList.remove("show"), 2000);
}


// ── SCROLL INDICATOR STATE ─────────────

let leftIndicatorPos  = 30;
let rightIndicatorPos = 30;
const indicatorResetTimer = 2500;
let leftReset, rightReset;

function moveIndicator(el, pct) {
    el.querySelector('::after') || null; // no-op, just for clarity
    const after = getComputedStyle(el);
    // we set a CSS custom property so the ::after can read it
    el.style.setProperty('--indicator-top', pct + '%');
}

function showIndicator(rail, pos) {
    pos = Math.max(5, Math.min(92, pos)); // clamp within rail (leave 8% for height)
    rail.style.setProperty('--indicator-top', pos + '%');
}
socket.on("disconnect",() => showToast("Disconnected","fail"));


// ── MOUSE STATE TRACKING ─────────────

let lastX = 0, lastY = 0;
let lastLeftScrollY  = 0, lastRightScrollY = 0;
let dotX = pad.clientWidth / 2, dotY = pad.clientHeight / 2;

// ── DOUBLE-TAP TRACKING ───────────────

let lastTapTime = 0;
const TAP_THRESHOLD = 300; // ms


// ── TOUCHPAD MOVEMENT (MOUSE MOVE) ───

pad.addEventListener("touchstart", e => {
    e.preventDefault();
    const now = Date.now();
    if (now - lastTapTime < TAP_THRESHOLD) {
        // double-tap → left click
        socket.emit("left");
        cursorDot.style.transform = "translate(-50%, -50%) scale(1.5)";
        setTimeout(() => {
            cursorDot.style.opacity = "0";
            cursorDot.style.transform = "translate(-50%, -50%) scale(1)";
        }, 150);
        setTimeout(() => cursorDot.style.opacity = "1", 300);
    }
    lastTapTime = now;

    const t = e.touches[0];
    lastX = t.clientX;
    lastY = t.clientY;
});

pad.addEventListener("touchmove", e => {
    e.preventDefault();
    const t = e.touches[0];

    let dx = (t.clientX - lastX) * sensitivity;
    let dy = (t.clientY - lastY) * sensitivity;

    if (Math.abs(dx) < 1 && Math.abs(dy) < 1) return;

    socket.emit("move", { dx, dy });

    // track cursor dot inside pad
    dotX += t.clientX - lastX;
    dotY += t.clientY - lastY;
    // clamp to pad bounds
    dotX = Math.max(5, Math.min(pad.clientWidth - 5, dotX));
    dotY = Math.max(5, Math.min(pad.clientHeight - 5, dotY));
    cursorDot.style.left = dotX + "px";
    cursorDot.style.top  = dotY + "px";

    lastX = t.clientX;
    lastY = t.clientY;
}, { passive: false });


// ── LEFT SCROLL WHEEL ────────────────

leftscroll.addEventListener("touchstart", e => {
    lastLeftScrollY = e.touches[0].clientY;
});

leftscroll.addEventListener("touchmove", e => {
    e.preventDefault();
    let dy = e.touches[0].clientY - lastLeftScrollY;
    if (Math.abs(dy) < 1) return;
    // move indicator — swipe up (dy<0) → scroll down → indicator goes down
    leftIndicatorPos += dy * 0.4;
    showIndicator(leftscroll, leftIndicatorPos);
    clearTimeout(leftReset);
    leftReset = setTimeout(() => {
        leftIndicatorPos = 30;
        showIndicator(leftscroll, leftIndicatorPos);
    }, indicatorResetTimer);
    socket.emit("scroll", { dy });
    lastLeftScrollY = e.touches[0].clientY;
}, { passive: false });


// ── RIGHT SCROLL WHEEL ───────────────

rightscroll.addEventListener("touchstart", e => {
    lastRightScrollY = e.touches[0].clientY;
});

rightscroll.addEventListener("touchmove", e => {
    e.preventDefault();
    let dy = e.touches[0].clientY - lastRightScrollY;
    if (Math.abs(dy) < 1) return;
    rightIndicatorPos += dy * 0.4;
    showIndicator(rightscroll, rightIndicatorPos);
    clearTimeout(rightReset);
    rightReset = setTimeout(() => {
        rightIndicatorPos = 30;
        showIndicator(rightscroll, rightIndicatorPos);
    }, indicatorResetTimer);
    socket.emit("scroll", { dy });
    lastRightScrollY = e.touches[0].clientY;
}, { passive: false });


// ── BUTTON ACTIONS ───────────────────

function leftClick()  { socket.emit("left");  }
function rightClick() { socket.emit("right"); }
function playPause()  { socket.emit("play");  }

function toggleFullscreen(){
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
    } else {
        document.exitFullscreen();
    }
}


// ── TEXT SEND ────────────────────────

function sendKeys(){
    const text = document.getElementById("keyboardInput").value;
    if (!text) return;
    socket.emit("type", { text });
    document.getElementById("keyboardInput").value = "";
    showToast("Typed: " + text, "ok");
}

// ── SENSITIVITY ADJUSTMENT ───────────

function setSensitivity(value) {
    const val = parseFloat(value);
    if (isNaN(val) || val < 1 || val > 10) {
        showToast("Invalid sensitivity. Must be between 1 and 10.", "fail");
        return;
    }
    sensitivity = val;
    showToast("Sensitivity set to: " + value, "ok");
}
</script>
</body>
</html>
"""


# ── ROUTE ─────────────────────────────

@app.route("/")
def index():
    return render_template_string(HTML)


# ── SERVER-SIDE INPUT HANDLERS ────────

@socketio.on("move")
def move(data):
    try:
        dx = int(float(data["dx"]))
        dy = int(float(data["dy"]))
        user32.mouse_event(0x0001, dx, dy, 0, 0)
    except (ValueError, TypeError) as e:
        print(f"Invalid movement data: {e}")


@socketio.on("scroll")
def scroll(data):
    try:
        dy = int(float(data["dy"]) * 4)
        user32.mouse_event(0x0800, 0, 0, -dy, 0)
    except (ValueError, TypeError) as e:
        print(f"Invalid scroll data: {e}")


@socketio.on("left")
def left():
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    user32.mouse_event(0x0004, 0, 0, 0, 0)


@socketio.on("right")
def right():
    user32.mouse_event(0x0008, 0, 0, 0, 0)
    user32.mouse_event(0x0010, 0, 0, 0, 0)


@socketio.on("play")
def play():
    try:
        user32.keybd_event(0xB3, 0, 0, 0)
    except Exception as e:
        print(f"Error sending play/pause: {e}")


@socketio.on("type")
def type_text(data):
    text = data.get("text", "")
    for char in text:
        try:
            vk = user32.VkKeyScanW(ord(char))
            keycode = vk & 0xff
            shift = (vk >> 8) & 0xff

            if shift & 1:
                user32.keybd_event(0x10, 0, 0, 0)

            user32.keybd_event(keycode, 0, 0, 0)
            user32.keybd_event(keycode, 0, 2, 0)

            if shift & 1:
                user32.keybd_event(0x10, 0, 2, 0)
        except Exception as e:
            print(f"Error typing character '{char}': {e}")


# ── RUN SERVER ────────────────────────

if __name__ == "__main__":
    # Suppress Werkzeug 3.x persistent warning (harmless for local LAN)
    import warnings
    warnings.filterwarnings("ignore", message=r".*development server.*")

    print("Port 5000 now open")
    socketio.run(app, host="0.0.0.0", port=5000)