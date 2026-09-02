import os
import httpx
import yt_dlp
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# Ultra-fast HTTP client using HTTP/2 and persistent pooling
http_client = httpx.Client(
    http2=True,
    timeout=httpx.Timeout(3.0, connect=1.5),
    limits=httpx.Limits(max_keepalive_connections=100, max_connections=200),
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
)

UI = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<link rel="manifest" href="/manifest.json">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#00ff66">
<title>TT Videos</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:system-ui,-apple-system,sans-serif}
body{background:#000;color:#fff;display:flex;justify-content:center;min-height:100vh;padding:12px}
.app{width:100%;max-width:440px;display:flex;flex-direction:column;gap:16px}

/* Header Navbar */
.nav{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;background:#050505;border:1px solid #00ff6644;border-radius:18px;box-shadow:0 0 12px #00ff6633,inset 0 0 12px #00ff6611}
.nav-btn{width:38px;height:38px;border-radius:12px;border:1px solid #00ff66;background:#00ff6610;display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 0 10px #00ff6688;transition:0.2s}
.nav-btn:active{transform:scale(0.92)}
.nav-title{color:#00ff66;font-weight:900;letter-spacing:2px;font-size:16px;text-shadow:0 0 10px #00ff66,0 0 20px #00ff66}

/* Search Input */
.search-box{display:flex;align-items:center;background:#080808;border:1px solid #00ff6688;border-radius:30px;padding:6px 8px 6px 16px;gap:10px;box-shadow:0 0 15px #00ff6644}
.search-box svg{width:18px;height:18px;fill:none;stroke:#00ff66;stroke-width:2.5;filter:drop-shadow(0 0 4px #00ff66)}
.search-box input{flex:1;background:transparent;border:0;color:#fff;font-size:13px;outline:none}
.go-btn{background:#00ff66;color:#000;font-weight:900;border:0;border-radius:20px;padding:8px 18px;font-size:13px;cursor:pointer;box-shadow:0 0 15px #00ff66,0 0 30px #00ff66aa;transition:0.2s}

/* Tabs */
.tabs{display:flex;background:#080808;border:1px solid #00ff6644;border-radius:30px;padding:4px;gap:4px}
.tab-btn{flex:1;display:flex;align-items:center;justify-content:center;gap:8px;padding:10px;border-radius:24px;border:0;background:transparent;color:#00ff66;font-weight:800;font-size:13px;cursor:pointer;transition:0.2s}
.tab-btn svg{width:16px;height:16px;fill:currentColor}
.tab-btn.active{background:#00ff66;color:#000;box-shadow:0 0 20px #00ff66,0 0 35px #00ff66aa}

/* Progress Bar */
.progress-box{display:none;flex-direction:column;gap:6px;margin-top:4px}
.progress-text-wrap{display:flex;justify-content:space-between;font-size:11px;color:#00ff66;font-weight:700;text-shadow:0 0 6px #00ff66}
.progress-container{width:100%;height:8px;background:#111;border-radius:10px;border:1px solid #00ff6644;overflow:hidden}
.progress-bar{width:0%;height:100%;background:#00ff66;box-shadow:0 0 12px #00ff66,0 0 24px #00ff66;transition:width 0.1s linear}

/* Media Card */
.card{background:#090909;border:1px solid #00ff6644;border-radius:20px;padding:16px;display:flex;flex-direction:column;gap:14px;box-shadow:0 0 15px #00ff6622}
.card-header{display:flex;gap:12px;align-items:center}
.thumb{width:80px;height:55px;border-radius:10px;background:#151515;object-fit:cover;border:1px solid #00ff6644}
.card-info{flex:1;min-width:0}
.card-info .title{font-size:12px;font-weight:700;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.card-info .sub{font-size:10px;color:#00ff66aa;margin-top:4px}

/* Action Buttons */
.actions{display:flex;gap:10px}
.act-btn{flex:1;display:flex;align-items:center;justify-content:center;gap:6px;padding:12px;border-radius:24px;border:0;font-weight:800;font-size:12px;cursor:pointer;transition:0.2s;text-decoration:none}
.act-btn svg{width:14px;height:14px;fill:currentColor}
.btn-play{background:#000;color:#fff;border:1px solid #00ff6688;box-shadow:inset 0 0 8px #00ff6633}
.btn-dl{background:#00ff66;color:#000;box-shadow:0 0 18px #00ff66,0 0 30px #00ff66aa}
</style>
</head>
<body>

<div class="app">
  <div class="nav">
    <button class="nav-btn" onclick="shareApp()" title="Share App">
      <svg viewBox="0 0 24 24" width="18" height="18" stroke="#00ff66" stroke-width="2.5" fill="none"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
    </button>
    <div class="nav-title">TikTok Video Downloader</div>
    <button class="nav-btn" id="installBtn" onclick="installApp()" title="Install App">
      <svg viewBox="0 0 24 24" width="18" height="18" stroke="#00ff66" stroke-width="2.5" fill="none"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
    </button>
  </div>

  <div class="search-box">
    <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
    <input id="urlInput" type="text" placeholder="Paste TikTok link..." value="">
    <button class="go-btn" onclick="fetchMedia()">GO</button>
  </div>

  <div class="tabs">
    <button class="tab-btn active" id="tab-mp4" onclick="setMode('mp4')">
      <svg viewBox="0 0 24 24"><path d="M17 10.5V7a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-3.5l4 4v-11l-4 4z"/></svg>
      MP4
    </button>
    <button class="tab-btn" id="tab-mp3" onclick="setMode('mp3')">
      <svg viewBox="0 0 24 24"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
      MP3
    </button>
  </div>

  <div class="progress-box" id="pWrap">
    <div class="progress-text-wrap">
      <span id="pStatus">Fetching...</span>
      <span id="pNum">0%</span>
    </div>
    <div class="progress-container">
      <div class="progress-bar" id="pBar"></div>
    </div>
  </div>

  <div class="card" id="resultCard" style="display:none;">
    <div class="card-header">
      <img id="mediaThumb" class="thumb" src="" alt="preview">
      <div class="card-info">
        <div class="title" id="mediaTitle">Title</div>
        <div class="sub">Instant Save Enabled</div>
      </div>
    </div>
    <div class="actions">
      <button class="act-btn btn-play" onclick="playMedia()">
        <svg viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg> PLAY
      </button>
      <a id="instantDlBtn" class="act-btn btn-dl" target="_blank" download>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg> DOWNLOAD
      </a>
    </div>
    <div id="playerArea"></div>
  </div>
</div>

<script>
let currentMode = 'mp4';
let currentData = null;
let deferredPrompt = null;

// Register Service Worker for home screen Web App capability
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(()=>{});
  });
}

// Store installation trigger for top button
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
});
document.getElementById('tab-mp3').classList.toggle('active', mode === 'mp3');
}

function updateProgress(pct, statusText) {
  const pWrap = document.getElementById('pWrap');
  const pBar = document.getElementById('pBar');
  const pNum = document.getElementById('pNum');
  const pStatus = document.getElementById('pStatus');
                                                        if (pct >= 0 && pct < 100) {
    pWrap.style.display = 'flex';
    pBar.style.width = pct + '%';
    pNum.innerText = Math.round(pct) + '%';               if(statusText) pStatus.innerText = statusText;
  } else {
    pBar.style.width = '100%';
    pNum.innerText = '100%';
    if(statusText) pStatus.innerText = statusText;
    setTimeout(() => { pWrap.style.display = 'none'; pBar.style.width = '0%'; }, 400);
  }
}

async function fetchMedia() {
  const url = document.getElementById('urlInput').value.trim();
  if(!url) return;

  updateProgress(40, "Fetching...");
  try {
    updateProgress(80, "Readying...");
    const res = await fetch(`/get?url=${encodeURIComponent(url)}&mode=${currentMode}`);
    const data = await res.json();

    if (data.error) {
      updateProgress(100, "Error!");
      alert(data.error);
      return;
    }

    updateProgress(100, "Done!");
    currentData = data;
    document.getElementById('resultCard').style.display = 'flex';
    document.getElementById('mediaTitle').innerText = data.title || 'TikTok Media';
    document.getElementById('mediaThumb').src = data.cover || 'https://cdn-icons-png.flaticon.com/512/3046/3046120.png';

    // Direct stream link for high-speed download
    const dlLink = document.getElementById('instantDlBtn');
    dlLink.href = `/download?url=${encodeURIComponent(data.direct)}&filename=trip_music_${Date.now()}.${currentMode}`;

    document.getElementById('playerArea').innerHTML = '';
  } catch(e) {
    updateProgress(100, "Failed!");
    alert('Failed to process link.');
  }
}

function playMedia() {
  if(!currentData || !currentData.direct) return;
  const area = document.getElementById('playerArea');
  if(currentMode === 'mp3') {
    area.innerHTML = `<audio controls autoplay src="${currentData.direct}" style="width:100%;margin-top:10px"></audio>`;
  } else {
    area.innerHTML = `<video controls autoplay playsinline src="${currentData.direct}" style="width:100%;border-radius:10px;margin-top:10px"></video>`;
  }
}
</script>
</body>
</html>"""

@app.route("/")
def home():
    return UI

@app.route("/manifest.json")
def manifest():
    return jsonify({
        "name": "TikTok Video Downloader",
        "short_name": "TikTok Video Downloader",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#000000",
        "theme_color": "#00ff66",
        "icons": [{"src": "https://cdn-icons-png.flaticon.com/512/3046/3046120.png", "sizes": "512x512", "type": "image/png"}]
    })

@app.route("/sw.js")
def service_worker():
    return Response("self.addEventListener('fetch', function(e) {});", mimetype="application/javascript")

@app.route("/download")
def download_stream():
    media_url = request.args.get("url")
    filename = request.args.get("filename", "download.mp4")
    if not media_url:
        return "Missing URL", 400

    def generate():
        with http_client.stream("GET", media_url) as res:
            for chunk in res.iter_bytes(chunk_size=131072):
                yield chunk

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "application/octet-stream"
    }
    return Response(generate(), headers=headers)

@app.route("/get")
def get():
    url = request.args.get("url", "").strip()
    mode = request.args.get("mode", "mp4")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Sub-second fast TikWM endpoint call
    try:
        res = http_client.get(f"https://www.tikwm.com/api/?url={url}")
        if res.status_code == 200:
            data = res.json().get("data")
            if data:
                direct = data.get("play")
                if mode == "mp3":
                    direct = data.get("music")
                if direct:
                    return jsonify({
                        "direct": direct,
                        "title": data.get("title", "TikTok Media"),
                        "cover": data.get("cover") or data.get("origin_cover")
                    })
    except Exception:
        pass

    # Instant yt-dlp fallback
    try:
        opts = {'quiet': True, 'nocheckcertificate': True, 'extract_flat': True, 'skip_download': True, 'format': 'best'}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info:
                v_url = info.get("url") or (info["formats"][-1].get("url") if info.get("formats") else None)
                if v_url:
                    return jsonify({
                        "direct": v_url,
                        "title": info.get("title", "Media Stream"),
                        "cover": info.get("thumbnail")
                    })
    except Exception:
        pass

    return jsonify({"error": "Unable to resolve media link"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
